"""Exact dual-arrangement audit for the glued fixed-{5} capacity frontier.

For U={5} (mask 16), impose gamma(U)=0 and sum(gamma)=0 by writing

    gamma_4 = 0,
    gamma_5 = -(gamma_0+gamma_1+gamma_2+gamma_3).

The homogeneous dual therefore has reduced coordinates
(r_A,r_B,gamma_0,...,gamma_3).  Its kink hyperplanes are

    gamma(T) + r_A 1[T=A] - r_B 1[T=B] = 0,

together with the two boundary hyperplanes r_A=0 and r_B=0.  Intersections
of five independent hyperplanes give every projective basic ray relevant to
the piecewise-linear dual.  Enumeration is exact modulo 61; Hadamard bounds
all 5-by-5 minors of these {-1,0,1} rows below 56.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from hunt_glued_local_circuits import (
    A_PLAYER,
    B_PLAYER,
    candidate_record,
    coefficient,
    determinant_bareiss,
    enumerate_local,
    glue,
    rank_mod_prime,
)
from search_both_sensitive_circuits import eliminated_matrix


N = 6
A = 0b000111
B = 0b011000
U = 0b010000


def kink_row(coalition):
    """Reduced row in coordinates (r_A,r_B,gamma_0,...,gamma_3)."""
    contains_player_6 = int(coalition >> 5 & 1)
    return (
        int(coalition == A),
        -int(coalition == B),
        *(
            int(coalition >> player & 1) - contains_player_6
            for player in range(4)
        ),
    )


def primitive_kernel(rows):
    """Primitive integer generator of a rank-five 5-by-6 kernel."""
    vector = [
        (-1) ** column * determinant_bareiss([
            list(row[:column] + row[column + 1:]) for row in rows
        ])
        for column in range(6)
    ]
    assert any(vector)
    assert all(
        sum(row[column] * vector[column] for column in range(6)) == 0
        for row in rows
    )
    divisor = abs(math.gcd(*vector))
    vector = [value // divisor for value in vector]
    for value in vector:
        if value:
            if value < 0:
                vector = [-entry for entry in vector]
            break
    return tuple(vector)


def feasible_orientation(ray):
    """Orient a line to r_A,r_B >= 0, or return None if impossible."""
    r_A, r_B = ray[:2]
    if r_A == r_B == 0 or r_A * r_B < 0:
        return None
    if r_A < 0 or r_B < 0:
        ray = tuple(-value for value in ray)
    assert ray[0] >= 0 and ray[1] >= 0
    return ray


def expand_ray(ray):
    r_A, r_B, *head = ray
    gamma_5 = -sum(head)
    return (r_A, r_B, *head, 0, gamma_5)


def swap_free_A_players(ray):
    """Swap players 2 and 3 (zero-based coordinates 1 and 2)."""
    return (ray[0], ray[1], ray[2], ray[4], ray[3], *ray[5:])


def symmetry_representative(ray):
    return min(ray, swap_free_A_players(ray))


def enumerate_glued_candidates():
    """Reproduce the exact factorized candidate enumeration."""
    matrix, _inequalities, _equalities, rowmeta = eliminated_matrix(N, A, B)
    mono_A = rowmeta.index(("mono", 0, 1, A_PLAYER, A))
    mono_B = rowmeta.index(("mono", 0, 2, B_PLAYER, B))
    root_B = rowmeta.index(("core", 0, B))
    leaf_A = rowmeta.index(("core", 1, A))
    crossed_A = rowmeta.index(("core", 2, A))
    leaf_B = rowmeta.index(("core", 2, B))

    roots = enumerate_local(matrix, rowmeta, 0, (mono_A, mono_B, root_B))
    first_leaves = enumerate_local(matrix, rowmeta, 1, (mono_A, leaf_A))
    second_leaves = enumerate_local(
        matrix, rowmeta, 2, (mono_B, crossed_A, leaf_B)
    )
    second_leaves = [
        circuit for circuit in second_leaves
        if coefficient(circuit, crossed_A) < coefficient(circuit, leaf_B)
    ]

    candidates = {}
    for root_index, root in enumerate(roots, 1):
        for first_index, first in enumerate(first_leaves, 1):
            for second_index, second in enumerate(second_leaves, 1):
                support, weights = glue(
                    root, first, second, mono_A, mono_B
                )
                signature = (support, weights)
                if signature in candidates:
                    continue
                record = candidate_record(rowmeta, support, weights)
                if record["product_gap"] >= 0:
                    continue
                record["local_indices"] = {
                    "root": root_index,
                    "first_leaf": first_index,
                    "second_leaf": second_index,
                }
                candidates[signature] = record
    return tuple(candidates.values()), {
        "root": len(roots),
        "first_leaf": len(first_leaves),
        "product_violating_second_leaf": len(second_leaves),
    }


def ray_hinge(ray, coalition):
    r_A, r_B, *gamma = ray
    return (
        sum(gamma[player] for player in range(N)
            if coalition >> player & 1)
        + r_A * int(coalition == A)
        - r_B * int(coalition == B)
    )


def less_ratio(left, right):
    """Compare nonnegative rational pairs (numerator, denominator)."""
    return left[0] * right[1] < right[0] * left[1]


def evaluate_rays(payload, expanded_rays):
    candidates, local_counts = enumerate_glued_candidates()
    universe = payload["support_structure"]["aggregate_coalition_universe"]
    hinges = [
        {coalition: max(ray_hinge(ray, coalition), 0)
         for coalition in universe}
        for ray in expanded_rays
    ]
    ray_minima = [None] * len(expanded_rays)
    ray_minimum_counts = [0] * len(expanded_rays)
    ray_minimum_witnesses = [None] * len(expanded_rays)
    ray_winner_counts = [0] * len(expanded_rays)
    capacity_histogram = Counter()
    violation_count = 0
    violation_records = []
    sharp_records = []

    for candidate in candidates:
        q = {coalition: int(weight) for coalition, weight
             in candidate["aggregate"].items()}
        assert all(F(weight).denominator == 1
                   for weight in candidate["aggregate"].values())
        x, y = int(candidate["x"]), int(candidate["y"])
        candidate_values = []
        candidate_best = None
        for index, (ray, hinge) in enumerate(zip(expanded_rays, hinges)):
            r_A, r_B = ray[:2]
            denominator = r_A * x + r_B * y
            assert denominator > 0
            numerator = r_B * q[B] + sum(
                weight * hinge[coalition]
                for coalition, weight in q.items()
            )
            value = (numerator, denominator)
            candidate_values.append(value)
            if ray_minima[index] is None or less_ratio(
                    value, ray_minima[index]):
                ray_minima[index] = value
                ray_minimum_counts[index] = 1
                ray_minimum_witnesses[index] = {
                    "local_indices": dict(candidate["local_indices"]),
                    "arm_masses": {
                        key: str(candidate[key])
                        for key in ("x", "y", "U", "V")
                    },
                }
            elif not less_ratio(ray_minima[index], value):
                ray_minimum_counts[index] += 1
            if 8 * numerator < 9 * denominator:
                violation_count += 1
                if len(violation_records) < 20:
                    violation_records.append({
                        "ray": list(ray),
                        "local_indices": candidate["local_indices"],
                        "value": str(F(numerator, denominator)),
                    })
            if candidate_best is None or less_ratio(value, candidate_best):
                candidate_best = value

        best = F(*candidate_best)
        capacity_histogram[best] += 1
        winners = [
            index for index, value in enumerate(candidate_values)
            if not less_ratio(value, candidate_best)
            and not less_ratio(candidate_best, value)
        ]
        for index in winners:
            ray_winner_counts[index] += 1
        if best == F(9, 8) and len(sharp_records) < 20:
            sharp_records.append({
                "local_indices": candidate["local_indices"],
                "arm_masses": {
                    key: str(candidate[key]) for key in ("x", "y", "U", "V")
                },
                "winning_rays": [list(expanded_rays[index])
                                 for index in winners],
            })

    expected_histogram = {
        F(value): count for value, count
        in payload["capacity_histogram"].items()
    }
    ray_rows = []
    for ray, minimum, minimum_count, minimum_witness, winner_count in zip(
            expanded_rays, ray_minima, ray_minimum_counts,
            ray_minimum_witnesses, ray_winner_counts):
        ray_rows.append({
            "ray": list(ray),
            "minimum_value": str(F(*minimum)),
            "minimum_count": minimum_count,
            "minimum_witness": minimum_witness,
            "9_over_8_cross_gap_at_minimum": (
                8 * minimum[0] - 9 * minimum[1]
            ),
            "optimal_for_candidate_count": winner_count,
        })
    winning_rays = {
        ray for ray, count in zip(expanded_rays, ray_winner_counts) if count
    }
    sharp_rays = {
        ray for ray, minimum in zip(expanded_rays, ray_minima)
        if F(*minimum) == F(9, 8)
    }
    return {
        "local_circuit_counts": local_counts,
        "candidate_count": len(candidates),
        "ray_candidate_pairs_checked": len(candidates) * len(expanded_rays),
        "strict_9_over_8_violations": violation_count,
        "violation_records": violation_records,
        "minimum_arrangement_capacity": str(min(capacity_histogram)),
        "minimum_arrangement_capacity_count": capacity_histogram[F(9, 8)],
        "capacity_histogram": {
            str(value): count
            for value, count in sorted(capacity_histogram.items())
        },
        "capacity_histogram_matches_lp_audit": (
            capacity_histogram == expected_histogram
        ),
        "rays_optimal_for_some_candidate": sum(
            count > 0 for count in ray_winner_counts
        ),
        "winning_ray_symmetry_orbits": len({
            symmetry_representative(ray) for ray in winning_rays
        }),
        "sharp_arrangement_rays": len(sharp_rays),
        "sharp_arrangement_ray_symmetry_orbits": len({
            symmetry_representative(ray) for ray in sharp_rays
        }),
        "ray_minima": ray_rows,
        "sharp_records": sharp_records,
    }


def audit(input_path, evaluate=False):
    payload = json.loads(Path(input_path).read_text())
    universe = payload["support_structure"]["aggregate_coalition_universe"]
    sources = {}
    for coalition in universe:
        row = kink_row(coalition)
        sources.setdefault(row, []).append(coalition)
    zero_sources = sources.pop((0,) * 6, [])
    sources.setdefault((1, 0, 0, 0, 0, 0), []).append("r_A=0")
    sources.setdefault((0, 1, 0, 0, 0, 0), []).append("r_B=0")
    rows = tuple(sorted(sources))

    rays = set()
    full_rank_combinations = 0
    feasible_combinations = 0
    for positions in itertools.combinations(range(len(rows)), 5):
        selected = tuple(rows[position] for position in positions)
        if rank_mod_prime(selected) != 5:
            continue
        full_rank_combinations += 1
        ray = feasible_orientation(primitive_kernel(selected))
        if ray is None:
            continue
        feasible_combinations += 1
        rays.add(ray)

    expanded = {expand_ray(ray) for ray in rays}
    observed = {
        tuple(item["ray"])
        for item in payload["dual_template_summary"][
            "most_common_projective_rays"
        ]
    }
    result = {
        "status": "exact fixed-{5} dual hyperplane-arrangement audit",
        "geometry": {"n": N, "A_mask": A, "B_mask": B, "witness": U},
        "reduced_coordinates": [
            "r_A", "r_B", "gamma_0", "gamma_1", "gamma_2", "gamma_3"
        ],
        "coalition_universe_size": len(universe),
        "zero_hyperplane_masks": zero_sources,
        "distinct_nonzero_kink_hyperplanes": len(rows) - 2,
        "distinct_hyperplanes_with_boundaries": len(rows),
        "five_hyperplane_combinations": math.comb(len(rows), 5),
        "rank_five_combinations": full_rank_combinations,
        "feasibly_oriented_combinations": feasible_combinations,
        "distinct_feasible_projective_rays": len(rays),
        "observed_optimal_ray_count": len(observed),
        "all_observed_optimal_rays_present": observed <= expanded,
        "unobserved_arrangement_ray_count": len(expanded - observed),
        "free_A_player_swap_symmetry_orbits": len({
            symmetry_representative(ray) for ray in expanded
        }),
        "hyperplanes": [
            {"row": list(row), "sources": source}
            for row, source in sorted(sources.items())
        ],
        "reduced_rays": [list(ray) for ray in sorted(rays)],
        "expanded_rays": [list(ray) for ray in sorted(expanded)],
    }
    if evaluate:
        result["capacity_evaluation"] = evaluate_rays(
            payload, tuple(sorted(expanded))
        )
    return result


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--evaluate", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(
        audit(args.input, evaluate=args.evaluate), indent=2
    ) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
