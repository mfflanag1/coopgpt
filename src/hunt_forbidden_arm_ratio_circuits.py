"""Target fundamental circuits violating the observed arm-ratio dichotomy.

Nonfinding is discovery evidence only: random bases can miss circuits with
small normal cones. Every reported hit and ratio is nevertheless exactified.
"""
from __future__ import annotations

import argparse
import json
import random
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from search_both_sensitive_circuits import eliminated_matrix, exactify_support


def arm_masses(rowmeta, support, weights, A, B):
    aggregate_A = aggregate_B = required_A = required_B = 0
    for index, weight in zip(support, weights):
        meta = rowmeta[index]
        if meta[0] != "core":
            continue
        game, coalition = meta[1], meta[2]
        if coalition == A:
            aggregate_A += weight
            if game == 1:
                required_A += weight
        if coalition == B:
            aggregate_B += weight
            if game == 2:
                required_B += weight
    assert required_A > 0 and required_B > 0
    return (
        F(aggregate_A), F(aggregate_B),
        F(required_A), F(required_B),
    )


def seeded_supports(seed_payload, rowmeta, bump_B):
    if seed_payload is None:
        return []
    details = seed_payload.get("circuits")
    if details is None:
        details = [
            circuit
            for batch in seed_payload["batches"]
            for circuit in batch["circuits"]
        ]
    metadata_index = {tuple(meta): index for index, meta in enumerate(rowmeta)}
    return [
        tuple(
            metadata_index[tuple(meta)]
            for meta in circuit["active_rows"]
            if metadata_index[tuple(meta)] != bump_B
        )
        for circuit in details
    ]


def extended_basis(matrix, anchor, candidates, rank, bump_A, mutations, rng):
    basis = [bump_A] + [column for column in anchor if column != bump_A]
    mutable = [column for column in basis if column != bump_A]
    for column in rng.sample(mutable, min(mutations, len(mutable))):
        basis.remove(column)
    if len(basis) == rank:
        return basis
    pool = list(set(candidates) - set(basis))
    rng.shuffle(pool)
    for column in pool:
        candidate = basis + [column]
        if np.linalg.matrix_rank(matrix[:, candidate]) > len(basis):
            basis.append(column)
            if len(basis) == rank:
                return basis
    return None


def hunt(n, A, B, trials, seed, seed_payload=None, mutations=0):
    matrix, _inequalities, _equalities, rowmeta = eliminated_matrix(n, A, B)
    rank = int(np.linalg.matrix_rank(matrix))
    bump_A = rowmeta.index(("core", 1, A))
    bump_B = rowmeta.index(("core", 2, B))
    candidates = [
        column for column in range(matrix.shape[1])
        if column not in (bump_A, bump_B)
    ]
    anchors = seeded_supports(seed_payload, rowmeta, bump_B)
    rng = random.Random(seed)
    full_rank_bases = positive_numerical = exact_circuits = 0
    signatures = set()
    ratios = {}
    forbidden = []
    cross_gap_violations = []
    best_gap = None
    best = None
    smallest_cross_gap = None
    smallest_cross = None

    for trial in range(trials):
        if anchors:
            basis = extended_basis(
                matrix, rng.choice(anchors), candidates, rank, bump_A,
                mutations, rng,
            )
            if basis is None:
                continue
        else:
            basis = [bump_A] + rng.sample(candidates, rank - 1)
        basis_matrix = matrix[:, basis]
        if np.linalg.matrix_rank(basis_matrix) < rank:
            continue
        full_rank_bases += 1
        coefficients = np.linalg.solve(basis_matrix, matrix[:, bump_B])
        if coefficients[0] >= -1e-8 or np.any(coefficients > 1e-8):
            continue
        positive_numerical += 1
        numerical_support = basis + [bump_B]
        numerical_weights = [-value for value in coefficients] + [1.0]
        support = tuple(sorted(
            column for column, weight in zip(numerical_support, numerical_weights)
            if weight > 1e-8
        ))
        if support in signatures:
            continue
        weights = exactify_support(matrix, support)
        if weights is None:
            continue
        # exactify_support follows the supplied support order.
        signatures.add(support)
        exact_circuits += 1
        aggregate_A, aggregate_B, required_A, required_B = arm_masses(
            rowmeta, support, weights, A, B
        )
        ratio_A = aggregate_A / required_A
        ratio_B = aggregate_B / required_B
        cross_gap_A = aggregate_A - required_A - required_B
        cross_gap_B = aggregate_B - required_B - required_A
        ratio_key = (str(ratio_A), str(ratio_B))
        ratios[ratio_key] = ratios.get(ratio_key, 0) + 1
        scalar_gap = 1 / ratio_A + 1 / ratio_B - 1
        if ratio_A > 1 and ratio_B > 1:
            cross_min = min(cross_gap_A, cross_gap_B)
            if smallest_cross_gap is None or cross_min < smallest_cross_gap:
                smallest_cross_gap = cross_min
                smallest_cross = {
                    "trial": trial,
                    "ratio_A": str(ratio_A),
                    "ratio_B": str(ratio_B),
                    "cross_gap_A": str(cross_gap_A),
                    "cross_gap_B": str(cross_gap_B),
                    "support_size": len(support),
                    "active_rows": [rowmeta[index] for index in support],
                    "weights": weights,
                }
            if best_gap is None or scalar_gap > best_gap:
                best_gap = scalar_gap
                best = {
                    "trial": trial,
                    "ratio_A": str(ratio_A),
                    "ratio_B": str(ratio_B),
                    "reciprocal_sum_minus_one": str(scalar_gap),
                    "support_size": len(support),
                    "active_rows": [rowmeta[index] for index in support],
                    "weights": weights,
                }
            if cross_gap_A < 0 or cross_gap_B < 0:
                cross_gap_violations.append(smallest_cross)
                break
            if scalar_gap > 0:
                forbidden.append(best)
                break

    return {
        "status": (
            "LINEAR CROSS-GAP VIOLATION FOUND" if cross_gap_violations
            else "FORBIDDEN EXACT CIRCUIT FOUND" if forbidden
            else "no forbidden circuit found; random-basis evidence only"
        ),
        "n": n,
        "A_mask": A,
        "B_mask": B,
        "trials": trials,
        "seed": seed,
        "seeded_circuit_count": len(anchors),
        "mutations_per_seed_basis": mutations,
        "rank": rank,
        "full_rank_bases": full_rank_bases,
        "positive_fundamental_dependences": positive_numerical,
        "distinct_exact_circuits": exact_circuits,
        "ratio_pairs": [
            {"ratio_A": left, "ratio_B": right, "count": count}
            for (left, right), count in sorted(ratios.items())
        ],
        "best_nonexclusive_gap": str(best_gap) if best_gap is not None else None,
        "best_nonexclusive_circuit": best,
        "forbidden_circuit": forbidden[0] if forbidden else None,
        "stronger_linear_conjecture": "aggregate_A-required_A >= required_B and aggregate_B-required_B >= required_A",
        "smallest_cross_gap": (
            str(smallest_cross_gap) if smallest_cross_gap is not None else None
        ),
        "smallest_cross_gap_circuit": smallest_cross,
        "cross_gap_violation": (
            cross_gap_violations[0] if cross_gap_violations else None
        ),
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--A", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--B", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--trials", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--seed-json", type=Path)
    parser.add_argument("--mutations", type=int, default=0)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    seed_payload = json.loads(args.seed_json.read_text()) if args.seed_json else None
    result = hunt(
        args.n, args.A, args.B, args.trials, args.seed,
        seed_payload=seed_payload, mutations=args.mutations,
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
