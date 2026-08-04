"""Verify the universal three-poorer external-sacrifice family.

For every poorer-side size m>=3 and richer-suffix size h>=2, a small
common-total lower envelope defines a singleton-normalized exact game whose
Lmin payoff strata are

    1 on m-1 poorer players, 2 on one poorer player, 3 on h rich players,

while the rich suffix has unit slack.  The manuscript proof is symbolic and
dimension-free.  This script audits the identities over a parameter grid and
can replay selected cases with the generic exact staged Lmin and Lmax
implementations.
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


def generators(m: int, h: int):
    if m < 3 or h < 2:
        raise ValueError("the family requires m>=3 and h>=2")

    q = m - 3
    total = m + 3 * h + 1

    # Poor players are p1,p2,p3,Q; rich players form H.  The last rich
    # player is zero in A, while every other rich player is zero in B.
    first = [2, 0, 3] + [1] * q
    first += [5] + [3] * (h - 2) + [0]

    second = [0, 2, 1] + [1] * q
    second += [4] + [3] * (h - 1)

    third = [0, 0, 0] + [1] * q
    third += [0] * (h - 1) + [3 * h + 4]

    phi = [1, 1, 2] + [1] * q + [3] * h
    points = [first, second, third, phi]

    # Zero every additional poorer singleton without changing either
    # load-bearing rich coalition: move its unit to p1.
    for player in range(3, m):
        point = list(phi)
        point[0] += 1
        point[player] = 0
        points.append(point)

    if any(sum(point) != total for point in points):
        raise RuntimeError(f"(m,h)=({m},{h}): common-total identity failed")
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
    n = m + h
    full = (1 << n) - 1
    richer = sum(1 << player for player in range(m, n))
    extra_poorer = tuple(range(3, m))
    points = generators(m, h)
    values = lower_envelope(points)
    game = Game(n, values)
    phi = tuple([1, 1, 2] + [1] * (m - 3) + [3] * h)
    total = m + 3 * h + 1

    if any(not game.in_core(point) for point in points):
        raise RuntimeError(f"(m,h)=({m},{h}): generator outside core")
    if any(game.v[1 << player] != 0 for player in range(n)):
        raise RuntimeError(f"(m,h)=({m},{h}): singleton normalization failed")
    if not game.in_core(phi):
        raise RuntimeError(f"(m,h)=({m},{h}): Lmin candidate outside core")

    # Indecomposability certificate.  In a singleton-normalized direct sum,
    # positive pair worth puts both players in the same summand.  When Q is
    # nonempty, its first player has pair worth one with every other player.
    # At m=3, positive pairs connect everyone except p2; one strict
    # higher-order interaction then attaches p2 to that component.
    if extra_poorer:
        bridge = extra_poorer[0]
        if any(
            game.v[(1 << bridge) | (1 << player)] != 1
            for player in range(n)
            if player != bridge
        ):
            raise RuntimeError(f"(m,h)=({m},{h}): pair bridge failed")
    else:
        last_rich = n - 1
        connected_pairs = (
            (0, last_rich),
            (2, last_rich),
            *((player, last_rich) for player in range(m, n - 1)),
        )
        if any(
            game.v[(1 << left) | (1 << right)] <= 0
            for left, right in connected_pairs
        ):
            raise RuntimeError(f"(m,h)=({m},{h}): endpoint pair graph failed")
        attachment = (1 << 0) | (1 << 2) | (1 << last_rich)
        if game.v[attachment] != 4 or game.v[attachment | (1 << 1)] != 5:
            raise RuntimeError(f"(m,h)=({m},{h}): endpoint attachment failed")

    rich_with_p3 = richer | (1 << 2)
    rich_with_p1 = richer | (1 << 0)
    if game.v[rich_with_p3] != 3 * h + 2:
        raise RuntimeError(f"(m,h)=({m},{h}): first pinning face failed")
    if game.v[rich_with_p1] != 3 * h + 1:
        raise RuntimeError(f"(m,h)=({m},{h}): second pinning face failed")
    if any(game.v[full ^ (1 << player)] != total - 1
           for player in extra_poorer):
        raise RuntimeError(f"(m,h)=({m},{h}): extra-poor pinning face failed")

    richer_value = game.v[richer]
    richer_payoff = coalition_sum(phi, richer)
    if richer_value != 3 * h - 1 or richer_payoff != 3 * h:
        raise RuntimeError(f"(m,h)=({m},{h}): rich-suffix slack failed")

    replayed_lmin = None
    replayed_lmax = None
    epsilon = Fraction(1, h + 1)
    ceiling = 3 - epsilon
    lmax_formula = tuple(
        [2 - epsilon, epsilon, ceiling]
        + [Fraction(1)] * (m - 3)
        + [ceiling] * h
    )
    if not game.in_core(lmax_formula):
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax formula outside core")
    if max(lmax_formula) != ceiling:
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax ceiling failed")
    if coalition_sum(lmax_formula, rich_with_p3) != 3 * h + 2:
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax top face failed")
    if coalition_sum(lmax_formula, rich_with_p1) != 3 * h + 1:
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax second face failed")
    if any(
        game.v[richer | (1 << 0) | (1 << player)] != 3 * h + 2
        for player in extra_poorer
    ):
        raise RuntimeError(f"(m,h)=({m},{h}): Lmax extra-poor face failed")

    if exact_replay:
        replayed_lmin = tuple(leximin_core_exact(game))
        replayed_lmax = tuple(leximax_core_exact(game))
        if replayed_lmin != phi:
            raise RuntimeError(
                f"(m,h)=({m},{h}): exact Lmin replay gave {replayed_lmin}"
            )
        if replayed_lmax != lmax_formula:
            raise RuntimeError(
                f"(m,h)=({m},{h}): exact Lmax replay gave {replayed_lmax}"
            )

    return {
        "poorer_side_size": m,
        "richer_suffix_size": h,
        "player_count": n,
        "generator_count": len(points),
        "indecomposable_certificate_checked": True,
        "generators": [list(point) for point in points],
        "lmin_formula": list(phi),
        "lmax_formula": [str(value) for value in lmax_formula],
        "lmin_lmax_l1_gap": str(sum(
            abs(Fraction(phi[player]) - lmax_formula[player])
            for player in range(n)
        )),
        "lmin_stratum_sizes": [m - 1, 1, h],
        "richer_suffix_value": str(richer_value),
        "richer_suffix_payoff": str(richer_payoff),
        "richer_suffix_slack": str(richer_payoff - richer_value),
        "exact_lmin_replayed": exact_replay,
        "exact_lmax_replayed": exact_replay,
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
    parser.add_argument("--max-poorer-side", type=int, default=6)
    parser.add_argument("--max-richer-suffix", type=int, default=6)
    parser.add_argument(
        "--exact-replay-through-players",
        type=int,
        default=0,
        help="replay generic exact staged Lmin and Lmax for every case up to n",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_poorer_side < 3 or args.max_richer_suffix < 2:
        raise ValueError("parameter maxima must satisfy m>=3 and h>=2")

    cases = [
        verify_case(
            m,
            h,
            exact_replay=(m + h <= args.exact_replay_through_players),
        )
        for m in range(3, args.max_poorer_side + 1)
        for h in range(2, args.max_richer_suffix + 1)
    ]
    payload = {
        "status": "universal three-poorer boundary family verified",
        "theorem": (
            "for every m>=3 and h>=2, a singleton-normalized integral exact "
            "game has a slack h-player Lmin suffix above m poorer players"
        ),
        "proof_scope": (
            "the manuscript proof is symbolic and dimension-free; this grid "
            "audits the identities, with exact staged Lmin/Lmax replay only "
            "where explicitly reported"
        ),
        "max_poorer_side": args.max_poorer_side,
        "max_richer_suffix": args.max_richer_suffix,
        "exact_replay_through_players": args.exact_replay_through_players,
        "case_count": len(cases),
        "exact_lmin_lmax_replayed_case_count": sum(
            case["exact_lmin_replayed"] and case["exact_lmax_replayed"]
            for case in cases
        ),
        "cases": cases,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
