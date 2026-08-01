"""Mine the quantitative relation between carrier escape and star opening.

For a core point phi and proper S, put P=N\S and

  gamma(S) = min_{empty != C proper subset S}
      slack_phi(P union C) - slack_phi(C),

  eta(S) = max{x(S)-phi(S): x in core, x_i >= phi_i for i in S}.

The carrier conjecture is the qualitative implication gamma>0 => eta>0.
This script asks whether a stronger ratio bound eta >= c gamma is plausible.
Float LPs screen random lower-envelope games; the smallest observed ratio is
recomputed from scratch with exact rational LPs before being reported.
"""
from __future__ import annotations

import argparse
import json
import random
import time
from fractions import Fraction as F

from hunt_exact_points import game_from_points
from hunt_off_side_carrier import (
    carrier_score,
    core_matrices,
    generate_points,
    maximize_target,
)
from lemD import core_max_xS, star_holds, xS
from leximin import leximin_core_exact, leximin_core_float


def members(mask, n):
    return [i + 1 for i in range(n) if mask >> i & 1]


def exactify(points, target):
    n = len(points[0])
    game = game_from_points(n, points)
    phi = leximin_core_exact(game)
    phi_s = xS(phi, target, n)
    maximum = core_max_xS(game, target)
    holds, star_maximum, witness = star_holds(game, phi, target)
    gamma, face, carrier = carrier_score(game, phi, target)
    eta = star_maximum - phi_s
    return {
        "points": [[str(F(value)) for value in point] for point in points],
        "S": members(target, n),
        "S_mask": target,
        "phi": [str(value) for value in phi],
        "binding": maximum > phi_s,
        "max_core_xS": str(maximum),
        "gamma": str(gamma),
        "eta": str(eta),
        "eta_over_gamma": None if gamma == 0 else str(eta / gamma),
        "minimizing_face": members(face, n),
        "carrier": members(carrier, n),
        "star_holds": holds,
        "star_maximum": str(star_maximum),
        "star_witness": None if witness is None else [str(value) for value in witness],
    }


def mine(n, trials, seed, mode, generators, min_s_size):
    rng = random.Random(seed)
    started = time.time()
    counts = {
        "games": 0,
        "binding_pairs": 0,
        "positive_gamma": 0,
        "qualitative_violations_float": 0,
        "ratio_below_one_float": 0,
    }
    best = None
    for trial in range(trials):
        points = generate_points(n, rng, mode, generators)
        game = game_from_points(n, points)
        phi = leximin_core_float(n, game.v, tol=1e-9)
        if phi is None:
            continue
        counts["games"] += 1
        rows, rhs = core_matrices(game)
        targets = [
            coalition for coalition in range(1, game.N)
            if min_s_size <= coalition.bit_count() < n
        ]
        rng.shuffle(targets)
        for target in targets:
            phi_s = xS(phi, target, n)
            maximum = maximize_target(game, target, rows, rhs)
            if maximum is None or maximum <= phi_s + 1e-7:
                continue
            counts["binding_pairs"] += 1
            gamma, face, carrier = carrier_score(game, phi, target)
            if gamma <= 1e-7:
                continue
            counts["positive_gamma"] += 1
            star_maximum = maximize_target(game, target, rows, rhs, lower=phi)
            if star_maximum is None:
                continue
            eta = max(0.0, star_maximum - phi_s)
            ratio = eta / gamma
            if eta <= 1e-7:
                counts["qualitative_violations_float"] += 1
            if ratio < 1 - 1e-7:
                counts["ratio_below_one_float"] += 1
            record = {
                "trial": trial,
                "points": points,
                "S": members(target, n),
                "S_mask": target,
                "phi_float": phi,
                "gamma_float": gamma,
                "eta_float": eta,
                "eta_over_gamma_float": ratio,
                "minimizing_face": members(face, n),
                "carrier": members(carrier, n),
            }
            if best is None or ratio < best["eta_over_gamma_float"]:
                best = record
    if best is not None:
        best["exactification"] = exactify(best["points"], best["S_mask"])
    return {
        "status": "float screen with exact extremal recomputation",
        "n": n,
        "trials": trials,
        "seed": seed,
        "mode": mode,
        "generators": generators,
        "min_s_size": min_s_size,
        "counts": counts,
        "smallest_ratio": best,
        "elapsed_seconds": time.time() - started,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--trials", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument(
        "--mode", choices=["composition", "signed", "nearby"], default="nearby"
    )
    parser.add_argument("--generators", type=int, default=3)
    parser.add_argument("--min-s-size", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(mine(
        args.n, args.trials, args.seed, args.mode, args.generators, args.min_s_size
    ), indent=2))


if __name__ == "__main__":
    main()
