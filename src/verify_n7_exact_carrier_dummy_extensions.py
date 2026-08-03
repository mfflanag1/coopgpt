"""Exact replay of null-player extensions of the n=7 counterexample.

The proof is dimension-free: appending any number of zero coordinates to all
three generators gives v_k(T)=v(T cap [7]).  The finite loop below checks the
identities through a user-selected dimension as a regression test.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F

from verify_n7_exact_carrier_counterexample import GENERATORS, payoff


BASE_N = 7
BASE_FULL = (1 << BASE_N) - 1
S = (1 << 3) - 1
BASE_P = BASE_FULL ^ S
BASE_PHI = (F(-3, 4), F(1, 4), F(3, 4), F(-1, 4), F(1, 2), F(-1, 4), F(-1, 4))


def base_value(mask):
    return min(payoff(generator, mask) for generator in GENERATORS)


def extended_value(mask):
    return base_value(mask & BASE_FULL)


def extended_payoff(allocation, mask):
    return sum(value for player, value in enumerate(allocation) if mask >> player & 1)


def verify(n):
    assert n >= BASE_N
    full = (1 << n) - 1
    outside = full ^ S
    generators = tuple(
        tuple(F(value) for value in generator) + (F(0),) * (n - BASE_N)
        for generator in GENERATORS
    )
    phi = BASE_PHI + (F(0),) * (n - BASE_N)

    # Lower-envelope exactness: every coalition is attained by an extended
    # generator, and every generator is an efficient core allocation.
    for coalition in range(1 << n):
        value = extended_value(coalition)
        generator_payoffs = tuple(
            extended_payoff(generator, coalition) for generator in generators
        )
        assert value == min(generator_payoffs)
        assert value in generator_payoffs
        assert extended_payoff(phi, coalition) >= value
    assert all(extended_payoff(generator, full) == 0 for generator in generators)

    # All new players are null and fixed at zero in the core: singleton
    # rationality gives x_d>=0, while the old-grand-coalition constraint and
    # efficiency give sum_d x_d<=0.
    for player in range(BASE_N, n):
        assert extended_value(1 << player) == 0
    assert extended_value(BASE_FULL) == extended_value(full) == 0

    # Null players add fixed zero gains ahead of the three original positive
    # Maschler strata, so the original leximin coordinates are unchanged.
    floors = tuple(F(extended_value(1 << player)) for player in range(n))
    gains = tuple(phi[player] - floors[player] for player in range(n))
    assert gains[:BASE_N] == (F(9, 4), F(9, 4), F(3, 4), F(3, 4), F(3, 2), F(3, 4), F(3, 4))
    assert gains[BASE_N:] == (F(0),) * (n - BASE_N)

    slack = tuple(extended_payoff(phi, coalition) - extended_value(coalition) for coalition in range(1 << n))
    differences = tuple(slack[outside | coalition] - slack[coalition] for coalition in range(1, S))
    assert differences == (F(3, 4),) * 6

    return {
        "n": n,
        "new_null_players": n - BASE_N,
        "gamma_S_at_leximin": "3/4",
        "eta_S_at_leximin": "0",
        "exact": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=12)
    args = parser.parse_args()
    assert args.max_n >= BASE_N
    checks = [verify(n) for n in range(BASE_N, args.max_n + 1)]
    print(json.dumps({
        "status": "null-player extension identities verified",
        "theorem": "the exact carrier inequality fails for every n>=7",
        "finite_regression": checks,
    }, indent=2))


if __name__ == "__main__":
    main()
