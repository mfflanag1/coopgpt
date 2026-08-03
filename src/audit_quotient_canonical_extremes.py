"""Audit extreme witnesses after quotienting the support-nullspace gauge."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from analyze_two_color_box_capacity import analyze, circuit_data
from audit_potential_guided_sources import CASES, type_i_payload


def rref(rows, column_count):
    matrix = [[F(value) for value in row] for row in rows]
    rank = 0
    pivots = []
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[rank])
            ]
        pivots.append(column)
        rank += 1
        if rank == len(matrix):
            break
    return matrix[:rank], pivots


def nullspace(rows, column_count):
    reduced, pivots = rref(rows, column_count)
    free = [column for column in range(column_count) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [F(0)] * column_count
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free_column]
        basis.append(vector)
    return basis


def solve_square(matrix, rhs):
    size = len(rhs)
    augmented = [
        [F(value) for value in row] + [F(value_rhs)]
        for row, value_rhs in zip(matrix, rhs)
    ]
    reduced, pivots = rref(augmented, size)
    assert pivots == list(range(size))
    return [reduced[row][-1] for row in range(size)]


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), F(0))


def support_nullspace(n, aggregate):
    rows = [[1] * n]
    rows.extend([
        [int(coalition >> player & 1) for player in range(n)]
        for coalition, weight in aggregate.items() if weight
    ])
    return nullspace(rows, n)


def orthogonal_representative(vector, basis):
    if not basis:
        return list(vector)
    gram = [[dot(left, right) for right in basis] for left in basis]
    coefficients = solve_square(gram, [-dot(item, vector) for item in basis])
    result = [
        value + sum((coefficient * direction[player]
                     for coefficient, direction in zip(coefficients, basis)), F(0))
        for player, value in enumerate(vector)
    ]
    assert all(dot(direction, result) == 0 for direction in basis)
    return result


def record(label, circuit, capacity_payload, index):
    ordinary = analyze(circuit, index)
    assert ordinary["primal_exact"] and ordinary["dual_exact"]
    n, _A, _B, aggregate, _required_A, _required_B = circuit_data(
        circuit, index
    )
    basis = support_nullspace(n, aggregate)
    original = [F(value) for value in ordinary["player_potential"]]
    canonical = orthogonal_representative(original, basis)
    assert sum(canonical, F(0)) == 0
    assert all(
        sum(original[player] for player in range(n) if coalition >> player & 1)
        == sum(canonical[player] for player in range(n) if coalition >> player & 1)
        for coalition, weight in aggregate.items() if weight
    )

    maximum, minimum = max(canonical), min(canonical)
    extrema = []
    for kind, value in (("maximum", maximum), ("minimum", minimum)):
        U = sum(
            1 << player for player, coordinate in enumerate(canonical)
            if coordinate == value
        )
        fixed = analyze(circuit, index, U)
        assert fixed["primal_exact"] and fixed["dual_exact"]
        extrema.append({
            "kind": kind,
            "coalition": U,
            "capacity": fixed["capacity"],
            "repairs_full_bumps": fixed["repairs_full_bumps"],
            "alpha": fixed["alpha"],
            "delta": fixed["delta"],
            "support_size": len(fixed["subcollection"]),
        })
    return {
        "label": label,
        "rho": ordinary["capacity"],
        "support_nullity": len(basis),
        "original_potential": [str(value) for value in original],
        "quotient_canonical_potential": [str(value) for value in canonical],
        "extreme_sets": extrema,
        "both_extremes_repair": all(
            item["repairs_full_bumps"] for item in extrema
        ),
    }


def audit(results_dir):
    records = []
    circuit, capacity, index = type_i_payload(results_dir)
    records.append(record("n5-Type-I", circuit, capacity, index))
    for label, circuit_name, capacity_name, index in CASES:
        circuit = json.loads((results_dir / circuit_name).read_text())
        capacity = json.loads((results_dir / capacity_name).read_text())
        records.append(record(label, circuit, capacity, index))
    return {
        "status": "exact quotient-canonical extreme-set audit",
        "case_count": len(records),
        "nontrivial_support_nullspace_cases": sum(
            item["support_nullity"] > 0 for item in records
        ),
        "all_both_extremes_repair": all(
            item["both_extremes_repair"] for item in records
        ),
        "minimum_extreme_capacity": str(min(
            F(extreme["capacity"])
            for item in records for extreme in item["extreme_sets"]
        )),
        "all_maximum_repairs_have_negative_defect": all(
            F(next(extreme for extreme in item["extreme_sets"]
                   if extreme["kind"] == "maximum")["delta"]) < 0
            for item in records
        ),
        "all_minimum_repairs_have_positive_defect": all(
            F(next(extreme for extreme in item["extreme_sets"]
                   if extreme["kind"] == "minimum")["delta"]) > 0
            for item in records
        ),
        "cases": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(args.results_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
