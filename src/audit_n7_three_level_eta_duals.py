"""Exact global-witness cone audit of the residual seven-player three-level
eta-dual orbits produced by enumerate_n7_three_level_eta_duals.cpp."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from hunt_balanced_cone_carrier_ratio import build_balanced_cone, members


N = 7
FULL = (1 << N) - 1


def rationalize(value):
    return F(float(value)).limit_denominator(1_000_000)


def objective_from_orbit(orbit, s_size):
    target = (1 << s_size) - 1
    objective = [F(0)] * (1 << N)
    balanced = []
    for term in orbit["balanced_support"]:
        coalition = int(term["mask"])
        weight = F(term["weight"])
        assert 0 < coalition < FULL and weight > 0
        balanced.append((coalition, weight))
        if coalition == target:
            assert weight == 1
        elif coalition.bit_count() == 1 and coalition & target:
            pass  # zero-cost target-floor variable
        else:
            objective[coalition] += weight
    degrees = [
        sum(weight for coalition, weight in balanced if coalition >> player & 1)
        for player in range(N)
    ]
    assert len(set(degrees)) == 1
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
        "value": str(primal_value),
        "primal_nonzero_slacks": [
            {"coalition": members(mask, N), "value": str(point[mask])}
            for mask in range(1 << N) if point[mask]
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


def audit_shape(shape):
    s_size = int(shape["S_size"])
    template = build_balanced_cone(N, s_size, witness_mode="global")
    records = []
    distribution = Counter()
    for index, orbit in enumerate(shape["orbits"]):
        assert orbit["orbit_index"] == index
        objective = objective_from_orbit(orbit, s_size)
        certificate = exact_optimum(template, objective)
        distribution[certificate["value"]] += 1
        records.append({
            "orbit_index": index,
            "balanced_support": orbit["balanced_support"],
            "carrier_mass": orbit["carrier_mass"],
            "eta_objective": [
                {"coalition": members(mask, N), "coefficient": str(coefficient)}
                for mask, coefficient in enumerate(objective) if coefficient
            ],
            "certificate": certificate,
        })
        print(
            f"S={s_size}: audited {index + 1}/{len(shape['orbits'])}; "
            f"value={certificate['value']}",
            flush=True,
        )
    minimum = min(F(value) for value in distribution)
    return {
        "S_size": s_size,
        "P_size": N - s_size,
        "orbit_count": len(records),
        "exact_value_distribution": dict(
            sorted(distribution.items(), key=lambda item: F(item[0]))
        ),
        "minimum": str(minimum),
        "carrier_bound_violated": minimum < 1,
        "orbits": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    census = json.loads(args.census.read_text())
    shapes = [audit_shape(shape) for shape in census["shapes"]]
    by_size = {shape["S_size"]: shape for shape in shapes}
    assert by_size[4]["exact_value_distribution"] == {"0": 14, "1": 12, "2": 8}
    assert by_size[5]["exact_value_distribution"] == {"3": 5}
    payload = {
        "status": "exact rational audit of residual n=7 three-level eta-dual orbits",
        "n": N,
        "witness_mode": "global exact-game witnesses",
        "shapes": shapes,
        "conclusion": (
            "the 5+2 split is universally safe at n=7; the 4+3 split has "
            "fourteen exact-cone zero-cost obstruction orbits"
        ),
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "status": payload["status"],
        "shapes": [
            {key: value for key, value in shape.items() if key != "orbits"}
            for shape in shapes
        ],
        "conclusion": payload["conclusion"],
    }, indent=2))


if __name__ == "__main__":
    main()
