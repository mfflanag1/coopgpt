#!/usr/bin/env python3
"""Isolated long-cap reruns for unknown rows from one or more census shards."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_core_closure_census import solve_one  # noqa: E402


def write_report(path, triage_path, indices, timeout, mode, rows):
    tally = {
        verdict: sum(row["result"] == verdict for row in rows)
        for verdict in ("sat", "unsat", "unknown")
    }
    report = {
        "status": "isolated generator-normal-form reruns of capped unknowns",
        "source": str(triage_path),
        "range": [min(indices), max(indices) + 1] if indices else [0, 0],
        "requested_indices": indices,
        "per_configuration_timeout_seconds": timeout,
        "workers": 1,
        "mode": mode,
        "encoding": "generators",
        "tally": tally,
        "maximum_seconds": max((row["seconds"] for row in rows), default=0),
        "rows": sorted(rows, key=lambda row: row["index"]),
    }
    path.write_text(json.dumps(report, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=600)
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

    triage = json.loads(args.triage.read_text())["survivors"]
    indices = sorted(
        {
            row["index"]
            for path in args.shards
            for row in json.loads(path.read_text())["rows"]
            if row["result"] == "unknown"
        }
    )
    for path in args.shards:
        observed_mode = json.loads(path.read_text()).get("mode")
        allowed_modes = (None, "failure") if args.mode == "failure" else (args.mode,)
        if observed_mode not in allowed_modes:
            raise AssertionError(
                f"{path}: mode {observed_mode!r}, expected {args.mode!r}"
            )
    rows = []
    for index in indices:
        r, c, table = triage[index]
        rows.append(
            solve_one(
                (index, r, c, table, args.timeout, args.mode, "generators")
            )
        )
        write_report(args.output, args.triage, indices, args.timeout, args.mode, rows)
    write_report(args.output, args.triage, indices, args.timeout, args.mode, rows)
    print(json.dumps(json.loads(args.output.read_text())["tally"], sort_keys=True))


if __name__ == "__main__":
    main()
