#!/usr/bin/env python3
r"""Exact parametric audit of the class-A/class-B row handover (PXC86).

The family is a one-parameter deformation of the pinned class-B control.
All arithmetic is rational and solver-free.  The verifier checks core
membership on the full continuum by partitioning at every affine-envelope
breakpoint.  The selector optimality argument itself is the short inequality
proof recorded in the paper and summarized in the JSON artifact.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


Affine = tuple[F, F]  # intercept + slope * t
ZERO: Affine = (F(0), F(0))
BREAK = F(1, 7)


GENERATORS: tuple[tuple[Affine, ...], ...] = (
    ((0, 0), (10, 0), (5, 0), (5, 0), (0, 0), (0, 0), (0, 0)),
    ((12, 0), (0, 0), (0, 0), (0, 0), (4, 0), (2, 0), (2, 0)),
    ((0, 0), (10, 0), (4, 0), (6, 0), (0, 0), (0, 0), (0, 0)),
    ((0, 0), (9, -1), (6, 0), (5, 1), (0, 0), (0, 0), (0, 0)),
    ((0, 0), (9, 0), (5, 0), (6, 0), (0, 0), (0, 0), (0, 0)),
    ((13, 0), (0, 0), (0, 0), (0, 0), (4, 0), (1, 0), (2, 0)),
)

X: tuple[Affine, ...] = (
    (6, 0), (4, 0), (2, 0), (2, 0), (2, 0), (2, 0), (2, 0)
)
Z_PAIR: tuple[Affine, ...] = (
    (F(9, 2), F(-1, 2)), (F(9, 2), F(-1, 2)),
    (4, 2), (4, 2), (1, -1), (1, -1), (1, -1),
)
Z_HEAVY: tuple[Affine, ...] = (
    (F(31, 7), 0), (F(31, 7), 0),
    (F(30, 7), 0), (F(30, 7), 0),
    (F(6, 7), 0), (F(6, 7), 0), (F(6, 7), 0),
)


def A(value: tuple[int | F, int | F]) -> Affine:
    return F(value[0]), F(value[1])


def add(left: Affine, right: Affine) -> Affine:
    return left[0] + right[0], left[1] + right[1]


def sub(left: Affine, right: Affine) -> Affine:
    return left[0] - right[0], left[1] - right[1]


def neg(line: Affine) -> Affine:
    return -line[0], -line[1]


def value(line: Affine, t: F) -> F:
    return line[0] + line[1] * t


def coalition_sum(point: tuple[Affine, ...], coalition: int) -> Affine:
    answer = ZERO
    for player, coordinate in enumerate(point):
        if coalition >> player & 1:
            answer = add(answer, A(coordinate))
    return answer


def generator_lines(coalition: int) -> tuple[Affine, ...]:
    return tuple(coalition_sum(generator, coalition) for generator in GENERATORS)


def breakpoints(lines: tuple[Affine, ...], lo: F, hi: F) -> list[F]:
    points = {lo, hi}
    for left in lines:
        for right in lines:
            slope = left[1] - right[1]
            if slope:
                crossing = (right[0] - left[0]) / slope
                if lo < crossing < hi:
                    points.add(crossing)
    return sorted(points)


def check_core(point: tuple[Affine, ...], lo: F, hi: F) -> int:
    """Check point(S) >= min_q q(S) for every S throughout [lo,hi]."""
    checked = 0
    for coalition in range(1 << 7):
        candidate = coalition_sum(point, coalition)
        lines = generator_lines(coalition)
        points = breakpoints(lines, lo, hi)
        for t in points:
            if value(candidate, t) < min(value(line, t) for line in lines):
                raise AssertionError(("core endpoint", coalition, t))
            checked += 1
        for left, right in zip(points, points[1:]):
            midpoint = (left + right) / 2
            envelope = min(lines, key=lambda line: value(line, midpoint))
            difference = sub(candidate, envelope)
            if value(difference, left) < 0 or value(difference, right) < 0:
                raise AssertionError(("core interval", coalition, left, right))
            checked += 1
    return checked


def check_envelope(line: Affine, coalition: int, lo: F, hi: F) -> None:
    lines = generator_lines(coalition)
    points = breakpoints(lines, lo, hi)
    for left, right in zip(points, points[1:]):
        midpoint = (left + right) / 2
        if value(line, midpoint) != min(value(q, midpoint) for q in lines):
            raise AssertionError(("envelope interval", coalition, midpoint))
        if value(line, left) != min(value(q, left) for q in lines):
            raise AssertionError(("envelope endpoint", coalition, left))
    if value(line, hi) != min(value(q, hi) for q in lines):
        raise AssertionError(("envelope endpoint", coalition, hi))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    generators = tuple(tuple(A(q) for q in generator) for generator in GENERATORS)
    x = tuple(A(q) for q in X)
    z_pair = tuple(A(q) for q in Z_PAIR)
    z_heavy = tuple(A(q) for q in Z_HEAVY)

    if any(coalition_sum(generator, 127) != (20, 0) for generator in generators):
        raise AssertionError("generator totals changed")
    if any(not any(generator[i] == ZERO for generator in generators)
           for i in range(7)):
        raise AssertionError("singleton normalization changed")

    checks = {
        "lmin_core": check_core(x, F(0), F(1)),
        "pair_branch_core": check_core(z_pair, F(0), BREAK),
        "heavy_branch_core": check_core(z_heavy, BREAK, F(1)),
    }

    pair = (1 << 0) | (1 << 1)
    heavy = sum(1 << i for i in (1, 4, 5, 6))
    double_rows = tuple(
        pair | (1 << a) | (1 << j) for a in (2, 3) for j in (4, 5, 6)
    )
    check_envelope((9, -1), pair, F(0), F(1))
    check_envelope((7, 0), heavy, F(0), F(1))
    for coalition in double_rows:
        check_envelope((14, 0), coalition, F(0), F(1))

    # Three t-independent lower rows give the full human Lmin proof after
    # complementation: two pin players 2..6 at level 2, the third pins player
    # 1 at level 4, and efficiency pins player 0 at level 6.
    lmin_rows = {
        "012": ((1 << 0) | (1 << 1) | (1 << 2), (12, 0)),
        "013": ((1 << 0) | (1 << 1) | (1 << 3), (12, 0)),
        "023": ((1 << 0) | (1 << 2) | (1 << 3), (10, 0)),
    }
    for coalition, line in lmin_rows.values():
        check_envelope(line, coalition, F(0), F(1))

    # Formula checks at both sides of the active-set breakpoint.
    pair_gap_left = sub(coalition_sum(z_pair, pair), (9, -1))
    heavy_gap_left = sub(coalition_sum(z_pair, heavy), (7, 0))
    pair_gap_right = sub(coalition_sum(z_heavy, pair), (9, -1))
    heavy_gap_right = sub(coalition_sum(z_heavy, heavy), (7, 0))
    if pair_gap_left != ZERO or heavy_gap_left != (F(1, 2), F(-7, 2)):
        raise AssertionError("pair branch gap formula changed")
    if pair_gap_right != (F(-1, 7), F(1)) or heavy_gap_right != ZERO:
        raise AssertionError("heavy branch gap formula changed")

    def packet_margin(point: tuple[Affine, ...]) -> Affine:
        root_loss = sub(x[0], point[0])
        heavy_gain = sub(point[1], x[1])
        sub_gain = sub(point[2], x[2])
        # The two sub-top gains are the equal maximum gains on both branches;
        # decoration and the n=7,g=3 cardinality reserve are zero.
        penalty = sub(add(heavy_gain, sub_gain), root_loss)
        return neg(penalty)

    if packet_margin(z_pair) != (-1, -1):
        raise AssertionError("pair-branch packet margin changed")
    if packet_margin(z_heavy) != (F(-8, 7), 0):
        raise AssertionError("heavy-branch packet margin changed")
    if sub(coalition_sum(x, pair), coalition_sum(z_pair, pair)) != (1, 1):
        raise AssertionError("PXC84 surplus formula changed")

    payload = {
        "claim": "exact class-B/class-A active-row handover on a continuous exact-game family",
        "parameter": "0 <= t <= 1",
        "breakpoint": "1/7",
        "lmin": ["6", "4", "2", "2", "2", "2", "2"],
        "lmax": {
            "0<=t<=1/7": ["(9-t)/2", "(9-t)/2", "4+2t", "4+2t", "1-t", "1-t", "1-t"],
            "1/7<=t<=1": ["31/7", "31/7", "30/7", "30/7", "6/7", "6/7", "6/7"],
        },
        "row_gaps": {
            "top_pair": "max(0,t-1/7)",
            "heavy_block": "max(0,(1-7t)/2)",
            "product_zero": True,
        },
        "packet_margin": {
            "0<=t<=1/7": "-(1+t)",
            "1/7<=t<=1": "-8/7",
            "strictly_negative": True,
        },
        "closure_handover": {
            "0<=t<=1/7": "PXC84 top-pair singleton cover",
            "1/7<=t<=1": "PXC78 double-co-star plus heavy-block cover",
            "both_at_t=1/7": True,
        },
        "human_optimality_certificate": {
            "lmin": "complements of tight rows 012 and 013 pin players 2..6 at 2; complement of 023 pins player 1 at 4; efficiency pins player 0 at 6",
            "pair_branch": "v(01)=9-t forces max y >= (9-t)/2; with the top pair pinned, summing the six inequalities y(01aj)>=14 forces the two sub-top players to 4+2t, then efficiency equalizes the outsiders at 1-t",
            "heavy_branch": "v(1,4,5,6)=7 and the six inequalities y(01aj)>=14 imply 44<=4R+A<=13+7 max(y), hence max(y)>=31/7; equality pins R, A and O successively",
        },
        "affine_core_checks": checks,
        "scope": "continuous seven-player family theorem; not the universal class-B closure conjecture",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
