"""Exhaust the eta-dual vertices for the first open 3+2 carrier case.

The eta dual is a five-equation standard-form polyhedron with 34
nonnegative variables.  Every optimum occurs at a basic feasible vertex
because all slack costs are nonnegative.  We enumerate its vertices, quotient
by S_3 x S_2 player symmetry, and minimize each representative's slack cost
over the universal exact-game cone with gamma normalized to one.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from hunt_n5_uniform_lift_exact_cone import N, PROPER, build_lp, members


VARIABLE_COUNT = len(PROPER) + 4


def dual_matrix():
    columns = []
    names = []
    for coalition in PROPER:
        columns.append([int(coalition >> player & 1) for player in range(N)])
        names.append(("lambda", coalition))
    for player in range(3):
        columns.append([int(other == player) for other in range(N)])
        names.append(("floor", player))
    columns.append([-1] * N)
    names.append(("rho", 0))
    return np.asarray(columns, dtype=float).T, names


def exact_solution(matrix, basis, rhs):
    augmented = [
        [F(int(matrix[row, column])) for column in basis] + [F(rhs[row])]
        for row in range(N)
    ]
    for pivot in range(N):
        candidate = next(
            (row for row in range(pivot, N) if augmented[row][pivot] != 0),
            None,
        )
        if candidate is None:
            return None
        augmented[pivot], augmented[candidate] = augmented[candidate], augmented[pivot]
        scale = augmented[pivot][pivot]
        augmented[pivot] = [value / scale for value in augmented[pivot]]
        for row in range(N):
            if row == pivot or augmented[row][pivot] == 0:
                continue
            scale = augmented[row][pivot]
            augmented[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[pivot])
            ]
    return [augmented[row][-1] for row in range(N)]


def enumerate_vertices():
    matrix, _ = dual_matrix()
    rhs = [0, 0, 0, 1, 1]
    vertices = set()
    for basis in itertools.combinations(range(VARIABLE_COUNT), N):
        numeric_basis = matrix[:, basis]
        if abs(np.linalg.det(numeric_basis)) < 1e-8:
            # The float determinant is only a speed prefilter; certify every
            # discarded basis singular by exact elimination so enumeration
            # completeness does not depend on a tolerance.
            assert exact_solution(matrix, basis, rhs) is None
            continue
        solution = exact_solution(matrix, basis, rhs)
        if solution is None or any(value < 0 for value in solution):
            continue
        vertex = [F(0)] * VARIABLE_COUNT
        for column, value in zip(basis, solution):
            vertex[column] = value
        # Independent exact feasibility check.
        for row in range(N):
            assert sum(
                F(int(matrix[row, column])) * vertex[column]
                for column in range(VARIABLE_COUNT)
            ) == rhs[row]
        vertices.add(tuple(vertex))
    return sorted(vertices)


def permutations():
    for inside in itertools.permutations(range(3)):
        for outside in ((3, 4), (4, 3)):
            yield tuple(inside) + outside


def permute_mask(mask, permutation):
    result = 0
    for old, new in enumerate(permutation):
        if mask >> old & 1:
            result |= 1 << new
    return result


def permute_vertex(vertex, permutation):
    result = [F(0)] * VARIABLE_COUNT
    coalition_index = {coalition: index for index, coalition in enumerate(PROPER)}
    for index, coalition in enumerate(PROPER):
        result[coalition_index[permute_mask(coalition, permutation)]] = vertex[index]
    floor_offset = len(PROPER)
    for player in range(3):
        result[floor_offset + permutation[player]] = vertex[floor_offset + player]
    result[-1] = vertex[-1]
    return tuple(result)


def symmetry_orbits(vertices):
    vertex_set = set(vertices)
    visited = set()
    orbits = []
    group = list(permutations())
    for vertex in vertices:
        if vertex in visited:
            continue
        orbit = {permute_vertex(vertex, permutation) for permutation in group}
        assert orbit <= vertex_set
        visited |= orbit
        orbits.append((min(orbit), len(orbit)))
    return orbits


def vertex_record(vertex):
    return {
        "lambda_support": [
            {
                "coalition": members(coalition),
                "coefficient": str(vertex[index]),
            }
            for index, coalition in enumerate(PROPER)
            if vertex[index] != 0
        ],
        "floor_weights": {
            str(player + 1): str(vertex[len(PROPER) + player])
            for player in range(3)
            if vertex[len(PROPER) + player] != 0
        },
        "rho": str(vertex[-1]),
    }


def rationalize(value):
    return F(float(value)).limit_denominator(1_000_000)


def solve_with_exact_dual(vertex, template):
    objective_float = np.zeros_like(template["objective"])
    objective_exact = [F(0)] * len(objective_float)
    for index, coalition in enumerate(PROPER):
        objective_float[coalition] = float(vertex[index])
        objective_exact[coalition] = vertex[index]
    result = linprog(
        objective_float,
        A_ub=template["A_ub"],
        b_ub=template["b_ub"],
        A_eq=template["A_eq"],
        b_eq=template["b_eq"],
        bounds=template["bounds"],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    exact_point = [rationalize(value) for value in result.x]
    for row in range(template["A_ub"].shape[0]):
        sparse_row = template["A_ub"].getrow(row)
        lhs = sum(
            F(int(coefficient)) * exact_point[column]
            for column, coefficient in zip(sparse_row.indices, sparse_row.data)
        )
        if lhs > F(int(template["b_ub"][row])):
            raise AssertionError(("primal inequality", row, lhs, template["b_ub"][row]))
    for row in range(template["A_eq"].shape[0]):
        sparse_row = template["A_eq"].getrow(row)
        lhs = sum(
            F(int(coefficient)) * exact_point[column]
            for column, coefficient in zip(sparse_row.indices, sparse_row.data)
        )
        if lhs != F(int(template["b_eq"][row])):
            raise AssertionError(("primal equality", row, lhs, template["b_eq"][row]))

    inequality_multipliers = {
        row: rationalize(-value)
        for row, value in enumerate(result.ineqlin.marginals)
        if abs(value) > 1e-8
    }
    equality_multipliers = {
        row: rationalize(-value)
        for row, value in enumerate(result.eqlin.marginals)
        if abs(value) > 1e-8
    }
    assert all(value >= 0 for value in inequality_multipliers.values())

    stationarity = objective_exact[:]
    for row, multiplier in inequality_multipliers.items():
        sparse_row = template["A_ub"].getrow(row)
        for column, coefficient in zip(sparse_row.indices, sparse_row.data):
            stationarity[column] += multiplier * F(int(coefficient))
    for row, multiplier in equality_multipliers.items():
        sparse_row = template["A_eq"].getrow(row)
        for column, coefficient in zip(sparse_row.indices, sparse_row.data):
            stationarity[column] += multiplier * F(int(coefficient))
    if any(value != 0 for value in stationarity):
        failures = [
            (index, str(value))
            for index, value in enumerate(stationarity)
            if value != 0
        ]
        raise AssertionError(f"rationalized dual stationarity failed: {failures[:10]}")

    exact_bound = -sum(
        multiplier * F(int(template["b_ub"][row]))
        for row, multiplier in inequality_multipliers.items()
    ) - sum(
        multiplier * F(int(template["b_eq"][row]))
        for row, multiplier in equality_multipliers.items()
    )
    if abs(float(exact_bound) - result.fun) > 1e-7:
        raise AssertionError((exact_bound, result.fun))
    exact_primal_value = sum(
        coefficient * value
        for coefficient, value in zip(objective_exact, exact_point)
    )
    if exact_primal_value != exact_bound:
        raise AssertionError((exact_primal_value, exact_bound))
    return result, exact_point, exact_bound, {
        "status": "independently verified exact rational primal/dual optimum",
        "lower_bound": str(exact_bound),
        "primal_value": str(exact_primal_value),
        "inequality_support": [
            {
                "constraint": template["inequality_names"][row],
                "multiplier": str(multiplier),
            }
            for row, multiplier in inequality_multipliers.items()
        ],
        "equality_support": [
            {
                "constraint": template["equality_names"][row],
                "multiplier": str(multiplier),
            }
            for row, multiplier in equality_multipliers.items()
        ],
    }


def run(witness_mode="global"):
    vertices = enumerate_vertices()
    orbits = symmetry_orbits(vertices)
    template = build_lp(0, witness_mode=witness_mode)
    audits = []
    minimum = None
    for orbit_index, (vertex, orbit_size) in enumerate(orbits):
        result, exact_point, exact_value, certificate = solve_with_exact_dual(vertex, template)
        value = float(exact_value)
        slacks = exact_point[: 1 << N]
        record = {
            "orbit_index": orbit_index,
            "orbit_size": orbit_size,
            "minimum_exact": str(exact_value),
            **vertex_record(vertex),
            "exact_dual_certificate": certificate,
        }
        audits.append(record)
        if minimum is None or value < minimum[0]:
            minimum = (value, record, slacks)
    assert sum(record["orbit_size"] for record in audits) == len(vertices)
    return {
        "status": "complete eta-dual vertex enumeration and symmetry-reduced universal exact-cone audit",
        "vertex_count": len(vertices),
        "symmetry_orbit_count": len(orbits),
        "normalization": "gamma >= 1",
        "witness_mode": witness_mode,
        "minimum_float": minimum[0],
        "carrier_bound_violated": minimum[0] < 1 - 1e-8,
        "minimum": {
            **minimum[1],
            "nonzero_slacks": {
                str(members(mask)): str(value)
                for mask, value in enumerate(minimum[2])
                if value != 0
            },
        },
        "orbits": audits,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "results"
        / "n5_exact_cone_eta_vertices.json",
    )
    parser.add_argument(
        "--witness-mode",
        choices=("global", "subgame"),
        default="global",
    )
    args = parser.parse_args()
    payload = run(args.witness_mode)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "orbits"}, indent=2))


if __name__ == "__main__":
    main()
