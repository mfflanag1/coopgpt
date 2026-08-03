"""Focused exact classification of the only n=6 eta duals not covered by
the two-level separator theorem.

If eta<gamma, the floor multipliers w_i form a separator with at least three
distinct levels.  In a minimal balanced collection containing S, every
positive w_i is represented by the singleton {i}.  Minimality excludes all
target singletons at once, and the six-column rank bound leaves at most three
nonfloor coalitions.  This script exhausts only that small residual incidence
problem, in exact integer arithmetic.
"""
from __future__ import annotations

import itertools
import argparse
import json
import math
from pathlib import Path
from fractions import Fraction as F

if not __debug__:
    raise RuntimeError("certificate verification must not run with Python -O")


N = 6
FULL = (1 << N) - 1


def determinant(matrix):
    """Fraction-free Bareiss determinant for a small integer square matrix."""
    n = len(matrix)
    if n == 0:
        return 1
    work = [list(row) for row in matrix]
    sign = 1
    previous = 1
    for pivot in range(n - 1):
        swap = next((row for row in range(pivot, n) if work[row][pivot]), None)
        if swap is None:
            return 0
        if swap != pivot:
            work[pivot], work[swap] = work[swap], work[pivot]
            sign = -sign
        value = work[pivot][pivot]
        for row in range(pivot + 1, n):
            for column in range(pivot + 1, n):
                numerator = (
                    work[row][column] * value
                    - work[row][pivot] * work[pivot][column]
                )
                assert numerator % previous == 0
                work[row][column] = numerator // previous
            work[row][pivot] = 0
        previous = value
    return sign * work[-1][-1]


def balancing_weights(support):
    """Return primitive positive integer balancing weights, or None."""
    size = len(support)
    differences = [
        [int(mask >> (row + 1) & 1) - int(mask & 1) for mask in support]
        for row in range(N - 1)
    ]
    for rows in itertools.combinations(range(N - 1), size - 1):
        kernel = []
        for omitted in range(size):
            square = [
                [differences[row][column] for column in range(size) if column != omitted]
                for row in rows
            ]
            kernel.append((-1 if omitted % 2 else 1) * determinant(square))
        if not any(kernel):
            continue
        if kernel[0] < 0:
            kernel = [-value for value in kernel]
        if not all(value > 0 for value in kernel):
            continue
        if any(
            sum(differences[row][column] * kernel[column] for column in range(size))
            for row in range(N - 1)
        ):
            continue
        divisor = math.gcd(*kernel)
        return tuple(value // divisor for value in kernel)
    return None


def group_permutations(s_size):
    for inside in itertools.permutations(range(s_size)):
        for outside in itertools.permutations(range(s_size, N)):
            yield inside + outside


def permute_mask(mask, permutation):
    result = 0
    for old, new in enumerate(permutation):
        if mask >> old & 1:
            result |= 1 << new
    return result


def canonical_key(support, weights, s_size):
    encodings = []
    for permutation in group_permutations(s_size):
        terms = sorted(
            (permute_mask(mask, permutation), weight)
            for mask, weight in zip(support, weights)
        )
        encodings.append(tuple(terms))
    return min(encodings)


def members(mask):
    return [player + 1 for player in range(N) if mask >> player & 1]


def classify(s_size):
    target = (1 << s_size) - 1
    target_singletons = {1 << player for player in range(s_size)}
    candidates = [
        coalition for coalition in range(1, FULL)
        if coalition != target and coalition not in target_singletons
    ]
    checked = 0
    raw_three_level = 0
    orbits = {}

    # At least two positive singleton multipliers are needed for three levels.
    # Taking all target singletons together with 1_S is linearly dependent, so
    # q ranges only through s_size-1.  Target symmetry lets us fix their labels.
    for singleton_count in range(2, s_size):
        singleton_masks = tuple(1 << player for player in range(singleton_count))
        max_nonfloor = N - 1 - singleton_count
        for nonfloor_count in range(1, max_nonfloor + 1):
            for nonfloors in itertools.combinations(candidates, nonfloor_count):
                checked += 1
                support = (target,) + singleton_masks + nonfloors
                weights = balancing_weights(support)
                if weights is None:
                    continue
                target_weight = weights[0]
                floors = [F(0)] * s_size
                for index, player in enumerate(range(singleton_count), start=1):
                    floors[player] = F(weights[index], target_weight)
                if len(set(floors)) < 3:
                    continue
                raw_three_level += 1
                key = canonical_key(support, weights, s_size)
                orbits.setdefault(key, (support, weights, tuple(floors)))

    return {
        "S_size": s_size,
        "P_size": N - s_size,
        "focused_supports_checked": checked,
        "raw_three_level_supports_with_canonical_singletons": raw_three_level,
        "three_level_orbit_count": len(orbits),
        "orbits": [
            {
                "balanced_support": [
                    {"coalition": members(mask), "weight": str(F(weight, weights[0]))}
                    for mask, weight in zip(support, weights)
                ],
                "floor_multipliers": [str(value) for value in floors],
            }
            for support, weights, floors in orbits.values()
        ],
        "_keys": set(orbits),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    shapes = [classify(3), classify(4)]
    assert shapes[0]["three_level_orbit_count"] == 0
    assert shapes[1]["three_level_orbit_count"] == 1

    exceptional_support = (1, 2, 15, 20, 37, 56)
    exceptional_weights = (1, 2, 1, 1, 1, 2)
    expected_key = canonical_key(exceptional_support, exceptional_weights, 4)
    assert shapes[1]["_keys"] == {expected_key}

    for shape in shapes:
        del shape["_keys"]
    payload = {
        "status": "complete exact classification of n=6 three-level eta-dual supports",
        "reduction": (
            "every violating dual needs at least three distinct floor-multiplier levels; "
            "all such rank-six supports are classified here"
        ),
        "shapes": shapes,
        "exceptional_objective": "s(35)+s(136)+2*s(456)",
        "direct_bound": (
            "carrier C={4} gives s(456)-s(4)>=gamma, so the exceptional "
            "objective is at least 2*gamma"
        ),
    }
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
