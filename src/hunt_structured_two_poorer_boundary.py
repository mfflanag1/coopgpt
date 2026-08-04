"""Targeted falsification of the two-poorer-player tight-suffix conjecture.

The random generator uses a projection pattern that can make a two-coordinate
leximin point fail to maximize their sum: (a,0), (a,b), and (0,z) with
z>a+b.  The remaining three coordinates are randomized at a common total,
with one zero rich coordinate in each generator to preserve singleton
normalization.  Lower envelopes of these generators are exact games.

Float hits are accepted only after exact-rational Lmin recomputation.
"""
from __future__ import annotations

import argparse
import json
import random
from fractions import Fraction as F
from pathlib import Path

from hunt_small_poorer_boundary import (
    coalition_sum,
    members,
    normalized_lower_envelope,
)
from leximin import leximin_core_exact, leximin_core_float
from tugame import Game


def split_two(rng, total):
    first = rng.randint(0, total)
    return first, total - first


def make_generators(rng):
    a = rng.randint(1, 5)
    b = rng.randint(a + 1, a + 6)
    z = rng.randint(a + b + 1, a + b + 8)
    total = rng.randint(z + 8, z + 30)
    poor = ((a, 0), (a, b), (0, z))
    generators = []
    for index, prefix in enumerate(poor):
        remainder = total - sum(prefix)
        left, right = split_two(rng, remainder)
        rich = [None, None, None]
        rich[index] = 0
        other = [j for j in range(3) if j != index]
        rich[other[0]], rich[other[1]] = left, right
        generators.append((*prefix, *rich))
    return tuple(generators)


def candidate(values, phi, tolerance=1e-7):
    richer = 0b11100
    if not (
        max(phi[0], phi[1]) < min(phi[2:]) - tolerance
    ):
        return None
    slack = coalition_sum(phi, richer) - values[richer]
    return slack if slack > tolerance else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    exact_hit = None
    strict_two_poorer = 0
    for trial in range(args.trials):
        generators = make_generators(rng)
        values = normalized_lower_envelope(generators)
        phi_float = leximin_core_float(5, values)
        if phi_float is None:
            continue
        if max(phi_float[:2]) < min(phi_float[2:]) - 1e-7:
            strict_two_poorer += 1
        if candidate(values, phi_float) is None:
            continue
        game = Game(5, [F(value) for value in values])
        phi = tuple(leximin_core_exact(game))
        slack = candidate(values, phi, 0)
        if slack is None:
            continue
        exact_hit = {
            "trial": trial,
            "generators": [list(point) for point in generators],
            "lmin": [str(value) for value in phi],
            "poorer": members(0b00011, 5),
            "richer": members(0b11100, 5),
            "richer_suffix_value": str(game.v[0b11100]),
            "richer_suffix_payoff": str(coalition_sum(phi, 0b11100)),
            "richer_suffix_slack": str(slack),
        }
        break

    payload = {
        "status": (
            "exact counterexample found"
            if exact_hit
            else "no counterexample found; falsification search only"
        ),
        "seed": args.seed,
        "trials_requested": args.trials,
        "strict_two_poorer_cases": strict_two_poorer,
        "exact_hit": exact_hit,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
