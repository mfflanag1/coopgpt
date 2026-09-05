"""Exact-rational leximin check for the sharp seven-player counterexample."""
from __future__ import annotations

import sys

if sys.flags.optimize:
    raise SystemExit(
        "This verifier requires assertions enabled; run without -O, -OO, or PYTHONOPTIMIZE."
    )

import json
from fractions import Fraction as F

from leximin import leximin_core_exact
from tugame import Game
from verify_n7_exact_carrier_counterexample import (
    ETA_SUPPORT,
    FULL,
    GENERATORS,
    N,
    P,
    S,
    members,
    payoff,
)


EXPECTED_LEXIMIN = (
    F(-3, 4),
    F(1, 4),
    F(3, 4),
    F(-1, 4),
    F(1, 2),
    F(-1, 4),
    F(-1, 4),
)
EXPECTED_FLOORS = (F(-3), F(-2), F(0), F(-1), F(-1), F(-1), F(-1))
EXPECTED_GAINS = (F(9, 4), F(9, 4), F(3, 4), F(3, 4), F(3, 2), F(3, 4), F(3, 4))
EXPECTED_STRATA = (
    (F(3, 4), (3, 4, 6, 7)),
    (F(3, 2), (5,)),
    (F(9, 4), (1, 2)),
)


def main():
    value = [
        F(min(payoff(generator, coalition) for generator in GENERATORS))
        for coalition in range(1 << N)
    ]
    game = Game(N, value)
    phi = tuple(leximin_core_exact(game))
    assert phi == EXPECTED_LEXIMIN
    assert game.in_core(phi)

    # Hand-checkable three-stage Maschler certificate.
    floors = tuple(value[1 << player] for player in range(N))
    gains = tuple(phi[player] - floors[player] for player in range(N))
    assert floors == EXPECTED_FLOORS
    assert gains == EXPECTED_GAINS

    # Stage 1.  The coalition 125 has value zero, so efficiency gives
    # x(3467) <= 0.  If all gains are at least t, then
    # x(3467) >= m_3+m_4+m_6+m_7+4t = -3+4t.  Hence t<=3/4.
    coalition_125 = (1 << 0) | (1 << 1) | (1 << 4)
    coalition_3467 = FULL ^ coalition_125
    assert value[coalition_125] == 0
    assert sum(EXPECTED_FLOORS[player] for player in (2, 3, 5, 6)) == -3
    assert payoff(phi, coalition_3467) == 0
    assert all(gains[player] == F(3, 4) for player in (2, 3, 5, 6))

    # Stage 2.  Once 3,4,6,7 are fixed, their sum is zero.  Tight core
    # constraints 13 and 27 imply x_1>=-3/4 and x_2>=1/4.  Efficiency then
    # gives x_5<=1/2, so its gain is at most 3/2.
    coalition_13 = (1 << 0) | (1 << 2)
    coalition_27 = (1 << 1) | (1 << 6)
    assert value[coalition_13] == value[coalition_27] == 0
    assert sum(phi[player] for player in (2, 3, 5, 6)) == 0
    assert phi[0] == -phi[2] == F(-3, 4)
    assert phi[1] == -phi[6] == F(1, 4)
    assert phi[4] == F(1, 2)
    assert gains[4] == F(3, 2)

    # Stage 3.  After player 5 is fixed, efficiency gives x_1+x_2=-1/2.
    # If their two gains are at least u, then -1/2>=m_1+m_2+2u=-5+2u,
    # so u<=9/4, attained by phi.
    assert sum(phi[player] for player in range(2, N)) == F(1, 2)
    assert phi[0] + phi[1] == F(-1, 2)
    assert gains[0] == gains[1] == F(9, 4)

    slack = [
        payoff(phi, coalition) - value[coalition]
        for coalition in range(1 << N)
    ]
    carrier_differences = {
        coalition: slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    }
    assert set(carrier_differences.values()) == {F(3, 4)}
    assert all(slack[coalition] == 0 for coalition in ETA_SUPPORT)

    # Apply the same degree-three identity to d=x-phi.  The four eta
    # coalitions are phi-tight, and d_i>=0 on S, so efficiency forces d(S)=0.
    balanced_support = {S: 1, **ETA_SUPPORT, 1: 1, 2: 2}
    balanced_degree = [
        sum(
            weight
            for coalition, weight in balanced_support.items()
            if coalition >> player & 1
        )
        for player in range(N)
    ]
    assert balanced_degree == [3] * N
    eta = F(0)

    summary = {
        "status": "exact-rational leximin counterexample verified",
        "n": N,
        "leximin": [str(value) for value in phi],
        "floors": [str(value) for value in floors],
        "gains": [str(value) for value in gains],
        "maschler_strata": [
            {"level": str(level), "players": list(players)}
            for level, players in EXPECTED_STRATA
        ],
        "S": members(S),
        "P": members(P),
        "carrier_differences": {
            str(members(coalition)): str(difference)
            for coalition, difference in carrier_differences.items()
        },
        "gamma_S_at_leximin": "3/4",
        "eta_S_at_leximin": str(eta),
        "carrier_bound_violated_at_leximin": eta < F(3, 4),
        "eta_support_is_leximin_tight": True,
        "balanced_identity_degree": balanced_degree[0],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
