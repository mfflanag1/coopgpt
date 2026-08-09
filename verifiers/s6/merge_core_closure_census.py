#!/usr/bin/env python3
"""Validate and merge checkpointed core-closure census shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=(
            "failure",
            "equality",
            "equality-triple",
            "equality-no-triple",
            "equality-subthird",
        ),
        default="failure",
    )
    parser.add_argument("shards", nargs="+", type=Path)
    args = parser.parse_args()

    triage = json.loads(args.triage.read_text())
    survivors = triage["survivors"]
    by_index = {}
    resolved_duplicates = []
    shard_ranges = []
    for path in args.shards:
        shard = json.loads(path.read_text())
        allowed_modes = (None, "failure") if args.mode == "failure" else (args.mode,)
        if shard.get("mode") not in allowed_modes:
            raise AssertionError(
                f"{path}: mode {shard.get('mode')!r}, expected {args.mode!r}"
            )
        shard_ranges.append(shard["range"])
        for row in shard["rows"]:
            index = row["index"]
            if index in by_index:
                prior = by_index[index]
                if prior["result"] == row["result"]:
                    resolved_duplicates.append(index)
                    continue
                if prior["result"] == "unknown" and row["result"] in ("sat", "unsat"):
                    by_index[index] = row
                    resolved_duplicates.append(index)
                    continue
                if row["result"] == "unknown" and prior["result"] in ("sat", "unsat"):
                    resolved_duplicates.append(index)
                    continue
                raise AssertionError(
                    f"conflicting decisive verdicts at survivor index {index}: "
                    f"{prior['result']} versus {row['result']}"
                )
            by_index[index] = row

    expected = set(range(len(survivors)))
    actual = set(by_index)
    if actual != expected:
        raise AssertionError(
            f"census coverage mismatch: missing={sorted(expected-actual)[:20]}, "
            f"extra={sorted(actual-expected)[:20]}"
        )

    rows = []
    for index, expected_configuration in enumerate(survivors):
        row = by_index[index]
        observed_configuration = [row["lmin"], row["lmax"], row["table"]]
        if observed_configuration != expected_configuration:
            raise AssertionError(f"configuration mismatch at survivor index {index}")
        merged_row = {
            "index": index,
            "lmin": row["lmin"],
            "lmax": row["lmax"],
            "table": row["table"],
            "result": row["result"],
        }
        for key in sorted(row):
            if key.startswith("candidate_"):
                merged_row[key] = row[key]
        rows.append(merged_row)

    tally = {
        verdict: sum(row["result"] == verdict for row in rows)
        for verdict in ("sat", "unsat", "unknown")
    }
    require_all_unsat = args.mode not in ("equality", "equality-triple")
    decisive = tally["unknown"] == 0
    expected = not require_all_unsat or tally["sat"] == 0
    passed = decisive and expected
    labels = {
        "failure": "strict-failure",
        "equality": "equality-feasibility",
        "equality-triple": "equality-with-triple feasibility",
        "equality-no-triple": "equality-no-triple negation",
        "equality-subthird": "equality-subthird negation",
    }
    targets = {
        "failure": "L1(Lmin,Lmax) > 2/3, equivalently overlap < 2/3",
        "equality": "L1(Lmin,Lmax) = 2/3",
        "equality-triple": (
            "L1(Lmin,Lmax) = 2/3 with a tight triple of Lmax-top players"
        ),
        "equality-no-triple": (
            "L1(Lmin,Lmax) = 2/3 without a tight triple of Lmax-top players"
        ),
        "equality-subthird": (
            "L1(Lmin,Lmax) = 2/3 with an Lmax over-cover of dispersion < 1/3"
        ),
    }
    report = {
        "status": (
            f"complete {labels[args.mode]} survivor census"
            if passed
            else f"incomplete or adverse {labels[args.mode]} survivor census"
        ),
        "mode": args.mode,
        "claim_scope": (
            "conditional on the separately audited hand-net exclusions and the "
            "full-staged encoding; solver verdicts are not yet independent "
            "rational infeasibility certificates"
        ),
        "target": targets[args.mode],
        "triage_source": str(args.triage),
        "triage_tally": triage["tally"],
        "shard_ranges": shard_ranges,
        "survivor_count": len(survivors),
        "tally": tally,
        "final_survivor_map_covers_every_index_exactly_once": True,
        "rerun_duplicate_indices_resolved": sorted(set(resolved_duplicates)),
        "all_configurations_match_triage_source": True,
        "rows": rows,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "survivor_count", "tally")}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
