"""Solver-free verifier for the sharp seven-player exact counterexample.

The game is the lower envelope of three integer allocations with equal total,
one of which is the zero reference point.
All assertions use integer arithmetic.  Coalition masks use player i in bit
i-1, with S={1,2,3} and P={4,5,6,7}.
"""
from __future__ import annotations

import sys

if sys.flags.optimize:
    raise SystemExit(
        "This verifier requires assertions enabled; run without -O, -OO, or PYTHONOPTIMIZE."
    )

import json
from fractions import Fraction


N = 7
FULL = (1 << N) - 1
S = (1 << 3) - 1
P = FULL ^ S

GENERATOR_A = (-3, 1, 3, -1, 2, -1, -1)
GENERATOR_B = (3, -2, 0, -1, -1, -1, 2)
GENERATOR_ZERO = (0,) * N
GENERATORS = (GENERATOR_ZERO, GENERATOR_A, GENERATOR_B)

# Deleting S and the target-singleton floor terms from the degree-three
# balanced identity leaves this zero-cost eta dual.
ETA_SUPPORT = {
    61: 1,   # 13456
    88: 1,   # 457
    108: 1,  # 3467
    112: 1,  # 567
}
TARGET_FLOORS = (1, 2, 0)
RHO = 2


def members(mask):
    return [player + 1 for player in range(N) if mask >> player & 1]


def payoff(allocation, coalition):
    return sum(
        allocation[player]
        for player in range(N)
        if coalition >> player & 1
    )


def incidence_rank(masks):
    matrix = [
        [Fraction(int(mask >> player & 1)) for player in range(N)]
        for mask in masks
    ]
    rank = 0
    for column in range(N):
        pivot = next(
            (row for row in range(rank, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][column]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or matrix[row][column] == 0:
                continue
            multiple = matrix[row][column]
            matrix[row] = [
                value - multiple * pivot_entry
                for value, pivot_entry in zip(matrix[row], matrix[rank])
            ]
        rank += 1
    return rank


def main():
    assert all(sum(generator) == 0 for generator in GENERATORS)

    value = tuple(
        min(payoff(generator, coalition) for generator in GENERATORS)
        for coalition in range(1 << N)
    )
    slack = tuple(-coalition_value for coalition_value in value)
    assert value[0] == value[FULL] == 0

    # Every generator is in the core and at least one generator attains the
    # lower envelope at each coalition.  Hence every coalition has a tight core
    # point and the game is exact; in particular, zero is the reference point.
    assert all(coalition_value <= 0 for coalition_value in value)
    for generator in GENERATORS:
        assert payoff(generator, FULL) == value[FULL]
        assert all(
            payoff(generator, coalition) >= value[coalition]
            for coalition in range(1 << N)
        )
    assert all(
        value[coalition]
        in tuple(payoff(generator, coalition) for generator in GENERATORS)
        for coalition in range(1 << N)
    )

    carrier_differences = {
        coalition: slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    }
    assert set(carrier_differences.values()) == {1}
    gamma = 1

    eta_degree = [
        sum(
            weight
            for coalition, weight in ETA_SUPPORT.items()
            if coalition >> player & 1
        )
        for player in range(N)
    ]
    assert eta_degree == [1, 0, 2, 3, 3, 3, 3]
    assert [
        eta_degree[player] + TARGET_FLOORS[player]
        for player in range(3)
    ] == [RHO] * 3
    assert eta_degree[3:] == [1 + RHO] * 4
    assert all(slack[coalition] == 0 for coalition in ETA_SUPPORT)
    assert sum(
        weight * slack[coalition]
        for coalition, weight in ETA_SUPPORT.items()
    ) == 0

    # Incidence identity:
    #   1_S + 1_13456 + 1_457 + 1_3467 + 1_567 + e_1 + 2e_2 = 3 1_N.
    # For any core allocation x nonnegative on S, every term on the left has
    # nonnegative payoff: the four eta coalitions have value zero.  Efficiency
    # makes the right side zero, so x(S)=0.  Since x=0 is feasible, eta_S=0.
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
    assert incidence_rank(balanced_support) == N
    eta = 0

    summary = {
        "status": "sharp exact seven-player counterexample verified without optimization",
        "n": N,
        "generators": [list(generator) for generator in GENERATORS],
        "game": "v(T)=min{0,a(T),b(T)}",
        "exact": True,
        "reference_core_point": [0] * N,
        "S": members(S),
        "P": members(P),
        "carrier_differences": {
            str(members(coalition)): difference
            for coalition, difference in carrier_differences.items()
        },
        "gamma_S": gamma,
        "eta_S": eta,
        "carrier_bound_violated": eta < gamma,
        "eta_dual": {
            "rho": RHO,
            "target_floors": list(TARGET_FLOORS),
            "support": [
                {"coalition": members(coalition), "coefficient": weight}
                for coalition, weight in ETA_SUPPORT.items()
            ],
            "cost": 0,
        },
        "balanced_identity_degree": balanced_degree[0],
        "balanced_support_incidence_rank": N,
        "sharpness": "the exact carrier theorem holds through n=6 and fails at n=7",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
