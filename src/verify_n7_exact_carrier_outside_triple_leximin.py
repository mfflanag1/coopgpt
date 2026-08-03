"""Exact-rational leximin scope check for the n=7 outside-triple example."""
from __future__ import annotations

import json
from fractions import Fraction as F

from leximin import leximin_core_exact
from tugame import Game
from verify_n7_exact_carrier_outside_triple_counterexample import (
    GENERATORS,
    N,
    P,
    S,
    payoff,
)


EXPECTED = (
    F(-2),
    F(1, 3),
    F(4, 3),
    F(4, 3),
    F(-5, 3),
    F(1, 3),
    F(1, 3),
)


def main():
    value = [
        F(min(payoff(generator, coalition) for generator in GENERATORS))
        for coalition in range(1 << N)
    ]
    game = Game(N, value)
    phi = tuple(leximin_core_exact(game))
    assert phi == EXPECTED and game.in_core(phi)
    slack = [
        payoff(phi, coalition) - value[coalition]
        for coalition in range(1 << N)
    ]
    carrier_differences = [
        slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    ]
    assert carrier_differences == [F(0)] * (S - 1)
    print(json.dumps({
        "status": "exact-rational leximin scope check passed",
        "leximin": [str(coordinate) for coordinate in phi],
        "carrier_differences": [str(value) for value in carrier_differences],
        "gamma_S_at_leximin": "0",
        "conclusion": (
            "this 4+3 game is an arbitrary-reference carrier obstruction, "
            "not a leximin carrier obstruction"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
