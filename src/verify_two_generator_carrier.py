"""Exact regression verifier for Proposition: two-generator lower envelopes."""
from __future__ import annotations

import random
from fractions import Fraction as F

from hunt_exact_points import game_from_points, rand_point_sum
from lemD import star_holds, xS
from leximin import leximin_core_exact


def verify_instance(points, phi=None, targets=None):
    n = len(points[0])
    game = game_from_points(n, points)
    phi = leximin_core_exact(game) if phi is None else [F(value) for value in phi]
    assert sum(phi) == game.v[game.N]
    assert all(xS(phi, coalition, n) >= game.v[coalition]
               for coalition in range(1, game.N))
    checked = 0
    for target in (range(1, game.N) if targets is None else targets):
        if target.bit_count() < 2:
            continue
        phi_target = xS(phi, target, n)
        generator_maximum = max(
            sum(point[i] for i in range(n) if target >> i & 1)
            for point in points
        )
        if generator_maximum <= phi_target:
            continue
        holds, _, _ = star_holds(game, phi, target)
        if holds:
            continue

        p, q = points
        if sum(p[i] for i in range(n) if target >> i & 1) < sum(
            q[i] for i in range(n) if target >> i & 1
        ):
            p, q = q, p
        face = sum(
            1 << i
            for i in range(n)
            if target >> i & 1 and F(p[i]) > phi[i]
        )
        assert face not in (0, target)
        off_side = game.N ^ target
        carrier = off_side | face
        assert game.v[carrier] - game.v[face] >= xS(phi, off_side, n)
        checked += 1
    return checked


def main():
    rng = random.Random(20260801)
    games = 0
    failures = 0
    fixtures = [
        (
            [[0, 5, 6, 8, 5, 0], [3, 2, 1, 3, 7, 8]],
            [F(3, 2), F(7, 2), 3, 5, F(13, 2), F(9, 2)],
            [47],
        ),
        (
            [[-1, 5, 6, 8, 6, 0], [3, 2, 1, 3, 7, 8]],
            [1, 4, 3, 5, 7, 4],
            [47],
        ),
    ]
    for points, phi, targets in fixtures:
        failures += verify_instance(points, phi=phi, targets=targets)
        games += 1
    for n, count in ((3, 3),):
        for _ in range(count):
            total = rng.randint(n, 6 * n)
            points = [rand_point_sum(n, total, rng) for _ in range(2)]
            failures += verify_instance(points)
            games += 1
    print(
        "TWO-GENERATOR CARRIER VERIFIED: "
        f"{games} exact games, {failures} binding star-failure coalitions"
    )


if __name__ == "__main__":
    main()
