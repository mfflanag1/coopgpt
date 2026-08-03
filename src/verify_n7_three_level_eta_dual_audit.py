"""Replay the saved n=7 three-level eta-dual lower bounds exactly.

This verifier never calls an optimizer.  It rebuilds the global exact-game
cone, parses the rational dual multipliers saved by
``audit_n7_three_level_eta_duals.py``, checks stationarity in every cone
coordinate, and recomputes every certified lower bound.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from audit_n7_three_level_eta_duals import N, objective_from_orbit
from hunt_balanced_cone_carrier_ratio import build_balanced_cone


def replay_shape(shape, witness_mode):
    s_size = int(shape["S_size"])
    template = build_balanced_cone(N, s_size, witness_mode=witness_mode)
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
        objective = objective_from_orbit(orbit, s_size)
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
        distribution[str(lower_bound)] += 1
        minimum = lower_bound if minimum is None else min(minimum, lower_bound)

    assert minimum == F(shape["minimum"])
    assert distribution == Counter(shape["exact_value_distribution"])
    if int(shape["P_size"]) <= 2:
        assert minimum >= 1
    return {
        "S_size": s_size,
        "P_size": int(shape["P_size"]),
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
    assert audit["n"] == N
    witness_mode = {
        "global exact-game witnesses": "global",
    }.get(audit["witness_mode"], audit["witness_mode"])
    assert witness_mode == "global"
    shapes = [replay_shape(shape, witness_mode) for shape in audit["shapes"]]
    by_size = {shape["S_size"]: shape for shape in shapes}
    assert by_size[4]["exact_lower_bound_distribution"] == {
        "0": 14,
        "1": 12,
        "2": 8,
    }
    assert by_size[5]["exact_lower_bound_distribution"] == {"3": 5}
    payload = {
        "status": (
            "all saved n=7 exact rational lower-bound certificates replayed "
            "without optimization"
        ),
        "witness_mode": witness_mode,
        "checks": [
            "nonnegative inequality multipliers",
            "exact stationarity in every cone coordinate",
            "exact dual objective reconstruction",
            "lower bound at least one for every outside-pair orbit",
            "reported value distributions and minima",
        ],
        "total_orbits": sum(shape["orbit_count"] for shape in shapes),
        "shapes": shapes,
        "conclusion": (
            "all five residual 5+2 orbits have certified lower bound 3; "
            "the outside-pair carrier inequality is safe at n=7"
        ),
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
