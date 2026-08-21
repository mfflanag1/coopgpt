#!/usr/bin/env python3
"""Independent rational replay of the PXC91c counterexample.

This verifier imports no project LP, selector, or cover code.  It enumerates
the full and reduced core vertices with a local Fraction eliminator, rebuilds
all coalition minima, and checks the human pinning and cover-uniqueness
arguments used in PXC92.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


N = 7
TOTAL = F(20)
X = (F(6), F(4), F(2), F(2), F(2), F(2), F(2))
Z = (F(29, 7), F(29, 7), F(27, 7), F(27, 7), F(4, 7), F(12, 7), F(12, 7))
Z_REDUCED = (
    F(29, 7), F(29, 7), F(26, 7), F(26, 7),
    F(5, 7), F(13, 7), F(12, 7),
)
ONE_AUX_POINTS = (
    (F(29, 7), F(29, 7), F(27, 7), F(26, 7), F(5, 7), F(12, 7), F(12, 7)),
    (F(29, 7), F(29, 7), F(26, 7), F(27, 7), F(4, 7), F(13, 7), F(12, 7)),
)


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


LMIN = (
    (mask(0, 1, 2), F(12)),
    (mask(0, 1, 3), F(12)),
    (mask(0, 2, 3), F(10)),
)
TOP = (
    (mask(0, 1, 3, 4), F(89, 7)),
    (mask(0, 1, 2, 5), F(97, 7)),
    (mask(1, 6), F(41, 7)),
)
AUX = (
    (mask(0, 1, 2, 6), F(97, 7)),
    (mask(0, 1, 3, 6), F(97, 7)),
)
FULL_CONSTRAINTS = TOP + LMIN + AUX
REDUCED_CONSTRAINTS = LMIN + TOP


def coalition_sum(point: tuple[F, ...], coalition: int) -> F:
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def solve_square(matrix: list[list[F]], rhs: list[F]):
    augmented = [
        [F(value) for value in row] + [F(value)]
        for row, value in zip(matrix, rhs)
    ]
    for column in range(N):
        pivot = next(
            (row for row in range(column, N) if augmented[row][column]), None
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(N):
            if row == column or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                left - scale * right
                for left, right in zip(augmented[row], augmented[column])
            ]
    return tuple(augmented[row][-1] for row in range(N))


def solve_unique(matrix: list[list[F]], rhs: list[F]):
    """Solve a square system of arbitrary dimension, rejecting rank loss."""
    dimension = len(matrix)
    augmented = [
        [F(value) for value in row] + [F(value)]
        for row, value in zip(matrix, rhs)
    ]
    for column in range(dimension):
        pivot = next(
            (row for row in range(column, dimension) if augmented[row][column]),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(dimension):
            if row == column or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                left - scale * right
                for left, right in zip(augmented[row], augmented[column])
            ]
    return tuple(augmented[row][-1] for row in range(dimension))


def vertices(constraints: tuple[tuple[int, F], ...]) -> tuple[tuple[F, ...], ...]:
    inequalities = [
        ([F(int(bool(coalition >> i & 1))) for i in range(N)], bound)
        for coalition, bound in constraints
    ]
    inequalities.extend(
        ([F(int(i == player)) for i in range(N)], F(0)) for player in range(N)
    )
    total_row = [F(1)] * N

    def feasible(point: tuple[F, ...]) -> bool:
        return (
            sum(point, F(0)) == TOTAL
            and all(value >= 0 for value in point)
            and all(
                coalition_sum(point, coalition) >= bound
                for coalition, bound in constraints
            )
        )

    found = set()
    for active in itertools.combinations(range(len(inequalities)), N - 1):
        matrix = [total_row] + [inequalities[index][0] for index in active]
        rhs = [TOTAL] + [inequalities[index][1] for index in active]
        point = solve_square(matrix, rhs)
        if point is not None and feasible(point):
            found.add(point)
    if not found:
        raise AssertionError("independent core vertex set is empty")
    return tuple(sorted(found))


def feasible(point: tuple[F, ...], constraints: tuple[tuple[int, F], ...]) -> bool:
    return (
        sum(point, F(0)) == TOTAL
        and all(value >= 0 for value in point)
        and all(
            coalition_sum(point, coalition) >= bound
            for coalition, bound in constraints
        )
    )


def envelope(core_vertices: tuple[tuple[F, ...], ...]) -> tuple[F, ...]:
    return tuple(
        min(coalition_sum(vertex, coalition) for vertex in core_vertices)
        for coalition in range(1 << N)
    )


def tight_rows(values: tuple[F, ...], point: tuple[F, ...]) -> tuple[int, ...]:
    return tuple(
        coalition for coalition in range(1, (1 << N) - 1)
        if coalition.bit_count() >= 2
        and coalition_sum(point, coalition) == values[coalition]
    )


def check_lmin_pinning(values: tuple[F, ...]) -> None:
    # min_i y_i <= min(y(3456),y(2456))/4 <= 2 from complements of 012,013.
    if values[mask(0, 1, 2)] != 12 or values[mask(0, 1, 3)] != 12:
        raise AssertionError("Lmin complement bounds changed")
    # Equality forces y2,...,y6=2.  Then 023>=10 gives y0>=6 and efficiency
    # gives y0+y1=10, so the second ascending coordinate is at most four.
    if values[mask(0, 2, 3)] != 10:
        raise AssertionError("Lmin ordered-pair pin changed")


def check_reduced_lmax_pinning() -> None:
    # Summing the three cover rows gives 20+y0+2y1 >= 227/7, hence max>=29/7.
    if sum((bound for _, bound in TOP), F(0)) != F(227, 7):
        raise AssertionError("top-cover scalar bound changed")
    if any(coalition_sum(Z_REDUCED, row) != bound for row, bound in TOP):
        raise AssertionError("reduced selector left a top-cover row slack")
    # At equality y0=y1=29/7 and all TOP rows bind.  They imply
    # y6=12/7, y2+y5=39/7, y3+y4=31/7.  The Lmin rows imply
    # y2,y3>=26/7, so the second ceiling is at least 26/7; equality pins all.
    if not all(coalition_sum(Z_REDUCED, row) >= bound for row, bound in LMIN):
        raise AssertionError("reduced selector violates an Lmin row")
    if (Z_REDUCED[6], Z_REDUCED[2] + Z_REDUCED[5], Z_REDUCED[3] + Z_REDUCED[4]) != (
        F(12, 7), F(39, 7), F(31, 7)
    ):
        raise AssertionError("reduced equality-face equations changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    full_vertices = vertices(FULL_CONSTRAINTS)
    reduced_vertices = vertices(REDUCED_CONSTRAINTS)
    full_values = envelope(full_vertices)
    reduced_values = envelope(reduced_vertices)
    if any(full_values[1 << i] for i in range(N)) or any(
        reduced_values[1 << i] for i in range(N)
    ):
        raise AssertionError("singleton normalization changed")
    if not feasible(X, FULL_CONSTRAINTS) or not feasible(Z, FULL_CONSTRAINTS):
        raise AssertionError("full claimed selectors are infeasible")
    if not feasible(X, REDUCED_CONSTRAINTS) or not feasible(
        Z_REDUCED, REDUCED_CONSTRAINTS
    ):
        raise AssertionError("reduced claimed selectors are infeasible")
    check_lmin_pinning(full_values)
    check_lmin_pinning(reduced_values)
    check_reduced_lmax_pinning()

    expected_tight = tuple(sorted(row for row, _ in TOP + AUX))
    if tight_rows(full_values, Z) != expected_tight:
        raise AssertionError("independent z-tight menu changed")

    # If (a,b,c,d,e) weight TOP+Aux in displayed order and eta is the
    # outsider load, players 4,5,2,3,6 give
    # a=eta, b=eta, b+d=eta, a+e=eta, c+d+e=eta.
    # Hence d=e=0 and a=b=c=eta.  Normalization gives 3 eta=1.
    # Variables are (a,b,c,d,e,eta).  The final row is alpha0+alpha1=1,
    # written directly from the two top loads minus 2 eta.
    cover_solution = solve_unique(
        [
            [1, 0, 0, 0, 0, -1],
            [0, 1, 0, 0, 0, -1],
            [0, 1, 0, 1, 0, -1],
            [1, 0, 0, 0, 1, -1],
            [0, 0, 1, 1, 1, -1],
            [2, 2, 1, 2, 2, -2],
        ],
        [F(0), F(0), F(0), F(0), F(0), F(1)],
    )
    if cover_solution != (F(1, 3), F(1, 3), F(1, 3), F(0), F(0), F(1, 3)):
        raise AssertionError(("unique normalized cover changed", cover_solution))
    weights = cover_solution[:5]
    loads = tuple(
        sum(
            (weight for weight, (row, _) in zip(weights, TOP + AUX) if row >> i & 1),
            F(0),
        )
        for i in range(N)
    )
    if loads != (F(2, 3), F(1), F(1, 3), F(1, 3), F(1, 3), F(1, 3), F(1, 3)):
        raise AssertionError("unique-cover load vector changed")

    tangent = tuple(a - b for a, b in zip(Z_REDUCED, Z))
    if sum(tangent, F(0)) or tangent[:2] != (F(0), F(0)) or tangent[2:4] != (
        F(-1, 7), F(-1, 7)
    ):
        raise AssertionError("later-stage improving tangent changed")

    # Each zero-cover auxiliary supplies one missing lower bound on the
    # equality face; both are tight at Z and violated by the reduced selector.
    if tuple(coalition_sum(Z_REDUCED, row) - bound for row, bound in AUX) != (
        F(-1, 7), F(-1, 7)
    ):
        raise AssertionError("auxiliary-row necessity changed")
    for index, point in enumerate(ONE_AUX_POINTS):
        kept = REDUCED_CONSTRAINTS + (AUX[index],)
        missing_row, missing_bound = AUX[1 - index]
        if not feasible(point, kept) or not (
            tuple(sorted(point, reverse=True)) < tuple(sorted(Z, reverse=True))
        ) or coalition_sum(point, missing_row) >= missing_bound:
            raise AssertionError(("one-auxiliary witness changed", index, point))

    payload = {
        "claim": "independent exact PXC91c refutation",
        "full_vertex_count": len(full_vertices),
        "reduced_vertex_count": len(reduced_vertices),
        "full_singleton_normalized": True,
        "reduced_singleton_normalized": True,
        "complete_lmin_human_certificate": True,
        "reduced_lmax_human_certificate": True,
        "all_z_tight_rows": list(expected_tight),
        "unique_normalized_cover_weights": [str(value) for value in weights],
        "reduced_lmax": [str(value) for value in Z_REDUCED],
        "later_stage_tangent": [str(value) for value in tangent],
        "two_zero_weight_auxiliaries_necessary": True,
        "one_auxiliary_improving_witnesses": [
            [str(value) for value in point] for point in ONE_AUX_POINTS
        ],
        "scope": "independent arithmetic refutation at n=7; no n<=6 exclusion",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
