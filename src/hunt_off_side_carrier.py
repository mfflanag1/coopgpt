"""Targeted counterexample hunt for the off-side carrier conjecture.

Games are exact by construction: proper-coalition worths are the lower envelope
of finitely many common-sum points.  The float screen keeps only coalitions S
that are binding at the leximin point and fail the star condition, then scores

    min_{empty != C proper subset S}
      slack_phi((N\\S) union C) - slack_phi(C).

A positive score would escape every off-side slack-domination certificate and
is therefore exactified before it is treated as a candidate.  Nonpositive best
scores are useful boundary data, not proof of the conjecture.
"""
from __future__ import annotations

import argparse
import json
import random
import time
from fractions import Fraction as F

from scipy.optimize import linprog

from hunt_exact_points import game_from_points, rand_point_sum
from classify_saved_capacity_frontier import residual_cover_float
from lemD import core_max_xS, residual_cover, star_holds, xS
from leximin import leximin_core_exact, leximin_core_float


def members(mask, n):
    return [i + 1 for i in range(n) if mask >> i & 1]


def core_matrices(game):
    rows = [
        [-1.0 if coalition >> i & 1 else 0.0 for i in range(game.n)]
        for coalition in range(1, game.N)
    ]
    rhs = [-float(game.v[coalition]) for coalition in range(1, game.N)]
    return rows, rhs


def maximize_target(game, target, rows, rhs, lower=None):
    inequalities = list(rows)
    bounds_rhs = list(rhs)
    if lower is not None:
        for player in range(game.n):
            if target >> player & 1:
                row = [0.0] * game.n
                row[player] = -1.0
                inequalities.append(row)
                bounds_rhs.append(-lower[player])
    result = linprog(
        [-1.0 if target >> i & 1 else 0.0 for i in range(game.n)],
        A_ub=inequalities,
        b_ub=bounds_rhs,
        A_eq=[[1.0] * game.n],
        b_eq=[float(game.v[game.N])],
        bounds=[(None, None)] * game.n,
        method="highs",
    )
    return None if not result.success else -result.fun


def carrier_score(game, phi, target):
    off_side = game.N ^ target
    exact = isinstance(phi[0], F)
    worth = (lambda coalition: game.v[coalition]) if exact else (
        lambda coalition: float(game.v[coalition])
    )
    comparisons = []
    for face in range(1, game.N):
        if face & target != face or face == target:
            continue
        carrier = off_side | face
        face_slack = xS(phi, face, game.n) - worth(face)
        carrier_slack = xS(phi, carrier, game.n) - worth(carrier)
        comparisons.append((carrier_slack - face_slack, face, carrier))
    return min(comparisons)


def signed_point(n, total, radius, rng):
    point = [rng.randint(-radius, radius) for _ in range(n - 1)]
    point.append(total - sum(point))
    rng.shuffle(point)
    return point


def generate_points(n, rng, mode, count=None):
    count = rng.randint(2, 5) if count is None else count
    total = rng.randint(n, 6 * n)
    if mode == "composition":
        return [rand_point_sum(n, total, rng) for _ in range(count)]
    if mode == "signed":
        return [signed_point(n, total, 3 * n, rng) for _ in range(count)]
    base = signed_point(n, total, 2 * n, rng)
    points = [base]
    for _ in range(count - 1):
        point = list(base)
        for __ in range(rng.randint(1, 2 * n)):
            source, target = rng.sample(range(n), 2)
            amount = rng.randint(-n, n)
            point[source] += amount
            point[target] -= amount
        points.append(point)
    return points


def exactify(points, target):
    game = game_from_points(len(points[0]), points)
    phi = leximin_core_exact(game)
    holds, star_value, _ = star_holds(game, phi, target)
    binding = core_max_xS(game, target) > xS(phi, target, game.n)
    score, face, carrier = carrier_score(game, phi, target)
    cover = None if holds else residual_cover(game, phi, target)
    return {
        "phi": [str(value) for value in phi],
        "binding": binding,
        "star_holds": holds,
        "star_value": str(star_value),
        "score": str(score),
        "minimizing_face": members(face, game.n),
        "carrier": members(carrier, game.n),
        "residual_levels": []
        if cover is None
        else [str(value) for value in sorted(set(cover["r"].values()))],
    }


