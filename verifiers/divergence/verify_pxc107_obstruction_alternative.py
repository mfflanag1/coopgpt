#!/usr/bin/env python3
"""Exact algebraic calibrations for the PXC107 obstruction alternative."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def csum(direction, coalition):
    return sum((direction[i] for i in range(len(direction))
                if coalition >> i & 1), F(0))


def matrix_rank(rows):
    rows = [list(map(F, row)) for row in rows]
    if not rows:
        return 0
    rank = 0
    width = len(rows[0])
    for col in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [q / scale for q in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                scale = rows[i][col]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def row(mask, n):
    return [F((mask >> i) & 1) for i in range(n)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # PXC98: one direction is tangent to both covers and vanishes on their
    # union.  Its only negative z-tight row is the forced-zero blocker rj=17.
    pxc98_d = (F(0), F(0), F(0), F(0), F(-1, 2), F(1, 2))
    pxc98_union = (3, 7, 11, 51)
    pxc98_menu = (3, 7, 11, 17, 51)
    if any(csum(pxc98_d, s) for s in pxc98_union):
        raise AssertionError("PXC98 union direction changed")
    pxc98_blockers = tuple(s for s in pxc98_menu if csum(pxc98_d, s) < 0)
    if pxc98_blockers != (17,):
        raise AssertionError(pxc98_blockers)

    # PXC104: normalize the a-stage decrease to d_a=-1.  The positive covers
    # have unique rays after efficiency.  Each is cut by a row in another
    # cover, yielding the directed two-cycle.
    pair = (F(0), F(0), F(-1), F(0), F(1, 2), F(1, 2))
    left = (F(0), F(0), F(-1), F(0), F(0), F(1))
    right = (F(0), F(0), F(-1), F(0), F(1), F(0))
    pxc104_union = (3, 11, 19, 23, 35, 39)
    if not (csum(left, 23) < 0 and csum(left, 39) == 0
            and csum(right, 39) < 0 and csum(right, 23) == 0
            and csum(pair, 23) < 0 and csum(pair, 39) < 0):
        raise AssertionError("PXC104 cross-cycle arithmetic changed")
    # There is no pair-cover local forced-zero ray.  Nonnegativity on the
    # union would require d_j,d_k>=1 and d_b>=0, contradicting efficiency
    # -1+d_b+d_j+d_k=0.  The two positive-cover rays are already unique and
    # have the displayed negative cross row.
    pair_local_farkas = {
        "normalization": "d_a=-1",
        "union_nonnegativity_implies": ["d_b>=0", "d_j>=1", "d_k>=1"],
        "efficiency": "-1+d_b+d_j+d_k=0",
        "contradiction": "left side >=1",
    }

    # PXC90 faithful calibration: the five non-top incidence columns of its
    # sole positive cover have full rank, so the later tangent kernel is zero.
    pxc90_rows = (23, 27, 39, 75, 114)
    pxc90_outsiders = tuple(range(2, 7))
    pxc90_matrix = [
        [F((mask >> player) & 1) for mask in pxc90_rows]
        for player in pxc90_outsiders
    ]
    pxc90_rank = matrix_rank(pxc90_matrix)
    if pxc90_rank != 5:
        raise AssertionError(("PXC90 rank", pxc90_rank))

    payload = {
        "claim": "PXC107 exact forced-zero/cross-cycle dichotomy",
        "dichotomy": [
            "common forced-zero direction (PXC103)",
            "directed cross-cover blocker cycle",
        ],
        "collapse_lemma": (
            "if a cover descent is nonnegative on the entire cover union, "
            "every positive cover identity forces it to vanish on that "
            "cover, so the descent is common to all covers"
        ),
        "pxc98": {
            "class": "common forced-zero",
            "direction": list(map(str, pxc98_d)),
            "cover_union": list(pxc98_union),
            "blockers_outside_union": list(pxc98_blockers),
        },
        "pxc104": {
            "class": "directed cross-cover cycle",
            "directions": [list(map(str, q)) for q in (pair, left, right)],
            "cover_union": list(pxc104_union),
            "edges": ["left cover --rhaj--> right cover",
                      "right cover --rhak--> left cover"],
            "pair_local_forced_zero_infeasibility": pair_local_farkas,
        },
        "pxc90": {
            "class": "faithful calibration; failure dichotomy not entered",
            "outsider_incidence_rank": pxc90_rank,
            "outsider_dimension": 5,
        },
        "third_cover_local_branch": "impossible by the collapse lemma",
        "scope": (
            "human finite-digraph alternative plus exact rational arithmetic "
            "on the negative, cycle, and faithful calibrations"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
