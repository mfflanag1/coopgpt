#!/usr/bin/env python3
"""Solver-free exact proof of the seven-player staged-congestion obstruction.

The lower envelope of two common-total allocations is an exact game.  Sparse
incidence identities certify its displayed Lmin and Lmax points stage by
stage.  A primal packet and a tangent-price dual then prove that one Lmin
stage with one gaining target has minimum auxiliary congestion exactly two.

This refutes the proposed target-count cap, not the hybrid-overlap bound.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


G = tuple(map(F, (1, 1, 0, 5, 0, 4, 1)))
H = tuple(map(F, (0, 0, 8, 0, 4, 0, 0)))
X = tuple(map(F, (1, 1, 2, 3, 1, 3, 1)))
Z = (F(8, 9), F(8, 9), F(8, 3), F(8, 3), F(4, 3), F(8, 3), F(8, 9))

# Each tuple is (stage, player, coalition weights, old-unit weights,
# current-unit weights, efficiency coefficient).  In the Lmin identity the
# current units and forced unit have positive sign; in Lmax they have negative
# sign.  Masks use zero-based player bits.
LMIN_CERTIFICATES = (
    (0, 0, ((48, F(1)), (78, F(1))), (), (), F(1)),
    (0, 1, ((48, F(1)), (77, F(1))), (), (), F(1)),
    (0, 4, ((44, F(1)),), (), ((0, F(1)), (1, F(1)), (6, F(1))), F(1)),
    (0, 6, ((15, F(1)), (48, F(1))), (), (), F(1)),
    (1, 2, ((24, F(1)), (44, F(1)), (48, F(1))),
     ((0, F(2)), (1, F(2)), (6, F(2))), (), F(2)),
    (2, 3, ((48, F(1)),),
     ((0, F(1)), (1, F(1)), (6, F(1)), (2, F(1))), (), F(1)),
    (2, 5, ((76, F(1)),),
     ((0, F(1)), (1, F(1)), (4, F(1))), (), F(1)),
)

LMAX_CERTIFICATES = (
    (0, 2, ((24, F(1)), (44, F(1)), (79, F(1))), (), ((3, F(2)),), F(1)),
    (0, 3, ((24, F(1, 2)), (44, F(1, 2)), (79, F(1, 2))),
     (), ((2, F(1, 2)),), F(1, 2)),
    (0, 5, ((44, F(1)),), (), ((2, F(1)), (3, F(1))), F(0)),
    (1, 4, ((24, F(1)),), ((3, F(-1)),), (), F(0)),
    (2, 0, ((79, F(1)),), ((2, F(-1)), (3, F(-1))),
     ((1, F(1)), (6, F(1))), F(0)),
    (2, 1, ((79, F(1)),), ((2, F(-1)), (3, F(-1))),
     ((0, F(1)), (6, F(1))), F(0)),
    (2, 6, ((79, F(1)),), ((2, F(-1)), (3, F(-1))),
     ((0, F(1)), (1, F(1))), F(0)),
)


def coalition_sum(point: tuple[F, ...], mask: int) -> F:
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def payoff_blocks(point: tuple[F, ...], mode: str) -> tuple[tuple[int, ...], ...]:
    levels = sorted(set(point), reverse=(mode == "max"))
    return tuple(tuple(i for i, value in enumerate(point) if value == level) for level in levels)


def verify_selection(
    values: tuple[F, ...],
    point: tuple[F, ...],
    mode: str,
    certificates,
) -> None:
    n = len(point)
    blocks = payoff_blocks(point, mode)
    by_key = {(stage, player): row for stage, player, *row in certificates}
    assert set(by_key) == {
        (stage, player) for stage, block in enumerate(blocks) for player in block
    }
    side = F(1 if mode == "min" else -1)
    for stage, block in enumerate(blocks):
        old = {i for earlier in blocks[:stage] for i in earlier}
        current = set(block)
        for player in block:
            coalition_weights, old_weights, current_weights, constant = by_key[
                (stage, player)
            ]
            assert all(weight >= 0 for _mask, weight in coalition_weights)
            assert all(index in old for index, _weight in old_weights)
            assert all(index in current for index, _weight in current_weights)
            assert all(weight >= 0 for _index, weight in current_weights)
            assert all(
                weight >= 0 if mode == "min" else weight <= 0
                for _index, weight in old_weights
            )
            for mask, weight in coalition_weights:
                if weight:
                    assert coalition_sum(point, mask) == values[mask]
            for coordinate in range(n):
                load = sum(
                    weight * F(int(bool(mask >> coordinate & 1)))
                    for mask, weight in coalition_weights
                )
                load += sum(
                    weight for index, weight in old_weights if index == coordinate
                )
                load += side * sum(
                    weight
                    for index, weight in current_weights
                    if index == coordinate
                )
                load += side * F(int(coordinate == player))
                assert load == constant


def audit() -> dict:
    n = 7
    full = (1 << n) - 1
    assert coalition_sum(G, full) == coalition_sum(H, full) == F(12)
    values = tuple(
        min(coalition_sum(G, mask), coalition_sum(H, mask))
        for mask in range(1 << n)
    )
    assert all(values[1 << i] == 0 for i in range(n))
    # Both generators are core allocations and one attains every coalition,
    # so the lower-envelope game is exact by definition.
    for generator in (G, H):
        assert coalition_sum(generator, full) == values[full]
        assert all(
            coalition_sum(generator, mask) >= values[mask]
            for mask in range(1, full)
        )
    assert all(
        min(coalition_sum(G, mask), coalition_sum(H, mask)) == values[mask]
        for mask in range(1, full)
    )
    for point in (X, Z):
        assert coalition_sum(point, full) == values[full]
        assert all(
            coalition_sum(point, mask) >= values[mask]
            for mask in range(1, full)
        )

    assert payoff_blocks(X, "min") == ((0, 1, 4, 6), (2,), (3, 5))
    assert payoff_blocks(Z, "max") == ((2, 3, 5), (4,), (0, 1, 6))
    verify_selection(values, X, "min", LMIN_CERTIFICATES)
    verify_selection(values, Z, "max", LMAX_CERTIFICATES)

    stage = 1
    target = 2
    cumulative = (0, 1, 4, 6, 2)
    targets = tuple(i for i in payoff_blocks(X, "min")[stage] if Z[i] > X[i])
    assert targets == (target,)

    # Primal certificate: congestion at most two.
    primal_masks = (24, 44, 48)
    primal_auxiliary = {0: F(2), 1: F(2), 6: F(2)}
    for mask in primal_masks:
        assert coalition_sum(X, mask) == values[mask]
    for coordinate in range(n):
        load = sum(F(int(bool(mask >> coordinate & 1))) for mask in primal_masks)
        load += primal_auxiliary.get(coordinate, F(0))
        load += F(int(coordinate == target))
        assert load == 2
    primal_congestion = max(primal_auxiliary.get(i, F(0)) for i in cumulative)
    assert primal_congestion == 2

    # Price-tangent dual: congestion at least two.
    price = (F(1), F(0), F(0), F(0), F(0))
    tangent = tuple(map(F, (-1, 0, 2, -1, 1, -1, 0)))
    assert sum(price, F(0)) == 1 and all(q >= 0 for q in price)
    assert sum(tangent, F(0)) == 0
    tight = tuple(
        mask
        for mask in range(1, full)
        if coalition_sum(X, mask) == values[mask]
    )
    assert all(coalition_sum(tangent, mask) >= 0 for mask in tight)
    assert all(tangent[j] >= -price[pos] for pos, j in enumerate(cumulative))
    dual_value = tangent[target]
    assert dual_value == primal_congestion == 2 > len(targets)

    # The obstruction is harmless for the main inequality because the sparse
    # Lmax anchor is already very strong: (1/3)1_44 is a zero-surplus
    # over-cover, uniformly pricing the three Lmax-top players.
    top = (2, 3, 5)
    top_mask = 44
    alpha = tuple(F(1, 3) if i in top else F(0) for i in range(n))
    assert coalition_sum(Z, top_mask) == values[top_mask]
    for coordinate in range(n):
        assert F(1, 3) * F(int(bool(top_mask >> coordinate & 1))) == alpha[coordinate]
    maximum = max(Z)
    assert sum((alpha[i] * X[i] for i in range(n)), F(0)) == maximum
    theta = F(1, 3)
    minimum = min(X)
    required_excess = (maximum - minimum) / theta
    lower_z = sorted((q for q in Z if q < maximum), reverse=True)
    spectral_candidates = []
    for chosen in itertools.combinations(range(n), len(top)):
        if sum((X[i] - minimum for i in chosen), F(0)) < required_excess:
            continue
        remaining_x = sorted(X[i] for i in range(n) if i not in chosen)
        spectral_candidates.append(
            sum((min(X[i], maximum) for i in chosen), F(0))
            + sum((min(a, b) for a, b in zip(remaining_x, lower_z)), F(0))
        )
    spectral_bound = min(spectral_candidates)
    assert spectral_bound == 11

    overlap = sum((min(a, b) for a, b in zip(X, Z)), F(0))
    sharp_target = F(4 * n, n * n - 1) * values[full]
    assert overlap == 11 and sharp_target == 7 and overlap > sharp_target
    return {
        "status": "solver-free exact rational counterexample to staged target-count congestion",
        "n": n,
        "generators": [[str(q) for q in G], [str(q) for q in H]],
        "singleton_normalized": True,
        "exact_by_lower_envelope": True,
        "total": str(values[full]),
        "lmin": [str(q) for q in X],
        "lmax": [str(q) for q in Z],
        "selection_proof": {
            "method": "fourteen sparse exact staged incidence identities",
            "lmin_certificates": len(LMIN_CERTIFICATES),
            "lmax_certificates": len(LMAX_CERTIFICATES),
        },
        "obstruction": {
            "lmin_stage": stage,
            "cumulative_players": list(cumulative),
            "gaining_targets": list(targets),
            "primal_coalition_masks": list(primal_masks),
            "primal_auxiliary": {str(i): str(q) for i, q in primal_auxiliary.items()},
            "minimum_congestion": str(primal_congestion),
            "target_count": len(targets),
            "dual_price": [str(q) for q in price],
            "dual_tangent": [str(q) for q in tangent],
            "dual_value": str(dual_value),
        },
        "lmax_overcover": {
            "support_mask": top_mask,
            "coalition_weight": "1/3",
            "alpha": [str(q) for q in alpha],
            "eta": "0",
            "hinge_surplus": "0",
            "spectral_bound": str(spectral_bound),
        },
        "hybrid_overlap": str(overlap),
        "conjectured_overlap_floor": str(sharp_target),
        "scope": "refutes the auxiliary congestion lemma, not the all-n hybrid-overlap inequality",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit()
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
