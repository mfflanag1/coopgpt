"""Replay every saved n=6 eta-dual lower-bound certificate exactly.

This verifier never calls an optimizer.  It reconstructs the universal
exact-game cone, parses the saved rational multipliers, checks stationarity
coordinate by coordinate, and recomputes each certified lower bound.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from audit_n6_eta_dual_vertices import N, objective_from_orbit
from hunt_balanced_cone_carrier_ratio import build_balanced_cone


def replay_shape(shape):
    s_size = int(shape["S_size"])
    template = build_balanced_cone(N, s_size, witness_mode="global")
    inequality_rows = {
        name: row for row, name in enumerate(template["inequality_names"])
    }
    equality_rows = {
        name: row for row, name in enumerate(template["equality_names"])
    }
    distribution = Counter()
    minimum = None
    for index, orbit in enumerate(shape["orbits"]):
        assert orbit["orbit_index"] == index
        orbit_with_degree = dict(orbit)
        orbit_with_degree["degree"] = str(1 + F(orbit["rho"]))
        objective = objective_from_orbit(orbit_with_degree, s_size)
        stationarity = list(objective) + [
            F(0)
        ] * (len(template["objective"]) - len(objective))
        certificate = orbit["certificate"]
        inequality_multipliers = {}
        for term in certificate["inequality_support"]:
            row = inequality_rows[term["constraint"]]
            multiplier = F(term["multiplier"])
            assert multiplier >= 0 and row not in inequality_multipliers
            inequality_multipliers[row] = multiplier
            sparse = template["A_ub"].getrow(row)
            for column, coefficient in zip(sparse.indices, sparse.data):
                stationarity[column] += multiplier * F(int(coefficient))
        equality_multipliers = {}
        for term in certificate["equality_support"]:
            row = equality_rows[term["constraint"]]
            multiplier = F(term["multiplier"])
            assert row not in equality_multipliers
            equality_multipliers[row] = multiplier
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
        assert lower_bound == F(certificate["value"])
        assert lower_bound >= 1
        distribution[str(lower_bound)] += 1
        minimum = lower_bound if minimum is None else min(minimum, lower_bound)
    assert minimum == F(shape["minimum"]) == 1
    assert distribution == Counter(shape["exact_value_distribution"])
    return {
        "S_size": s_size,
        "orbit_count": len(shape["orbits"]),
        "exact_lower_bound_distribution": dict(
            sorted(distribution.items(), key=lambda item: F(item[0]))
        ),
        "minimum": str(minimum),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text())
    assert audit["n"] == N and not audit["carrier_bound_violated"]
    shapes = [replay_shape(shape) for shape in audit["shapes"]]
    payload = {
        "status": "all saved exact rational lower-bound certificates replayed without optimization",
        "checks": [
            "nonnegative inequality multipliers",
            "exact stationarity in every cone coordinate",
            "exact dual objective reconstruction",
            "lower bound at least one for every orbit",
            "reported value distributions and minima",
        ],
        "total_orbits": sum(shape["orbit_count"] for shape in shapes),
        "shapes": shapes,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
