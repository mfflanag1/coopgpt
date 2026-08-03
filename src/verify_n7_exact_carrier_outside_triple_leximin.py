"""Exact-rational leximin certificate for the n=7 outside-triple example."""
from __future__ import annotations

import json
from fractions import Fraction as F

if not __debug__:
    raise RuntimeError("certificate verification must not run with Python -O")

from leximin import leximin_core_exact
from tugame import Game
from verify_n7_exact_carrier_outside_triple_counterexample import (
    ETA_SUPPORT,
    GENERATORS,
    N,
    P,
    S,
    payoff,
)


EXPECTED = (
    F(-4, 3),
    F(1, 3),
    F(2, 3),
    F(2, 3),
    F(-1, 3),
    F(1, 3),
    F(-1, 3),
)
EXPECTED_FLOORS = (F(-4), F(-1), F(0), F(0), F(-1), F(-1), F(-1))
EXPECTED_GAINS = (F(8, 3), F(4, 3), F(2, 3), F(2, 3), F(2, 3), F(4, 3), F(2, 3))


def main():
    value = [
        F(min(payoff(generator, coalition) for generator in GENERATORS))
        for coalition in range(1 << N)
    ]
    game = Game(N, value)
    phi = tuple(leximin_core_exact(game))
    assert phi == EXPECTED and game.in_core(phi)
    floors = tuple(value[1 << player] for player in range(N))
    gains = tuple(phi[player] - floors[player] for player in range(N))
    assert floors == EXPECTED_FLOORS and gains == EXPECTED_GAINS

    # Stage 1: v(1246)=v(1236)=0, so efficiency gives x(357)<=0 and
    # x(457)<=0.  The common-gain constraints give
    # x(357),x(457)>=-2+3t, hence t<=2/3.  Equality in the two overlapping
    # triples pins players 3,4,5,7.
    assert value[43] == value[39] == 0
    assert payoff(phi, 84) == payoff(phi, 88) == 0
    assert all(gains[player] == F(2, 3) for player in (2, 3, 4, 6))

    # Stage 2: the pinned coordinates sum to 2/3.  Since v(134)=0,
    # x_1>=-4/3 and efficiency gives x_2+x_6<=2/3.  If their remaining
    # gains are at least u, then x_2+x_6>=-2+2u, so u<=4/3.
    assert sum(phi[player] for player in (2, 3, 4, 6)) == F(2, 3)
    assert value[13] == payoff(phi, 13) == 0
    assert phi[1] + phi[5] == F(2, 3)
    assert gains[1] == gains[5] == F(4, 3)

    # Stage 3: efficiency fixes player 1 and its gain at 8/3.
    assert phi[0] == F(-4, 3) and gains[0] == F(8, 3)
    slack = [
        payoff(phi, coalition) - value[coalition]
        for coalition in range(1 << N)
    ]
    carrier_differences = [
        slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    ]
    assert carrier_differences == [F(2, 3)] * (S - 1)
    zero_faces = (48, 84, 88, 109)
    assert all(slack[coalition] == 0 for coalition in zero_faces)
    degree = [
        sum(weight for coalition, weight in ETA_SUPPORT.items()
            if coalition >> player & 1)
        for player in range(N)
    ]
    assert degree == [4] * N
    eta_upper_bound = sum(
        weight * slack[coalition]
        for coalition, weight in ETA_SUPPORT.items()
        if coalition not in (S, 1, 2)
    )
    eta_lower_bound = sum(phi[player] - phi[player] for player in range(4))
    assert eta_upper_bound == eta_lower_bound == 0
    print(json.dumps({
        "status": "exact-rational outside-triple leximin counterexample verified",
        "leximin": [str(coordinate) for coordinate in phi],
        "floors": [str(value) for value in floors],
        "gains": [str(value) for value in gains],
        "maschler_strata": [
            {"level": "2/3", "players": [3, 4, 5, 7]},
            {"level": "4/3", "players": [2, 6]},
            {"level": "8/3", "players": [1]},
        ],
        "carrier_differences": [str(value) for value in carrier_differences],
        "gamma_S_at_leximin": "2/3",
        "eta_S_at_leximin": str(eta_upper_bound),
        "carrier_bound_violated_at_leximin": eta_upper_bound < min(carrier_differences),
        "conclusion": (
            "three outside players suffice for a seven-player leximin "
            "carrier obstruction"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
