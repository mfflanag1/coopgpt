"""Targeted hunt against the minimum-residual-class carrier conjecture.

Games are exact lower envelopes of common-sum points.  The float screen keeps
binding coalitions that fail the star condition with at least three residual
levels, then maximizes

    slack_phi(P union K) - slack_phi(K),

where K is the full minimum-residual class of the failure cover.  Every
positive candidate is recomputed with exact leximin and rational arithmetic.
"""
from __future__ import annotations

import argparse
import json
import random
import time
from fractions import Fraction as F

from classify_saved_capacity_frontier import residual_cover_float
from hunt_exact_points import game_from_points
from hunt_off_side_carrier import (
    core_matrices,
    generate_points,
    maximize_target,
    members,
)
from lemD import core_max_xS, residual_cover, star_holds, xS
from leximin import leximin_core_exact, leximin_core_float


def class_margin(game, phi, target, residuals):
    r0 = min(residuals.values())
    minimum_class = sum(
        1 << player for player, value in residuals.items() if value == r0
    )
    outside = game.N ^ target
    carrier = outside | minimum_class
    class_slack = xS(phi, minimum_class, game.n) - game.v[minimum_class]
    carrier_slack = xS(phi, carrier, game.n) - game.v[carrier]
    return carrier_slack - class_slack, minimum_class


def exactify(points, target):
    game = game_from_points(len(points[0]), points)
    phi = leximin_core_exact(game)
    holds, star_value, _point = star_holds(game, phi, target)
    binding = core_max_xS(game, target) > xS(phi, target, game.n)
    cover = None if holds else residual_cover(game, phi, target)
    if cover is None:
        return {
            "binding": binding,
            "star_holds": holds,
            "star_value": str(star_value),
        }
    margin, minimum_class = class_margin(game, phi, target, cover["r"])
    return {
        "binding": binding,
        "star_holds": holds,
        "star_value": str(star_value),
        "phi": [str(value) for value in phi],
        "residuals": {
            str(player + 1): str(value)
            for player, value in cover["r"].items()
        },
        "minimum_residual_class": members(minimum_class, game.n),
        "class_carrier_margin": str(margin),
        "class_carrier_certifies": margin <= 0,
    }


def hunt(n, trials, seed, mode, generators=None):
    rng = random.Random(seed)
    started = time.time()
    star_failures = 0
    multilevel_failures = 0
    best = None
    for trial in range(trials):
        points = generate_points(n, rng, mode, generators)
        game = game_from_points(n, points)
        phi = leximin_core_float(n, game.v, tol=1e-9)
        if phi is None:
            continue
        rows, rhs = core_matrices(game)
        coalitions = [
            target for target in range(1, game.N)
            if 2 <= target.bit_count() < n
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
            if len(levels) < 3:
                continue
            multilevel_failures += 1
            r0 = min(residuals.values())
            minimum_class = sum(
                1 << player for player, value in residuals.items()
                if abs(value - r0) <= 1e-7
            )
            outside = game.N ^ target
            carrier = outside | minimum_class
            margin = (
                xS(phi, carrier, n) - float(game.v[carrier])
                - xS(phi, minimum_class, n) + float(game.v[minimum_class])
            )
            record = {
                "trial": trial,
                "S": members(target, n),
                "S_mask": target,
                "minimum_residual_class_float": members(minimum_class, n),
                "class_carrier_margin_float": margin,
                "residual_levels_float": levels,
                "points": points,
            }
            if best is None or margin > best["class_carrier_margin_float"]:
                best = record
            if margin > 1e-7:
                record["exactification"] = exactify(points, target)
                if (
                    record["exactification"].get("class_carrier_certifies")
                    is False
                ):
                    return {
                        "status": "exact class-carrier counterexample found",
                        "n": n,
                        "mode": mode,
                        "generators": generators,
                        "seed": seed,
                        "trials_requested": trials,
                        "trials_completed": trial + 1,
                        "star_failures": star_failures,
                        "multilevel_failures": multilevel_failures,
                        "best": record,
                    }
    if best is not None:
        best["exactification"] = exactify(best["points"], best["S_mask"])
    return {
        "status": "no positive float candidate; best boundary case exactified",
        "n": n,
        "mode": mode,
        "generators": generators,
        "seed": seed,
        "trials_requested": trials,
        "trials_completed": trials,
        "star_failures": star_failures,
        "multilevel_failures": multilevel_failures,
        "elapsed_seconds": time.time() - started,
        "best": best,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--trials", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument(
        "--mode", choices=["composition", "signed", "nearby"],
        default="nearby",
    )
    parser.add_argument("--generators", type=int)
    parser.add_argument("--output")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = hunt(args.n, args.trials, args.seed, args.mode, args.generators)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(rendered)
    else:
        print(rendered, end="")
