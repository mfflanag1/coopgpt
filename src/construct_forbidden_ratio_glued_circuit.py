"""Construct an exact nonexclusive circuit outside the scalar arm frontier.

The three game blocks are glued along one monotonicity column per arm.  Each
local block support is a nullity-one positive circuit.  Matching the shared
monotonicity weights produces a global nullity-one positive circuit with

    (x, y, U, V) = (1, 2, 1, 1).

Thus both proposed cross-arm inequalities and the product condition fail,
although exact two-color reoptimization still has capacity one.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import sympy as sp

from analyze_two_color_box_capacity import analyze, circuit_data
from search_both_sensitive_circuits import (
    eliminated_matrix,
    exactify_support,
    full_ray,
)


N = 6
A = 0b000111
B = 0b011000

ROWS = [
    ("core", 0, 24),
    ("core", 0, 3),
    ("core", 0, 45),
    ("core", 1, 7),
    ("core", 1, 58),
    ("core", 1, 60),
    ("core", 2, 7),
    ("core", 2, 24),
    ("core", 2, 35),
    ("core", 2, 37),
    ("core", 2, 54),
    ("mono", 0, 1, 0, 7),
    ("mono", 0, 2, 3, 24),
]


def rank(matrix) -> int:
    return int(sp.Matrix(matrix.astype(int).tolist()).rank())


def construct():
    matrix, inequalities, equalities, rowmeta = eliminated_matrix(N, A, B)
    support = [rowmeta.index(row) for row in ROWS]
    weights = exactify_support(matrix, support)
    assert weights == [1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]
    assert rank(matrix[:, support]) == len(support) - 1

    block_size = N - 1
    local = []
    for game in range(3):
        incident = [
            index
            for index, row in zip(support, ROWS)
            if (
                (row[0] == "core" and row[1] == game)
                or (row[0] == "mono" and game in row[1:3])
            )
        ]
        block = matrix[
            game * block_size:(game + 1) * block_size,
            incident,
        ]
        local_weights = [weights[support.index(index)] for index in incident]
        assert rank(block) == len(incident) - 1
        assert all(
            sum(
                F(int(block[row, column])) * local_weights[column]
                for column in range(len(incident))
            ) == 0
            for row in range(block_size)
        )
        local.append({
            "game": game,
            "support_size": len(incident),
            "rank": rank(block),
            "active_rows": [list(rowmeta[index]) for index in incident],
            "weights": local_weights,
        })

    ray = full_ray(weights, support, inequalities, equalities, N)
    payload = {
        "n": N,
        "A_mask": A,
        "B_mask": B,
        "construction": "three nullity-one local circuits glued along one monotonicity column per arm",
        "circuits": [{
            "model_support_size": len(support),
            "circuit_weights": weights,
            "efficiency_weights": ray[len(rowmeta):],
            "active_rows": [list(row) for row in ROWS],
        }],
    }

    _n, _A, _B, aggregate, x, y = circuit_data(payload, 1)
    U = aggregate[A] - x
    V = aggregate[B] - y
    assert (x, y, U, V) == (1, 2, 1, 1)

    capacity = analyze(payload, 1)
    fixed = {str(witness): analyze(payload, 1, witness) for witness in (16, 14)}
    assert capacity["capacity"] == "1"
    assert capacity["primal_exact"] and capacity["dual_exact"]
    assert all(
        item["primal_exact"] and item["dual_exact"]
        for item in fixed.values()
    )

    payload.update({
        "status": "exact forbidden-ratio positive circuit; non-scalar repair succeeds",
        "global_support_size": len(support),
        "global_rank": rank(matrix[:, support]),
        "global_nullity": 1,
        "local_block_circuits": local,
        "arm_masses": {
            "x": str(x),
            "y": str(y),
            "U": str(U),
            "V": str(V),
            "ratio_A": str((x + U) / x),
            "ratio_B": str((y + V) / y),
            "cross_gap_A": str(U - y),
            "cross_gap_B": str(V - x),
            "product_gap": str(U * V - x * y),
            "reciprocal_sum_minus_one": str(
                x / (x + U) + y / (y + V) - 1
            ),
        },
        "ordinary_capacity": capacity,
        "fixed_witness_capacities": fixed,
    })
    return payload


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(construct(), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
