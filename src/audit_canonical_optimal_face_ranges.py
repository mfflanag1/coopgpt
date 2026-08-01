"""Audit extreme-set orthogonality over the reduced dual optimal face."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from analyze_two_color_box_capacity import analyze, circuit_data, rat
from audit_potential_guided_sources import CASES, type_i_payload


def rational_rank(rows):
    matrix = [[F(value) for value in row] for row in rows]
    if not matrix:
        return 0
    rank = 0
    column_count = len(matrix[0])
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
        rank += 1
        if rank == len(matrix):
            break
    return rank


def support_rigid(n, aggregate, U):
    rows = [[1] * n]
    rows.extend([
        [int(coalition >> player & 1) for player in range(n)]
        for coalition, weight in aggregate.items() if weight
    ])
    indicator = [int(U >> player & 1) for player in range(n)]
    return rational_rank(rows + [indicator]) == rational_rank(rows)


def optimize_on_face(payload, circuit_index, U, rho, direction):
    n, A, B, aggregate, required_A, required_B = circuit_data(
        payload, circuit_index
    )
    coalitions = tuple(sorted(aggregate))
    r_A, r_B = 0, 1
    z_offset = 2
    t_offset = z_offset + n
    variable_count = t_offset + len(coalitions)

    target = np.zeros(variable_count)
    for player in range(n):
        if U >> player & 1:
            target[z_offset + player] = direction
    if U == A:
        target[r_A] = direction
    if U == B:
        target[r_B] = -direction

    A_eq, b_eq = [], []
    row = np.zeros(variable_count)
    row[r_A] = float(required_A)
    row[r_B] = float(required_B)
    A_eq.append(row)
    b_eq.append(1)

    row = np.zeros(variable_count)
    row[z_offset:z_offset + n] = 1
    A_eq.append(row)
    b_eq.append(0)

    row = np.zeros(variable_count)
    row[r_B] = float(aggregate[B])
    for index, coalition in enumerate(coalitions):
        row[t_offset + index] = float(aggregate[coalition])
    A_eq.append(row)
    b_eq.append(float(rho))

    A_ub, b_ub = [], []
    for index, coalition in enumerate(coalitions):
        row = np.zeros(variable_count)
        for player in range(n):
            if coalition >> player & 1:
                row[z_offset + player] = 1
        if coalition == A:
            row[r_A] = 1
        if coalition == B:
            row[r_B] = -1
        row[t_offset + index] = -1
        A_ub.append(row)
        b_ub.append(0)

    bounds = [(0, None), (0, None)]
    bounds.extend([(None, None)] * n)
    bounds.extend([(0, None)] * len(coalitions))
    result = linprog(
        target, A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    if not result.success:
        if "unbounded" in result.message.lower():
            return {
                "status": "unbounded reduced-dual optimal-face direction",
                "unbounded": True,
                "value": "-inf" if direction == 1 else "inf",
            }
        return {"status": result.message}
    solution = [rat(value) for value in result.x]
    exact = all(
        sum(rat(a) * x for a, x in zip(row, solution) if a) == rat(rhs)
        for row, rhs in zip(A_eq, b_eq)
    ) and all(
        sum(rat(a) * x for a, x in zip(row, solution) if a) <= rat(rhs)
        for row, rhs in zip(A_ub, b_ub)
    ) and all(
        (lower is None or value >= lower)
        and (upper is None or value <= upper)
        for value, (lower, upper) in zip(solution, bounds)
    )
    signed_value = sum(rat(a) * x for a, x in zip(target, solution) if a)
    return {
        "status": "exact reduced-dual optimal-face extremum",
        "exact": exact,
        "unbounded": False,
        "value": str(direction * signed_value),
        "retention_prices": {
            "A": str(solution[r_A]), "B": str(solution[r_B])
        },
        "potential": [
            str(solution[z_offset + player]) for player in range(n)
        ],
    }


def record(label, circuit, capacity_payload, index):
    ordinary = analyze(circuit, index)
    assert ordinary["primal_exact"] and ordinary["dual_exact"]
    rho = F(ordinary["capacity"])
    n, _A, _B, aggregate, _required_A, _required_B = circuit_data(
        circuit, index
    )
    fixed_by_kind = {}
    records = []
    for kind, U in (
        ("maximum", ordinary["maximum_set"]),
        ("minimum", ordinary["minimum_set"]),
    ):
        lower = optimize_on_face(circuit, index, U, rho, 1)
        upper = optimize_on_face(circuit, index, U, rho, -1)
        assert (lower.get("exact") or lower.get("unbounded")) and (
            upper.get("exact") or upper.get("unbounded")
        ), (
            label, kind, lower, upper
        )
        fixed = analyze(circuit, index, U)
        assert fixed["primal_exact"] and fixed["dual_exact"]
        lo = None if lower.get("unbounded") else F(lower["value"])
        hi = None if upper.get("unbounded") else F(upper["value"])
        includes_zero = (lo is None or lo <= 0) and (hi is None or hi >= 0)
        stays_at_rho = F(fixed["capacity"]) == rho
        rigid = support_rigid(n, aggregate, U)
        fixed_by_kind[kind] = fixed["capacity"]
        records.append({
            "kind": kind,
            "coalition": U,
            "optimal_face_range": [
                "-inf" if lo is None else str(lo),
                "inf" if hi is None else str(hi),
            ],
            "range_includes_zero": includes_zero,
            "fixed_capacity": fixed["capacity"],
            "fixed_capacity_stays_at_rho": stays_at_rho,
            "range_criterion_matches": includes_zero == stays_at_rho,
            "support_rigid": rigid,
            "support_flexibility_matches_failure": (not rigid) == stays_at_rho,
        })
    return {
        "label": label,
        "rho": str(rho),
        "extreme_sets": records,
        "both_ranges_include_zero": all(
            item["range_includes_zero"] for item in records
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
    extrema = [extreme for item in records for extreme in item["extreme_sets"]]
    return {
        "status": "exact canonical reduced-dual optimal-face range audit",
        "case_count": len(records),
        "extreme_set_count": len(extrema),
        "all_range_criteria_match_fixed_capacities": all(
            item["range_criterion_matches"] for item in extrema
        ),
        "zero_containing_range_count": sum(
            item["range_includes_zero"] for item in extrema
        ),
        "no_case_has_both_ranges_containing_zero": not any(
            item["both_ranges_include_zero"] for item in records
        ),
        "all_support_flexibility_matches_failures": all(
            item["support_flexibility_matches_failure"] for item in extrema
        ),
        "support_flexible_extreme_count": sum(
            not item["support_rigid"] for item in extrema
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
