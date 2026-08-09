#!/usr/bin/env python3
"""Recompute one shard of the Lmin handover premise-dependency audit.

The three sections are deliberately shardable so each Z3 process has bounded
lifetime.  Merge complete, nonoverlapping shards with
``merge_positive_lmin_handover_layers.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from search_positive_handover_directions import (  # noqa: E402
    blocker_formula,
    critical_all_witness_solver,
)


def source_rows(payload, section):
    if section == "critical":
        return [
            row
            for row in payload["rows"]
            if row.get("critical_algebra_verdict") == "unsat"
        ]
    if section == "direction":
        return [row for row in payload["rows"] if row.get("direction") is not None]
    return [
        row
        for row in payload["rows"]
        if row.get("full_direction_menu_verdict") == "unsat"
    ]


def critical_verdicts(index, configuration):
    results = {}
    for name, distance, witnesses, comparisons in (
        ("without_distance", False, True, True),
        ("without_witnesses", True, False, True),
        ("payoff_critical", False, False, True),
        ("common_sign_only", False, False, False),
    ):
        solver, _, _ = critical_all_witness_solver(
            index,
            configuration,
            include_distance=distance,
            include_witnesses=witnesses,
            include_triple_comparisons=comparisons,
        )
        results[name] = str(solver.check())
    return results


def blocker_verdicts(index, configuration, directions):
    results = {}
    for name, distance, use_blocker_witnesses in (
        ("full", True, True),
        ("without_distance", False, True),
        ("without_blocker_witnesses", True, False),
        ("without_distance_or_blocker_witnesses", False, False),
    ):
        solver, _, witnesses = critical_all_witness_solver(
            index, configuration, include_distance=distance
        )
        for direction in directions:
            blocker, _ = blocker_formula(
                index,
                configuration,
                direction,
                "min",
                witnesses if use_blocker_witnesses else (),
            )
            solver.add(blocker)
        results[name] = str(solver.check())
    assert results["full"] == "unsat"
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", choices=("critical", "direction", "menu"), required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--source",
        type=Path,
        default=HERE / "positive_lmin_handover_directions.json",
    )
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.source.read_text())
    survivors = json.loads(args.triage.read_text())["survivors"]
    selected = source_rows(source, args.section)
    stop = len(selected) if args.stop is None else args.stop
    if not 0 <= args.start <= stop <= len(selected):
        raise ValueError("invalid shard interval")
    rows = []
    for position, row in enumerate(selected[args.start:stop], args.start):
        index = row["survivor_index"]
        configuration = survivors[index]
        assert configuration == row["configuration"]
        if args.section == "critical":
            verdicts = critical_verdicts(index, configuration)
            extra = {}
        elif args.section == "direction":
            verdicts = blocker_verdicts(
                index, configuration, (tuple(row["direction"]),)
            )
            extra = {"direction": row["direction"]}
        else:
            menu = tuple(tuple(direction) for direction in row["minimized_direction_menu"])
            verdicts = blocker_verdicts(index, configuration, menu)
            extra = {"minimized_direction_menu": row["minimized_direction_menu"]}
        rows.append(
            {
                "position": position,
                "survivor_index": index,
                "configuration": configuration,
                **extra,
                **verdicts,
            }
        )
    payload = {
        "schema": "positive-lmin-handover-dependency-shard-v1",
        "scope": "exact QF_LRA premise ablation; solver evidence, not proof objects",
        "section": args.section,
        "start": args.start,
        "stop": stop,
        "section_total": len(selected),
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("section", "start", "stop", "section_total")}, sort_keys=True))


if __name__ == "__main__":
    main()
