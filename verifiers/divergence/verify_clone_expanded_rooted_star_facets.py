#!/usr/bin/env python3
"""Exact audit of clone-expanded saturated rooted-star facet supports."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from verify_rooted_hinge_projection import decomposition_witnesses, matrix_rank  # noqa: E402


SUPPORTS = (
    (1, 3, 5, 9, 17, 33),
    (1, 3, 5, 9, 49),
    (1, 3, 5, 25, 41, 49),
    (1, 3, 5, 25, 41, 51),
    (1, 3, 13, 53, 57),
)


def solve_and_determinant(matrix: list[list[F]]) -> tuple[list[F], F]:
    n = len(matrix)
    augmented = [row[:] + [F(1)] for row in matrix]
    determinant = F(1)
    for column in range(n):
        pivot = next((row for row in range(column, n) if augmented[row][column]), None)
        if pivot is None:
            return [], F(0)
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
            determinant *= -1
        scale = augmented[column][column]
        determinant *= scale
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(n):
            if row == column or augmented[row][column] == 0:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]
    return [augmented[row][-1] for row in range(n)], determinant


def audit_support(support: tuple[int, ...]) -> dict:
    root = 0
    positive = tuple(coalition for coalition in support if coalition != 1)
    signatures = {}
    for player in range(1, 6):
        signature = tuple((coalition >> player) & 1 for coalition in positive)
        signatures.setdefault(signature, []).append(player)
    clone_classes = tuple(tuple(players) for _signature, players in sorted(signatures.items()))
    matrix = [
        [F((coalition >> players[0]) & 1) for coalition in positive]
        for players in clone_classes
    ]
    if len(matrix) != len(positive):
        raise AssertionError("clone compression is not saturated")
    weights, determinant = solve_and_determinant(matrix)
    exceptional_weight = sum(weights, F(0)) - 1
    if determinant == 0 or any(weight <= 0 for weight in weights) or exceptional_weight <= 0:
        raise AssertionError("compressed rooted-star matrix failed positivity")

    loads = []
    for player in range(6):
        load = sum(
            (weight for coalition, weight in zip(positive, weights) if coalition >> player & 1),
            F(0),
        )
        if player == root:
            load -= exceptional_weight
        loads.append(load)
    if loads != [F(1)] * 6 or matrix_rank(support, 6) != len(support):
        raise AssertionError("expanded incidence identity or minimality failed")
    if decomposition_witnesses(support, 6):
        raise AssertionError("expanded support is decomposable")

    # Collapse every clone class to one player and independently reapply the
    # exceptional-set test on the saturated base support.
    base_positive = []
    for coalition in positive:
        mask = 1
        for index, players in enumerate(clone_classes, start=1):
            if coalition >> players[0] & 1:
                mask |= 1 << index
        base_positive.append(mask)
    base_support = tuple(sorted((1, *base_positive)))
    base_n = len(clone_classes) + 1
    if matrix_rank(base_support, base_n) != len(base_support):
        raise AssertionError("compressed base support is not minimal")
    if decomposition_witnesses(base_support, base_n):
        raise AssertionError("compressed base support is decomposable")
    return {
        "expanded_support": list(support),
        "clone_classes": [list(players) for players in clone_classes],
        "clone_class_sizes": [len(players) for players in clone_classes],
        "compressed_support": list(base_support),
        "compressed_nonroot_dimension": len(clone_classes),
        "determinant": str(determinant),
        "positive_weights": [str(weight) for weight in weights],
        "exceptional_root_weight": str(exceptional_weight),
        "expanded_support_rank": len(support),
        "expanded_indecomposable": True,
        "compressed_indecomposable": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [audit_support(support) for support in SUPPORTS]
    report = {
        "status": "exact clone-expanded rooted-star facet audit passed",
        "facet_orbits": len(rows),
        "already_saturated_orbits": sum(
            all(size == 1 for size in row["clone_class_sizes"]) for row in rows
        ),
        "proper_clone_expansions": sum(
            any(size > 1 for size in row["clone_class_sizes"]) for row in rows
        ),
        "all_compressed_bases_saturated_positive_and_indecomposable": True,
        "all_expansions_minimal_and_indecomposable": True,
        "rows": rows,
        "scope": (
            "five finite n=6 atlas supports; the clone-expansion preservation "
            "statement is the human dimension-free theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
