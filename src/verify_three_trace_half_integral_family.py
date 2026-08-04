"""Exact audit of the three-trace half-integral obstruction family.

For two poorer players a,b and a richer block H=C disjoint-union A
disjoint-union B, with |C| >= 1 and |A|,|B| >= 2, consider the compact
polytope

    x >= 0,  x(N)=2+2|H|,
    x(C union A) >= 2(|C|+|A|),
    x(C union B) >= 2(|C|+|B|),
    x({b} union A union B) >= 1+2(|A|+|B|).

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


def defining_coalitions(t: int, u: int, w: int):
    if t < 1 or u < 2 or w < 2:
        raise ValueError("the family requires |C|>=1 and |A|,|B|>=2")
    # Player order: a,b,C...,A...,B...
    a, b = 0, 1
    C = tuple(range(2, 2 + t))
    A = tuple(range(2 + t, 2 + t + u))
    B = tuple(range(2 + t + u, 2 + t + u + w))
    h = t + u + w
    constraints = (
        (C + A, F(2 * (t + u))),
        (C + B, F(2 * (t + w))),
        ((b,) + A + B, F(1 + 2 * (u + w))),
    )
    return (a, b), C, A, B, constraints


def vertices(t: int, u: int, w: int):
    players, C, A, B, constraints = defining_coalitions(t, u, w)
    n = 2 + t + u + w
    total = F(2 + 2 * (t + u + w))
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


def verify_case(t: int, u: int, w: int, staged_replay: bool):
    (a, b), C, A, B, constraints = defining_coalitions(t, u, w)
    n = 2 + t + u + w
    h = t + u + w
    points = vertices(t, u, w)
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
        "C_size": t,
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


def audit_three_column_classification():
    """Enumerate row types, not games, to audit the human support theorem."""
    row_types = tuple(range(1, 8))
    fractional_systems = []
    for support_size in range(1, len(row_types) + 1):
        for types in itertools.combinations(row_types, support_size):
            matrix = sp.Matrix(
                [[int(row_type >> column & 1) for column in range(3)]
                 for row_type in types]
            )
            if matrix.rank() != 3:
                continue
            solution_set = sp.linsolve((matrix, sp.ones(len(types), 1)))
            if solution_set is sp.EmptySet:
                continue
            solutions = list(solution_set)
            if len(solutions) != 1:
                continue
            beta = tuple(F(int(x.p), int(x.q)) for x in solutions[0])
            if any(x <= 0 for x in beta):
                continue
            if any(x.denominator > 1 for x in beta):
                fractional_systems.append((types, beta))

    expected_types = (0b011, 0b101, 0b110)
    if fractional_systems != [(expected_types, (F(1, 2),) * 3)]:
        raise RuntimeError(
            f"unexpected fractional three-column systems: {fractional_systems}"
        )

    feasible_labels = []
    beta = (F(1, 2),) * 3
    # Label states: bit 0 is losing poor player a; bit 1 is gaining b.
    for labels in itertools.product(range(4), repeat=3):
        r_a = sum(beta[j] for j, label in enumerate(labels) if label & 1)
        r_b = sum(beta[j] for j, label in enumerate(labels) if label & 2)
        if r_a < r_b < 1:
            feasible_labels.append(labels)
    expected_labels = [(0, 0, 2), (0, 2, 0), (2, 0, 0)]
    if feasible_labels != expected_labels:
        raise RuntimeError(f"unexpected underloaded labelings: {feasible_labels}")
    return {
        "fractional_vertex_count_up_to_row_type_repetition": 1,
        "unique_row_types_binary": ["011", "101", "110"],
        "unique_cover": ["1/2", "1/2", "1/2"],
        "underloaded_labelings_up_to_column_permutation": 1,
        "canonical_labels": ["none", "none", "gaining-b"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-central-block", type=int, default=2)
    parser.add_argument("--max-block", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = []
    for t in range(1, args.max_central_block + 1):
        for u in range(2, args.max_block + 1):
            for w in range(2, args.max_block + 1):
                cases.append(
                    verify_case(t, u, w, staged_replay=(t == 1 and u == w == 2))
                )
    result = {
        "status": "verified",
        "theorem": "three-column obstruction classification and realization",
        "abstract_classification": audit_three_column_classification(),
        "cases": cases,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
