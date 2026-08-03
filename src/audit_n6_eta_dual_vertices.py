"""Audit the complete six-player eta-dual vertex census exactly.

The input is produced by ``enumerate_n6_eta_dual_vertices.cpp``.  Every
record is a minimal balanced collection containing the canonical target S,
normalized so S has coefficient one.  Removing S and interpreting target
singletons as floor variables gives every undominated eta-dual vertex.

For each symmetry orbit this script minimizes the resulting slack objective
over the global-witness exact-game cone.  It then verifies exact rational
primal and dual solutions, making the finite theorem independently
checkable without trusting floating-point objective values.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from hunt_balanced_cone_carrier_ratio import build_balanced_cone, members


N = 6
FULL = (1 << N) - 1


def rationalize(value):
    return F(float(value)).limit_denominator(1_000_000)


def parse_fraction(value):
    return F(value)


def objective_from_orbit(orbit, s_size):
    target = (1 << s_size) - 1
    objective = [F(0)] * (1 << N)
    balanced = []
    for term in orbit["balanced_support"]:
        coalition = int(term["mask"])
        weight = parse_fraction(term["weight"])
        assert 0 < coalition < FULL and weight > 0
        balanced.append((coalition, weight))
        if coalition == target:
            assert weight == 1
        elif coalition.bit_count() == 1 and coalition & target:
            # This is an eta floor variable and has zero slack cost.
            pass
        else:
            objective[coalition] += weight

    degree = parse_fraction(orbit["degree"])
    rho = parse_fraction(orbit["rho"])
    assert degree == 1 + rho and rho >= 0
    for player in range(N):
        assert sum(
            weight for coalition, weight in balanced
            if coalition >> player & 1
        ) == degree
    return objective


def exact_optimum(template, objective_exact):
    objective = np.zeros_like(template["objective"])
    objective[: 1 << N] = [float(value) for value in objective_exact]
    result = linprog(
        objective,
        A_ub=template["A_ub"],
        b_ub=template["b_ub"],
        A_eq=template["A_eq"],
        b_eq=template["b_eq"],
        bounds=template["bounds"],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    point = [rationalize(value) for value in result.x]
    for row in range(template["A_ub"].shape[0]):
        sparse = template["A_ub"].getrow(row)
        lhs = sum(
            F(int(coefficient)) * point[column]
            for column, coefficient in zip(sparse.indices, sparse.data)
        )
        assert lhs <= F(int(template["b_ub"][row]))
    for row in range(template["A_eq"].shape[0]):
        sparse = template["A_eq"].getrow(row)
        lhs = sum(
            F(int(coefficient)) * point[column]
            for column, coefficient in zip(sparse.indices, sparse.data)
        )
        assert lhs == F(int(template["b_eq"][row]))

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
    stationarity = list(objective_exact) + [
        F(0)
    ] * (len(template["objective"]) - len(objective_exact))
    for row, multiplier in inequality_multipliers.items():
        sparse = template["A_ub"].getrow(row)
        for column, coefficient in zip(sparse.indices, sparse.data):
            stationarity[column] += multiplier * F(int(coefficient))
    for row, multiplier in equality_multipliers.items():
        sparse = template["A_eq"].getrow(row)
        for column, coefficient in zip(sparse.indices, sparse.data):
            stationarity[column] += multiplier * F(int(coefficient))
    assert all(value == 0 for value in stationarity)

    lower_bound = -sum(
        multiplier * F(int(template["b_ub"][row]))
        for row, multiplier in inequality_multipliers.items()
    ) - sum(
        multiplier * F(int(template["b_eq"][row]))
        for row, multiplier in equality_multipliers.items()
    )
    primal_value = sum(
        coefficient * value
        for coefficient, value in zip(objective_exact, point)
    )
    assert primal_value == lower_bound
    return {
        "status": "independently verified exact rational primal/dual optimum",
        "value": str(primal_value),
        "primal_nonzero_slacks": [
            {"coalition": members(mask, N), "value": str(point[mask])}
            for mask in range(1 << N)
            if point[mask] != 0
        ],
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


def audit_shape(shape, witness_mode):
    s_size = int(shape["S_size"])
    template = build_balanced_cone(N, s_size, witness_mode=witness_mode)
    records = []
    distribution = Counter()
    minimum = None
    for index, orbit in enumerate(shape["orbits"]):
        assert orbit["orbit_index"] == index
        objective = objective_from_orbit(orbit, s_size)
        certificate = exact_optimum(template, objective)
        distribution[certificate["value"]] += 1
        value = parse_fraction(certificate["value"])
        minimum = value if minimum is None else min(minimum, value)
        records.append({
            "orbit_index": index,
            "rho": orbit["rho"],
            "balanced_support": orbit["balanced_support"],
            "eta_objective": [
                {"coalition": members(mask, N), "coefficient": str(coefficient)}
                for mask, coefficient in enumerate(objective)
                if coefficient
            ],
            "certificate": certificate,
        })
        if (index + 1) % 50 == 0:
            print(
                f"S={s_size}: audited {index + 1}/{len(shape['orbits'])}; "
                f"minimum={minimum}",
                flush=True,
            )
    assert minimum is not None and minimum >= 1
    return {
        "S_size": s_size,
        "P_size": N - s_size,
        "orbit_count": len(records),
        "exact_value_distribution": dict(
            sorted(distribution.items(), key=lambda item: F(item[0]))
        ),
        "minimum": str(minimum),
        "carrier_bound_violated": False,
        "orbits": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--witness-mode", choices=("global", "subgame"), default="global"
    )
    parser.add_argument(
        "--s-size", type=int, action="append",
        help="audit only these target sizes (repeatable)",
    )
    args = parser.parse_args()
    census = json.loads(args.census.read_text())
    assert census["n"] == N and len(census["shapes"]) == 2
    selected = [
        shape for shape in census["shapes"]
        if args.s_size is None or int(shape["S_size"]) in args.s_size
    ]
    if not selected:
        raise ValueError("no census shape selected")
    shapes = [audit_shape(shape, args.witness_mode) for shape in selected]
    payload = {
        "status": "complete exact audit of all undominated n=6 eta-dual vertex orbits",
        "n": N,
        "vertex_correspondence": (
            "minimal balanced collections containing S, normalized to give S "
            "coefficient one; target singletons are zero-cost floor variables"
        ),
        "witness_mode": args.witness_mode,
        "shapes": shapes,
        "minimum": str(min(F(shape["minimum"]) for shape in shapes)),
        "carrier_bound_violated": False,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "status": payload["status"],
        "minimum": payload["minimum"],
        "shapes": [
            {key: value for key, value in shape.items() if key != "orbits"}
            for shape in shapes
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
