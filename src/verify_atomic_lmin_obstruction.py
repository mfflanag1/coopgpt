"""Exact audit of the two displayed atomic Lmin obstruction circuits.

This checks the five-player broken diamond and seven-player three-trace
examples.  It is a regression test for the examples, not a proof of the
dimension-free conformal-circuit reduction.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximin_core_exact
from tugame import Game
from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope,
)
from verify_three_trace_half_integral_family import (
    defining_coalitions,
    lower_envelope as three_trace_envelope,
    mask,
    vertices,
)


def rank(rows):
    matrix = [list(map(F, row)) for row in rows]
    if not matrix:
        return 0
    row = 0
    for column in range(len(matrix[0])):
        pivot = next((j for j in range(row, len(matrix)) if matrix[j][column]), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        scale = matrix[row][column]
        matrix[row] = [entry / scale for entry in matrix[row]]
        for j in range(len(matrix)):
            if j == row or not matrix[j][column]:
                continue
            scale = matrix[j][column]
            matrix[j] = [a - scale * b for a, b in zip(matrix[j], matrix[row])]
        row += 1
    return row


def quotient_column(n, coalition):
    last = F(bool(coalition >> (n - 1) & 1))
    return [F(bool(coalition >> i & 1)) - last for i in range(n - 1)]


def audit_circuit(n, support, coefficients, exceptional):
    loads = [F(0)] * n
    for coalition, coefficient in zip(support, coefficients):
        for player in range(n):
            if coalition >> player & 1:
                loads[player] += coefficient
    if len(set(loads)) != 1:
        raise AssertionError("signed incidence combination is not constant")
    if coefficients[support.index(exceptional)] >= 0:
        raise AssertionError("exceptional coalition is not the unique negative element")
    if sum(coefficient < 0 for coefficient in coefficients) != 1:
        raise AssertionError("circuit has more than one negative element")

    columns = [quotient_column(n, coalition) for coalition in support]
    transposed = list(map(list, zip(*columns)))
    if rank(transposed) != len(support) - 1:
        raise AssertionError("support has nullity other than one")
    for removed in range(len(support)):
        subset = [column for j, column in enumerate(columns) if j != removed]
        if rank(list(map(list, zip(*subset)))) != len(subset):
            raise AssertionError("signed dependence is not a circuit")
    if len(support) > n:
        raise AssertionError("circuit exceeds the dimension bound")
    return {
        "players": n,
        "support_size": len(support),
        "constant_load": str(loads[0]),
        "unique_negative_exceptional_coalition": True,
        "every_proper_subsupport_independent": True,
        "support_bound_verified": True,
    }


def five_player_case():
    game = Game(5, lower_envelope(BASE_GENERATORS))
    if tuple(leximin_core_exact(game)) != PHI_BASE:
        raise AssertionError("five-player Lmin changed")
    left = mask((0, 2, 4))
    right = mask((2, 3, 4))
    target = left & right
    exterior = ((1 << 5) - 1) & ~(left | right)
    return audit_circuit(5, [left, right, exterior, target], [F(1), F(1), F(1), F(-1)], target)


def seven_player_case():
    t, u, w = 1, 2, 2
    (poor_a, _), _, _, _, constraints = defining_coalitions(t, u, w)
    game = three_trace_envelope(vertices(t, u, w))
    phi = tuple([F(1), F(1)] + [F(2)] * (t + u + w))
    if tuple(leximin_core_exact(game)) != phi:
        raise AssertionError("seven-player Lmin changed")
    traces = [mask(coalition) for coalition, _ in constraints]
    target = mask(range(2, 7))
    support = traces + [1 << poor_a, target]
    coefficients = [F(1, 2)] * 4 + [F(-1, 2)]
    return audit_circuit(7, support, coefficients, target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "status": "atomic Lmin obstruction examples audited",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "five_player_broken_diamond": five_player_case(),
        "seven_player_three_trace": seven_player_case(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
