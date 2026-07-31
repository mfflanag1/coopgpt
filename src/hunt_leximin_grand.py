"""Grand-coalition resource-monotonicity hunt and invariant miner.

For an exact game v, v^r differs only at N: v^r(N)=v(N)+r.  Every v^r is
exact, so any coordinate drop in the leximin-above-floors point is an exact
counterexample to grand-coalition resource monotonicity.

The search has two purposes:
  * screen dense rational grids and exactly certify every apparent drop;
  * record labeled leximin strata across r, looking for a proof invariant.

Games are generated as lower envelopes of equal-sum integer points, hence are
exact by construction.  The biased generator makes thin cores and frequent
stratum changes.  All reported counters are checked with Fraction arithmetic.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter
from fractions import Fraction as F

from hunt_exact_points import game_from_points, rand_point_sum
from leximin import leximin_core_exact, leximin_core_float
from tugame import Game


def compositions(total: int, n: int):
    """Yield nonnegative integer n-vectors with the prescribed sum."""
    if n == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, n - 1):
            yield (first,) + tail


def biased_points(n: int, total: int, count: int, rng: random.Random):
    """Nearby equal-sum points; these generate thin, highly faceted cores."""
    base = rand_point_sum(n, total, rng)
    points = [base]
    for _ in range(count - 1):
        point = list(base)
        indices = rng.sample(range(n), rng.randint(2, n))
        mass = sum(point[i] for i in indices)
        replacement = rand_point_sum(len(indices), mass, rng)
        for i, value in zip(indices, replacement):
            point[i] = value
        points.append(point)
    return points


def bumped_game(game: Game, r: F) -> Game:
    worths = list(game.v)
    worths[game.N] += r
    return Game(game.n, worths)


def gain_strata(game: Game, allocation, tol=1e-7):
    gains = [float(allocation[i] - game.v[1 << i]) for i in range(game.n)]
    levels = []
    strata = []
    for i in sorted(range(game.n), key=lambda j: (gains[j], j)):
        if not levels or abs(gains[i] - levels[-1]) > tol:
            levels.append(gains[i])
            strata.append([])
        strata[-1].append(i)
    return tuple(tuple(group) for group in strata)


def exact_drop(game: Game, r0: F, r1: F):
    x0 = leximin_core_exact(bumped_game(game, r0))
    x1 = leximin_core_exact(bumped_game(game, r1))
    if x0 is None or x1 is None:
        return None
    drops = [i for i in range(game.n) if x1[i] < x0[i]]
    if not drops:
        return None
    return {
        "n": game.n,
        "v": [str(value) for value in game.v],
        "r0": str(r0),
        "r1": str(r1),
        "phi0": [str(value) for value in x0],
        "phi1": [str(value) for value in x1],
        "drops": drops,
    }


def scan_game(game: Game, step: F, steps: int, stats: Counter):
    previous = None
    previous_r = None
    previous_strata = None
    for k in range(steps + 1):
        r = step * k
        worths = [float(value) for value in game.v]
        worths[game.N] += float(r)
        current = leximin_core_float(game.n, worths, tol=1e-9)
        if current is None:
            stats["float_fail"] += 1
            return None
        strata = gain_strata(game, current)
        stats["grid_points"] += 1
        if previous is not None:
            if strata != previous_strata:
                stats["stratum_transitions"] += 1
            deltas = [current[i] - previous[i] for i in range(game.n)]
            if min(deltas) < -1e-7:
                stats["float_drop_candidates"] += 1
                certificate = exact_drop(game, previous_r, r)
                if certificate is not None:
                    stats["exact_drops"] += 1
                    return certificate
                stats["false_positive_drops"] += 1
            elif min(deltas) >= -1e-9:
                stats["monotone_steps"] += 1
            if max(deltas) - min(deltas) > 1e-7:
                stats["nonuniform_steps"] += 1
        previous = current
        previous_r = r
        previous_strata = strata
    stats["games_clean"] += 1
    return None


def exhaustive_pair_games(n: int, max_total: int):
    """Canonical two-point exact games, deduplicated by their worth vector."""
    seen = set()
    for total in range(1, max_total + 1):
        points = list(compositions(total, n))
        for p, q in itertools.combinations_with_replacement(points, 2):
            game = game_from_points(n, [p, q])
            key = tuple(game.v)
            if key not in seen:
                seen.add(key)
                yield game


def run(args):
    rng = random.Random(args.seed)
    step = F(args.step)
    stats = Counter()

    if args.exhaustive_total:
        games = exhaustive_pair_games(args.n, args.exhaustive_total)
    else:
        def random_games():
            for _ in range(args.games):
                total = rng.randint(args.n, args.max_total)
                count = rng.randint(2, args.max_points)
                if rng.random() < args.bias:
                    points = biased_points(args.n, total, count, rng)
                else:
                    points = [rand_point_sum(args.n, total, rng) for _ in range(count)]
                yield game_from_points(args.n, points)
        games = random_games()

    for index, game in enumerate(games, start=1):
        stats["games"] += 1
        certificate = scan_game(game, step, args.steps, stats)
        if certificate is not None:
            print("EXACT GRAND-RESOURCE COUNTEREXAMPLE")
            print(json.dumps(certificate, indent=2))
            return 1
        if args.progress and index % args.progress == 0:
            print(json.dumps(dict(stats), sort_keys=True), flush=True)

    print("GRAND-RESOURCE SCREEN CLEAN")
    print(json.dumps(dict(stats), indent=2, sort_keys=True))
    return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--games", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--max-total", type=int, default=30)
    parser.add_argument("--max-points", type=int, default=4)
    parser.add_argument("--bias", type=float, default=0.7)
    parser.add_argument("--step", default="1/4")
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument("--exhaustive-total", type=int, default=0)
    parser.add_argument("--progress", type=int, default=250)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
