#!/usr/bin/env python3
"""Solver-free exact proof of a coefficient-seven Lmin packet obstruction."""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from verify_n7_staged_congestion_obstruction import (
    coalition_sum,
    payoff_blocks,
    verify_selection,
)


G = tuple(map(F, (0, 0, 7, 4, 3, 2, 0, 0)))
H = tuple(map(F, (4, 1, 0, 0, 0, 0, 6, 5)))
X = (F(8, 3), F(2, 3), F(7, 3), F(4, 3), F(1), F(2, 3), F(4), F(10, 3))
Z = (F(28, 13), F(7, 13), F(42, 13), F(24, 13), F(18, 13),
     F(12, 13), F(42, 13), F(35, 13))


def exact_rank(rows: list[list[F]]) -> int:
    matrix = [row[:] for row in rows]
    rank = 0
    width = len(matrix[0]) if matrix else 0
    for column in range(width):
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [q / scale for q in matrix[rank]]
        for r in range(len(matrix)):
            if r == rank or not matrix[r][column]:
                continue
            scale = matrix[r][column]
            matrix[r] = [a - scale * b for a, b in zip(matrix[r], matrix[rank])]
        rank += 1
    return rank

LMIN_CERTIFICATES = (
    (0, 1, ((9, F(1, 2)), (85, F(1, 2)), (176, F(1, 2)), (204, F(1, 2))),
     (), ((5, F(1, 2)),), F(1)),
    (0, 5, ((9, F(1)), (85, F(1)), (176, F(1)), (204, F(1))),
     (), ((1, F(2)),), F(2)),
    (1, 4, ((9, F(1)), (85, F(1)), (104, F(1)), (165, F(1)),
            (176, F(1)), (204, F(1))), ((1, F(3)),), (), F(3)),
    (2, 3, ((9, F(1)), (85, F(2)), (104, F(1)), (165, F(1)),
            (176, F(2)), (204, F(1))), ((1, F(4)),), (), F(4)),
    (3, 2, ((9, F(3)), (85, F(3)), (104, F(2)), (165, F(1)),
            (176, F(4)), (204, F(2))), ((1, F(7)),), (), F(7)),
    (4, 0, ((90, F(1)), (151, F(1)), (204, F(1))), ((5, F(2)),), (), F(2)),
    (5, 7, ((9, F(1)), (70, F(1, 2)), (85, F(1, 2)), (90, F(1)),
            (151, F(1)), (204, F(1, 2))), ((5, F(5, 2)),), (), F(5, 2)),
    (6, 6, ((9, F(1)), (90, F(1)), (151, F(2)), (204, F(1))),
     ((5, F(3)),), (), F(3)),
)

LMAX_CERTIFICATES = (
    (0, 2, ((70, F(2, 3)), (85, F(1, 2)), (104, F(1, 3)),
            (165, F(1, 6)), (176, F(1, 6)), (204, F(1, 3))),
     (), ((6, F(7, 6)),), F(2, 3)),
    (0, 6, ((70, F(4, 7)), (85, F(3, 7)), (104, F(2, 7)),
            (165, F(1, 7)), (176, F(1, 7)), (204, F(2, 7))),
     (), ((2, F(6, 7)),), F(4, 7)),
    (1, 7, ((70, F(1, 7)), (151, F(3, 7)), (165, F(2, 7)),
            (170, F(1, 7)), (176, F(2, 7)), (204, F(4, 7))),
     ((2, F(-5, 7)),), (), F(5, 7)),
    (2, 0, ((9, F(4, 7)), (51, F(1, 7)), (70, F(2, 7)),
            (85, F(2, 7)), (151, F(1, 7)), (165, F(3, 7))),
     ((2, F(-4, 7)),), (), F(4, 7)),
    (3, 3, ((9, F(1, 3)), (90, F(1, 3)), (104, F(1, 3)), (204, F(1, 3))),
     ((6, F(-2, 3)),), (), F(1, 3)),
    (4, 4, ((85, F(1, 2)), (90, F(1, 2)), (176, F(1, 2))),
     ((6, F(-1, 2)),), (), F(1, 2)),
    (5, 5, ((51, F(1, 3)), (70, F(1, 3)), (104, F(2, 3)),
            (165, F(1, 3)), (176, F(1, 3))), ((6, F(-1, 3)),), (), F(2, 3)),
    (6, 1, ((9, F(1, 7)), (51, F(2, 7)), (70, F(4, 7)),
            (90, F(1, 7)), (151, F(2, 7)), (170, F(3, 7))),
     ((2, F(-1, 7)),), (), F(5, 7)),
)


