#!/usr/bin/env python3
"""Independent exact replay of the split-matching class-B counterexample.

Unlike audit_class_b_support_alternative.py, this verifier does not use the
project's exact LP or selector implementations.  It enumerates the vertices
of the defining core polytope using a local Fraction Gaussian eliminator,
reconstructs all coalition minima from those vertices, and checks the short
human Lmin/Lmax proofs and the conjecture-refuting gaps directly.
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
Z = (F(31, 7), F(31, 7), F(23, 7), F(23, 7), F(13, 7), F(13, 7), F(6, 7))


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


CONSTRAINTS = (
    (mask(0, 1, 3, 4), F(14)),
    (mask(0, 1, 2, 5), F(14)),
    (mask(1, 6), F(37, 7)),
    (mask(0, 1, 2), F(12)),
    (mask(0, 1, 3), F(12)),
    (mask(0, 2, 3), F(10)),
    (mask(0, 1, 2, 6), F(13)),
    (mask(0, 1, 3, 6), F(13)),
)


def coalition_sum(point: tuple[F, ...], coalition: int) -> F:
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def solve_square(matrix: list[list[F]], rhs: list[F]) -> tuple[F, ...] | None:
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    for column in range(N):
        pivot = next((row for row in range(column, N) if augmented[row][column]), None)
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


def feasible(point: tuple[F, ...]) -> bool:
    return (
        sum(point, F(0)) == TOTAL
        and all(value >= 0 for value in point)
        and all(coalition_sum(point, coalition) >= bound for coalition, bound in CONSTRAINTS)
    )


def vertices() -> tuple[tuple[F, ...], ...]:
    # The efficiency hyperplane has dimension six.  A vertex has six
    # independent active inequalities among the eight coalition rows and
    # seven nonnegativity rows.
    inequalities = [
        ([F(int(bool(coalition >> i & 1))) for i in range(N)], bound)
        for coalition, bound in CONSTRAINTS
    ]
    inequalities.extend(
        ([F(int(i == player)) for i in range(N)], F(0)) for player in range(N)
    )
    found = set()
    total_row = [F(1)] * N
    for active in itertools.combinations(range(len(inequalities)), N - 1):
        matrix = [total_row] + [inequalities[index][0] for index in active]
        rhs = [TOTAL] + [inequalities[index][1] for index in active]
        point = solve_square(matrix, rhs)
        if point is not None and feasible(point):
            found.add(point)
    if not found:
        raise AssertionError("independent vertex enumeration found an empty core")
    return tuple(sorted(found))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    core_vertices = vertices()
    values = tuple(
        min(coalition_sum(vertex, coalition) for vertex in core_vertices)
        for coalition in range(1 << N)
    )
    if any(values[1 << player] != 0 for player in range(N)):
        raise AssertionError("independent replay lost singleton exactness")
    if not feasible(X) or not feasible(Z):
        raise AssertionError("a claimed selector left the defining core")

    # Human Lmin proof.  The complements of 012 and 013 have sums at most
    # eight, so the smallest coordinate is at most two.  Equality forces
    # players 2..6 to equal two.  Then efficiency gives y0+y1=10 and 023>=10
    # gives y0>=6, so the next coordinate is at most four.  X attains every
    # bound and is consequently the unique increasing-lexicographic maximum.
    if values[mask(0, 1, 2)] != 12 or values[mask(0, 1, 3)] != 12 or values[mask(0, 2, 3)] != 10:
        raise AssertionError("Lmin pinning rows changed")

    # Human Lmax proof.  Adding the first three defining rows yields
    # TOTAL+y0+2y1 >= 233/7, hence max(y)>=31/7.  Equality at that ceiling
    # pins y0=y1=31/7 and all three rows.  Row 16 pins y6=6/7; rows 0126 and
    # 0136 then pin y2=y3=23/7; efficiency pins y4=y5=13/7.
    if F(14) + F(14) + F(37, 7) - TOTAL != F(93, 7):
        raise AssertionError("top-cover arithmetic changed")
    if any(coalition_sum(Z, coalition) != bound for coalition, bound in CONSTRAINTS[:3]):
        raise AssertionError("matching top support is not tight at Z")
    if coalition_sum(Z, mask(0, 1, 2, 6)) != 13 or coalition_sum(Z, mask(0, 1, 3, 6)) != 13:
        raise AssertionError("second-stage Lmax pins changed")

    pair = mask(0, 1)
    heavy_block = mask(1, 4, 5, 6)
    doubles = tuple(sorted({
        mask(0, 1, other, outsider)
        for other in (2, 3)
        for outsider in (4, 5, 6)
    }))
    pair_gap = coalition_sum(Z, pair) - values[pair]
    heavy_gap = coalition_sum(Z, heavy_block) - values[heavy_block]
    double_gaps = tuple(coalition_sum(Z, row) - values[row] for row in doubles)
    if pair_gap != F(6, 7) or heavy_gap != F(26, 7) or double_gaps != (
        F(2), F(0), F(0), F(2), F(0), F(0)
    ):
        raise AssertionError(("special-row gaps changed", pair_gap, heavy_gap, double_gaps))

    # The clean rooted rows 012, 013 and 023 with weights 1/2 give the
    # saturated g=3 packet and zero decoration.  The n=7 cardinality slack is
    # zero.  Gains are (3,9,9)/7 and the root loss is 11/7.
    gains = (Z[1] - X[1], Z[2] - X[2], Z[3] - X[3])
    root_loss = X[0] - Z[0]
    penalty = sum(gains, F(0)) - max(gains) - root_loss
    packet_margin = -penalty
    if gains != (F(3, 7), F(9, 7), F(9, 7)) or packet_margin != F(-1, 7):
        raise AssertionError(("packet computation changed", gains, root_loss, packet_margin))

    # The new three-row over-cover is checked directly.
    matching_rows = CONSTRAINTS[:3]
    loads = tuple(
        sum((F(1, 3) for coalition, _ in matching_rows if coalition >> player & 1), F(0))
        for player in range(N)
    )
    if loads != (F(2, 3), F(1), F(1, 3), F(1, 3), F(1, 3), F(1, 3), F(1, 3)):
        raise AssertionError(("matching over-cover loads changed", loads))

    overlap = sum((min(x, z) for x, z in zip(X, Z)), F(0))
    target = F(7, 12) * TOTAL
    if overlap != 17 or overlap - target != F(16, 3):
        raise AssertionError(("hybrid safety margin changed", overlap, target))

    payload = {
        "claim": "independent exact replay of the s=2 class-B closure counterexample",
        "vertex_count": len(core_vertices),
        "singleton_normalized": True,
        "lmin_human_certificate": True,
        "lmax_human_certificate": True,
        "packet_margin": "-1/7",
        "top_pair_gap": "6/7",
        "heavy_block_gap": "26/7",
        "double_costar_gaps": [str(value) for value in double_gaps],
        "matching_cover": {
            "weights": ["1/3", "1/3", "1/3"],
            "eta": "1/3",
            "alpha": ["1/3", "2/3"],
            "theta": "2/3"
        },
        "overlap": "17",
        "hybrid_target": "35/3",
        "hybrid_margin": "16/3",
        "scope": "refutes the PXC78-or-tight-top-pair selection claim, not the hybrid-overlap theorem"
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
