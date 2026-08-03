"""Exact checks for a nontrivial two-parameter family of n=7 failures.

Use generators 0, a, kappa*a+theta*b with
    kappa>=0, theta-2*kappa>1/4, kappa+theta<=1.
The hand proof in the paper shows that phi=a/4 is the leximin point and
gamma=theta-2*kappa-1/4>eta=0.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F

from verify_n7_exact_carrier_counterexample import (
    ETA_SUPPORT,
    FULL,
    GENERATOR_A,
    GENERATOR_B,
    GENERATOR_ZERO,
    N,
    P,
    S,
    members,
    payoff,
)


PHI = tuple(F(value, 4) for value in GENERATOR_A)


def verify(kappa, theta):
    assert kappa >= 0
    assert theta - 2 * kappa > F(1, 4)
    assert kappa + theta <= 1
    tilted_b = tuple(
        kappa * a_value + theta * b_value
        for a_value, b_value in zip(GENERATOR_A, GENERATOR_B)
    )
    generators = (GENERATOR_ZERO, GENERATOR_A, tilted_b)
    value = tuple(
        min(payoff(generator, coalition) for generator in generators)
        for coalition in range(1 << N)
    )
    assert all(sum(generator) == 0 for generator in generators)
    assert all(payoff(PHI, coalition) >= value[coalition] for coalition in range(1 << N))
    assert all(
        value[coalition] in tuple(payoff(generator, coalition) for generator in generators)
        for coalition in range(1 << N)
    )

    floors = tuple(value[1 << player] for player in range(N))
    assert floors == (
        -3, kappa - 2 * theta, 0, -1, 2 * kappa - theta, -1, -1,
    )
    gains = tuple(PHI[player] - floors[player] for player in range(N))
    assert gains == (
        F(9, 4), F(1, 4) - kappa + 2 * theta, F(3, 4), F(3, 4),
        F(1, 2) - 2 * kappa + theta, F(3, 4), F(3, 4),
    )
    # These comparisons are precisely the three-stage hand certificate.
    assert F(3, 4) < F(1, 2) - 2 * kappa + theta
    assert F(1, 2) - 2 * kappa + theta < F(1, 4) - kappa + 2 * theta
    assert F(1, 4) - kappa + 2 * theta <= F(9, 4)

    slack = tuple(payoff(PHI, coalition) - value[coalition] for coalition in range(1 << N))
    differences = {
        coalition: slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    }
    for coalition, difference in differences.items():
        if coalition & 1:
            expected = F(3, 4)
        elif coalition == 4:
            expected = theta - 2 * kappa - F(1, 4)
        else:
            expected = kappa + theta - F(1, 4)
        assert difference == expected
    gamma = theta - 2 * kappa - F(1, 4)
    assert gamma > 0

    assert all(value[coalition] == payoff(PHI, coalition) == 0 for coalition in ETA_SUPPORT)
    coalition_135 = (1 << 0) | (1 << 2) | (1 << 4)
    assert value[S] == 0
    assert tuple(payoff(generator, coalition_135) for generator in generators) == (
        0, 2, 2 * (kappa + theta),
    )
    eta = F(0)
    return {
        "kappa": str(kappa),
        "theta": str(theta),
        "leximin": [str(value) for value in PHI],
        "gamma": str(gamma),
        "eta": str(eta),
        "exact_bump_capacity_at_S_123": "0",
        "violated": eta < gamma,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parameter", action="append", default=[],
        help="repeatable rational pair kappa,theta",
    )
    args = parser.parse_args()
    parameters = (
        [tuple(F(value) for value in item.split(",")) for item in args.parameter]
        if args.parameter else
        [(F(0), F(1, 3)), (F(0), F(1, 2)), (F(1, 20), F(1, 2)),
         (F(1, 10), F(3, 4)), (F(0), F(1))]
    )
    assert all(len(pair) == 2 for pair in parameters)
    print(json.dumps({
        "status": "exact two-parameter counterexample family verified",
        "range": "kappa>=0, theta-2*kappa>1/4, kappa+theta<=1",
        "formula": "v_(kappa,theta)(T)=min{0,a(T),(kappa*a+theta*b)(T)}",
        "gamma_formula": "theta-2*kappa-1/4",
        "eta_formula": "0",
        "finite_regression": [verify(kappa, theta) for kappa, theta in parameters],
    }, indent=2))


if __name__ == "__main__":
    main()
