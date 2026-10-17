#!/usr/bin/env python3
"""Offline descriptive replay of three pinned M100 parquet members.

No downloads, persistent input database, imputation, or physical/pooling inference.
Python 3.10+ and an already installed DuckDB 1.4.1 are required.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import time


INPUTS = {
    "ps0_input_power": ("ps0_input_power__a_0.parquet", 2830525,
        "a2e9925ed8590d3096ba9e2d78039ad3a6a9b7e541b5fe94f0a910720194095e"),
    "ps1_input_power": ("ps1_input_power__a_0.parquet", 2896957,
        "370340c4f330d6efcfc266bfa315cc9206884621243248af0ebdd61f5c8aca35"),
    "total_power": ("total_power__a_0.parquet", 2511767,
        "7cd3425bac3dfaebe804299b39742ee084df8af34d16d7549f470dc2ae20c51e"),
}
# These are comparison targets, never inputs to the descriptive computations.
# Sources: preserved M100_RANGE_INTAKE, PANEL_INSPECTION, PANEL_SUPPLEMENT reports.
ACCEPTED = {
    "rows": {"ps0_input_power": 4787828, "ps1_input_power": 4787831,
             "total_power": 4750202},
    "psu_pairs": 4787824,
    "triple_rows": 4750202,
    "triple_delta_min_w": -1290,
    "triple_delta_max_w": 910,
    "triple_delta_mean_w": -160.62955217483383,
    "triple_delta_median_w": -150.0,
    "all980_times": {"total_power": 965, "psu_sum": 1722},
    "all980_longest_run_cells": {"total_power": 1, "psu_sum": 71},
    "global_max_gap_ns": 184880000000000,
}
NS_PER_MS = 1_000_000
CADENCE_NS = 20_000_000_000
NODES = 980


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def query(connection, sql: str, parameters=None) -> list[dict]:
    cursor = connection.execute(sql, parameters or [])
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def times_summary(times: list[int]) -> dict:
    """Exact nanosecond keys; a run has endpoints separated by (cells-1)*20s."""
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("Timeline must be strictly increasing and deduplicated")
    run = best = int(bool(times))
    start = best_start = times[0] if times else None
    for previous, current in zip(times, times[1:]):
        if current - previous == CADENCE_NS:
            run += 1
        else:
            run, start = 1, current
        if run > best:
            best, best_start = run, start
    best_last = best_start + (best - 1) * CADENCE_NS if best else None
    return {
        "count": len(times),
        "first_ms": times[0] // NS_PER_MS if times else None,
        "last_ms": times[-1] // NS_PER_MS if times else None,
        "first_two_ms": [t // NS_PER_MS for t in times[:2]],
        "longest_postselected_exact20s_run": {
            "cells": best,
            "first_ms": best_start // NS_PER_MS if best else None,
            "last_ms": best_last // NS_PER_MS if best else None,
            "elapsed_seconds": (best - 1) * 20 if best else 0,
        },
    }


def validate_inputs(raw_dir: Path) -> tuple[list[dict], dict[str, Path]]:
    records, paths = [], {}
    for metric, (name, size, expected_hash) in INPUTS.items():
        path = raw_dir / name
        if not path.is_file():
            raise ValueError(f"Required local input is absent: {name}")
        record = {"metric": metric, "filename": name, "bytes": path.stat().st_size,
                  "sha256": sha256(path), "expected_bytes": size,
                  "expected_sha256": expected_hash}
        if record["bytes"] != size or record["sha256"] != expected_hash:
            raise ValueError(f"Pinned input mismatch: {name}; got {record}")
        records.append(record)
        paths[metric] = path
    return records, paths


def analyze(connection, paths: dict[str, Path]) -> dict:
    report = {"schema": []}
    parts = []
    for index, (metric, path) in enumerate(paths.items()):
        view = f"input_{index}"
        connection.read_parquet(str(path)).create_view(view)
        columns = query(connection, f"DESCRIBE {view}")
        actual = {r["column_name"]: r["column_type"] for r in columns}
        expected = {"timestamp": "TIMESTAMP WITH TIME ZONE",
                    "value": "INTEGER", "node": "VARCHAR"}
        if actual != expected:
            raise ValueError(f"Unexpected schema for {metric}: {actual}")
        report["schema"].append({"metric": metric, "columns": columns})
        parts.append(f"SELECT '{metric}' AS metric, node, "
                     f"epoch_ns(timestamp) AS t, value::BIGINT AS v FROM {view}")
    connection.execute("CREATE VIEW raw AS " + " UNION ALL ".join(parts))
    report["raw_by_metric"] = query(connection, """
        SELECT metric, count(*) AS rows, count(DISTINCT node) AS nodes,
          min(t)//1000000 AS first_ms, max(t)//1000000 AS last_ms,
          count(*) FILTER(WHERE node IS NULL) AS null_node,
          count(*) FILTER(WHERE t IS NULL) AS null_time,
          count(*) FILTER(WHERE v IS NULL) AS null_value,
          count(*) FILTER(WHERE v<0) AS negative_value,
          count(*) FILTER(WHERE v=0) AS zero_value,
          count(*) FILTER(WHERE try_cast(node AS INTEGER) NOT BETWEEN 0 AND 979
            OR try_cast(node AS INTEGER) IS NULL) AS unmapped_node,
          count(*) FILTER(WHERE node != cast(try_cast(node AS INTEGER) AS VARCHAR))
            AS noncanonical_node,
          count(*) FILTER(WHERE t%1000000000<>0) AS subsecond_rows,
          count(*) FILTER(WHERE t%1000000<>0) AS submillisecond_rows,
          min(v) AS min_w, max(v) AS max_w,
          quantile_cont(v,[0.01,0.5,0.99]) AS quantile_w,
          count(DISTINCT v) AS distinct_w,
          count(*) FILTER(WHERE v%100=0) AS multiple100_w
        FROM raw GROUP BY metric ORDER BY metric
    """)
    # Group before joining: exact duplicates never multiply pair/triple counts.
    connection.execute("""CREATE TABLE cells AS
        SELECT metric,node,t,count(*) AS multiplicity,count(v) AS nonnull_count,
               min(v) AS lo,max(v) AS hi FROM raw GROUP BY metric,node,t""")
    report["keys_by_metric"] = query(connection, """
        SELECT metric,count(*) AS distinct_keys,
          count(*) FILTER(WHERE multiplicity>1) AS duplicated_keys,
          sum(multiplicity-1) AS extra_rows,
          count(*) FILTER(WHERE lo<>hi) AS conflicting_keys,
          count(*) FILTER(WHERE nonnull_count=0) AS all_null_keys,
          count(*) FILTER(WHERE nonnull_count>0 AND nonnull_count<multiplicity)
            AS null_mixed_keys, max(multiplicity) AS max_multiplicity
        FROM cells GROUP BY metric ORDER BY metric
    """)
    connection.execute("""CREATE TABLE clean AS
        SELECT metric,node,t,lo AS v FROM cells
        WHERE node IS NOT NULL AND t IS NOT NULL AND lo=hi AND lo>=0""")
    connection.execute("DROP TABLE cells")
    report["clean_policy"] = (
        "Collapse exact node/metric/nanosecond duplicates. Exclude conflicting, "
        "all-null, negative, null-node and null-time keys. Retain a mixed-null "
        "key only if all nonnull values agree; count those keys separately. "
        "No rounding, imputation, health-state filtering or upper-value cutoff.")
    report["phase_counts"] = query(connection, """
        SELECT metric,t%20000000000 AS nanosecond_phase20s,count(*) AS cells
        FROM clean GROUP BY metric,nanosecond_phase20s ORDER BY metric,2
    """)
    report["global_max_gap_by_metric"] = query(connection, """
        WITH times AS (SELECT DISTINCT metric,t FROM clean),
        gaps AS (SELECT metric,lag(t) OVER(PARTITION BY metric ORDER BY t)
                 AS from_ns,t AS to_ns FROM times),
        ranked AS (SELECT *,to_ns-from_ns AS gap_ns,
                   row_number() OVER(PARTITION BY metric
                   ORDER BY to_ns-from_ns DESC NULLS LAST,from_ns) AS pos FROM gaps)
        SELECT metric,from_ns,to_ns,gap_ns FROM ranked WHERE pos=1 ORDER BY metric
    """)
    connection.execute("""CREATE TABLE psu AS
        SELECT a.node,a.t,a.v+b.v AS v FROM clean a JOIN clean b USING(node,t)
        WHERE a.metric='ps0_input_power' AND b.metric='ps1_input_power'""")
    report["psu_pairs"] = query(connection, """
        SELECT count(*) AS n,count(DISTINCT node) AS nodes,
          min(t)//1000000 AS first_ms,max(t)//1000000 AS last_ms,
          min(v) AS min_w,max(v) AS max_w FROM psu
    """)[0]
    connection.execute("""CREATE TABLE triples AS
        SELECT a.node,a.t,a.v AS input_w,b.v AS total_w,b.v-a.v AS delta_w
        FROM psu a JOIN clean b USING(node,t) WHERE b.metric='total_power'""")
    report["triples"] = query(connection, """
        SELECT count(*) AS n,count(DISTINCT node) AS nodes,
          min(delta_w) AS min_delta_w,max(delta_w) AS max_delta_w,
          avg(delta_w) AS mean_delta_w,quantile_cont(delta_w,0.5) AS median_delta_w,
          quantile_cont(abs(delta_w),[0.5,0.9,0.99]) AS abs_delta_quantiles,
          count(*) FILTER(WHERE delta_w=0) AS equal_values,
          count(*) FILTER(WHERE input_w=0) AS input_zero,
          count(*) FILTER(WHERE total_w=0) AS total_zero,
          avg(delta_w::DOUBLE/input_w) FILTER(WHERE input_w>0) AS mean_relative_delta
        FROM triples
    """)[0]
    report["simultaneity"] = {}
    sources = {metric: f"SELECT node,t FROM clean WHERE metric='{metric}'"
               for metric in paths}
    sources.update(psu_sum="SELECT node,t FROM psu", triples="SELECT node,t FROM triples")
    for name, source in sources.items():
        connection.execute("CREATE OR REPLACE TEMP VIEW selected AS " + source)
        nodes = connection.execute("SELECT count(DISTINCT node) FROM selected").fetchone()[0]
        timeline = query(connection, """SELECT t,count(DISTINCT node) AS n_nodes
            FROM selected GROUP BY t ORDER BY t""")
        all_times = [r["t"] for r in timeline if r["n_nodes"] == NODES]
        histogram = {}
        for row in timeline:
            histogram[row["n_nodes"]] = histogram.get(row["n_nodes"], 0) + 1
        pair = query(connection, """SELECT t FROM selected WHERE node IN ('0','1')
            GROUP BY t HAVING count(DISTINCT node)=2 ORDER BY t""")
        report["simultaneity"][name] = {
            "nodes": nodes, "required_node_ids": "every canonical string ID 0..979",
            "node_count_per_time_histogram": [
                {"n_nodes": n, "times": count} for n,count in sorted(histogram.items())],
            "all980": times_summary(all_times),
            "preselected_nodes_0_and_1": times_summary([r["t"] for r in pair]),
        }
    return report


def compare_value(actual, expected, path: str, differences: list) -> None:
    if isinstance(expected, dict):
        for key, value in expected.items():
            if key not in actual:
                differences.append({"path": path+"."+key, "error": "missing"})
            else:
                compare_value(actual[key], value, path+"."+key, differences)
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            differences.append({"path": path, "actual_length": len(actual),
                                "expected_length": len(expected)})
        else:
            for i,(a,e) in enumerate(zip(actual,expected)):
                compare_value(a,e,f"{path}[{i}]",differences)
    elif isinstance(expected, float):
        if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-9):
            differences.append({"path": path, "actual": actual, "expected": expected})
    elif actual != expected:
        differences.append({"path": path, "actual": actual, "expected": expected})


def compare_reports(report: dict, reference_dir: Path | None) -> dict:
    differences = []
    for row in report["raw_by_metric"]:
        compare_value(row, {"rows": ACCEPTED["rows"][row["metric"]], "nodes": NODES,
            "null_node": 0, "null_time": 0, "null_value": 0, "negative_value": 0,
            "unmapped_node": 0, "noncanonical_node": 0, "subsecond_rows": 0,
            "submillisecond_rows": 0}, "raw."+row["metric"], differences)
    for row in report["keys_by_metric"]:
        compare_value(row,{"duplicated_keys":0,"extra_rows":0,"conflicting_keys":0},
                      "keys."+row["metric"],differences)
    compare_value(report["psu_pairs"]["n"],ACCEPTED["psu_pairs"],"psu_pairs.n",differences)
    compare_value(report["triples"], {
        "n": ACCEPTED["triple_rows"], "min_delta_w": ACCEPTED["triple_delta_min_w"],
        "max_delta_w": ACCEPTED["triple_delta_max_w"],
        "mean_delta_w": ACCEPTED["triple_delta_mean_w"],
        "median_delta_w": ACCEPTED["triple_delta_median_w"]},"triples",differences)
    for metric,count in ACCEPTED["all980_times"].items():
        compare_value(report["simultaneity"][metric]["all980"],
            {"count":count,"longest_postselected_exact20s_run":
             {"cells":ACCEPTED["all980_longest_run_cells"][metric]}},
             "simultaneity."+metric,differences)
    for row in report["global_max_gap_by_metric"]:
        compare_value(row["gap_ns"],ACCEPTED["global_max_gap_ns"],
                      "global_max_gap."+row["metric"],differences)
    references = []
    if reference_dir is not None:
        inspection_path = reference_dir/"M100_PANEL_INSPECTION.json"
        supplement_path = reference_dir/"M100_PANEL_SUPPLEMENT.json"
        inspection = json.loads(inspection_path.read_text())
        supplement = json.loads(supplement_path.read_text())
        for path in (inspection_path,supplement_path):
            references.append({"filename":path.name,"sha256":sha256(path)})
        for key in ("raw_by_metric","keys_by_metric","triples"):
            compare_value(report[key],inspection[key],"reference."+key,differences)
        compare_value(report["psu_pairs"]["n"],supplement["psu_key_count"],
                      "reference.psu_key_count",differences)
        for name, original in inspection["simultaneity"].items():
            new = report["simultaneity"][name]
            compare_value(new["all980"],original["all_observed_nodes"],
                          "reference.simultaneity."+name+".all980",differences)
            compare_value(new["preselected_nodes_0_and_1"],
                          original["preselected_nodes_0_and_1"],
                          "reference.simultaneity."+name+".pair",differences)
            compare_value(new["node_count_per_time_histogram"],
                          original["node_count_per_time_histogram"],
                          "reference.simultaneity."+name+".histogram",differences)
        for row in report["global_max_gap_by_metric"]:
            prior = max((r for r in supplement["global_gaps"] if r["metric"]==row["metric"]),
                        key=lambda r:r["gap"])
            compare_value(row,{"from_ns":prior["from_ms"]*NS_PER_MS,
                               "to_ns":prior["to_ms"]*NS_PER_MS,
                               "gap_ns":prior["gap"]*NS_PER_MS},
                          "reference.global_max_gap."+row["metric"],differences)
    return {"status":"PASS" if not differences else "DISCREPANCY",
            "comparison_targets":"embedded accepted key claims, plus optional preserved reports",
            "floating_tolerance":{"absolute":1e-9,"relative":1e-12},
            "reference_files":references,"differences":differences}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path,help="New JSON file; existing files are refused")
    parser.add_argument("--reference-dir",type=Path,help="Optional preserved checks/ directory; read only")
    args = parser.parse_args()
    raw_dir, output = args.raw_dir.resolve(), args.output.resolve()
    if output.exists() or output.is_relative_to(raw_dir):
        parser.error("--output must be a new path outside --raw-dir; no existing artifact is overwritten")
    if not output.parent.is_dir():
        parser.error("--output parent directory must already exist")
    started = time.monotonic()
    report = {"status":"RUNNING","started_utc":utc_now(),"python":sys.version,
              "script_sha256":sha256(Path(__file__)),"raw_directory":str(raw_dir),
              "offline":True,"scope":"Descriptive released-data gate only; no downtime, pooling, ownership or reliability inference."}
    try:
        inputs, paths = validate_inputs(raw_dir)
        report["inputs"] = inputs
        import duckdb
        if duckdb.__version__ != "1.4.1":
            raise ValueError(f"DuckDB1.4.1 required; found {duckdb.__version__}")
        report["duckdb"] = duckdb.__version__
        with tempfile.TemporaryDirectory(prefix="m100-offline-replay-") as scratch:
            connection = duckdb.connect(str(Path(scratch)/"fresh.duckdb"), config={
                "memory_limit":"1GB","threads":"2",
                "autoinstall_known_extensions":"false","autoload_known_extensions":"false"})
            try:
                connection.execute("SET TimeZone='UTC'")
                report["database_settings"] = query(connection,"""SELECT name,value FROM duckdb_settings()
                    WHERE name IN ('memory_limit','threads','TimeZone','autoinstall_known_extensions',
                    'autoload_known_extensions') ORDER BY name""")
                report.update(analyze(connection,paths))
            finally:
                connection.close()
        report["comparison"] = compare_reports(report,args.reference_dir)
        report["input_hashes_unchanged_after_analysis"] = all(
            sha256(paths[r["metric"]])==r["sha256"] for r in inputs)
        if not report["input_hashes_unchanged_after_analysis"]:
            raise ValueError("An input changed during analysis")
        report["status"] = report["comparison"]["status"]
        report["interpretation_limits"] = [
            "total_power and PSU input sum are distinct meter quantities; their difference is descriptive, not a calibration correction.",
            "No operational-state or workload filters; no causal attribution of missing observations or zero values.",
            "Global gaps are gaps between timestamps having at least one released clean node; they differ from per-node gaps.",
            "All980 intersections require canonical IDs0..979 and exact nanosecond equality, not nearest-time matching.",
            "Longest runs are postselected descriptive runs, not an ex ante sampling or reliability guarantee.",
            "The pinned complete archive members cover April1-4 observations; missing rest-of-month records do not establish sensor downtime.",
            "1GB is DuckDB's buffer-memory limit, not a strict operating-system RSS cap; temporary spill files are removed."]
    except Exception as error:
        report["status"] = "ERROR"
        report["error"] = f"{type(error).__name__}: {error}"
    report["completed_utc"] = utc_now()
    report["elapsed_seconds"] = time.monotonic()-started
    # Exclusive creation also protects against another process creating output mid-run.
    with output.open("x") as stream:
        json.dump(report,stream,indent=2,allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status":report["status"],"output":str(output),
                      "elapsed_seconds":report["elapsed_seconds"],
                      "differences":report.get("comparison",{}).get("differences",[]),
                      "error":report.get("error")}))
    return 0 if report["status"]=="PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
