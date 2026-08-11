#!/usr/bin/env python3
"""Exact arithmetic audit of the null-player hybrid-overlap descent.

The general descent is proved by convexity and exactness in the paper.  This
script checks the target constants symbolically over a configurable range and
replays the existing null-padded five-player exact control.  It is a bug audit,
not the proof of the convex-cover lemma.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
SOURCE = COOPGAMES / "verifiers" / "s5close" / "completeness3.json"


def target(n):
    return F(4 * n, n * n - (n % 2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=64)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    constants = []
    for n in range(7, args.max_n + 1):
        previous, current = target(n - 1), target(n)
        if previous <= current:
            raise AssertionError("hybrid target is not strictly decreasing")
        constants.append(
            {
                "n": n,
                "previous_target": str(previous),
                "current_target": str(current),
                "descent_margin": str(previous - current),
            }
        )
    if F(3, 4) < target(6):
        raise AssertionError("five-player overlap theorem does not seed n=6 null descent")

    source = json.loads(SOURCE.read_text())[3]["audit"]
    old_values = tuple(F(q) for q in source["v"])
    old_x = tuple(F(q) for q in source["Lmin"])
    old_z = tuple(F(q) for q in source["Lmax"])
    padded_values = tuple(old_values[coalition & 31] for coalition in range(64))
    padded_x, padded_z = old_x + (F(0),), old_z + (F(0),)
    for coalition in range(32):
        if padded_values[coalition | 32] != padded_values[coalition]:
            raise AssertionError("padded player is not null")
    old_overlap = sum((min(a, b) for a, b in zip(old_x, old_z)), F(0))
    padded_overlap = sum((min(a, b) for a, b in zip(padded_x, padded_z)), F(0))
    if old_overlap != padded_overlap or padded_overlap != F(25, 28):
        raise AssertionError("null padding changed the control overlap")
    report = {
        "status": "exact null-player hybrid-descent arithmetic audit",
        "human_theorem": (
            "zero Lmin floor forces a common-zero/null player; restriction preserves "
            "the exact core, both selections, total worth, and overlap"
        ),
        "target_monotonicity": constants,
        "n6_seed": {
            "known_n5_overlap_floor": "3/4",
            "n6_target": str(target(6)),
            "margin": str(F(3, 4) - target(6)),
        },
        "null_padded_control": {
            "source": str(SOURCE.relative_to(COOPGAMES)),
            "source_trail": "$[3].audit",
            "new_null_player": 5,
            "old_overlap": str(old_overlap),
            "padded_overlap": str(padded_overlap),
            "null_identities_verified": 32,
            "selection_vectors_are_zero_padded": True,
        },
        "scope": "arithmetic and fixed-control audit; the general result is the human proof",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
