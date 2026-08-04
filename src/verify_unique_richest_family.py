"""Verify the dimension-free unique-richest exact-game obstruction family.

For every n=m+1>=5, four common-total integer allocations define an exact
lower-envelope game with distinct closed-form Lmin and Lmax allocations and a
slack richest singleton.  The script checks the parametric identities through
a requested dimension and independently recomputes exact Lmin and Lmax in the
smaller requested dimensions.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

from leximin import leximax_core_exact, leximin_core_exact
from tugame import Game


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


def generators(m):
    n = m + 1
    richest = m
    first = [0] * n
    first[3] = m - 1
    first[richest] = m - 1

    second = [0] * n
    second[2] = m - 1
    second[3] = m - 1

    third = [0] * n
    third[0] = third[1] = third[2] = 1
    if m >= 5:
        third[4] = m - 4
    third[richest] = m - 1

    phi = [1] * m + [m - 2]
    return tuple(tuple(point) for point in (first, second, third, phi))


def coalition_sum(vector, coalition):
    return sum(
        vector[player]
        for player in range(len(vector))
        if coalition >> player & 1
    )


def lower_envelope(points):
    n = len(points[0])
    full = (1 << n) - 1
    values = [0] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(
            coalition_sum(point, coalition) for point in points
        )
    values[full] = sum(points[0])
    return values


def verify_case(m, exact_lmin_replay, exact_lmax_replay):
    n = m + 1
    full = (1 << n) - 1
    richest_player = m
    richest = 1 << richest_player
    points = generators(m)
    phi = points[-1]
    total = 2 * m - 2
    if any(sum(point) != total for point in points):
        raise RuntimeError(f"n={n}: generator totals disagree")

    values = lower_envelope(points)
    game = Game(n, values)
    if any(not game.in_core(point) for point in points):
        raise RuntimeError(f"n={n}: a generator is not in the core")
    if any(game.v[1 << player] != 0 for player in range(n)):
        raise RuntimeError(f"n={n}: singleton normalization failed")

    load_bearing = {
        full ^ (1 << 0): total - 1,
        full ^ (1 << 1): total - 1,
        (1 << 2) | richest: m - 1,
        (1 << 3) | richest: m - 1,
    }
    if any(game.v[coalition] != worth for coalition, worth in load_bearing.items()):
        raise RuntimeError(f"n={n}: a load-bearing worth failed")
    if game.v[richest] != 0 or phi[richest_player] != m - 2:
        raise RuntimeError(f"n={n}: richest-singleton slack failed")

    low = Fraction(m - 1, 2 * (m - 2))
    high = Fraction(m - 1, 2)
    lmax_formula = tuple(
        high if player in (2, 3, richest_player) else low
        for player in range(n)
    )
    blend_weight = low
    blended = tuple(
        blend_weight * points[3][player]
        + (1 - blend_weight) * points[1][player]
        for player in range(n)
    )
    if blended != lmax_formula or not game.in_core(lmax_formula):
        raise RuntimeError(f"n={n}: Lmax convex-combination formula failed")
    if max(lmax_formula) != high or sum(lmax_formula) != total:
        raise RuntimeError(f"n={n}: Lmax ceiling or efficiency failed")
    if (
        lmax_formula[2] + lmax_formula[richest_player] != m - 1
        or lmax_formula[3] + lmax_formula[richest_player] != m - 1
    ):
        raise RuntimeError(f"n={n}: Lmax forcing pairs failed")

    replayed_lmin = None
    if exact_lmin_replay:
        replayed_lmin = tuple(leximin_core_exact(game))
        if replayed_lmin != phi:
            raise RuntimeError(f"n={n}: exact Lmin replay disagrees")

    replayed_lmax = None
    if exact_lmax_replay:
        replayed_lmax = tuple(leximax_core_exact(game))
        if replayed_lmax != lmax_formula:
            raise RuntimeError(f"n={n}: exact Lmax replay disagrees")

    protector_3 = (1 << 2) | richest
    protector_4 = (1 << 3) | richest
    weights = {protector_3: 1, protector_4: 1, richest: -1}
    for player in range(m):
        if player not in (2, 3):
            weights[1 << player] = 1
    coverage = [
        sum(
            weight
            for coalition, weight in weights.items()
            if coalition >> player & 1
        )
        for player in range(n)
    ]
    if coverage != [1] * n:
        raise RuntimeError(f"n={n}: exact-balanced coverage failed")
    slacks = {
        coalition: coalition_sum(phi, coalition) - game.v[coalition]
        for coalition in weights
    }
    weighted_slack = sum(
        weight * slacks[coalition]
        for coalition, weight in weights.items()
    )
    if weighted_slack != 0:
        raise RuntimeError(f"n={n}: circuit slack does not balance")
    if slacks[richest] != m - 2:
        raise RuntimeError(f"n={n}: wrong negative slack")

    return {
        "player_count": n,
        "poorer_player_count": m,
        "generators": [list(point) for point in points],
        "lmin_formula": list(phi),
        "exact_lmin_replayed": exact_lmin_replay,
        "exact_lmin_replay": (
            [str(value) for value in replayed_lmin]
            if replayed_lmin is not None
            else None
        ),
        "lmax_formula": [str(value) for value in lmax_formula],
        "lmax_convex_combination": {
            "g4_weight": str(blend_weight),
            "g2_weight": str(1 - blend_weight),
        },
        "exact_lmax_replayed": exact_lmax_replay,
        "exact_lmax_replay": (
            [str(value) for value in replayed_lmax]
            if replayed_lmax is not None
            else None
        ),
        "lmin_lmax_distinct": phi != lmax_formula,
        "richest_singleton_slack": str(slacks[richest]),
        "positive_singleton_budget": str(m - 2),
        "weighted_slack_total": str(weighted_slack),
        "player_coverage": coverage,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-players", type=int, default=12)
    parser.add_argument("--exact-lmin-through", type=int, default=7)
    parser.add_argument("--exact-lmax-through", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_players < 5:
        raise ValueError("--max-players must be at least five")

    cases = [
        verify_case(
            n - 1,
            n <= args.exact_lmin_through,
            n <= args.exact_lmax_through,
        )
        for n in range(5, args.max_players + 1)
    ]
    payload = {
        "status": "dimension-free unique-richest obstruction family verified",
        "theorem": (
            "for every n=m+1>=5, a four-generator singleton-normalized exact "
            "game has distinct closed-form Lmin and Lmax allocations and "
            "richest-singleton slack m-2"
        ),
        "proof_type": (
            "parametric generator, incidence, and Lmax convex-combination "
            "identities in every reported dimension; independent exact staged "
            "Lmin and Lmax replays through the stated bounds"
        ),
        "max_players_checked": args.max_players,
        "exact_lmin_replayed_through": args.exact_lmin_through,
        "exact_lmax_replayed_through": args.exact_lmax_through,
        "cases": cases,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
