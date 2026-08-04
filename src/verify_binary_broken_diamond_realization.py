"""Exact audit of the universal binary broken-diamond realization."""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

import sympy as sp

from leximin import leximin_core_exact
from tugame import Game


def mask(players):
    return sum(1 << player for player in players)


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def instance(c, x, y, r, rich_payoff=F(2), poor_payoff=F(1)):
    rich_payoff, poor_payoff = F(rich_payoff), F(poor_payoff)
    if min(c, x, y, r) < 1:
        raise ValueError("requires four nonempty blocks")
    if not rich_payoff > poor_payoff > 0:
        raise ValueError("requires rich_payoff > poor_payoff > 0")
    if c == 1 and poor_payoff * r < rich_payoff:
        raise ValueError("singleton intersection lacks exterior payoff capacity")
    n = c + x + y + r
    C = tuple(range(c))
    X = tuple(range(c, c + x))
    Y = tuple(range(c + x, c + x + y))
    R = tuple(range(c + x + y, n))
    A, B = mask(C + X), mask(C + Y)
    phi = tuple(
        [rich_payoff] * c + [poor_payoff] * (x + y + r)
    )
    total = sum(phi)
    active = [("zero", player) for player in range(n)] + [("set", A), ("set", B)]
    points = set()
    for rows in itertools.combinations(active, n - 1):
        matrix = [[F(1)] * n]
        rhs = [total]
        for kind, index in rows:
            if kind == "zero":
                matrix.append([F(int(player == index)) for player in range(n)])
                rhs.append(F(0))
            else:
                matrix.append([F(int(index >> player & 1)) for player in range(n)])
                rhs.append(payoff(phi, index))
        M = sp.Matrix(matrix)
        if M.rank() < n:
            continue
        solution = M.inv() * sp.Matrix(rhs)
        point = tuple(F(int(value.p), int(value.q)) for value in solution)
        if any(value < 0 for value in point):
            continue
        if payoff(point, A) < payoff(phi, A) or payoff(point, B) < payoff(phi, B):
            continue
        points.add(point)
    if not points:
        raise AssertionError("no vertices")

    full = (1 << n) - 1
    values = [F(0)] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(payoff(point, coalition) for point in points)
    values[full] = total
    game = Game(n, values)
    C_mask, R_mask, U = mask(C), mask(R), A | B

    if any(values[1 << player] != 0 for player in range(n)):
        raise AssertionError("singleton normalization failed")
    if not all(game.in_core(point) for point in points):
        raise AssertionError("a vertex left the lower-envelope core")
    if values[A] != payoff(phi, A) or values[B] != payoff(phi, B):
        raise AssertionError("protector pair is not tight")
    expected_c_value = max(F(0), rich_payoff * c - poor_payoff * r)
    expected_u_value = rich_payoff * c + poor_payoff * max(x, y)
    if values[C_mask] != expected_c_value or values[U] != expected_u_value:
        raise AssertionError("broken-diamond formula failed")
    if payoff(phi, C_mask) - values[C_mask] != min(
        rich_payoff * c, poor_payoff * r
    ):
        raise AssertionError("intersection slack formula failed")
    if payoff(phi, U) - values[U] != poor_payoff * min(x, y):
        raise AssertionError("union slack formula failed")

    replay = None
    if n <= 6:
        replay = tuple(leximin_core_exact(game))
        if replay != phi:
            raise AssertionError(f"generic Lmin replay gave {replay}, expected {phi}")

    return {
        "block_sizes": {"C": c, "X": x, "Y": y, "R": r},
        "payoff_levels": {
            "intersection": str(rich_payoff),
            "outside": str(poor_payoff),
        },
        "player_count": n,
        "vertex_count": len(points),
        "lmin_formula": [str(value) for value in phi],
        "generic_lmin_replayed": replay is not None,
        "generic_lmin": [str(value) for value in replay] if replay else None,
        "intersection_value": str(values[C_mask]),
        "intersection_slack": str(payoff(phi, C_mask) - values[C_mask]),
        "union_value": str(values[U]),
        "union_slack": str(payoff(phi, U) - values[U]),
        "exterior_value": str(values[R_mask]),
        "exterior_slack": str(payoff(phi, R_mask) - values[R_mask]),
        "strict_cover_loads": {"C": 2, "X": 1, "Y": 1, "R": 0},
        "singleton_normalized": True,
        "exact_lower_envelope": True,
        "broken_tight_diamond": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-block-size", type=int, default=2)
    args = parser.parse_args()
    cases = [
        instance(c, x, y, r)
        for c in range(1, args.max_block_size + 1)
        for x in range(1, args.max_block_size + 1)
        for y in range(1, args.max_block_size + 1)
        for r in range(1, args.max_block_size + 1)
        if c >= 2 or r >= 2
    ]
    five_player_shapes = [
        case["block_sizes"] for case in cases if case["player_count"] == 5
    ]
    expected = [
        {"C": 1, "X": 1, "Y": 1, "R": 2},
        {"C": 2, "X": 1, "Y": 1, "R": 1},
    ]
    if five_player_shapes != expected:
        raise AssertionError(f"unexpected sharp five-player shapes: {five_player_shapes}")
    payload = {
        "status": "binary broken-diamond realization verified",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "sharp_minimum_player_count": 5,
        "sharp_five_player_shapes": five_player_shapes,
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
