"""Exact checks for a nontrivial one-parameter family of n=7 failures.

For 1/4 < theta <= 1, use generators 0, a, theta*b.  The hand proof in the
paper shows that phi=a/4 is the leximin point and gamma=theta-1/4>eta=0.
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


def verify(theta):
    assert F(1, 4) < theta <= 1
    scaled_b = tuple(theta * value for value in GENERATOR_B)
    generators = (GENERATOR_ZERO, GENERATOR_A, scaled_b)
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
    assert floors == (-3, -2 * theta, 0, -1, -theta, -1, -1)
    gains = tuple(PHI[player] - floors[player] for player in range(N))
    assert gains == (
        F(9, 4), F(1, 4) + 2 * theta, F(3, 4), F(3, 4),
        F(1, 2) + theta, F(3, 4), F(3, 4),
    )
    # These comparisons are precisely the three-stage hand certificate.
    assert F(3, 4) <= F(1, 2) + theta
    assert F(1, 2) + theta <= F(1, 4) + 2 * theta
    assert F(1, 4) + 2 * theta <= F(9, 4)

    slack = tuple(payoff(PHI, coalition) - value[coalition] for coalition in range(1 << N))
    differences = {
        coalition: slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    }
    for coalition, difference in differences.items():
        expected = F(3, 4) if coalition & 1 else theta - F(1, 4)
        assert difference == expected
    gamma = theta - F(1, 4)
    assert gamma > 0

    assert all(value[coalition] == payoff(PHI, coalition) == 0 for coalition in ETA_SUPPORT)
    coalition_135 = (1 << 0) | (1 << 2) | (1 << 4)
    assert value[S] == 0
    assert tuple(payoff(generator, coalition_135) for generator in generators) == (0, 2, 2 * theta)
    eta = F(0)
    return {
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
        "--theta", action="append", default=[],
        help="rational parameter, repeatable (default: 1/3, 1/2, 4/5, 1)",
    )
    args = parser.parse_args()
    parameters = [F(value) for value in args.theta] if args.theta else [F(1, 3), F(1, 2), F(4, 5), F(1)]
    print(json.dumps({
        "status": "exact one-parameter counterexample family verified",
        "range": "1/4 < theta <= 1",
        "formula": "v_theta(T)=min{0,a(T),theta*b(T)}",
        "gamma_formula": "theta-1/4",
        "eta_formula": "0",
        "finite_regression": [verify(theta) for theta in parameters],
    }, indent=2))


if __name__ == "__main__":
    main()
