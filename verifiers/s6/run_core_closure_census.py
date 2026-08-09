#!/usr/bin/env python3
"""Run the core-closure full-staged encoding on archived hand-net survivors."""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core_closure_pipeline import (  # noqa: E402
    pipeline2_core_closure,
    require_equality_with_subthird_overcover,
    require_equality_without_uniform_triple_anchor,
)


def solve_one(task):
    index, r, c, table, timeout, mode = task
    data = pipeline2_core_closure(
        6, tuple(r), tuple(c), table, F(2, 3), mode == "failure"
    )
    if mode == "equality-no-triple":
        require_equality_without_uniform_triple_anchor(data, tuple(c))
    elif mode == "equality-subthird":
        require_equality_with_subthird_overcover(data, tuple(c))
    data["solver"].set(timeout=timeout * 1000)
    started = time.monotonic()
    verdict = data["solver"].check()
    elapsed = time.monotonic() - started
    row = {
        "index": index,
        "lmin": r,
        "lmax": c,
        "table": table,
        "result": str(verdict),
        "seconds": round(elapsed, 4),
    }
    if verdict == z3.sat:
        model = data["solver"].model()
        row["candidate_lmin"] = [str(model.eval(q)) for q in data["lmin"]]
        row["candidate_lmax"] = [str(model.eval(q)) for q in data["lmax"]]
        row["candidate_singleton_witnesses"] = [
            [str(model.eval(q)) for q in witness]
            for witness in data["singleton_witnesses"]
        ]
        row["candidate_distance"] = str(model.eval(data["distance"]))
    return row


def write_report(path, source, start, stop, timeout, workers, mode, rows):
    tally = {key: sum(row["result"] == key for row in rows) for key in ("sat", "unsat", "unknown")}
    report = {
        "status": "core-closure full-staged census; each row is one stratum/table configuration",
        "source": str(source),
        "range": [start, stop],
        "per_configuration_timeout_seconds": timeout,
        "workers": workers,
        "mode": mode,
        "tally": tally,
        "maximum_seconds": max((row["seconds"] for row in rows), default=0),
        "rows": sorted(rows, key=lambda row: row["index"]),
    }
    path.write_text(json.dumps(report, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--mode",
        choices=("failure", "equality-no-triple", "equality-subthird"),
        default="failure",
    )
    args = parser.parse_args()

    survivors = json.loads(args.input.read_text())["survivors"]
    stop = len(survivors) if args.limit is None else min(len(survivors), args.start + args.limit)
    selected = survivors[args.start:stop]
    tasks = [
        (args.start + offset, r, c, table, args.timeout, args.mode)
        for offset, (r, c, table) in enumerate(selected)
    ]
    rows = []
    if args.workers == 1:
        for task in tasks:
            rows.append(solve_one(task))
            write_report(
                args.output, args.input, args.start, stop, args.timeout, 1, args.mode, rows
            )
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(solve_one, task) for task in tasks]
            for future in as_completed(futures):
                rows.append(future.result())
                write_report(
                    args.output,
                    args.input,
                    args.start,
                    stop,
                    args.timeout,
                    args.workers,
                    args.mode,
                    rows,
                )
    write_report(
        args.output,
        args.input,
        args.start,
        stop,
        args.timeout,
        args.workers,
        args.mode,
        rows,
    )
    print(json.dumps(json.loads(args.output.read_text())["tally"], sort_keys=True))


if __name__ == "__main__":
    main()
