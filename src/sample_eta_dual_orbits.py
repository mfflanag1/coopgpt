"""Sample symmetry orbits of eta-dual vertices and audit their cone costs.

This targets the finite obstruction polyhedron directly.  Random generic
coalition costs select basic feasible eta-dual vertices; exact rationalization
and S_m x S_k canonicalization deduplicate them before each representative is
minimized over the universal subgame or global-witness slack cone.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from hunt_balanced_cone_carrier_ratio import (
    build_balanced_cone,
    eta_dual,
    members,
    minimize_cone,
    proper_coalitions,
)


def player_permutations(n, s_size):
    for inside in itertools.permutations(range(s_size)):
        for outside_raw in itertools.permutations(range(n - s_size)):
            outside = tuple(s_size + player for player in outside_raw)
            yield tuple(inside) + outside


def permute_mask(mask, permutation):
    result = 0
    for old, new in enumerate(permutation):
        if mask >> old & 1:
            result |= 1 << new
    return result


def rationalize_vertex(n, s_size, lambdas, dual_point):
    proper = proper_coalitions(n)
    coalition_count = len(proper)
    vertex = [F(0)] * (1 << n)
    for coalition in proper:
        vertex[coalition] = F(float(lambdas[coalition])).limit_denominator(10_000)
    floors = [
        F(float(dual_point[coalition_count + player])).limit_denominator(10_000)
        for player in range(s_size)
    ]
    rho = F(float(dual_point[-1])).limit_denominator(10_000)
    assert all(value >= 0 for value in vertex + floors + [rho])
    for player in range(n):
        degree = sum(
            vertex[coalition]
            for coalition in proper
            if coalition >> player & 1
        )
        if player < s_size:
            assert degree + floors[player] == rho
        else:
            assert degree == 1 + rho
    return tuple(vertex), tuple(floors), rho


def canonical_key(n, s_size, vertex, floors, rho, group):
    keys = []
    for permutation in group:
        permuted = [F(0)] * (1 << n)
        for coalition, value in enumerate(vertex):
            if value:
                permuted[permute_mask(coalition, permutation)] = value
        permuted_floors = [F(0)] * s_size
        for player, value in enumerate(floors):
            permuted_floors[permutation[player]] = value
        keys.append(tuple(permuted) + tuple(permuted_floors) + (rho,))
    return min(keys)


def random_costs(n, rng, mode):
    costs = np.zeros(1 << n)
    for coalition in proper_coalitions(n):
        if mode == 0:
            costs[coalition] = rng.uniform(0.01, 20.0)
        elif mode == 1:
            costs[coalition] = 10 ** rng.uniform(-2.0, 2.0)
        else:
            costs[coalition] = rng.randint(1, 50) + rng.random() * 1e-4
    return costs


def run(n, s_size, samples, seed, witness_mode):
    rng = random.Random(seed)
    group = list(player_permutations(n, s_size))
    orbits = {}
    saturation = []
    checkpoint = max(1, samples // 20)
    for sample in range(samples):
        costs = random_costs(n, rng, sample % 3)
        _, lambdas, dual_point = eta_dual(n, s_size, costs)
        vertex, floors, rho = rationalize_vertex(
            n, s_size, lambdas, dual_point
        )
        key = canonical_key(n, s_size, vertex, floors, rho, group)
        if key not in orbits:
            orbits[key] = {
                "first_sample": sample,
                "vertex": vertex,
                "floors": floors,
                "rho": rho,
            }
        if (sample + 1) % checkpoint == 0 or sample + 1 == samples:
            saturation.append({"samples": sample + 1, "orbits": len(orbits)})

    template = build_balanced_cone(n, s_size, witness_mode=witness_mode)
    records = []
    minimum = None
    for orbit_index, data in enumerate(orbits.values()):
        objective = np.asarray([float(value) for value in data["vertex"]])
        value, slacks = minimize_cone(template, objective)
        record = {
            "orbit_index": orbit_index,
            "first_sample": data["first_sample"],
            "minimum_float": value,
            "rho": str(data["rho"]),
            "lambda_support": [
                {
                    "coalition": members(coalition, n),
                    "coefficient": str(data["vertex"][coalition]),
                }
                for coalition in proper_coalitions(n)
                if data["vertex"][coalition] != 0
            ],
            "floor_weights": [str(value) for value in data["floors"]],
        }
        records.append(record)
        if minimum is None or value < minimum[0]:
            minimum = (value, record, slacks)
    return {
        "status": "symmetry-reduced eta-dual vertex sample and universal-cone audit",
        "n": n,
        "S_size": s_size,
        "P_size": n - s_size,
        "samples": samples,
        "seed": seed,
        "symmetry_group_size": len(group),
        "witness_mode": witness_mode,
        "distinct_sampled_orbits": len(orbits),
        "saturation": saturation,
        "carrier_bound_violated": minimum is not None and minimum[0] < 1 - 1e-8,
        "minimum": None if minimum is None else {
            **minimum[1],
            "nonzero_slacks": {
                str(members(mask, n)): float(value)
                for mask, value in enumerate(minimum[2])
                if abs(value) > 1e-8
            },
        },
        "orbits": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--s-size", type=int, default=3)
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261109)
    parser.add_argument(
        "--witness-mode", choices=("subgame", "global"), default="global"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(
        args.n,
        args.s_size,
        args.samples,
        args.seed,
        args.witness_mode,
    )
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "orbits"}, indent=2))


if __name__ == "__main__":
    main()
