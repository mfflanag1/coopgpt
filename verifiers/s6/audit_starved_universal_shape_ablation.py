#!/usr/bin/env python3
"""Ablate direction shapes in the table-free starved exchange lemma."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import audit_starved_universal_exchange_lemma as universal


SWAP = (-1, 0, 0, 0, 0, 1)
TWO = (-1, -1, 0, 0, 1, 1)
THREE = (-1, -1, -1, 1, 1, 1)
COEFFICIENT_TWO = (-1, -1, -1, 0, 1, 2)
VARIANTS = (
    ("swaps", (SWAP,)),
    ("swaps_plus_two_for_two", (SWAP, TWO)),
    ("swaps_plus_two_and_three", (SWAP, TWO, THREE)),
    ("final_three_shapes", (SWAP, TWO, COEFFICIENT_TWO)),
    ("all_four_observed_shapes", (SWAP, TWO, THREE, COEFFICIENT_TWO)),
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    original = universal.SHAPES
    rows = []
    try:
        for name, shapes in VARIANTS:
            universal.SHAPES = shapes
            verdicts = {}
            for side in ("min", "max"):
                solver, *_ = universal.abstract_solver(side, args.timeout_ms)
                verdicts[side] = str(solver.check())
            rows.append(
                {
                    "variant": name,
                    "shapes": [list(shape) for shape in shapes],
                    "direction_count": len(universal.direction_family()),
                    "verdicts": verdicts,
                }
            )
    finally:
        universal.SHAPES = original
    assert {row["variant"]: row["verdicts"] for row in rows} == {
        "swaps": {"min": "sat", "max": "sat"},
        "swaps_plus_two_for_two": {"min": "sat", "max": "unsat"},
        "swaps_plus_two_and_three": {"min": "sat", "max": "unsat"},
        "final_three_shapes": {"min": "unsat", "max": "unsat"},
        "all_four_observed_shapes": {"min": "unsat", "max": "unsat"},
    }
    payload = {
        "schema": "starved-universal-shape-ablation-v1",
        "scope": "exact QF_LRA discovery ablation; not proof objects",
        "rows": rows,
        "individual_verdict_summary": dict(
            sorted(Counter(value for row in rows for value in row["verdicts"].values()).items())
        ),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
