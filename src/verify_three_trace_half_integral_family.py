"""Exact audit of the three-trace half-integral obstruction family.

For two poorer players a,b and a richer block H={c} disjoint-union A
disjoint-union B, with |A|,|B| >= 2, consider the compact polytope

    x >= 0,  x(N)=2+2|H|,
    x(c union A) >= 2(|A|+1),
    x(c union B) >= 2(|B|+1),
    x({b} union A union B) >= 2|H|-1.

The lower envelope of its vertices is an exact game whose Lmin and Lmax are
(1,1,2,...,2), while H has slack one.  At that point the only proper tight
coalitions are the three displayed ones, and their rich traces have the
unique exact cover (1/2,1/2,1/2).

The manuscript contains the symbolic proof.  This script independently
enumerates the rational vertices, constructs the lower-envelope game, and
uses the generic exact staged solvers on the smallest member.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

from leximin import leximax_core_exact, leximin_core_exact
from tugame import Game


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


F = Fraction


def defining_coalitions(u: int, w: int):
    if u < 2 or w < 2:
        raise ValueError("the family requires |A|,|B| >= 2")
    # Player order: a,b,c,A...,B...
    a, b, c = 0, 1, 2
    A = tuple(range(3, 3 + u))
    B = tuple(range(3 + u, 3 + u + w))
    h = 1 + u + w
    constraints = (
        ((c,) + A, F(2 * (u + 1))),
        ((c,) + B, F(2 * (w + 1))),
        ((b,) + A + B, F(2 * h - 1)),
    )
    return (a, b, c), A, B, constraints


def vertices(u: int, w: int):
    players, A, B, constraints = defining_coalitions(u, w)
    n = 3 + u + w
    total = F(2 + 2 * (1 + u + w))
    active_rows = [("zero", i) for i in range(n)]
    active_rows += [("coalition", j) for j in range(3)]
    found = set()
    for active in itertools.combinations(active_rows, n - 1):
        matrix = [[F(1)] * n]
        rhs = [total]
        for kind, index in active:
            row = [F(0)] * n
            if kind == "zero":
                row[index] = F(1)
                value = F(0)
            else:
                coalition, value = constraints[index]
                for player in coalition:
                    row[player] = F(1)
            matrix.append(row)
            rhs.append(value)
        M = sp.Matrix(matrix)
        if M.rank() < n:
            continue
        solution = M.inv() * sp.Matrix(rhs)
        point = tuple(F(int(x.p), int(x.q)) for x in solution)
        if any(x < 0 for x in point):
            continue
        if any(
            sum(point[i] for i in coalition) < value
            for coalition, value in constraints
        ):
            continue
        found.add(point)
    return tuple(sorted(found))


def coalition_sum(point, coalition: int):
    return sum(
        point[player]
        for player in range(len(point))
        if coalition >> player & 1
    )


def lower_envelope(points):
    n = len(points[0])
    full = (1 << n) - 1
    values = [F(0)] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(
            coalition_sum(point, coalition) for point in points
        )
    values[full] = sum(points[0])
    return Game(n, values)


def mask(players):
    return sum(1 << player for player in players)


def verify_case(u: int, w: int, staged_replay: bool):
    (a, b, c), A, B, constraints = defining_coalitions(u, w)
    n = 3 + u + w
    h = 1 + u + w
    points = vertices(u, w)
    game = lower_envelope(points)
    phi = tuple([F(1), F(1)] + [F(2)] * h)
    full = (1 << n) - 1
    H = tuple(range(2, n))

    if any(sum(point) != 2 + 2 * h for point in points):
        raise RuntimeError("common-total identity failed")
    if any(
        (2 * coordinate).denominator != 1
        for point in points
        for coordinate in point
    ):
        raise RuntimeError("doubling does not give an integral vertex set")
    if not all(game.in_core(point) for point in points):
        raise RuntimeError("a declared lower-envelope vertex left the core")
    if any(game.v[1 << player] != 0 for player in range(n)):
        raise RuntimeError("singleton normalization failed")
    if not game.in_core(phi):
        raise RuntimeError("the candidate Lmin point is outside the core")

    expected_tight = {mask(coalition) for coalition, _ in constraints}
    actual_tight = {
        coalition
        for coalition in range(1, full)
        if coalition_sum(phi, coalition) == game.v[coalition]
    }
    if actual_tight != expected_tight:
        raise RuntimeError(
            f"unexpected proper tight coalitions: {actual_tight ^ expected_tight}"
        )

    richer_mask = mask(H)
    if game.v[richer_mask] != 2 * h - 1:
        raise RuntimeError("wrong richer-suffix value")
    if coalition_sum(phi, richer_mask) - game.v[richer_mask] != 1:
        raise RuntimeError("wrong richer-suffix slack")

    traces = tuple(mask(coalition) & richer_mask for coalition, _ in constraints)
    half_cover = [
        sum(F(1, 2) for trace in traces if trace >> player & 1)
        for player in H
    ]
    if half_cover != [F(1)] * h:
        raise RuntimeError("the three traces do not form the claimed half-cover")
    trace_matrix = sp.Matrix(
        [[int(trace >> player & 1) for trace in traces] for player in H]
    )
    if trace_matrix.rank() != 3:
        raise RuntimeError("the trace exact cover is not unique")

    replay_lmin = replay_lmax = None
    if staged_replay:
        replay_lmin = tuple(leximin_core_exact(game))
        replay_lmax = tuple(leximax_core_exact(game))
        if replay_lmin != phi or replay_lmax != phi:
            raise RuntimeError("generic exact staged replay failed")

    return {
        "A_size": u,
        "B_size": w,
        "player_count": n,
        "richer_size": h,
        "vertex_count": len(points),
        "integral_after_scaling_by_two": True,
        "lmin_formula": [str(x) for x in phi],
        "lmax_formula": [str(x) for x in phi],
        "richer_suffix_value": str(game.v[richer_mask]),
        "richer_suffix_payoff": str(coalition_sum(phi, richer_mask)),
        "richer_suffix_slack": "1",
        "proper_tight_coalition_count": len(actual_tight),
        "unique_trace_cover": ["1/2", "1/2", "1/2"],
        "staged_replay": staged_replay,
        "replayed_lmin": (
            [str(x) for x in replay_lmin] if replay_lmin is not None else None
        ),
        "replayed_lmax": (
            [str(x) for x in replay_lmax] if replay_lmax is not None else None
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-block", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = []
    for u in range(2, args.max_block + 1):
        for w in range(2, args.max_block + 1):
            cases.append(verify_case(u, w, staged_replay=(u == w == 2)))
    result = {
        "status": "verified",
        "theorem": "three-trace half-integral obstruction family",
        "cases": cases,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