def audit() -> dict:
    n = 8
    full = (1 << n) - 1
    values = tuple(
        min(coalition_sum(G, mask), coalition_sum(H, mask))
        for mask in range(1 << n)
    )
    assert coalition_sum(G, full) == coalition_sum(H, full) == values[full] == 16
    assert all(values[1 << i] == 0 for i in range(n))
    for generator in (G, H):
        assert all(coalition_sum(generator, mask) >= values[mask] for mask in range(1, full))
    for point in (X, Z):
        assert coalition_sum(point, full) == values[full]
        assert all(coalition_sum(point, mask) >= values[mask] for mask in range(1, full))

    assert payoff_blocks(X, "min") == ((1, 5), (4,), (3,), (2,), (0,), (7,), (6,))
    assert payoff_blocks(Z, "max") == ((2, 6), (7,), (0,), (3,), (4,), (5,), (1,))
    verify_selection(values, X, "min", LMIN_CERTIFICATES)
    verify_selection(values, Z, "max", LMAX_CERTIFICATES)

    stage = 3
    target = 2
    cumulative = (1, 5, 4, 3, 2)
    assert Z[target] > X[target]
    assert tuple(i for i in payoff_blocks(X, "min")[stage] if Z[i] > X[i]) == (target,)

    primal = ((9, F(3)), (85, F(3)), (104, F(2)),
              (165, F(1)), (176, F(4)), (204, F(2)))
    auxiliary = {1: F(7)}
    for mask, weight in primal:
        if weight:
            assert coalition_sum(X, mask) == values[mask]
    for coordinate in range(n):
        load = sum(
            weight * F(int(bool(mask >> coordinate & 1)))
            for mask, weight in primal
        )
        load += auxiliary.get(coordinate, F(0))
        load += F(int(coordinate == target))
        assert load == 7
    primal_value = max(auxiliary.get(i, F(0)) for i in cumulative)
    circuit_columns = [
        [F(int(bool(mask >> coordinate & 1))) for coordinate in range(n)]
        for mask, _weight in primal
    ]
    circuit_columns += [
        [F(int(coordinate == player)) for coordinate in range(n)]
        for player in (1, target)
    ]
    projected_rows = [
        [column[coordinate] - column[-1] for column in circuit_columns]
        for coordinate in range(n - 1)
    ]
    assert len(circuit_columns) == n and exact_rank(projected_rows) == n - 1

    price = tuple(F(1) if i == 1 else F(0) for i in cumulative)
    tangent = tuple(G[i] - H[i] for i in range(n))
    tight = tuple(
        mask for mask in range(1, full)
        if coalition_sum(X, mask) == values[mask]
    )
    assert sum(price, F(0)) == 1 and sum(tangent, F(0)) == 0
    assert all(coalition_sum(tangent, mask) >= 0 for mask in tight)
    assert all(tangent[j] >= -price[pos] for pos, j in enumerate(cumulative))
    dual_value = tangent[target]
    assert primal_value == dual_value == 7 > 1

    # Exact sparse Lmax over-cover and its spectral consequence.
    overcover = ((70, F(4, 13)), (85, F(3, 13)), (104, F(2, 13)),
                 (165, F(1, 13)), (176, F(1, 13)), (204, F(2, 13)))
    eta = F(4, 13)
    alpha = tuple(F(6, 13) if i == 2 else F(7, 13) if i == 6 else F(0)
                  for i in range(n))
    for coordinate in range(n):
        load = sum(
            weight * F(int(bool(mask >> coordinate & 1)))
            for mask, weight in overcover
        )
        assert load == eta + alpha[coordinate]
    assert sum(alpha, F(0)) == 1
    maximum = max(Z)
    assert sum((alpha[i] * X[i] for i in range(n)), F(0)) == maximum
    theta = max(alpha)
    top = tuple(i for i, q in enumerate(Z) if q == maximum)
    lower_z = sorted((q for q in Z if q < maximum), reverse=True)
    required = (maximum - min(X)) / theta
    candidates = []
    for chosen in itertools.combinations(range(n), len(top)):
        if sum((X[i] - min(X) for i in chosen), F(0)) < required:
            continue
        remaining = sorted(X[i] for i in range(n) if i not in chosen)
        candidates.append(
            sum((min(X[i], maximum) for i in chosen), F(0))
            + sum((min(a, b) for a, b in zip(remaining, lower_z)), F(0))
        )
    spectral_bound = min(candidates)
    overlap = sum((min(a, b) for a, b in zip(X, Z)), F(0))
    target_floor = F(4 * n, n * n) * values[full]
    assert spectral_bound == F(139, 13) > target_floor == 8
    assert overlap == F(544, 39) > spectral_bound

    return {
        "status": "solver-free exact coefficient-seven staged-congestion obstruction",
        "n": n,
        "generators": [[str(q) for q in G], [str(q) for q in H]],
        "singleton_normalized": True,
        "exact_by_lower_envelope": True,
        "total": str(values[full]),
        "lmin": [str(q) for q in X],
        "lmax": [str(q) for q in Z],
        "selection_proof": {
            "method": "sixteen sparse exact staged incidence identities",
            "lmin_certificates": len(LMIN_CERTIFICATES),
            "lmax_certificates": len(LMAX_CERTIFICATES),
        },
        "obstruction": {
            "lmin_stage": stage,
            "cumulative_players": list(cumulative),
            "gaining_target": target,
            "minimum_congestion": str(primal_value),
            "target_count": 1,
            "primal_coalition_weights": [[mask, str(q)] for mask, q in primal],
            "primal_auxiliary": {str(i): str(q) for i, q in auxiliary.items()},
            "dual_price": [str(q) for q in price],
            "dual_tangent": [str(q) for q in tangent],
            "dual_value": str(dual_value),
            "projected_positive_circuit_support": len(circuit_columns),
            "primitive_circuit_coefficients": [
                *[str(weight) for _mask, weight in primal], "7", "1"
            ],
        },
        "lmax_overcover": {
            "theta": str(theta),
            "eta": str(eta),
            "alpha": [str(q) for q in alpha],
            "hinge_surplus": "0",
            "spectral_bound": str(spectral_bound),
        },
        "hybrid_overlap": str(overlap),
        "conjectured_overlap_floor": str(target_floor),
        "scope": "large local congestion is compensated by the opposite spectral certificate",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(audit(), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
