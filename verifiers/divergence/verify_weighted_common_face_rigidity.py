#!/usr/bin/env python3
"""Exact identity audit for the weighted common-face rigidity theorem.

The proof is human: fixing one complementary pair endpoint creates two
fixed-total role pairs; movement toward weighted equality in either pair is
a Pigou--Dalton transfer, and in each dispersion orthant only one remaining
pair strip has a negative-slope Pareto boundary.  This script checks the two
algebraic ingredients exactly.  Its finite rational grids are regression
evidence, not a substitute for the dimension-free convex argument.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
from fractions import Fraction as F
from pathlib import Path


def repeated_pair(split, total, weights):
    left, right = weights
    return [split / left] * left + [(total - split) / right] * right


def lorenz_dominates(better, worse):
    better = sorted(better)
    worse = sorted(worse)
    if sum(better, F(0)) != sum(worse, F(0)):
        return False
    partial_better = F(0)
    partial_worse = F(0)
    strict = False
    for a, b in zip(better, worse):
        partial_better += a
        partial_worse += b
        if partial_better < partial_worse:
            return False
        strict |= partial_better > partial_worse
    return strict


def pair_transfer_audit(max_weight=6, denominator=12):
    checked = 0
    for h0 in range(1, max_weight + 1):
        for h1 in range(1, max_weight + 1):
            total = F(1)
            center = F(h0, h0 + h1)
            points = [F(k, denominator) for k in range(denominator + 1)]
            for farther in points:
                for nearer in points:
                    same_side = (farther - center) * (nearer - center) >= 0
                    if not same_side or abs(nearer - center) >= abs(farther - center):
                        continue
                    checked += 1
                    if not lorenz_dominates(
                        repeated_pair(nearer, total, (h0, h1)),
                        repeated_pair(farther, total, (h0, h1)),
                    ):
                        raise AssertionError((h0, h1, farther, nearer))
    return checked


def block_sum_audit(max_weight=4, denominator=6):
    checked = 0
    for h0 in range(1, max_weight + 1):
        for h1 in range(1, max_weight + 1):
            for h2 in range(1, max_weight + 1):
                for h3 in range(1, max_weight + 1):
                    centers = (F(h0, h0 + h1), F(h2, h2 + h3))
                    points = [F(k, denominator) for k in range(denominator + 1)]
                    for far0 in points:
                        near0 = (far0 + centers[0]) / 2
                        for far1 in points:
                            near1 = (far1 + centers[1]) / 2
                            if near0 == far0 and near1 == far1:
                                continue
                            worse = repeated_pair(far0, F(1), (h0, h1)) + repeated_pair(
                                far1, F(1), (h2, h3)
                            )
                            better = repeated_pair(
                                near0, F(1), (h0, h1)
                            ) + repeated_pair(near1, F(1), (h2, h3))
                            checked += 1
                            if not lorenz_dominates(better, worse):
                                raise AssertionError(
                                    ((h0, h1, h2, h3), far0, far1, near0, near1)
                                )
    return checked


def orthant_table():
    rows = []
    for epsilon_1 in (-1, 1):
        for epsilon_2 in (-1, 1):
            y1 = (epsilon_1, epsilon_2)
            y2 = (epsilon_1, -epsilon_2)
            if y1[0] == y1[1]:
                same_partition, same_normal = 1, y1
                opposite_normal = y2
            else:
                same_partition, same_normal = 2, y2
                opposite_normal = y1
            inward_endpoint = "L" if same_normal == (1, 1) else "U"
            if opposite_normal[0] != -opposite_normal[1]:
                raise AssertionError((epsilon_1, epsilon_2, opposite_normal))
            rows.append(
                {
                    "epsilon": [epsilon_1, epsilon_2],
                    "same_sign_pair_coordinate": same_partition,
                    "same_sign_normal": list(same_normal),
                    "pareto_inward_endpoint": inward_endpoint,
                    "other_normal": list(opposite_normal),
                    "other_boundary_direction": [1, 1]
                    if opposite_normal == (1, -1)
                    else [-1, -1],
                }
            )
    return rows


def polygon_vertices(constraints):
    """Vertices of a rational two-dimensional halfspace intersection."""

    vertices = set()
    for (a1, b1, c1), (a2, b2, c2) in itertools.combinations(constraints, 2):
        determinant = a1 * b2 - a2 * b1
        if determinant == 0:
            continue
        d1 = F(c1 * b2 - c2 * b1, determinant)
        d2 = F(a1 * c2 - a2 * c1, determinant)
        if all(a * d1 + b * d2 <= c for a, b, c in constraints):
            vertices.add((d1, d2))
    return tuple(sorted(vertices))


def pareto_vertices(constraints, vertices):
    efficient = []
    for vertex in vertices:
        clipped = constraints + ((1, 0, vertex[0]), (0, 1, vertex[1]))
        candidates = polygon_vertices(clipped)
        if min((a + b for a, b in candidates), default=sum(vertex)) == sum(vertex):
            efficient.append(vertex)
    return tuple(efficient)


def polygon_frontier_audit(samples=5000, seed=20260813):
    rng = random.Random(seed)
    checked = 0
    multiple = 0
    for _ in range(samples):
        epsilon_1 = rng.choice((-1, 1))
        epsilon_2 = rng.choice((-1, 1))
        same = (
            (epsilon_1, epsilon_2)
            if epsilon_1 == epsilon_2
            else (epsilon_1, -epsilon_2)
        )
        opposite = (
            (epsilon_1, -epsilon_2)
            if epsilon_1 == epsilon_2
            else (epsilon_1, epsilon_2)
        )
        upper_1, upper_2 = rng.randint(1, 8), rng.randint(1, 8)
        witness = (F(rng.randint(0, upper_1)), F(rng.randint(0, upper_2)))

        same_value = same[0] * witness[0] + same[1] * witness[1]
        opposite_value = opposite[0] * witness[0] + opposite[1] * witness[1]
        same_lower = same_value - rng.randint(0, 4)
        same_upper = same_value + rng.randint(0, 4)
        opposite_lower = opposite_value - rng.randint(0, 4)
        opposite_upper = opposite_value + rng.randint(0, 4)
        constraints = (
            (-1, 0, F(0)),
            (0, -1, F(0)),
            (1, 0, F(upper_1)),
            (0, 1, F(upper_2)),
            (same[0], same[1], same_upper),
            (-same[0], -same[1], -same_lower),
            (opposite[0], opposite[1], opposite_upper),
            (-opposite[0], -opposite[1], -opposite_lower),
        )
        vertices = polygon_vertices(constraints)
        efficient = pareto_vertices(constraints, vertices)
        checked += 1
        if len(efficient) <= 1:
            continue
        multiple += 1
        inward_sum = same_lower if same == (1, 1) else -same_upper
        if any(d1 + d2 != inward_sum for d1, d2 in efficient):
            raise AssertionError(
                (same, opposite, constraints, vertices, efficient, inward_sum)
            )
    return checked, multiple


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    pair_checks = pair_transfer_audit()
    block_checks = block_sum_audit()
    polygon_checks, nonsingleton_frontiers = polygon_frontier_audit()
    report = {
        "status": "weighted common-face rigidity identities verified",
        "evidence_class": "exact symbolic identities plus finite rational regression",
        "human_proof": (
            "block-diagonal Pigou--Dalton contraction and the two-dimensional "
            "Pareto-frontier argument (FEC6)--(FEC9)"
        ),
        "pair_transfer_checks": pair_checks,
        "block_diagonal_lorenz_checks": block_checks,
        "exact_dispersion_polygons_checked": polygon_checks,
        "nonsingleton_pareto_frontiers_checked": nonsingleton_frontiers,
        "orthants": orthant_table(),
        "scope": (
            "audits the algebra used by the dimension-free proof; it does not "
            "prove the remaining opposite-endpoint types III and IV"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
