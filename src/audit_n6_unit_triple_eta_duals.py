"""Complete exact audit of the first n=6 multilevel eta-dual layer.

For S={1,2,3}, P={4,5,6}, consider eta duals with rho=1, zero floor
weights, and three unit-weight coalitions.  Equivalently every target player
has degree one and every outside player degree two.  There are only 16
S_3 x S_3 symmetry classes.  Each fixed dual cost is minimized over the
universal exact-game slack cone and certified by exact rational primal and
dual solutions.
"""
from __future__ import annotations

import itertools
import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from hunt_balanced_cone_carrier_ratio import build_balanced_cone, members
from sample_eta_dual_orbits import permute_mask, player_permutations

if not __debug__:
    raise RuntimeError("certificate generation must not run with Python -O")


N = 6
S_SIZE = 3
FULL = (1 << N) - 1


def rationalize(value):
    return F(float(value)).limit_denominator(1_000_000)


def enumerate_orbits():
    group = list(player_permutations(N, S_SIZE))
    representatives = set()
    # sa maps each target player to its unique edge; pa maps each outside
    # player to the unique edge from which it is absent.
    for target_assignment in itertools.product(range(3), repeat=3):
        for outside_absence in itertools.product(range(3), repeat=3):
            edges = [0, 0, 0]
            for player, edge in enumerate(target_assignment):
                edges[edge] |= 1 << player
            for player, absent_edge in enumerate(outside_absence, start=3):
                for edge in range(3):
                    if edge != absent_edge:
                        edges[edge] |= 1 << player
            if any(edge in (0, FULL) for edge in edges):
                continue
            canonical = min(
                tuple(sorted(permute_mask(edge, permutation) for edge in edges))
                for permutation in group
            )
            representatives.add(canonical)
    return sorted(representatives)


def exact_optimum(template, support):
    objective_exact = [F(0)] * len(template["objective"])
    for coalition in support:
        objective_exact[coalition] += 1
    objective = np.asarray([float(value) for value in objective_exact])
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
    stationarity = objective_exact[:]
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    representatives = enumerate_orbits()
    assert len(representatives) == 16
    template = build_balanced_cone(N, S_SIZE, witness_mode="global")
    records = []
    for orbit_index, support in enumerate(representatives):
        certificate = exact_optimum(template, support)
        records.append({
            "orbit_index": orbit_index,
            "support": [members(coalition, N) for coalition in support],
            "certificate": certificate,
        })
    distribution = Counter(record["certificate"]["value"] for record in records)
    assert distribution == Counter({"2": 9, "1": 7})
    payload = {
        "status": "complete exact audit of n=6 rho=1 unit-triple eta duals",
        "split": {"S": [1, 2, 3], "P": [4, 5, 6]},
        "degree_pattern": "degree one on S and degree two on P",
        "symmetry_group": "S3 x S3",
        "orbit_count": len(records),
        "exact_value_distribution": dict(sorted(distribution.items())),
        "minimum": "1",
        "carrier_bound_violated": False,
        "orbits": records,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "orbits"}, indent=2))


if __name__ == "__main__":
    main()
