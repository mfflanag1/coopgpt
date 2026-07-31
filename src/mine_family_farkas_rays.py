"""Sample extreme rays of the three-game family Farkas cone.

For fixed n and two bump labels A,B, the constraint matrix of the family LP is
independent of coalition worths.  Its Farkas cone is therefore the finite
combinatorial object behind the universal three-game question.  This tool
normalizes the cone, optimizes many deterministic random objectives, and emits
canonical exact-looking ray signatures together with only the invariants useful
for a proof: support size, monotonicity rows, and how supported coalitions meet
A, B, and the remainder.

This is a discovery miner, not a completeness claim.  Any proposed finite
classification still needs full vertex enumeration or a structural proof.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from fractions import Fraction as F
from functools import reduce

from scipy.optimize import linprog

from family_infeasible import build_constraints
from tugame import Game


def lcm(a, b):
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def members(mask, n):
    return tuple(i + 1 for i in range(n) if mask >> i & 1)


def relation(coalition, A, B, grand):
    remainder = grand & ~(A | B)
    parts = []
    if coalition & A:
        parts.append("A")
    if coalition & B:
        parts.append("B")
    if coalition & remainder:
        parts.append("R")
    return "".join(parts) or "empty"


def canonical_ray(values, inequality_count, tolerance=1e-8):
    fractions = [
        F(0) if abs(value) <= tolerance else F(float(value)).limit_denominator(10000)
        for value in values
    ]
    denominators = [value.denominator for value in fractions if value]
    scale = reduce(lcm, denominators, 1)
    integers = [int(value * scale) for value in fractions]
    nonzero = [abs(value) for value in integers if value]
    divisor = reduce(math.gcd, nonzero) if nonzero else 1
    integers = [value // divisor for value in integers]
    # Farkas inequality multipliers are oriented by nonnegative inequality rows.
    if next((value for value in integers[:inequality_count] if value), 1) < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def ray_invariants(ray, rowmeta, n, A, B, grand):
    inequality_count = len(rowmeta)
    active_ineq = []
    relation_counts = Counter()
    mono_counts = Counter()
    bump_sensitivity = Counter()
    for index, weight in enumerate(ray[:inequality_count]):
        if not weight:
            continue
        meta = rowmeta[index]
        if meta[0] == "core":
            _kind, game, coalition = meta
            if game == 1 and coalition == A:
                bump_sensitivity["A"] += weight
            if game == 2 and coalition == B:
                bump_sensitivity["B"] += weight
            rel = relation(coalition, A, B, grand)
            relation_counts[f"g{game}:{rel}"] += 1
            active_ineq.append(
                {"kind": "core", "game": game, "coalition": members(coalition, n),
                 "relation": rel, "weight": weight}
            )
        else:
            _kind, source, target, player, label = meta
            arm = "A" if label == A else "B"
            mono_counts[arm] += 1
            active_ineq.append(
                {"kind": "mono", "edge": [source, target], "arm": arm,
                 "player": player + 1, "weight": weight}
            )
    equality_weights = ray[inequality_count:]
    return {
        "support_size": len(active_ineq) + sum(weight != 0 for weight in equality_weights),
        "inequality_support_size": len(active_ineq),
        "core_relation_counts": dict(sorted(relation_counts.items())),
        "mono_counts": dict(sorted(mono_counts.items())),
        "bump_sensitivity": dict(sorted(bump_sensitivity.items())),
        "efficiency_weights": list(equality_weights),
        "active_inequalities": active_ineq,
    }


def mine(n, A, B, samples, seed):
    grand = (1 << n) - 1
    zero = Game(n, [F(0)] * (1 << n))
    _nv, a_ub, _b_ub, a_eq, _b_eq, rowmeta = build_constraints(
        [zero, zero, zero], [(0, 1, A), (0, 2, B)]
    )
    p, q = len(a_ub), len(a_eq)
    # Farkas variables are (lambda >= 0, beta free).  Stationarity is
    # lambda^T A_ub + beta^T A_eq = 0.  Sum(lambda)=1 normalizes each ray.
    stationarity = []
    for column in range(len(a_ub[0])):
        stationarity.append(
            [a_ub[row][column] for row in range(p)]
            + [a_eq[row][column] for row in range(q)]
        )
    stationarity.append([1.0] * p + [0.0] * q)
    rhs = [0.0] * (len(stationarity) - 1) + [1.0]
    bounds = [(0.0, None)] * p + [(None, None)] * q

    rng = random.Random(seed)
    rays = {}
    bump_A_index = next(
        index for index, meta in enumerate(rowmeta)
        if meta == ("core", 1, A)
    )
    bump_B_index = next(
        index for index, meta in enumerate(rowmeta)
        if meta == ("core", 2, B)
    )
    for sample in range(samples):
        objective = [rng.uniform(-1, 1) for _ in range(p + q)]
        # A quarter of the objectives target the only rays that can couple the
        # two changed worths.  Random perturbations select vertices of the
        # exposed face instead of returning an arbitrary convex combination.
        if sample < samples // 4:
            focus = 10.0 ** (1 + sample % 4)
            objective[bump_A_index] -= focus
            objective[bump_B_index] -= focus
        result = linprog(
            objective,
            A_eq=stationarity,
            b_eq=rhs,
            bounds=bounds,
            method="highs",
        )
        if not result.success:
            continue
        ray = canonical_ray(result.x, p)
        rays.setdefault(ray, ray_invariants(ray, rowmeta, n, A, B, grand))

    support_histogram = Counter(item["support_size"] for item in rays.values())
    relation_signatures = Counter(
        json.dumps(item["core_relation_counts"], sort_keys=True)
        for item in rays.values()
    )
    both_sensitive = sum(
        set(item["bump_sensitivity"]) == {"A", "B"}
        for item in rays.values()
    )
    return {
        "status": "sampled extreme rays; not a complete enumeration",
        "n": n,
        "A": members(A, n),
        "B": members(B, n),
        "R": members(grand & ~(A | B), n),
        "objectives": samples,
        "distinct_rays": len(rays),
        "support_histogram": dict(sorted(support_histogram.items())),
        "relation_signature_count": len(relation_signatures),
        "both_bump_sensitive_rays": both_sensitive,
        "relation_signatures": [
            {"count": count, "signature": json.loads(signature)}
            for signature, count in relation_signatures.most_common()
        ],
        "rays": list(rays.values()),
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--A", type=lambda value: int(value, 0), default=0b00011)
    parser.add_argument("--B", type=lambda value: int(value, 0), default=0b01100)
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260731)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(mine(args.n, args.A, args.B, args.samples, args.seed), indent=2))
