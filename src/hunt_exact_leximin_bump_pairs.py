"""Direct search for exact-game leximin coalition-monotonicity violations.

An endpoint game ``w`` is generated as the lower envelope of common-sum
allocations.  For a proper nonsingleton target ``S``, solve for an allocation
``p`` satisfying every endpoint core inequality except the one at ``S`` and
minimizing ``p(S)``.  If ``p(S) < w(S)``, then

    v = lower_envelope(endpoint_generators + [p])

is exact, ``w`` is exact, and the two games differ only at ``S``.  Thus every
pair examined by the leximin comparison is an exact-preserving coalition bump
by construction, rather than a random game perturbation that must later be
filtered for exactness.

Floating-point LPs are used only for screening.  Any apparent target-player
drop is rebuilt with the repository's exact rational LP and checked again by
the exact leximin implementation before being reported as a candidate.
"""
from __future__ import annotations

import argparse
import json
import random
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog

from hunt_exact_points import game_from_points
from leximin import leximin_core_exact, leximin_core_float
from tugame import exact_lp_min


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def lower_envelope(n, points):
    full = (1 << n) - 1
    total = sum(points[0])
    values = [0.0] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(payoff(point, coalition) for point in points)
    values[full] = total
    return values


def random_common_sum_points(n, count, radius, rng):
    points = []
    for _ in range(count):
        prefix = [rng.randint(-radius, radius) for _ in range(n - 1)]
        points.append(prefix + [-sum(prefix)])
    return points


def relaxed_target_float(n, values, target):
    full = (1 << n) - 1
    objective = np.array([
        1.0 if target >> player & 1 else 0.0 for player in range(n)
    ])
    rows, bounds = [], []
    for coalition in range(1, full):
        if coalition == target:
            continue
        rows.append([
            -1.0 if coalition >> player & 1 else 0.0
            for player in range(n)
        ])
        bounds.append(-values[coalition])
    result = linprog(
        objective,
        A_ub=np.array(rows),
        b_ub=np.array(bounds),
        A_eq=np.ones((1, n)),
        b_eq=np.array([values[full]]),
        bounds=[(None, None)] * n,
        method="highs",
    )
    if not result.success:
        return None
    return result.fun, result.x.tolist()


def relaxed_target_exact(n, values, target):
    full = (1 << n) - 1
    objective = [F(1) if target >> player & 1 else F(0)
                 for player in range(n)]
    rows, bounds = [], []
    for coalition in range(1, full):
        if coalition == target:
            continue
        rows.append([
            F(-1) if coalition >> player & 1 else F(0)
            for player in range(n)
        ])
        bounds.append(-F(values[coalition]))
    optimum, point = exact_lp_min(
        objective,
        rows,
        bounds,
        [[F(1)] * n],
        [F(values[full])],
    )
    if optimum is None or optimum == "unbounded":
        return None
    return optimum, point


def members(coalition, n):
    return [player + 1 for player in range(n) if coalition >> player & 1]


def exactify_candidate(n, endpoint_points, target):
    endpoint_values = lower_envelope(n, endpoint_points)
    relaxed = relaxed_target_exact(n, endpoint_values, target)
    if relaxed is None:
        return None
    base_target, added_point = relaxed
    endpoint_game = game_from_points(n, endpoint_points)
    base_game = game_from_points(n, endpoint_points + [added_point])
    full = (1 << n) - 1
    changed = [
        coalition for coalition in range(1, full)
        if base_game.v[coalition] != endpoint_game.v[coalition]
    ]
    if changed != [target] or not base_target < endpoint_game.v[target]:
        return None
    base_phi = leximin_core_exact(base_game)
    endpoint_phi = leximin_core_exact(endpoint_game)
    drops = [
        player for player in range(n)
        if target >> player & 1 and endpoint_phi[player] < base_phi[player]
    ]
    return {
        "n": n,
        "target": members(target, n),
        "endpoint_generators": endpoint_points,
        "added_base_generator": [str(value) for value in added_point],
        "base_target_value": str(base_game.v[target]),
        "endpoint_target_value": str(endpoint_game.v[target]),
        "base_leximin": [str(value) for value in base_phi],
        "endpoint_leximin": [str(value) for value in endpoint_phi],
        "target_player_drops": [player + 1 for player in drops],
        "changed_coalitions": [members(coalition, n) for coalition in changed],
    }


def hunt(n, trials, seed, radius, generators):
    rng = random.Random(seed)
    full = (1 << n) - 1
    targets = [
        coalition for coalition in range(1, full)
        if 2 <= coalition.bit_count() < n
    ]
    counts = {
        "trials": 0,
        "relaxable_targets": 0,
        "binding_pairs": 0,
        "float_drops": 0,
        "exact_candidates": 0,
    }
    slope_patterns = {}
    for _ in range(trials):
        count = rng.randint(generators[0], generators[1])
        points = random_common_sum_points(n, count, radius, rng)
        values = lower_envelope(n, points)
        target = rng.choice(targets)
        counts["trials"] += 1
        relaxed = relaxed_target_float(n, values, target)
        if relaxed is None or relaxed[0] >= values[target] - 1e-8:
            continue
        counts["relaxable_targets"] += 1
        added_point = relaxed[1]
        base_values = lower_envelope(n, points + [added_point])
        changed = [
            coalition for coalition in range(1, full)
            if abs(base_values[coalition] - values[coalition]) > 1e-7
        ]
        if changed != [target]:
            continue
        base_phi = leximin_core_float(n, base_values, tol=1e-8)
        endpoint_phi = leximin_core_float(n, values, tol=1e-8)
        if base_phi is None or endpoint_phi is None:
            continue
        if sum(base_phi[player] for player in range(n) if target >> player & 1) >= values[target] - 1e-7:
            continue
        counts["binding_pairs"] += 1
        signs = tuple(
            1 if endpoint_phi[player] > base_phi[player] + 1e-7 else
            -1 if endpoint_phi[player] < base_phi[player] - 1e-7 else 0
            for player in range(n) if target >> player & 1
        )
        key = "".join("+" if sign > 0 else "-" if sign < 0 else "0"
                      for sign in signs)
        slope_patterns[key] = slope_patterns.get(key, 0) + 1
        if any(sign < 0 for sign in signs):
            counts["float_drops"] += 1
            exact = exactify_candidate(n, points, target)
            if exact is not None and exact["target_player_drops"]:
                counts["exact_candidates"] += 1
                return {"status": "exact counterexample candidate", "counts": counts,
                        "target_sign_patterns": slope_patterns, "candidate": exact}
    return {
        "status": "no exact target-player drop found",
        "scope": "finite randomized discovery screen, not a theorem",
        "n": n,
        "seed": seed,
        "radius": radius,
        "generator_range": list(generators),
        "counts": counts,
        "target_sign_patterns": slope_patterns,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--trials", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--radius", type=int, default=20)
    parser.add_argument("--min-generators", type=int, default=3)
    parser.add_argument("--max-generators", type=int, default=7)
    args = parser.parse_args()
    report = hunt(
        args.n,
        args.trials,
        args.seed,
        args.radius,
        (args.min_generators, args.max_generators),
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
