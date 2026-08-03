"""Solver-free verifier for the sharp-dimension exact counterexample with
four target players and three outside players.

The game is the lower envelope of three integer allocations.  At the core
reference zero it has gamma=1 and eta=0.  This complements the leximin
counterexample of shape 3+4 and proves that an outside set of size four is not
minimal among seven-player arbitrary-reference obstructions.
"""
from __future__ import annotations

import json
from fractions import Fraction as F


N = 7
FULL = (1 << N) - 1
S = (1 << 4) - 1
P = FULL ^ S
ZERO = (0, 0, 0, 0, 0, 0, 0)
A = (-4, 1, 2, 2, -3, 1, 1)
B = (2, -1, 0, 0, 1, -1, -1)
GENERATORS = (ZERO, A, B)

# S and four zero-valued core faces, together with the artificial target-floor
# columns e_1 and 3e_2, form the eta certificate.
ETA_SUPPORT = {
    S: 1,
    1: 1,
    2: 3,
    22: 1,   # 235
    56: 2,   # 456
    88: 2,   # 457
    101: 3,  # 1367
}


def payoff(allocation, coalition):
    return sum(
        allocation[player] for player in range(N) if coalition >> player & 1
    )


def members(mask):
    return [player + 1 for player in range(N) if mask >> player & 1]


def incidence_rank(masks):
    matrix = [
        [F(int(mask >> player & 1)) for player in range(N)]
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
        value = matrix[rank][column]
        matrix[rank] = [entry / value for entry in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or matrix[row][column] == 0:
                continue
            multiple = matrix[row][column]
            matrix[row] = [
                entry - multiple * pivot_entry
                for entry, pivot_entry in zip(matrix[row], matrix[rank])
            ]
        rank += 1
    return rank


def main():
    assert all(sum(generator) == 0 for generator in GENERATORS)
    value = tuple(
        min(payoff(generator, coalition) for generator in GENERATORS)
        for coalition in range(1 << N)
    )

    # Lower-envelope exactness: every generator is an efficient core point and
    # some generator attains every coalition value.
    for generator in GENERATORS:
        assert payoff(generator, FULL) == 0
        assert all(
            payoff(generator, coalition) >= value[coalition]
            for coalition in range(1 << N)
        )
    assert all(
        value[coalition]
        in tuple(payoff(generator, coalition) for generator in GENERATORS)
        for coalition in range(1 << N)
    )

    slack = tuple(-value[coalition] for coalition in range(1 << N))
    carrier_differences = {
        coalition: slack[P | coalition] - slack[coalition]
        for coalition in range(1, S)
    }
    assert set(carrier_differences.values()) == {1}
    gamma = 1

    degree = [
        sum(
            weight for coalition, weight in ETA_SUPPORT.items()
            if coalition >> player & 1
        )
        for player in range(N)
    ]
    assert degree == [5] * N
    assert incidence_rank(ETA_SUPPORT) == N
    assert value[S] == 0
    zero_faces = (22, 56, 88, 101)
    assert all(value[coalition] == 0 for coalition in zero_faces)

    # For any core point x with x_i>=0 on S, every term in the balanced
    # identity is nonnegative.  Its weighted sum equals 5*x(N)=0, hence x(S)=0.
    # The zero generator is feasible, so eta=0.
    eta = 0
    assert sum(
        weight * slack[coalition]
        for coalition, weight in ETA_SUPPORT.items()
        if coalition not in (S, 1, 2)
    ) == 0

    print(json.dumps({
        "status": "solver-free exact outside-triple carrier counterexample verified",
        "n": N,
        "generators": [list(generator) for generator in GENERATORS],
        "game": "v(T)=min{0,A(T),B(T)}",
        "reference_core_point": [0] * N,
        "S": members(S),
        "P": members(P),
        "gamma_S": gamma,
        "eta_S": eta,
        "carrier_bound_violated": eta < gamma,
        "balanced_degree": degree[0],
        "balanced_support_incidence_rank": incidence_rank(ETA_SUPPORT),
        "eta_balanced_support": [
            {"coalition": members(coalition), "coefficient": weight}
            for coalition, weight in ETA_SUPPORT.items()
        ],
        "scope": (
            "counterexample at the core reference zero; leximin behavior is "
            "checked separately"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
