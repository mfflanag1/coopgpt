#!/usr/bin/env python3
"""Exact audit of weighted water filling on one-, two-, and three-role cores.

The human theorem is that every three-role TU core is a box intersected with
efficiency, and the clipped weighted equalizer Lorenz-dominates every feasible
repeated per-capita vector.  This script checks the formula and all weighted
Lorenz partial sums on a finite integer grid by enumerating every box vertex.
It is a regression/falsification audit, not a premise of the theorem.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in compositions(total - first, parts - 1):
            yield (first,) + tail


def weighted_water_fill(weights, lower, upper, total):
    breakpoints = sorted(
        {F(lower[i], weights[i]) for i in range(len(weights))}
        | {F(upper[i], weights[i]) for i in range(len(weights))}
    )
    candidates = breakpoints + [
        (breakpoints[i] + breakpoints[i + 1]) / 2
        for i in range(len(breakpoints) - 1)
    ]
    for probe in candidates:
        free = [
            i
            for i in range(len(weights))
            if F(lower[i], weights[i]) <= probe <= F(upper[i], weights[i])
        ]
        fixed = sum(
            (
                F(lower[i])
                if probe < F(lower[i], weights[i])
                else F(upper[i])
                if probe > F(upper[i], weights[i])
                else F(0)
                for i in range(len(weights))
            ),
            F(0),
        )
        free_weight = sum((weights[i] for i in free), 0)
        if not free_weight:
            continue
        level = F(total - fixed, free_weight)
        point = tuple(
            max(F(lower[i]), min(F(upper[i]), F(weights[i]) * level))
            for i in range(len(weights))
        )
        if sum(point, F(0)) == total:
            return point
    raise AssertionError((weights, lower, upper, total, "water fill failed"))


def box_vertices(lower, upper, total):
    roles = len(lower)
    vertices = set()
    for free in range(roles):
        fixed_roles = [i for i in range(roles) if i != free]
        for sides in itertools.product((0, 1), repeat=len(fixed_roles)):
            point = [None] * roles
            for i, side in zip(fixed_roles, sides):
                point[i] = F(upper[i] if side else lower[i])
            point[free] = F(total) - sum(
                (point[i] for i in fixed_roles), F(0)
            )
            if F(lower[free]) <= point[free] <= F(upper[free]):
                vertices.add(tuple(point))
    return tuple(sorted(vertices))


def repeated(point, weights):
    return tuple(
        value / weight
        for value, weight in zip(point, weights)
        for _ in range(weight)
    )


def lower_sums(vector):
    ordered = sorted(vector)
    total = F(0)
    result = []
    for value in ordered:
        total += value
        result.append(total)
    return tuple(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = 0
    vertices_checked = 0
    equality_rows = 0
    for roles in (1, 2, 3):
        for atomic_total in range(roles, 9):
            for weights in compositions(atomic_total, roles):
                for lower in itertools.product(range(3), repeat=roles):
                    for widths in itertools.product(range(3), repeat=roles):
                        upper = tuple(lower[i] + widths[i] for i in range(roles))
                        for total in range(sum(lower), sum(upper) + 1):
                            vertices = box_vertices(lower, upper, F(total))
                            if not vertices:
                                continue
                            candidate = weighted_water_fill(
                                weights, lower, upper, F(total)
                            )
                            candidate_sums = lower_sums(repeated(candidate, weights))
                            for vertex in vertices:
                                vertex_sums = lower_sums(repeated(vertex, weights))
                                if any(a < b for a, b in zip(candidate_sums, vertex_sums)):
                                    raise AssertionError(
                                        (weights, lower, upper, total, candidate, vertex)
                                    )
                            rows += 1
                            vertices_checked += len(vertices)
                            equality_rows += len(set(vertices)) == 1

    report = {
        "status": "exact weighted box water-filling audit passed",
        "role_range": "1..3",
        "atomic_weight_range": "number of roles..8",
        "integer_lower_bounds": "0..2",
        "integer_box_widths": "0..2",
        "feasible_box_rows": rows,
        "vertices_checked": vertices_checked,
        "singleton_box_rows": equality_rows,
        "human_theorem": (
            "every at-most-three-role TU core is a box intersected with "
            "efficiency; its clipped weighted equalizer Lorenz-dominates all "
            "feasible repeated per-capita role vectors, so weighted Lmin=Lmax"
        ),
        "scope": (
            "finite exact arithmetic regression grid; the exchange/water-filling "
            "argument is the dimension-free proof in the role weights"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
