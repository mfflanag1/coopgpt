"""Falsification search for a dimension-free small-poorer-side conjecture.

Generate exact games as lower envelopes of common-total additive allocations,
singleton-normalize them, compute Lmin, and look for a slack richer suffix
whose poorer side has at most two players.  Float LPs screen; every hit is
recomputed with the exact-rational Lmin implementation before being reported.

No-hit output is discovery evidence only, never a proof.
"""
from __future__ import annotations

import argparse
import json
import random
from fractions import Fraction as F
from pathlib import Path

from leximin import leximin_core_exact, leximin_core_float
from scipy.optimize import linprog
from tugame import Game


def random_composition(rng, total, size):
    cuts = sorted(rng.sample(range(total + size - 1), size - 1))
    bars = [-1, *cuts, total + size - 1]
    return tuple(bars[index + 1] - bars[index] - 1 for index in range(size))


def coalition_sum(point, coalition):
    return sum(
        point[player]
        for player in range(len(point))
        if coalition >> player & 1
    )


def normalized_lower_envelope(generators):
    n = len(generators[0])
    full = (1 << n) - 1
    raw = [0] * (1 << n)
    for coalition in range(1, full):
        raw[coalition] = min(
            coalition_sum(point, coalition) for point in generators
        )
    raw[full] = sum(generators[0])
    singleton = [raw[1 << player] for player in range(n)]
    normalized = [
        raw[coalition] - coalition_sum(singleton, coalition)
        for coalition in range(1 << n)
    ]
    return normalized


def slack_small_poorer_boundaries(values, phi, tolerance=1e-7):
    n = len(phi)
    full = (1 << n) - 1
    ordered = sorted(range(n), key=lambda player: phi[player])
    hits = []
    for split in range(1, min(2, n - 1) + 1):
        if phi[ordered[split - 1]] >= phi[ordered[split]] - tolerance:
            continue
        poorer = sum(1 << player for player in ordered[:split])
        richer = full ^ poorer
        slack = coalition_sum(phi, richer) - values[richer]
        if slack > tolerance:
            hits.append((poorer, richer, slack))
    return hits


def small_poorer_boundaries(phi, tolerance=1e-7):
    n = len(phi)
    full = (1 << n) - 1
    ordered = sorted(range(n), key=lambda player: phi[player])
    for split in range(1, min(2, n - 1) + 1):
        if phi[ordered[split - 1]] < phi[ordered[split]] - tolerance:
            poorer = sum(1 << player for player in ordered[:split])
            yield poorer, full ^ poorer


def blocker_defect_float(values, phi, richer, tolerance=1e-7):
    """Boundary defect using all tight coalitions except the target itself."""
    n = len(phi)
    full = (1 << n) - 1
    tight = [
        coalition
        for coalition in range(1, full)
        if coalition != richer
        and abs(coalition_sum(phi, coalition) - values[coalition]) <= tolerance
    ]
    objective = [
        -coalition_sum(phi, coalition) for coalition in tight
    ] + [values[full]]
    A_ub, b_ub = [], []
    for player in range(n):
        A_ub.append(
            [int(coalition >> player & 1) for coalition in tight] + [-1]
        )
        b_ub.append(1 if richer >> player & 1 else 0)
    result = linprog(
        objective,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=[(0, None)] * len(objective),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"blocker-defect LP failed: {result.message}")
    return coalition_sum(phi, richer) + result.fun


def members(coalition, n):
    return [player + 1 for player in range(n) if coalition >> player & 1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    screened = 0
    exact_hits = []
    by_dimension = {5: 0, 6: 0, 7: 0}
    small_boundary_count = 0
    positive_blocker_defects = 0
    first_positive_blocker_defect = None
    for trial in range(args.trials):
        n = (5, 6, 7)[trial % 3]
        total = rng.randint(n + 3, 4 * n + 8)
        generator_count = rng.randint(2, min(7, n + 2))
        generators = tuple(
            random_composition(rng, total, n)
            for _ in range(generator_count)
        )
        values = normalized_lower_envelope(generators)
        phi_float = leximin_core_float(n, values)
        if phi_float is None:
            continue
        screened += 1
        by_dimension[n] += 1
        for poorer, richer in small_poorer_boundaries(phi_float):
            small_boundary_count += 1
            defect = blocker_defect_float(values, phi_float, richer)
            if defect > 1e-6:
                positive_blocker_defects += 1
                if first_positive_blocker_defect is None:
                    first_positive_blocker_defect = {
                        "trial": trial,
                        "n": n,
                        "generators": [list(point) for point in generators],
                        "lmin_float": phi_float,
                        "poorer": members(poorer, n),
                        "richer": members(richer, n),
                        "blocker_defect_excluding_target": defect,
                    }
        float_hits = slack_small_poorer_boundaries(values, phi_float)
        if not float_hits:
            continue

        game = Game(n, [F(value) for value in values])
        phi = tuple(leximin_core_exact(game))
        for poorer, richer, _ in slack_small_poorer_boundaries(values, phi, 0):
            slack = coalition_sum(phi, richer) - game.v[richer]
            exact_hits.append({
                "trial": trial,
                "n": n,
                "generators": [list(point) for point in generators],
                "lmin": [str(value) for value in phi],
                "poorer": members(poorer, n),
                "richer": members(richer, n),
                "richer_suffix_slack": str(slack),
            })
        if exact_hits:
            break

    payload = {
        "status": (
            "exact counterexample found"
            if exact_hits
            else "no counterexample found; falsification search only"
        ),
        "conjecture_screened": (
            "every strict Lmin boundary with at most two poorer players is tight"
        ),
        "game_family": "singleton-normalized lower envelopes of random common-total allocations",
        "seed": args.seed,
        "trials_requested": args.trials,
        "games_screened": screened,
        "games_by_dimension": by_dimension,
        "strict_boundaries_with_at_most_two_poorer_players": small_boundary_count,
        "positive_blocker_defects_excluding_target": positive_blocker_defects,
        "first_positive_blocker_defect": first_positive_blocker_defect,
        "exact_hits": exact_hits,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
