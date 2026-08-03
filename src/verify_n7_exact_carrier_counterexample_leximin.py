"""Exact-rational leximin check for the sharp seven-player counterexample."""
from __future__ import annotations

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


def main():
    value = [
        F(min(payoff(generator, coalition) for generator in GENERATORS))
        for coalition in range(1 << N)
    ]
    game = Game(N, value)
    phi = tuple(leximin_core_exact(game))
    assert phi == EXPECTED_LEXIMIN
    assert game.in_core(phi)

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
