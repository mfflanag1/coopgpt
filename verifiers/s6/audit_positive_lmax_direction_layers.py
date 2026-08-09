#!/usr/bin/env python3
"""Ablate distance and exactness witnesses in the Lmax direction layer.

This is a structural dependency audit, not an independent proof.  It rebuilds
each of the 109 positive-residue rows handled by one explicit Lmax direction
and asks which premises are actually needed to exclude every blocker.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from search_positive_handover_directions import (  # noqa: E402
    blocker_formula,
    critical_all_witness_solver,
)


EXPECTED = {
    "N(0,0)_P(-1,0,0)_r1": {
        "rows": 80,
        "full": {"unsat": 80},
        "without_distance": {"unsat": 80},
        "without_witness_blockers": {"sat": 80},
        "without_distance_or_witness_blockers": {"sat": 80},
    },
    "N(1,1)_P(-2,-2,-1)_r3": {
        "rows": 21,
        "full": {"unsat": 21},
        "without_distance": {"unsat": 21},
        "without_witness_blockers": {"unsat": 21},
        "without_distance_or_witness_blockers": {"unsat": 21},
    },
    "N(-1,1)_P(0,0,0)_r0": {
        "rows": 8,
        "full": {"unsat": 8},
        "without_distance": {"sat": 8},
        "without_witness_blockers": {"sat": 8},
        "without_distance_or_witness_blockers": {"sat": 8},
    },
}


def template(row: dict) -> str:
    direction = row["direction"]
    poor = tuple(sorted(direction[i] for i in row["poor_players"]))
    middle = tuple(sorted(direction[i] for i in row["P_players"]))
    rich = direction[row["rich_player"]]
    return (
        f"N({','.join(map(str, poor))})_"
        f"P({','.join(map(str, middle))})_r{rich}"
    )


def verdict(configuration, index, direction, include_distance, use_witnesses):
    solver, _, witnesses = critical_all_witness_solver(
        index, configuration, include_distance=include_distance
    )
    blocker, _ = blocker_formula(
        index,
        configuration,
        direction,
        "max",
        witnesses if use_witnesses else (),
    )
    solver.add(blocker)
    return str(solver.check())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument(
        "--directions",
        type=Path,
        default=HERE / "positive_lmax_handover_directions.json",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    survivors = json.loads(args.triage.read_text())["survivors"]
    source = json.loads(args.directions.read_text())["rows"]
    rows = []
    for row in source:
        if row.get("selected_side") != "max" or row.get("direction") is None:
            continue
        index = row["survivor_index"]
        configuration = survivors[index]
        assert configuration == row["configuration"]
        direction = tuple(row["direction"])
        results = {
            "full": verdict(configuration, index, direction, True, True),
            "without_distance": verdict(
                configuration, index, direction, False, True
            ),
            "without_witness_blockers": verdict(
                configuration, index, direction, True, False
            ),
            "without_distance_or_witness_blockers": verdict(
                configuration, index, direction, False, False
            ),
        }
        rows.append(
            {
                "survivor_index": index,
                "template": template(row),
                "direction": list(direction),
                **results,
            }
        )

    summary = {}
    for name in sorted({row["template"] for row in rows}):
        selected = [row for row in rows if row["template"] == name]
        summary[name] = {"rows": len(selected)}
        for mode in (
            "full",
            "without_distance",
            "without_witness_blockers",
            "without_distance_or_witness_blockers",
        ):
            summary[name][mode] = dict(
                sorted(collections.Counter(row[mode] for row in selected).items())
            )
    assert summary == EXPECTED
    payload = {
        "schema": "positive-lmax-direction-dependency-audit-v1",
        "scope": "exact QF_LRA dependency audit; solver evidence, not proof objects",
        "summary": summary,
        "rows": rows,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
