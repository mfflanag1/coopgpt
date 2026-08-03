"""Exact checks for the two-parameter outside-triple leximin family."""
from __future__ import annotations

import json
from fractions import Fraction as F

if not __debug__:
    raise RuntimeError("certificate verification must not run with Python -O")

from verify_n7_exact_carrier_outside_triple_counterexample import (
    A,
    B,
    FULL,
    N,
    P,
    S,
    ZERO,
    payoff,
)


PHI = tuple(F(coordinate, 3) for coordinate in A)
ZERO_FACES = (48, 84, 88, 109)  # 56,357,457,13467


def verify(kappa, theta):
    assert kappa >= 0
    assert theta - 3 * kappa > F(1, 3)
    assert kappa + theta <= 1
    deformed = tuple(
        kappa * F(a) + theta * F(b) for a, b in zip(A, B)
    )
    generators = (tuple(map(F, ZERO)), tuple(map(F, A)), deformed)
    assert all(sum(generator) == 0 for generator in generators)
    value = tuple(
        min(payoff(generator, coalition) for generator in generators)
        for coalition in range(1 << N)
    )
    assert all(
        payoff(generator, coalition) >= value[coalition]
        for generator in generators for coalition in range(1 << N)
    )
    assert all(
        value[coalition]
        in tuple(payoff(generator, coalition) for generator in generators)
        for coalition in range(1 << N)
    )
    assert all(
        payoff(PHI, coalition) >= value[coalition]
        for coalition in range(1 << N)
    )

    floors = tuple(value[1 << player] for player in range(N))
    assert floors == (
        F(-4),
        kappa - theta,
        F(0),
        F(0),
        F(-1),
        kappa - theta,
        F(-1),
    )
    gains = tuple(PHI[player] - floors[player] for player in range(N))
    assert all(gains[player] == F(2, 3) for player in (2, 3, 4, 6))
    assert gains[1] == gains[5] == theta - kappa + F(1, 3) > F(2, 3)
    assert gains[0] == F(8, 3) >= gains[1]

    # The same three coalitional bounds give the Maschler stages.
    assert value[43] == value[39] == value[13] == 0  # 1246,1236,134
    assert payoff(PHI, 84) == payoff(PHI, 88) == payoff(PHI, 13) == 0

    slack = tuple(
        payoff(PHI, coalition) - value[coalition]
        for coalition in range(1 << N)
    )
    differences = tuple(
        slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    )
    gamma = theta - 3 * kappa - F(1, 3)
    assert min(differences) == gamma > 0
    assert all(slack[coalition] == 0 for coalition in ZERO_FACES)

    # The degree-four identity from the base example is unchanged and all its
    # coalition faces remain phi-tight, hence eta=0.
    eta = F(0)
    return {
        "kappa": str(kappa),
        "theta": str(theta),
        "deformed_generator": [str(value) for value in deformed],
        "floors": [str(value) for value in floors],
        "gamma": str(gamma),
        "eta": str(eta),
        "violated": eta < gamma,
        "carrier_difference_values": sorted({str(value) for value in differences}),
    }


def main():
    parameters = (
        (F(0), F(1)),
        (F(0), F(1, 2)),
        (F(1, 20), F(1, 2)),
        (F(1, 20), F(3, 4)),
        (F(1, 10), F(9, 10)),
    )
    checks = [verify(kappa, theta) for kappa, theta in parameters]
    print(json.dumps({
        "status": "exact outside-triple two-parameter leximin family verified",
        "parameter_region": (
            "kappa>=0, theta-3*kappa>1/3, kappa+theta<=1"
        ),
        "leximin": [str(value) for value in PHI],
        "gamma_formula": "theta-3*kappa-1/3",
        "eta": "0",
        "interpretation": (
            "a relatively open two-dimensional wedge of exact seven-player "
            "leximin counterexamples with three outside players"
        ),
        "checks": checks,
    }, indent=2))


if __name__ == "__main__":
    main()
