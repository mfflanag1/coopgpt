"""Verify the two-parameter exact-game rich-block obstruction family.

For every h>=1 and m>=h+3, four common-total integral allocations on a
poorer block of size m and a tied richer block of size h define an exact
lower-envelope game.  The script checks the closed-form Lmin and Lmax forcing
identities, the Lmax convex combination, and the saturated slack circuit over
a requested parameter grid.  The dimension-free proof is in the manuscript;
finite grid agreement is an audit, not its logical basis.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

from leximin import leximin_core_exact
from tugame import Game


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


def generators(m: int, h: int):
    if h < 1 or m < h + 3:
        raise ValueError("the family requires h>=1 and m>=h+3")
    n = m + h
    rich = range(m, n)

    first = [0] * n
    first[3] = h * (m - 1)
    for player in rich:
        first[player] = m - 1

    second = [0] * n
    second[2] = second[3] = h * (m - 1)

    third = [0] * n
    third[0] = third[1] = third[2] = h
    third[4] = h * (m - 4)
    for player in rich:
        third[player] = m - 1

    phi = [h] * m + [m - 2] * h
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


def as_string(value):
    return str(value)


def verify_case(m: int, h: int, exact_lmin_replay: bool = False):
    n = m + h
    full = (1 << n) - 1
    rich_mask = sum(1 << player for player in range(m, n))
    points = generators(m, h)
    phi = points[-1]
    total = 2 * h * (m - 1)
    if any(sum(point) != total for point in points):
        raise RuntimeError(f"(m,h)=({m},{h}): generator totals disagree")

    values = lower_envelope(points)
    game = Game(n, values)
    if any(not game.in_core(point) for point in points):
        raise RuntimeError(f"(m,h)=({m},{h}): generator outside core")
    if any(game.v[1 << player] != 0 for player in range(n)):
        raise RuntimeError(f"(m,h)=({m},{h}): singleton normalization failed")

    rich_3 = rich_mask | (1 << 2)
    rich_4 = rich_mask | (1 << 3)
    load_bearing = {
        full ^ (1 << 0): total - h,
        full ^ (1 << 1): total - h,
        rich_3: h * (m - 1),
        rich_4: h * (m - 1),
    }
    if any(game.v[S] != worth for S, worth in load_bearing.items()):
        raise RuntimeError(f"(m,h)=({m},{h}): load-bearing worth failed")
    if game.v[rich_mask] != 0:
        raise RuntimeError(f"(m,h)=({m},{h}): richer suffix is not slack")

    # These are the exact quantities used by the two-stage Lmin proof.
    first_level = h
    excess = h * (m - h - 2)
    if sum(phi) - n * first_level != excess:
        raise RuntimeError(f"(m,h)=({m},{h}): Lmin excess identity failed")
    if game.v[rich_3] - (h + 1) * first_level != excess:
        raise RuntimeError(f"(m,h)=({m},{h}): first rich-block forcing failed")
    if game.v[rich_4] - (h + 1) * first_level != excess:
        raise RuntimeError(f"(m,h)=({m},{h}): second rich-block forcing failed")
    if sum(phi[m:]) != h * (m - 2):
        raise RuntimeError(f"(m,h)=({m},{h}): second Lmin level failed")
    replayed_lmin = None
    if exact_lmin_replay:
        replayed_lmin = tuple(leximin_core_exact(game))
        if replayed_lmin != phi:
            raise RuntimeError(f"(m,h)=({m},{h}): exact Lmin replay failed")

    high = Fraction(h * (m - 1), h + 1)
    low = Fraction(h * h * (m - 1), (h + 1) * (m - 2))
    lmax_formula = tuple(
        high if player in (2, 3) or player >= m else low
        for player in range(n)
    )
    blend_weight = Fraction(h * (m - 1), (h + 1) * (m - 2))
    if not 0 < blend_weight < 1:
        raise RuntimeError(f"(m,h)=({m},{h}): invalid convex weight")
    blended = tuple(
        blend_weight * points[3][player]
        + (1 - blend_weight) * points[1][player]
        for player in range(n)
    )
    if blended != lmax_formula or not game.in_core(lmax_formula):
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax blend failed")
    if max(lmax_formula) != high or sum(lmax_formula) != total:
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax ceiling failed")
    if (
        coalition_sum(lmax_formula, rich_3) != h * (m - 1)
        or coalition_sum(lmax_formula, rich_4) != h * (m - 1)
    ):
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax forcing face failed")

    circuit = {rich_3: 1, rich_4: 1, rich_mask: -1}
    for player in range(m):
        if player not in (2, 3):
            circuit[1 << player] = 1
    coverage = [
        sum(
            weight
            for coalition, weight in circuit.items()
            if coalition >> player & 1
        )
        for player in range(n)
    ]
    if coverage != [1] * n:
        raise RuntimeError(f"(m,h)=({m},{h}): circuit coverage failed")
    slacks = {
        coalition: coalition_sum(phi, coalition) - game.v[coalition]
        for coalition in circuit
    }
    weighted_slack = sum(
        weight * slacks[coalition]
        for coalition, weight in circuit.items()
    )
    if weighted_slack != 0 or slacks[rich_mask] != h * (m - 2):
        raise RuntimeError(f"(m,h)=({m},{h}): slack circuit failed")

    l1_gap = sum(abs(Fraction(phi[i]) - lmax_formula[i]) for i in range(n))
    expected_gap = Fraction(4 * h * (m - h - 2), h + 1)
    if l1_gap != expected_gap:
        raise RuntimeError(f"(m,h)=({m},{h}): L1 gap identity failed")

    return {
        "poorer_block_size": m,
        "richer_block_size": h,
        "player_count": n,
        "generators": [list(point) for point in points],
        "lmin_formula": list(phi),
        "exact_lmin_replayed": exact_lmin_replay,
        "exact_lmin_replay": (
            [as_string(value) for value in replayed_lmin]
            if replayed_lmin is not None
            else None
        ),
        "richer_suffix_value": "0",
        "richer_suffix_slack": str(h * (m - 2)),
        "lmax_formula": [as_string(value) for value in lmax_formula],
        "lmax_convex_combination": {
            "g4_weight": as_string(blend_weight),
            "g2_weight": as_string(1 - blend_weight),
        },
        "lmin_lmax_l1_gap": as_string(l1_gap),
        "normalized_l1_gap": as_string(l1_gap / total),
        "circuit_player_coverage": coverage,
        "circuit_weighted_slack": as_string(weighted_slack),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rich-block", type=int, default=4)
    parser.add_argument("--extra-poorer", type=int, default=4)
    parser.add_argument(
        "--exact-replay-smallest-nontrivial",
        action="store_true",
        help="independently replay Lmin for the h=2,m=5 case",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_rich_block < 1 or args.extra_poorer < 0:
        raise ValueError("parameter bounds must be nonnegative and nonempty")

    cases = [
        verify_case(
            m,
            h,
            exact_lmin_replay=(
                args.exact_replay_smallest_nontrivial and h == 2 and m == 5
            ),
        )
        for h in range(1, args.max_rich_block + 1)
        for m in range(h + 3, h + 4 + args.extra_poorer)
    ]
    payload = {
        "status": "two-parameter rich-block obstruction family verified",
        "theorem": (
            "for every h>=1 and m>=h+3, a four-generator integral exact "
            "game has a slack h-player richest suffix and distinct closed-form "
            "Lmin and Lmax allocations"
        ),
        "proof_scope": (
            "the manuscript proof is symbolic and dimension-free; this exact "
            "grid audit checks all identities over the reported parameter range"
        ),
        "max_rich_block": args.max_rich_block,
        "extra_poorer_values_per_rich_block": args.extra_poorer,
        "case_count": len(cases),
        "smallest_nontrivial_exact_lmin_replayed": (
            args.exact_replay_smallest_nontrivial
        ),
        "cases": cases,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