def rational_screen(game, phi_float, target, denominator=10000):
    """Recover the apparent rational point and certify its core/tight geometry.

    This is much cheaper than recomputing leximin exactly.  It is a discovery
    screen only; a positive carrier score still triggers full exactification.
    """
    phi = [F(float(value)).limit_denominator(denominator) for value in phi_float]
    if sum(phi) != game.v[game.N]:
        return None
    if any(xS(phi, coalition, game.n) < game.v[coalition]
           for coalition in range(1, game.N)):
        return None
    cover = residual_cover(game, phi, target)
    if cover is None:
        return None
    score, face, carrier = carrier_score(game, phi, target)
    return {
        "phi": [str(value) for value in phi],
        "score": str(score),
        "minimizing_face": members(face, game.n),
        "carrier": members(carrier, game.n),
        "residual_levels": [
            str(value) for value in sorted(set(cover["r"].values()))
        ],
    }


def hunt(n, trials, seed, mode, min_levels, generators=None):
    rng = random.Random(seed)
    started = time.time()
    star_failures = 0
    float_eligible_failures = 0
    eligible_failures = 0
    best = None
    for trial in range(trials):
        points = generate_points(n, rng, mode, generators)
        game = game_from_points(n, points)
        phi = leximin_core_float(n, game.v, tol=1e-9)
        if phi is None:
            continue
        rows, rhs = core_matrices(game)
        coalitions = [
            target
            for target in range(1, game.N)
            if target.bit_count() >= 2
        ]
        rng.shuffle(coalitions)
        for target in coalitions:
            phi_target = xS(phi, target, n)
            maximum = maximize_target(game, target, rows, rhs)
            if maximum is None or maximum <= phi_target + 1e-7:
                continue
            star_value = maximize_target(game, target, rows, rhs, lower=phi)
            if star_value is None or star_value > phi_target + 1e-7:
                continue
            star_failures += 1
            residuals = residual_cover_float(game, phi, target)
            levels = sorted({round(value, 7) for value in residuals.values()})
            if len(levels) < min_levels:
                continue
            float_eligible_failures += 1
            rational_record = rational_screen(game, phi, target)
            if rational_record is None or len(rational_record["residual_levels"]) < min_levels:
                continue
            eligible_failures += 1
            score, face, carrier = carrier_score(game, phi, target)
            record = {
                "trial": trial,
                "S": members(target, n),
                "S_mask": target,
                "score_float": score,
                "minimizing_face": members(face, n),
                "carrier": members(carrier, n),
                "phi_float": phi,
                "residual_levels_float": levels,
                "v": [str(value) for value in game.v],
                "points": points,
                "rational_screen": rational_record,
            }
            if best is None or score > best["score_float"]:
                best = record
            if F(rational_record["score"]) > 0:
                record["exactification"] = exactify(points, target)
                if F(record["exactification"]["score"]) <= 0:
                    continue
                return {
                    "status": "positive float candidate found and exactified",
                    "n": n,
                    "mode": mode,
                    "generators": generators,
                    "seed": seed,
                    "trials_requested": trials,
                    "trials_completed": trial + 1,
                    "binding_star_failures": star_failures,
                    "float_eligible_residual_failures": float_eligible_failures,
                    "eligible_residual_failures": eligible_failures,
                    "best": record,
                }
    if best is not None:
        best["exactification"] = exactify(best["points"], best["S_mask"])
    return {
        "status": "no counterexample; best boundary case exactified",
        "n": n,
        "mode": mode,
        "generators": generators,
        "seed": seed,
        "trials_requested": trials,
        "trials_completed": trials,
        "binding_star_failures": star_failures,
        "float_eligible_residual_failures": float_eligible_failures,
        "eligible_residual_failures": eligible_failures,
        "elapsed_seconds": time.time() - started,
        "best": best,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--trials", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument(
        "--mode", choices=["composition", "signed", "nearby"], default="nearby"
    )
    parser.add_argument("--min-levels", type=int, default=3)
    parser.add_argument("--generators", type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(
        json.dumps(
            hunt(
                args.n,
                args.trials,
                args.seed,
                args.mode,
                args.min_levels,
                args.generators,
            ),
            indent=2,
        )
    )
