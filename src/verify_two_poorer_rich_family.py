"""Verify a dimension-free internal-sacrifice obstruction family.

For every poorer-block size m>=2 and richer-block size h>=4, an integral lower
envelope defines a singleton-normalized exact game with Lmin equal to D on the
poorer block and 2D on the richer block, a slack richer suffix, and Lmax=Lmin.
Here D=(h-2)(h-3).  The manuscript gives the symbolic proof; this script audits
the formulas over a requested grid and can replay the smallest case with the
generic exact staged Lmin/Lmax implementations.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from leximin import leximax_core_exact, leximin_core_exact
from tugame import Game


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


def generators(m: int, h: int):
    if m < 2 or h < 4:
        raise ValueError("the family requires m>=2 and h>=4")
    r = h - 2
    d = r * (r - 1)
    n = m + h
    extra_poorer = range(2, m)
    rich_3, rich_4 = m, m + 1
    remainder = range(m + 2, n)
    points = []

    # The only row with player 1 equal to zero.
    first = [0, d] + [d] * (m - 2) + [3 * d, 3 * d]
    first += [(2 * r - 1) * (r - 1)] * r
    points.append(first)

    # The suffix-slack row; it also zeros player 2 and the two distinguished
    # richer players.
    slack_row = [4 * d, 0] + [d] * (m - 2) + [0, 0]
    slack_row += [2 * (r * r - 1)] * r
    points.append(slack_row)

    # One row zeros each remaining richer player.
    other_value = r * (2 * r - 1)
    for zero_player in remainder:
        point = [d, 0] + [d] * (m - 2) + [3 * d, 3 * d]
        point += [other_value] * r
        point[zero_player] = 0
        points.append(point)

    phi = [d] * m + [2 * d] * h
    points.append(phi)

    # Zero each additional poorer singleton without changing any
    # load-bearing coalition: move its D units to player 1.
    for zero_player in extra_poorer:
        point = list(phi)
        point[0] += d
        point[zero_player] = 0
        points.append(point)
    return tuple(tuple(point) for point in points)


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


def verify_case(m: int, h: int, exact_replay: bool):
    r = h - 2
    d = r * (r - 1)
    n = m + h
    full = (1 << n) - 1
    richer = sum(1 << player for player in range(m, n))
    rich_3, rich_4 = m, m + 1
    remainder = tuple(range(m + 2, n))
    points = generators(m, h)
    phi = tuple([d] * m + [2 * d] * h)
    total = d * (m + 2 * h)
    if any(sum(point) != total for point in points):
        raise RuntimeError(f"(m,h)=({m},{h}): common-total identity failed")

    game = Game(n, lower_envelope(points))
    if any(not game.in_core(point) for point in points):
        raise RuntimeError(f"(m,h)=({m},{h}): generator outside the core")
    if any(game.v[1 << player] != 0 for player in range(n)):
        raise RuntimeError(f"(m,h)=({m},{h}): singleton normalization failed")

    richer_without_4 = richer ^ (1 << rich_4)
    richer_without_3 = richer ^ (1 << rich_3)
    load_bearing = {
        full ^ (1 << 1): total - d,
        richer_without_4: 2 * d * (h - 1),
        richer_without_3: 2 * d * (h - 1),
    }
    for player in remainder:
        coalition = (
            (1 << 0) | (1 << rich_3) | (1 << rich_4)
            | sum(1 << other for other in remainder if other != player)
        )
        load_bearing[coalition] = d * (2 * h - 1)
    if any(game.v[S] != worth for S, worth in load_bearing.items()):
        raise RuntimeError(f"(m,h)=({m},{h}): a load-bearing worth failed")

    richer_value = game.v[richer]
    richer_payoff = coalition_sum(phi, richer)
    if richer_value != 2 * d * (h - 1):
        raise RuntimeError(f"(m,h)=({m},{h}): wrong richer-suffix value")
    if richer_payoff - richer_value != 2 * d:
        raise RuntimeError(f"(m,h)=({m},{h}): wrong richer-suffix slack")

    # Exact identities used in the two-stage Lmin proof.
    total_excess = total - n * d
    if total_excess != h * d:
        raise RuntimeError(f"(m,h)=({m},{h}): first-level excess failed")
    if any(
        worth - d * coalition.bit_count() != (h - 1) * d
        for coalition, worth in load_bearing.items()
        if coalition != full ^ (1 << 1)
    ):
        raise RuntimeError(f"(m,h)=({m},{h}): Lmin forcing excess failed")

    replayed_lmin = None
    replayed_lmax = None
    if exact_replay:
        replayed_lmin = tuple(leximin_core_exact(game))
        replayed_lmax = tuple(leximax_core_exact(game))
        if replayed_lmin != phi or replayed_lmax != phi:
            raise RuntimeError(f"(m,h)=({m},{h}): generic staged replay failed")

    return {
        "poorer_block_size": m,
        "richer_block_size": h,
        "player_count": n,
        "integral_scale_D": d,
        "generator_count": len(points),
        "generators": [list(point) for point in points],
        "lmin_formula": list(phi),
        "lmax_formula": list(phi),
        "lmin_equals_lmax": True,
        "richer_suffix_value": str(richer_value),
        "richer_suffix_payoff": str(richer_payoff),
        "richer_suffix_slack": str(richer_payoff - richer_value),
        "exact_staged_replayed": exact_replay,
        "exact_lmin_replay": (
            [str(value) for value in replayed_lmin]
            if replayed_lmin is not None else None
        ),
        "exact_lmax_replay": (
            [str(value) for value in replayed_lmax]
            if replayed_lmax is not None else None
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-poorer-block", type=int, default=5)
    parser.add_argument("--max-rich-block", type=int, default=10)
    parser.add_argument("--exact-replay-m2-h4", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_poorer_block < 2 or args.max_rich_block < 4:
        raise ValueError("parameter maxima must satisfy m>=2 and h>=4")

    cases = [
        verify_case(
            m,
            h,
            exact_replay=(
                args.exact_replay_m2_h4 and m == 2 and h == 4
            ),
        )
        for m in range(2, args.max_poorer_block + 1)
        for h in range(4, args.max_rich_block + 1)
    ]
    payload = {
        "status": "dimension-free internal-sacrifice family verified",
        "theorem": (
            "for every m>=2 and h>=4, an integral singleton-normalized exact "
            "game has a slack h-player richest suffix above m poorer players "
            "while Lmin and Lmax coincide"
        ),
        "proof_scope": (
            "the manuscript argument is symbolic; the grid is an identity "
            "audit, with optional generic exact staged replay at (m,h)=(2,4)"
        ),
        "max_poorer_block": args.max_poorer_block,
        "max_rich_block": args.max_rich_block,
        "m2_h4_exact_staged_replayed": args.exact_replay_m2_h4,
        "case_count": len(cases),
        "cases": cases,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
