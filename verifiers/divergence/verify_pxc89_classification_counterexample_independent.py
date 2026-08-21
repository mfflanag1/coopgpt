#!/usr/bin/env python3
"""Independent exact replay of the PXC89 four-arm counterexample.

This verifier imports no project LP or selector code.  It enumerates the core
vertices using a local Fraction eliminator, reconstructs every coalition
minimum, checks human selector certificates, and separately expands the
direct-packet and split-matching predicates.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


N = 7
TOTAL = F(20)
TARGET = F(7, 12)
X = (F(6), F(4), F(2), F(2), F(2), F(2), F(2))
Z = tuple(F(value, 7) for value in (29, 29, 28, 28, 8, 9, 9))


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


TOP_ROWS = (23, 27, 39, 75, 114)
TOP_BOUNDS = (F(94, 7), F(94, 7), F(95, 7), F(95, 7), F(55, 7))
TOP_WEIGHTS = (F(1, 7), F(1, 7), F(2, 7), F(2, 7), F(1, 7))
CONSTRAINTS = tuple(zip(TOP_ROWS, TOP_BOUNDS)) + (
    (mask(0, 1, 2), F(12)),
    (mask(0, 1, 3), F(12)),
    (mask(0, 2, 3), F(10)),
)


def coalition_sum(point: tuple[F, ...], coalition: int) -> F:
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def solve_square(matrix: list[list[F]], rhs: list[F]):
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
        and all(coalition_sum(point, row) >= bound for row, bound in CONSTRAINTS)
    )


def vertices() -> tuple[tuple[F, ...], ...]:
    inequalities = [
        ([F(int(bool(row >> i & 1))) for i in range(N)], bound)
        for row, bound in CONSTRAINTS
    ]
    inequalities.extend(
        ([F(int(i == player)) for i in range(N)], F(0)) for player in range(N)
    )
    total_row = [F(1)] * N
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


def direct_packet_exists(x: tuple[F, ...], z: tuple[F, ...]) -> bool:
    gainers = tuple(i for i in range(N) if z[i] > x[i])
    nongainers = tuple(i for i in range(N) if z[i] <= x[i])
    for h_size in range(1, len(nongainers)):
        for h_set in itertools.combinations(nongainers, h_size):
            p_set = tuple(i for i in nongainers if i not in h_set)
            p, g, h = len(p_set), len(gainers), len(h_set)
            q = g + h
            for packet_size in range(g):
                for packet in itertools.combinations(gainers, packet_size):
                    denominator = p + g - packet_size
                    base = F(1) - F(g * p, q * denominator)
                    if base < TARGET:
                        continue
                    high_z = sum((z[i] for i in gainers + h_set), F(0)) / q
                    gainer_packet = sum((z[i] - x[i] for i in packet), F(0))
                    h_loss = sum((x[i] - z[i] for i in h_set), F(0))
                    residual_budget = (
                        (p - packet_size) * sum((x[i] for i in gainers), F(0))
                        - g * sum((x[i] for i in p_set), F(0))
                        + (p - packet_size)
                        * (sum((z[i] for i in h_set), F(0)) - h * high_z)
                        + g * packet_size * high_z
                    ) / g
                    if h_loss <= gainer_packet <= residual_budget:
                        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    core_vertices = vertices()
    values = tuple(
        min(coalition_sum(vertex, coalition) for vertex in core_vertices)
        for coalition in range(1 << N)
    )
    if any(values[1 << player] for player in range(N)):
        raise AssertionError("independent replay lost singleton normalization")
    if not feasible(X) or not feasible(Z):
        raise AssertionError("claimed selector left the core")

    lmin_rows = (mask(0, 1, 2), mask(0, 1, 3), mask(0, 2, 3))
    if tuple(values[row] for row in lmin_rows) != (F(12), F(12), F(10)):
        raise AssertionError("independent Lmin rows changed")
    gainers = (1, 2, 3)
    rooted_tight = tuple(
        row for row in range(1, (1 << N) - 1)
        if row & 1 and coalition_sum(X, row) == values[row]
    )
    if any(sum(int(not (row >> i & 1)) for i in gainers) >= 2 for row in rooted_tight):
        raise AssertionError("independent saturated-packet support changed")
    # The three clean co-stars at weight 1/2 attain 3/2; every rooted tight
    # row contains at least two gainers, so the three unit capacities bound
    # every packing by 3/2.
    packing_value = F(3, 2)

    weighted_bound = sum(
        (weight * bound for weight, bound in zip(TOP_WEIGHTS, TOP_BOUNDS)), F(0)
    )
    loads = tuple(
        sum(
            (weight for row, weight in zip(TOP_ROWS, TOP_WEIGHTS) if row >> i & 1),
            F(0),
        )
        for i in range(N)
    )
    if weighted_bound != F(89, 7) or loads != (
        F(6, 7), F(1), F(3, 7), F(3, 7), F(3, 7), F(3, 7), F(3, 7)
    ):
        raise AssertionError("independent forked-cover arithmetic changed")
    # The weighted rows imply 3T/7 + 3y0/7 + 4y1/7 >= 89/7, so max y>=29/7.
    # Equality forces y0=y1=29/7 and all five positive-weight rows tight.
    equality_rows = [[F(1)] * N]
    equality_rhs = [TOTAL]
    for player in (0, 1):
        equality_rows.append([F(int(i == player)) for i in range(N)])
        equality_rhs.append(F(29, 7))
    for row, bound in zip(TOP_ROWS, TOP_BOUNDS):
        equality_rows.append([F(int(bool(row >> i & 1))) for i in range(N)])
        equality_rhs.append(bound)
    pinned = None
    for selected in itertools.combinations(range(len(equality_rows)), N):
        point = solve_square(
            [equality_rows[index] for index in selected],
            [equality_rhs[index] for index in selected],
        )
        if point is not None:
            if pinned is None:
                pinned = point
            elif point != pinned:
                raise AssertionError("Lmax equality system is inconsistent")
    if pinned != Z:
        raise AssertionError(("independent Lmax pinning changed", pinned))

    gains = tuple(Z[i] - X[i] for i in gainers)
    root_loss = X[0] - Z[0]
    packet_margin = root_loss - (sum(gains, F(0)) - max(gains))
    if gains != (F(1, 7), F(2), F(2)) or packet_margin != F(-2, 7):
        raise AssertionError("independent packet arithmetic changed")
    if direct_packet_exists(X, Z):
        raise AssertionError("independent direct enumeration found a packet")

    pair = mask(0, 1)
    heavy_block = mask(1, 4, 5, 6)
    double_costars = tuple(sorted({
        mask(0, 1, other, outsider)
        for other in (2, 3) for outsider in (4, 5, 6)
    }))
    pair_gap = coalition_sum(Z, pair) - values[pair]
    heavy_gap = coalition_sum(Z, heavy_block) - values[heavy_block]
    double_gaps = tuple(coalition_sum(Z, row) - values[row] for row in double_costars)
    matching = False
    for first, second in itertools.permutations((4, 5, 6), 2):
        remaining = next(i for i in (4, 5, 6) if i not in (first, second))
        rows = (mask(0, 1, 3, first), mask(0, 1, 2, second), mask(1, remaining))
        if all(coalition_sum(Z, row) == values[row] for row in rows):
            matching = True
    if (
        pair_gap != F(29, 28)
        or heavy_gap != 0
        or double_gaps != (F(0), F(0), F(0), F(11, 7), F(11, 7), F(0))
        or matching
    ):
        raise AssertionError("independent support classification changed")

    overlap = sum((min(x, z) for x, z in zip(X, Z)), F(0))
    target = TARGET * TOTAL
    payload = {
        "claim": "independent exact refutation of the corrected four-arm classification",
        "vertex_count": len(core_vertices),
        "singleton_normalized": True,
        "lmin_human_certificate": True,
        "lmax_human_certificate": True,
        "ordered_saturated_packing_value": str(packing_value),
        "packet_margin": str(packet_margin),
        "direct_packet_exists": False,
        "top_pair_gap": str(pair_gap),
        "heavy_block_gap": str(heavy_gap),
        "double_costar_gaps": [str(value) for value in double_gaps],
        "full_pxc78": False,
        "split_matching": False,
        "forked_cover": True,
        "classification_escape": True,
        "overlap": str(overlap),
        "hybrid_target": str(target),
        "hybrid_margin": str(overlap - target),
        "scope": "refutes the four-arm selection statement, not the hybrid-overlap bound",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
