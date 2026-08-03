"""Solver-free structural classification of the n=7 counterexample."""
from __future__ import annotations

import json

from verify_n7_exact_carrier_counterexample import (
    GENERATOR_A,
    GENERATOR_B,
    GENERATOR_ZERO,
    GENERATORS,
    N,
    incidence_rank,
    members,
    payoff,
)


FULL = (1 << N) - 1
BALANCED_FACE = (15, 19, 39, 61, 66, 88, 108, 112)


def main():
    value = tuple(
        min(payoff(generator, coalition) for generator in GENERATORS)
        for coalition in range(1 << N)
    )

    # These eight zero-valued coalitions form a degree-four balanced
    # collection.  Every core point is therefore tight on every one of them.
    assert all(value[coalition] == 0 for coalition in BALANCED_FACE)
    degree = [
        sum(int(coalition >> player & 1) for coalition in BALANCED_FACE)
        for player in range(N)
    ]
    assert degree == [4] * N
    assert incidence_rank(BALANCED_FACE) == 5
    assert all(
        payoff(generator, coalition) == 0
        for generator in (GENERATOR_A, GENERATOR_B)
        for coalition in BALANCED_FACE
    )
    # Rank five in R^7 leaves a two-dimensional nullspace, and a,b are
    # independent members.  Hence every core point has form alpha*a+beta*b.
    assert GENERATOR_A != GENERATOR_B
    assert GENERATOR_A[0] * GENERATOR_B[2] - GENERATOR_A[2] * GENERATOR_B[0] != 0

    # In that plane the core constraints at 3, 13, and 4 respectively give
    # alpha>=0, beta>=0, and alpha+beta<=1.  Conversely the three vertices are
    # core points, so Core(v)=conv{0,a,b}.
    coalition_3 = 1 << 2
    coalition_13 = (1 << 0) | (1 << 2)
    coalition_4 = 1 << 3
    assert value[coalition_3] == 0
    assert payoff(GENERATOR_A, coalition_3) == 3
    assert payoff(GENERATOR_B, coalition_3) == 0
    assert value[coalition_13] == 0
    assert payoff(GENERATOR_A, coalition_13) == 0
    assert payoff(GENERATOR_B, coalition_13) == 3
    assert value[coalition_4] == -1
    assert payoff(GENERATOR_A, coalition_4) == payoff(GENERATOR_B, coalition_4) == -1

    # Each triangle vertex uniquely minimizes a coalition, so no
    # lower-envelope representation by core allocations can use fewer than
    # three generators.
    unique_coalitions = {
        "a": 1,       # singleton 1
        "b": 2,       # singleton 2
        "zero": 7,    # coalition 123
    }
    vertices = (GENERATOR_A, GENERATOR_B, GENERATOR_ZERO)
    expected_minimizers = {"a": 0, "b": 1, "zero": 2}
    for label, coalition in unique_coalitions.items():
        payoffs = tuple(payoff(vertex, coalition) for vertex in vertices)
        minimum = min(payoffs)
        assert [index for index, item in enumerate(payoffs) if item == minimum] == [expected_minimizers[label]]

    # The carrier-failure target S=123 cannot be bumped while preserving
    # exactness.  Coalition 135 is uniquely tight at zero, and zero has
    # x(123)=v(123)=0, so the exact bump capacity is zero.
    target = 7
    coalition_135 = (1 << 0) | (1 << 2) | (1 << 4)
    assert value[target] == 0
    assert tuple(payoff(vertex, coalition_135) for vertex in vertices) == (2, 2, 0)

    # The blocking face is forced by the tight balanced geometry.  In
    # incidence-vector form,
    #   1_135 - 2*1_123 = 1_13456 + 1_457 + 1_567 - 2*1_N.
    # Thus every efficient allocation nonnegative on the three zero-valued
    # right-hand faces satisfies x(135)>=2*x(123).  A point of F_135 has both
    # sides zero, so it cannot support a positive bump of 123.
    robust_blocking_faces = (61, 88, 112)  # 13456, 457, 567
    for player in range(N):
        left = int(coalition_135 >> player & 1) - 2 * int(target >> player & 1)
        right = (
            sum(int(coalition >> player & 1) for coalition in robust_blocking_faces)
            - 2
        )
        assert left == right
    assert all(value[coalition] == 0 for coalition in robust_blocking_faces)

    print(json.dumps({
        "status": "solver-free structural classification verified",
        "balanced_zero_face": [members(mask) for mask in BALANCED_FACE],
        "balanced_degree": 4,
        "incidence_rank": 5,
        "core_dimension": 2,
        "core": "conv{0,a,b}",
        "minimum_lower_envelope_generator_count": 3,
        "exact_bump_capacity_at_S_123": 0,
        "capacity_blocking_face": members(coalition_135),
        "certificate_intrinsic_blocking_faces": [
            members(coalition) for coalition in robust_blocking_faces
        ],
        "blocking_inequality": "x(135) >= 2*x(123) for every core point",
        "indispensable_generator_coalitions": {
            label: members(mask) for label, mask in unique_coalitions.items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
