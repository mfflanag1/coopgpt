#!/usr/bin/env python3
"""Exact four-role obstruction to extending weighted Lmin=Lmax.

The role game has weights (3,1,1,1).  This script constructs its canonical
six-clone expansion, proves exactness by explicit block-witness placement,
and recomputes ordinary Lmin/Lmax with the independent exact simplex.  The
human weighted interpretation then follows from block symmetry.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from lexsimplex import lex_point_with_trace  # noqa: E402
from exactlp import exact_linprog  # noqa: E402


WEIGHTS = (3, 1, 1, 1)
ROLE_VALUES = tuple(map(F, (0, 11, 0, 14, 0, 14, 0, 16, 0, 12, 0, 15, 0, 15, 0, 18)))
BLOCKS = ((0, 1, 2), (3,), (4,), (5,))
EXPECTED_LMIN = tuple(map(F, (4, 4, 4, 2, 2, 2)))
EXPECTED_LMAX = tuple(map(F, (F(11, 3), F(11, 3), F(11, 3), 3, 3, 1)))


def completed_role_mask(coalition):
    result = 0
    for role, block in enumerate(BLOCKS):
        if all(coalition >> player & 1 for player in block):
            result |= 1 << role
    return result


def expand_values():
    return tuple(
        ROLE_VALUES[completed_role_mask(coalition)]
        for coalition in range(1 << 6)
    )


def role_sum(point, coalition):
    return sum((point[i] for i in range(4) if coalition >> i & 1), F(0))


def role_witnesses():
    witnesses = {}
    for coalition in range(1 << 4):
        inequalities = []
        rhs = []
        for other in range(1, (1 << 4) - 1):
            inequalities.append(
                [F(-1 if other >> i & 1 else 0) for i in range(4)]
            )
            rhs.append(-ROLE_VALUES[other])
        equalities = [[F(1)] * 4]
        equality_rhs = [ROLE_VALUES[-1]]
        objective = [F(1 if coalition >> i & 1 else 0) for i in range(4)]
        status, optimum, witness = exact_linprog(
            objective,
            inequalities,
            rhs,
            equalities,
            equality_rhs,
        )
        if status != "optimal" or optimum != ROLE_VALUES[coalition]:
            raise AssertionError(("missing role exactness witness", coalition, status, optimum))
        witness = tuple(witness)
        if any(
            role_sum(witness, other) < ROLE_VALUES[other]
            for other in range(1 << 4)
        ):
            raise AssertionError(("role witness outside core", coalition))
        witnesses[coalition] = witness
    return witnesses


def clone_witness(role_point, coalition):
    allocation = [F(0)] * 6
    for role, block in enumerate(BLOCKS):
        if all(coalition >> player & 1 for player in block):
            allocation[block[0]] = role_point[role]
        elif any(coalition >> player & 1 for player in block):
            outside = next(player for player in block if not (coalition >> player & 1))
            allocation[outside] = role_point[role]
        else:
            allocation[block[0]] = role_point[role]
    return tuple(allocation)


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(6) if coalition >> i & 1), F(0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values = expand_values()
    witnesses = role_witnesses()
    clone_witness_count = 0
    for coalition in range(1 << 6):
        role_mask = completed_role_mask(coalition)
        witness = clone_witness(witnesses[role_mask], coalition)
        if coalition_sum(witness, coalition) != values[coalition]:
            raise AssertionError(("clone attainment", coalition))
        if any(
            coalition_sum(witness, other) < values[other]
            for other in range(1 << 6)
        ):
            raise AssertionError(("clone witness outside core", coalition))
        clone_witness_count += 1

    lmin, lmin_trace = lex_point_with_trace(6, values, "min")
    lmax, lmax_trace = lex_point_with_trace(6, values, "max")
    if tuple(lmin) != EXPECTED_LMIN or tuple(lmax) != EXPECTED_LMAX:
        raise AssertionError((lmin, lmax))
    overlap = sum((min(a, b) for a, b in zip(lmin, lmax)), F(0))
    total = values[-1]
    if overlap != F(16) or overlap / total != F(8, 9):
        raise AssertionError("overlap arithmetic")

    report = {
        "status": "exact weighted four-role obstruction verified",
        "role_weights": list(WEIGHTS),
        "role_values_binary_order": [str(value) for value in ROLE_VALUES],
        "weighted_lmin_role_totals": ["12", "2", "2", "2"],
        "weighted_lmax_role_totals": ["11", "3", "3", "1"],
        "canonical_clone_lmin": [str(value) for value in lmin],
        "canonical_clone_lmax": [str(value) for value in lmax],
        "lmin_trace": [
            {
                "level": str(row["level"]),
                "newly_pinned": list(row["newly_pinned"]),
            }
            for row in lmin_trace
        ],
        "lmax_trace": [
            {
                "level": str(row["level"]),
                "newly_pinned": list(row["newly_pinned"]),
            }
            for row in lmax_trace
        ],
        "role_exactness_witnesses": 16,
        "clone_exactness_witnesses": clone_witness_count,
        "singleton_normalized": all(values[1 << i] == 0 for i in range(6)),
        "total": str(total),
        "overlap": str(overlap),
        "overlap_ratio": str(overlap / total),
        "six_player_target": "2/3",
        "interpretation": (
            "weighted Lmin=Lmax is sharp through three roles and fails at four; "
            "this obstruction has large slack above the hybrid-overlap target"
        ),
        "scope": (
            "one exact role game and its canonical clone expansion; it refutes "
            "four-role weighted coincidence but not the main overlap conjecture"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
