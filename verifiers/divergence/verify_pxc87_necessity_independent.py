#!/usr/bin/env python3
"""Independent rational replay of the direct-failing PXC87 control.

This verifier imports neither the project LP stack nor either selector
implementation.  It enumerates every core vertex with a local Fraction
eliminator, reconstructs all coalition minima, checks the short human
selector certificates, and independently enumerates the direct-packet
criterion from its displayed arithmetic formula.
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
Z = (F(29, 7), F(29, 7), F(27, 7), F(27, 7), F(4, 7), F(12, 7), F(12, 7))


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


CONSTRAINTS = (
    (mask(0, 1, 3, 4), F(89, 7)),
    (mask(0, 1, 2, 5), F(97, 7)),
    (mask(1, 6), F(41, 7)),
    (mask(0, 1, 2), F(12)),
    (mask(0, 1, 3), F(12)),
    (mask(0, 2, 3), F(10)),
    (mask(0, 1, 2, 6), F(97, 7)),
    (mask(0, 1, 3, 6), F(97, 7)),
)


def coalition_sum(point: tuple[F, ...], coalition: int) -> F:
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def solve_square(matrix: list[list[F]], rhs: list[F]):
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
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


def feasible(point: tuple[F, ...]) -> bool:
    return (
        sum(point, F(0)) == TOTAL
        and all(value >= 0 for value in point)
        and all(
            coalition_sum(point, coalition) >= bound
            for coalition, bound in CONSTRAINTS
        )
    )


def vertices() -> tuple[tuple[F, ...], ...]:
    inequalities = [
        ([F(int(bool(coalition >> i & 1))) for i in range(N)], bound)
        for coalition, bound in CONSTRAINTS
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
    """Independent finite expansion of the direct master criterion."""
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
        raise AssertionError("claimed selector left the defining core")

    # Lmin: complements of 012 and 013 bound the minimum by two.  Equality
    # pins players 2..6 at two; efficiency and 023 then pin players 0 and 1.
    if tuple(values[row] for row in (mask(0, 1, 2), mask(0, 1, 3), mask(0, 2, 3))) != (
        F(12), F(12), F(10)
    ):
        raise AssertionError("independent Lmin pinning rows changed")

    # Lmax: the first three rows sum to TOTAL+y0+2y1 >= 227/7, forcing
    # max(y)>=29/7.  Equality pins the two tops and those rows; the final two
    # rows pin y2=y3=27/7 and the first rows then pin all outsiders.
    if sum((bound for _, bound in CONSTRAINTS[:3]), F(0)) != F(227, 7):
        raise AssertionError("independent top-cover arithmetic changed")
    if any(coalition_sum(Z, row) != bound for row, bound in CONSTRAINTS[:3]):
        raise AssertionError("independent matching rows are not Z-tight")

    gains = (Z[1] - X[1], Z[2] - X[2], Z[3] - X[3])
    root_loss = X[0] - Z[0]
    packet_margin = root_loss - (sum(gains, F(0)) - max(gains))
    if gains != (F(1, 7), F(13, 7), F(13, 7)) or packet_margin != F(-1, 7):
        raise AssertionError("independent packet arithmetic changed")
    if direct_packet_exists(X, Z):
        raise AssertionError("independent direct-packet enumeration found a packet")

    pair = mask(0, 1)
    heavy_block = mask(1, 4, 5, 6)
    double_costars = tuple(sorted({
        mask(0, 1, other, outsider)
        for other in (2, 3)
        for outsider in (4, 5, 6)
    }))
    pair_gap = coalition_sum(Z, pair) - values[pair]
    heavy_gap = coalition_sum(Z, heavy_block) - values[heavy_block]
    double_gaps = tuple(
        coalition_sum(Z, row) - values[row] for row in double_costars
    )
    if pair_gap != F(4, 7) or heavy_gap != F(16, 7) or double_gaps != (
        F(5, 7), F(0), F(0), F(13, 7), F(0), F(0)
    ):
        raise AssertionError("independent support gaps changed")

    loads = tuple(
        sum(
            (F(1, 3) for row, _ in CONSTRAINTS[:3] if row >> player & 1),
            F(0),
        )
        for player in range(N)
    )
    if loads != (F(2, 3), F(1), F(1, 3), F(1, 3), F(1, 3), F(1, 3), F(1, 3)):
        raise AssertionError("independent PXC87 cover loads changed")

    overlap = sum((min(x, z) for x, z in zip(X, Z)), F(0))
    target = TARGET * TOTAL
    payload = {
        "claim": "independent exact PXC87 nonredundancy control",
        "vertex_count": len(core_vertices),
        "singleton_normalized": True,
        "lmin_human_certificate": True,
        "lmax_human_certificate": True,
        "packet_margin": str(packet_margin),
        "direct_packet_exists": False,
        "top_pair_gap": str(pair_gap),
        "heavy_block_gap": str(heavy_gap),
        "double_costar_gaps": [str(value) for value in double_gaps],
        "split_matching_cover": True,
        "overlap": str(overlap),
        "hybrid_target": str(target),
        "hybrid_margin": str(overlap - target),
        "scope": (
            "proves the PXC87 arm is not redundant with the top-pair, full "
            "PXC78, or direct arms; does not prove universal selection"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
