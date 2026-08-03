"""Targeted screen for dimension-minimality of the exact Lmin counterexample.

The five-player theorem raises one proper coalition and lowers no other worth.
This script generates four-player pairs with exactly that property by taking an
endpoint lower envelope of common-sum allocations and adjoining one allocation
that lowers only the target S=N\{p}.  It then compares the singleton-normalized
Lmin points.  Floating LPs are only a discovery screen; every apparent decrease
is replayed by the exact rational implementation before it can be reported.

This is finite evidence, not a proof of four-player monotonicity.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from fractions import Fraction as F

from hunt_exact_points import game_from_points
from leximin import leximin_core_exact, leximin_core_float


if sys.flags.optimize:
    raise RuntimeError("run this audit without Python -O")


N = 4
FULL = (1 << N) - 1
TARGET = FULL ^ 1  # outside player is coordinate 0; S={2,3,4}


def payoff(point, coalition):
    return sum(point[i] for i in range(N) if coalition >> i & 1)


def random_zero_sum_point(radius, rng):
    point = [rng.randint(-radius, radius) for _ in range(N - 1)]
    point.append(-sum(point))
    return tuple(point)


def changed_coalitions(endpoint_points, added_point):
    changed = []
    for coalition in range(1, FULL):
        endpoint = min(payoff(point, coalition) for point in endpoint_points)
        if payoff(added_point, coalition) < endpoint:
            changed.append(coalition)
    return changed


def sign_pattern(base_phi, endpoint_phi, tolerance=1e-7):
    signs = []
    for player in range(1, N):
        delta = endpoint_phi[player] - base_phi[player]
        signs.append("+" if delta > tolerance else "-" if delta < -tolerance else "0")
    return "".join(signs)


def run_family(*, trials, seed, radius, min_generators, max_generators):
    rng = random.Random(seed)
    counts = {
        "draws": 0,
        "pairs_differing_only_at_target": 0,
        "binding_pairs": 0,
        "floating_drop_flags": 0,
        "exact_drops": 0,
    }
    patterns = {}
    exact_counterexample = None
    started = time.time()

    for _ in range(trials):
        generator_count = rng.randint(min_generators, max_generators)
        endpoint_points = [(0, 0, 0, 0)]
        endpoint_points.extend(
            random_zero_sum_point(radius, rng)
            for _ in range(generator_count - 1)
        )
        added_point = random_zero_sum_point(radius, rng)
        counts["draws"] += 1

        if changed_coalitions(endpoint_points, added_point) != [TARGET]:
            continue
        counts["pairs_differing_only_at_target"] += 1

        base = game_from_points(N, endpoint_points + [added_point])
        endpoint = game_from_points(N, endpoint_points)
        base_phi = leximin_core_float(N, [float(value) for value in base.v], tol=1e-8)
        endpoint_phi = leximin_core_float(
            N, [float(value) for value in endpoint.v], tol=1e-8
        )
        if base_phi is None or endpoint_phi is None:
            raise RuntimeError("floating Lmin solver failed on an exact lower envelope")
        if sum(base_phi[1:]) >= float(endpoint.v[TARGET]) - 1e-7:
            continue
        counts["binding_pairs"] += 1

        pattern = sign_pattern(base_phi, endpoint_phi)
        patterns[pattern] = patterns.get(pattern, 0) + 1
        if "-" not in pattern:
            continue
        counts["floating_drop_flags"] += 1

        exact_base_phi = leximin_core_exact(base)
        exact_endpoint_phi = leximin_core_exact(endpoint)
        exact_pattern = "".join(
            "+" if exact_endpoint_phi[i] > exact_base_phi[i]
            else "-" if exact_endpoint_phi[i] < exact_base_phi[i]
            else "0"
            for i in range(1, N)
        )
        if "-" in exact_pattern:
            counts["exact_drops"] += 1
            exact_counterexample = {
                "endpoint_generators": endpoint_points,
                "added_base_generator": added_point,
                "base_lmin": [str(value) for value in exact_base_phi],
                "endpoint_lmin": [str(value) for value in exact_endpoint_phi],
                "target_sign_pattern": exact_pattern,
            }
            break

    return {
        "parameters": {
            "trials": trials,
            "seed": seed,
            "radius": radius,
            "generator_range": [min_generators, max_generators],
        },
        "counts": counts,
        "target_sign_patterns": dict(sorted(patterns.items())),
        "exact_counterexample": exact_counterexample,
        "elapsed_seconds": time.time() - started,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    scale = 1 if args.full else 25
    report = {
        "status": "finite targeted screen; not a four-player theorem",
        "n": N,
        "target": [2, 3, 4],
        "families": [
            run_family(
                trials=500_000 // scale,
                seed=8_675_309,
                radius=30,
                min_generators=2,
                max_generators=2,
            ),
            run_family(
                trials=750_000 // scale,
                seed=424_242,
                radius=40,
                min_generators=2,
                max_generators=6,
            ),
        ],
    }
    report["exact_drops"] = sum(
        family["counts"]["exact_drops"] for family in report["families"]
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
