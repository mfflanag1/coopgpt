"""Exact boundary stress test for the multi-generator carrier conjecture.

Starting from the sharp two-generator equality fixture, add a third generator
that lowers off-side coalitions by transferring mass from player 5 across the
five players of S.  The carrier margin becomes strictly positive, but the same
deformation immediately restores the star condition.  Thus the most direct
way to cross the two-generator carrier boundary does not preserve the premise
of the conjecture.

The finite simplex-grid scan is only a float discovery diagnostic.  The stated
anchor deformation and every mathematical quantity printed for it are
recomputed in exact rational arithmetic.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F

from hunt_exact_points import game_from_points
from hunt_off_side_carrier import (
    carrier_score,
    core_matrices,
    maximize_target,
)
from lemD import core_max_xS, star_holds, xS
from leximin import leximin_core_exact, leximin_core_float


P = [-1, 5, 6, 8, 6, 0]
Q = [3, 2, 1, 3, 7, 8]
S = 47  # {1,2,3,4,6}; the off-side player is 5.
S_PLAYERS = (0, 1, 2, 3, 5)
PHI = [F(1), F(4), F(3), F(5), F(7), F(4)]


def members(mask, n=6):
    return [i + 1 for i in range(n) if mask >> i & 1]


def compositions(total, parts, prefix=()):
    if parts == 1:
        yield prefix + (total,)
        return
    for value in range(total + 1):
        yield from compositions(total - value, parts - 1, prefix + (value,))


def third_generator(amount, weights):
    assert len(weights) == len(S_PLAYERS)
    assert sum(weights) == 1
    point = [F(value) for value in Q]
    point[4] -= amount
    for player, weight in zip(S_PLAYERS, weights):
        point[player] += amount * weight
    assert sum(point) == sum(Q)
    return point


def float_grid_screen(resolution):
    counts = {
        "deformations": 0,
        "binding": 0,
        "star_failures": 0,
        "positive_carrier_margin": 0,
        "positive_margin_and_star_failure": 0,
    }
    best_star_failure = None
    smallest_opening_ratio = None
    for integer_weights in compositions(resolution, len(S_PLAYERS)):
        weights = [F(value, resolution) for value in integer_weights]
        point = third_generator(F(1), weights)
        game = game_from_points(6, [P, Q, point])
        phi = leximin_core_float(6, game.v, tol=1e-9)
        rows, rhs = core_matrices(game)
        phi_s = xS(phi, S, 6)
        maximum = maximize_target(game, S, rows, rhs)
        star_maximum = maximize_target(game, S, rows, rhs, lower=phi)
        score, face, carrier = carrier_score(game, phi, S)
        binding = maximum > phi_s + 1e-7
        star_failure = star_maximum <= phi_s + 1e-7
        positive = score > 1e-7
        counts["deformations"] += 1
        counts["binding"] += int(binding)
        counts["star_failures"] += int(star_failure)
        counts["positive_carrier_margin"] += int(positive)
        counts["positive_margin_and_star_failure"] += int(star_failure and positive)
        record = {
            "integer_weights": list(integer_weights),
            "carrier_margin": score,
            "star_opening": star_maximum - phi_s,
            "minimizing_face": members(face),
            "carrier": members(carrier),
        }
        if star_failure and (
            best_star_failure is None
            or score > best_star_failure["carrier_margin"]
        ):
            best_star_failure = record
        if positive:
            record["opening_to_margin_ratio"] = (
                (star_maximum - phi_s) / score
            )
            if smallest_opening_ratio is None or (
                record["opening_to_margin_ratio"]
                < smallest_opening_ratio["opening_to_margin_ratio"]
            ):
                smallest_opening_ratio = record
    return {
        "resolution": resolution,
        "amount": 1,
        "counts": counts,
        "best_star_failure": best_star_failure,
        "smallest_opening_ratio": smallest_opening_ratio,
        "status": "diagnostic only; all decisions above use floating-point LPs",
    }


def exact_anchor():
    amount = F(1, 10)
    weights = [F(1, 5)] * 5
    point = third_generator(amount, weights)
    game = game_from_points(6, [P, Q, point])
    generators = [[F(value) for value in generator] for generator in [P, Q, point]]
    unique_minimizers = {index: [] for index in range(3)}
    for coalition in range(1, game.N):
        values = [xS(generator, coalition, 6) for generator in generators]
        winners = [index for index, value in enumerate(values) if value == min(values)]
        if len(winners) == 1:
            unique_minimizers[winners[0]].append(members(coalition))
    assert all(unique_minimizers.values())
    phi = leximin_core_exact(game)
    assert phi == PHI
    assert all(xS(phi, coalition, 6) >= game.v[coalition]
               for coalition in range(1, game.N))
    maximum = core_max_xS(game, S)
    assert maximum == 18 > xS(phi, S, 6)
    holds, star_maximum, witness = star_holds(game, phi, S)
    expected_witness = [
        F(26, 25), F(4), F(153, 50), F(253, 50), F(171, 25), F(4)
    ]
    assert holds
    assert star_maximum == F(429, 25)
    assert star_maximum - xS(phi, S, 6) == F(4, 25)
    assert witness == expected_witness
    assert game.in_core(witness)
    assert all(witness[i] >= phi[i] for i in S_PLAYERS)
    score, face, carrier = carrier_score(game, phi, S)
    assert (score, face, carrier) == (F(1, 50), 15, 31)
    return {
        "points": [[str(F(value)) for value in point] for point in [P, Q, point]],
        "unique_minimizer_counts": {
            str(index + 1): len(coalitions)
            for index, coalitions in unique_minimizers.items()
        },
        "third_generator_unique_at": unique_minimizers[2],
        "S": members(S),
        "phi": [str(value) for value in phi],
        "binding": True,
        "max_core_xS": str(maximum),
        "carrier_escape_margin": str(score),
        "minimizing_face": members(face),
        "carrier": members(carrier),
        "star_holds": holds,
        "star_maximum": str(star_maximum),
        "star_opening": str(star_maximum - xS(phi, S, 6)),
        "star_witness": [str(value) for value in witness],
        "ratio_star_opening_to_carrier_margin": str(
            (star_maximum - xS(phi, S, 6)) / score
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolution", type=int, default=8)
    args = parser.parse_args()
    report = {
        "status": "exact anchor verified; grid is diagnostic evidence",
        "exact_anchor": exact_anchor(),
        "float_simplex_grid": float_grid_screen(args.resolution),
    }
    print(json.dumps(report, indent=2))
    print("THREE-GENERATOR BOUNDARY ESCAPE BLOCKED IN EXACT ANCHOR")


if __name__ == "__main__":
    main()
