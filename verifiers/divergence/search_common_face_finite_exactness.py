#!/usr/bin/env python3
"""Hostile exact search on the six finite common-face weight rows.

The unrestricted endowed-seesaw projection can miss the atomic target only
on six ordered weight patterns with n=6,...,9.  For each sharp relaxed line
and each possible hub orientation, this discovery tool adjoins exact
singleton witnesses for every unit role, forms their lower-envelope exact
game, and independently recomputes both weighted selectors.  It is a
counterexample search, not proof evidence.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

import explore_weighted_four_role_faces as faces  # noqa: E402
import verify_weighted_endowed_seesaw as seesaw  # noqa: E402


FINITE_ROWS = (
    (1, 2, 1, 2),
    (1, 3, 1, 1),
    (1, 3, 1, 2),
    (1, 4, 1, 1),
    (1, 5, 1, 1),
    (1, 6, 1, 1),
)


def compositions(total, parts=4):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, parts - 1):
            yield (first,) + tail


def actual_order(row):
    """Convert LP order (p,r,q,b) to line order (p,q,r,b)."""

    p, r, q, b = row
    return (p, q, r, b)


def actual_endowments(solution):
    e_p, e_r, e_q, e_b, width, level = solution
    return (e_p, e_q, e_r, e_b), width, level


def line_point(endowments, width, parameter):
    return (
        endowments[0] + parameter,
        endowments[1] + width - parameter,
        endowments[2] + parameter,
        endowments[3] + width - parameter,
    )


def hub_pairs(hub):
    same_direction_opposite = {0: 2, 2: 0, 1: 3, 3: 1}[hub]
    arms = [role for role in range(4) if role not in (hub, same_direction_opposite)]
    return tuple((1 << hub) | (1 << arm) for arm in arms)


def lcm_denominators(points):
    scale = 1
    for point in points:
        for value in point:
            scale = math.lcm(scale, value.denominator)
    return scale


def witness_candidates(total, singleton, pairs, pair_totals):
    rows = []
    for point in compositions(total):
        if point[singleton] != 0:
            continue
        if any(
            sum(point[i] for i in range(4) if pair >> i & 1) < bound
            for pair, bound in zip(pairs, pair_totals)
        ):
            continue
        rows.append(point)
    return rows


def encode_point(point):
    return [str(value) for value in point]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=2000)
    parser.add_argument("--grid-refinement", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260813)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    checked = 0
    retained_divergence = 0
    violations = []
    best = {}
    witness_grid_infeasible = []

    for row in FINITE_ROWS:
        weights = actual_order(row)
        status, _, solution = seesaw.independent_adjacent_gap_lp(
            *row, enforce_unit_endowments=False
        )
        if status != "optimal":
            raise AssertionError((row, status))
        endowments, width, level = actual_endowments(solution)
        endpoints = (
            line_point(endowments, width, F(0)),
            line_point(endowments, width, width),
        )
        expected_lmin = line_point(endowments, width, level + 1)
        expected_lmax = line_point(endowments, width, level)
        n = sum(weights)
        target = seesaw.atomic_target(n)
        for hub in range(4):
            pairs = hub_pairs(hub)
            pair_totals = tuple(
                faces.coalition_sum(endpoints[0], pair) for pair in pairs
            )
            if any(
                faces.coalition_sum(endpoints[1], pair) != bound
                for pair, bound in zip(pairs, pair_totals)
            ):
                raise AssertionError((row, hub, "line pair"))
            scale = args.grid_refinement * lcm_denominators(endpoints)
            scaled_endpoints = tuple(
                tuple(int(value * scale) for value in point) for point in endpoints
            )
            scaled_pair_totals = tuple(int(value * scale) for value in pair_totals)
            total = sum(scaled_endpoints[0])
            unit_roles = [role for role, weight in enumerate(weights) if weight == 1]
            candidates = {
                role: witness_candidates(total, role, pairs, scaled_pair_totals)
                for role in unit_roles
            }
            if any(not candidates[role] for role in unit_roles):
                witness_grid_infeasible.append(
                    {
                        "weights_p_r_q_b": list(row),
                        "hub_in_line_order_p_q_r_b": hub,
                        "roles_without_grid_witness": [
                            role for role in unit_roles if not candidates[role]
                        ],
                    }
                )
                continue
            # Extremal lexicographic candidates are always included before
            # seeded sampling of the Cartesian product.
            combinations = [
                tuple(candidates[role][0] for role in unit_roles),
                tuple(candidates[role][-1] for role in unit_roles),
            ]
            combinations.extend(
                tuple(rng.choice(candidates[role]) for role in unit_roles)
                for _ in range(args.trials)
            )
            for witnesses in combinations:
                generators = scaled_endpoints + witnesses
                values = faces.role_values(generators)
                lmin, _ = faces.weighted_lex_point(values, weights, "min")
                lmax, _ = faces.weighted_lex_point(values, weights, "max")
                checked += 1
                if lmin != lmax:
                    retained_divergence += 1
                ratio = sum(min(a, b) for a, b in zip(lmin, lmax)) / values[15]
                key = (row, hub)
                if key not in best or ratio < best[key][0]:
                    best[key] = (ratio, lmin, lmax, generators)
                if ratio < target:
                    violations.append((row, hub, weights, values, lmin, lmax, ratio, generators))
                    break

    report = {
        "status": "finite common-face exactness discovery search; not proof evidence",
        "seed": args.seed,
        "trials_per_weight_and_hub": args.trials,
        "witness_grid_refinement": args.grid_refinement,
        "exact_lower_envelope_games_checked": checked,
        "games_retaining_weighted_divergence": retained_divergence,
        "target_violation_count": len(violations),
        "witness_grid_infeasible_orientations": witness_grid_infeasible,
        "target_violations": [
            {
                "weights_p_r_q_b": list(row),
                "hub_in_line_order_p_q_r_b": hub,
                "line_order_weights": list(weights),
                "values": [str(value) for value in values],
                "lmin": encode_point(lmin),
                "lmax": encode_point(lmax),
                "overlap_ratio": str(ratio),
                "generators": [encode_point(point) for point in generators],
            }
            for row, hub, weights, values, lmin, lmax, ratio, generators in violations
        ],
        "minimum_by_weight_and_hub": [
            {
                "weights_p_r_q_b": list(row),
                "hub_in_line_order_p_q_r_b": hub,
                "overlap_ratio": str(result[0]),
                "atomic_target": str(seesaw.atomic_target(sum(row))),
                "lmin": encode_point(result[1]),
                "lmax": encode_point(result[2]),
                "generators": [encode_point(point) for point in result[3]],
            }
            for (row, hub), result in sorted(best.items())
        ],
        "scope": (
            "samples singleton-witness realizations of the six relaxed rows; "
            "absence of a violation is discovery evidence only"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(
        json.dumps(
            {
                "status": report["status"],
                "checked": checked,
                "divergent": retained_divergence,
                "violations": len(violations),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
