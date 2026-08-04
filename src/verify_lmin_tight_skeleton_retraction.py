"""Exact audit of the dimension-free Lmin tight-skeleton retraction.

The human theorem is in paper3/LMIN_TIGHT_SKELETON_RETRACTION.md.  This
script independently rebuilds the skeleton polytope of three structurally
different exact lower-envelope games and checks the theorem coalitionwise.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy as sp

from tugame import Game, exact_lp_min
from verify_three_poorer_boundary_family import (
    generators as three_poorer_generators,
    lower_envelope as integer_lower_envelope,
)
from verify_three_trace_half_integral_family import (
    lower_envelope as fractional_lower_envelope,
    vertices as three_trace_vertices,
)
from verify_two_poorer_rich_family import (
    generators as two_poorer_generators,
)


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


F = Fraction


def coalition_sum(point, coalition: int):
    return sum(
        point[player]
        for player in range(len(point))
        if coalition >> player & 1
    )


def proper_tight_coalitions(game: Game, phi):
    full = (1 << game.n) - 1
    return tuple(
        coalition
        for coalition in range(1, full)
        if game.v[coalition] == coalition_sum(phi, coalition)
    )


def skeleton_vertices(game: Game, phi, tight):
    """Enumerate vertices of nonnegativity + efficiency + tight skeleton."""
    n = game.n
    full = (1 << n) - 1
    total = F(game.v[full])
    active_rows = tuple(("zero", i) for i in range(n)) + tuple(
        ("tight", coalition) for coalition in tight
    )
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
                for player in range(n):
                    if index >> player & 1:
                        row[player] = F(1)
                value = F(coalition_sum(phi, index))
            matrix.append(row)
            rhs.append(value)
        # Screen the many zero-one active sets numerically, then validate every
        # retained solution in exact rational arithmetic below.  For these
        # matrices the screening avoids thousands of repeated symbolic ranks;
        # it is not used to accept a vertex.
        matrix_np = np.asarray(matrix, dtype=float)
        if np.linalg.matrix_rank(matrix_np) != n:
            continue
        approximate = np.linalg.solve(matrix_np, np.asarray(rhs, dtype=float))
        point = tuple(F(float(x)).limit_denominator(1_000_000) for x in approximate)
        if any(
            sum(matrix[row][column] * point[column] for column in range(n))
            != rhs[row]
            for row in range(n)
        ):
            # This should not occur in the small audit instances.  Fall back
            # to an exact solve rather than trusting rational reconstruction.
            matrix_sp = sp.Matrix(matrix)
            solution = matrix_sp.inv() * sp.Matrix(rhs)
            point = tuple(F(int(x.p), int(x.q)) for x in solution)
        if any(value < 0 for value in point):
            continue
        if any(
            coalition_sum(point, coalition)
            < coalition_sum(phi, coalition)
            for coalition in tight
        ):
            continue
        found.add(point)
    if not found:
        raise RuntimeError("skeleton polytope has no enumerated vertices")
    return tuple(sorted(found))


def lower_envelope_from_points(points):
    n = len(points[0])
    full = (1 << n) - 1
    values = [F(0)] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(
            coalition_sum(point, coalition) for point in points
        )
    values[full] = sum(points[0])
    return Game(n, values)


def skeleton_retraction(game: Game, phi):
    tight = proper_tight_coalitions(game, phi)
    points = skeleton_vertices(game, phi, tight)
    return lower_envelope_from_points(points), points, tight


def leximin_skeleton_exact(n: int, total, tight, phi):
    """Generic staged Lmin over the small skeleton inequality system."""
    fixed = {}

    def base_rows(extra_variable: bool):
        width = n + int(extra_variable)
        rows = []
        rhs = []
        for player in range(n):
            row = [F(0)] * width
            row[player] = F(-1)
            rows.append(row)
            rhs.append(F(0))
        for coalition in tight:
            row = [F(0)] * width
            for player in range(n):
                if coalition >> player & 1:
                    row[player] = F(-1)
            rows.append(row)
            rhs.append(-F(coalition_sum(phi, coalition)))
        return rows, rhs

    def equalities(extra_variable: bool):
        width = n + int(extra_variable)
        rows = [[F(1)] * n + ([F(0)] if extra_variable else [])]
        rhs = [F(total)]
        for player, value in fixed.items():
            row = [F(0)] * width
            row[player] = F(1)
            rows.append(row)
            rhs.append(value)
        return rows, rhs

    def solve_level(free):
        rows, rhs = base_rows(True)
        for player in free:
            row = [F(0)] * (n + 1)
            row[player] = F(-1)
            row[n] = F(1)
            rows.append(row)
            rhs.append(F(0))
        eq, eq_rhs = equalities(True)
        objective = [F(0)] * (n + 1)
        objective[n] = F(-1)
        optimum, _ = exact_lp_min(objective, rows, rhs, eq, eq_rhs)
        return None if optimum in (None, "unbounded") else -optimum

    def maximize_player(target, free, level):
        rows, rhs = base_rows(False)
        for player in free:
            row = [F(0)] * n
            row[player] = F(-1)
            rows.append(row)
            rhs.append(-level)
        eq, eq_rhs = equalities(False)
        objective = [F(0)] * n
        objective[target] = F(-1)
        optimum, _ = exact_lp_min(objective, rows, rhs, eq, eq_rhs)
        return None if optimum in (None, "unbounded") else -optimum

    free = list(range(n))
    while free:
        level = solve_level(free)
        if level is None:
            raise RuntimeError("skeleton Lmin stage is infeasible or unbounded")
        pinned = [
            player
            for player in free
            if maximize_player(player, free, level) == level
        ]
        if not pinned:
            raise RuntimeError("skeleton Lmin stage pins no player")
        for player in pinned:
            fixed[player] = level
            free.remove(player)
    return tuple(fixed[player] for player in range(n))


def make_cases():
    # Three payoff strata, five players.
    points_5 = three_poorer_generators(3, 2)
    game_5 = Game(5, integer_lower_envelope(points_5))

    # Four-co-singleton packet, six players.
    points_6 = two_poorer_generators(2, 4)
    game_6 = Game(6, integer_lower_envelope(points_6))

    # Three-column blown-up triangle, seven players.
    points_7 = three_trace_vertices(1, 2, 2)
    game_7 = fractional_lower_envelope(points_7)

    return (
        ("three-stratum-five-player", game_5, (F(1), F(1), F(2), F(3), F(3))),
        ("four-cosingleton-six-player", game_6, (F(2), F(2)) + (F(4),) * 4),
        ("three-column-seven-player", game_7, (F(1), F(1)) + (F(2),) * 5),
    )


def verify_case(name: str, game: Game, phi):
    retracted, points, tight = skeleton_retraction(game, phi)
    retracted_lmin = leximin_skeleton_exact(
        game.n, game.v[(1 << game.n) - 1], tight, phi
    )
    if retracted_lmin != tuple(phi):
        raise RuntimeError(f"{name}: retracted Lmin mismatch: {retracted_lmin}")
    if any(retracted.v[S] > game.v[S] for S in range(1 << game.n)):
        raise RuntimeError(f"{name}: retraction is not pointwise below input")
    if any(retracted.v[1 << i] != 0 for i in range(game.n)):
        raise RuntimeError(f"{name}: singleton normalization was lost")
    if any(not retracted.in_core(point) for point in points):
        raise RuntimeError(f"{name}: a skeleton vertex is outside the new core")

    retracted_tight = proper_tight_coalitions(retracted, phi)
    if retracted_tight != tight:
        raise RuntimeError(f"{name}: full proper tight set changed")
    if any(
        (game.v[S] == coalition_sum(phi, S))
        != (retracted.v[S] == coalition_sum(phi, S))
        for S in range(1, (1 << game.n) - 1)
    ):
        raise RuntimeError(f"{name}: coalitionwise tight/slack pattern changed")

    twice, points_twice, tight_twice = skeleton_retraction(retracted, phi)
    if twice.v != retracted.v or tight_twice != tight:
        raise RuntimeError(f"{name}: retraction is not idempotent")

    strict_decreases = sum(
        retracted.v[S] < game.v[S] for S in range(1 << game.n)
    )
    return {
        "case": name,
        "players": game.n,
        "proper_tight_coalitions": len(tight),
        "skeleton_vertices": len(points),
        "second_retraction_vertices": len(points_twice),
        "strictly_decreased_coalition_values": strict_decreases,
        "lmin": [str(value) for value in retracted_lmin],
        "full_tight_slack_pattern_preserved": True,
        "pointwise_below_original": True,
        "singleton_normalized": True,
        "idempotent": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [verify_case(*case) for case in make_cases()]
    payload = {
        "status": "verified",
        "theorem": "Lmin tight-skeleton retraction",
        "proof_scope": (
            "the theorem is human and dimension-free; this exact audit uses "
            "three unrelated finite representatives"
        ),
        "cases": cases,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
