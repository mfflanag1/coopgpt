"""Exact probe for decompositions of the displayed Lmin obstruction atoms.

For an atom S, a coalition E outside S yields a Studeny--Kratochvil
decomposition exactly when E is exceptional in S union {E}.  After fixing
the coefficient of E to -1, this is a rational linear feasibility problem.
The script is a discovery probe, not a general theorem.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3

from verify_three_trace_half_integral_family import defining_coalitions, mask


def rational(value):
    if not z3.is_rational_value(value):
        raise AssertionError(f"non-rational model value: {value}")
    return F(value.numerator_as_long(), value.denominator_as_long())


def members(n, coalition):
    return [i + 1 for i in range(n) if coalition >> i & 1]


def decompositions(n, support):
    full = (1 << n) - 1
    answers = []
    for exceptional in range(1, full):
        if exceptional in support:
            continue
        solver = z3.Solver()
        weights = [z3.Real(f"w_{exceptional}_{j}") for j in range(len(support))]
        common = z3.Real(f"r_{exceptional}")
        solver.add(*(weight >= 0 for weight in weights))
        for player in range(n):
            load = sum(
                weight
                for coalition, weight in zip(support, weights)
                if coalition >> player & 1
            )
            solver.add(load - (1 if exceptional >> player & 1 else 0) == common)
        if solver.check() != z3.sat:
            continue
        model = solver.model()
        answers.append(
            {
                "new_exceptional": members(n, exceptional),
                "common_load": str(rational(model.eval(common, model_completion=True))),
                "support_weights": [
                    str(rational(model.eval(weight, model_completion=True)))
                    for weight in weights
                ],
            }
        )
    return answers


def cases():
    left = mask((0, 2, 4))
    right = mask((2, 3, 4))
    target5 = left & right
    exterior = ((1 << 5) - 1) & ~(left | right)
    support5 = [left, right, exterior, target5]

    (poor_a, _), _, _, _, constraints = defining_coalitions(1, 2, 2)
    traces = [mask(coalition) for coalition, _ in constraints]
    target7 = mask(range(2, 7))
    support7 = traces + [1 << poor_a, target7]
    rooted5 = [left, right, target5 | exterior, target5]
    rooted7 = traces + [target7 | (1 << poor_a), target7]
    return [
        ("five_player_broken_diamond", 5, support5),
        ("five_player_rooted_atom", 5, rooted5),
        ("seven_player_three_trace", 7, support7),
        ("seven_player_rooted_atom", 7, rooted7),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {"status": "Lmin atom indecomposability probed", "arithmetic": "exact rational"}
    for name, n, support in cases():
        witnesses = decompositions(n, support)
        payload[name] = {
            "support": [members(n, coalition) for coalition in support],
            "indecomposable": not witnesses,
            "decomposition_count": len(witnesses),
            "decompositions": witnesses,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
