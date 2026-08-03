"""Compact exact verifier for the conceptual n=6 three-level classification.

The proof quotients the balanced-support incidence columns by the target
column and its positive target singletons.  What remains is a matrix with at
most three columns.  Equal balanced degrees become equal subset sums of a
positive weight vector.  This script exhausts only those reduced row patterns,
not coalition supports or exact-game cones.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(matrix):
    work = [[F(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                work[row][j] - scale * work[pivot_row][j]
                for j in range(columns)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def unique_solution(matrix, rhs):
    """Return the unique solution of an overdetermined exact system."""
    rows = len(matrix)
    columns = len(matrix[0])
    work = [
        [F(value) for value in matrix[row]] + [F(rhs[row])]
        for row in range(rows)
    ]
    pivot_row = 0
    pivot_columns = []
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                work[row][j] - scale * work[pivot_row][j]
                for j in range(columns + 1)
            ]
        pivot_columns.append(column)
        pivot_row += 1
    if any(all(not work[row][column] for column in range(columns))
           and work[row][-1] for row in range(rows)):
        return None
    if len(pivot_columns) != columns:
        return None
    answer = [F(0)] * columns
    for row, column in enumerate(pivot_columns):
        answer[column] = work[row][-1]
    return tuple(answer)


def subset_sums(weights):
    return sorted({
        sum(weights[j] for j in range(len(weights)) if mask >> j & 1)
        for mask in range(1 << len(weights))
    })


def max_lower_height_count(weights):
    sums = subset_sums(weights)
    return max(
        (sum(value < height for value in sums) for height in sums if height < 1),
        default=0,
    )


def canonical_binary_matrix(matrix):
    rows = len(matrix)
    columns = len(matrix[0])
    images = []
    for row_permutation in itertools.permutations(range(rows)):
        for column_permutation in itertools.permutations(range(columns)):
            images.append(tuple(
                tuple(matrix[row_permutation[i]][column_permutation[j]]
                      for j in range(columns))
                for i in range(rows)
            ))
    return min(images)


def full_target_quotient(outside_size):
    """Cases where S plus its target singletons span every target row."""
    maximum_columns = outside_size
    records = {}
    for columns in range(1, maximum_columns + 1):
        for bits in itertools.product((0, 1), repeat=outside_size * columns):
            matrix = tuple(
                tuple(bits[row * columns + column] for column in range(columns))
                for row in range(outside_size)
            )
            if rank(matrix) != columns:
                continue
            weights = unique_solution(matrix, [1] * outside_size)
            if weights is None or not all(value > 0 for value in weights):
                continue
            key = canonical_binary_matrix(matrix)
            records.setdefault(key, {
                "columns": columns,
                "matrix": [list(row) for row in key],
                "weights": [str(value) for value in weights],
                "max_distinct_subset_heights_below_zero_floor":
                    max_lower_height_count(weights),
            })
    return list(records.values())


def q2_short_cases():
    """The 4+2 split with two floor columns and at most two others."""
    maximum = 0
    feasible_patterns = 0
    for columns in (1, 2):
        row_types = tuple(itertools.product((0, 1), repeat=4))
        for column_data in itertools.product(row_types, repeat=columns):
            a3 = [column[0] for column in column_data]
            a4 = [column[1] for column in column_data]
            outside5 = [column[2] for column in column_data]
            outside6 = [column[3] for column in column_data]
            quotient = [
                [a3[j] - a4[j] for j in range(columns)],
                outside5,
                outside6,
            ]
            if rank(quotient) != columns:
                continue
            weights = unique_solution(quotient, [0, 1, 1])
            if weights is None or not all(value > 0 for value in weights):
                continue
            height3 = sum(weights[j] * a3[j] for j in range(columns))
            height4 = sum(weights[j] * a4[j] for j in range(columns))
            if height3 != height4 or height3 >= 1:
                continue
            feasible_patterns += 1
            lower = sum(value < height3 for value in subset_sums(weights))
            maximum = max(maximum, lower)
    return feasible_patterns, maximum


def canonical_four_row_columns(columns):
    images = []
    for swap_zero in (False, True):
        for swap_outside in (False, True):
            transformed = []
            for a3, a4, outside5, outside6 in columns:
                if swap_zero:
                    a3, a4 = a4, a3
                if swap_outside:
                    outside5, outside6 = outside6, outside5
                transformed.append((a3, a4, outside5, outside6))
            images.append(tuple(sorted(transformed)))
    return min(images)


def q2_three_column_cases():
    """The only full-rank quotient where three floor levels can survive."""
    row_types = tuple(itertools.product((0, 1), repeat=4))
    orbits = {}
    for columns in itertools.combinations(row_types, 3):
        quotient_columns = [
            (column[0] - column[1], column[2], column[3])
            for column in columns
        ]
        quotient = [
            [quotient_columns[column][row] for column in range(3)]
            for row in range(3)
        ]
        if rank(quotient) != 3:
            continue
        weights = unique_solution(quotient, [0, 1, 1])
        if weights is None or not all(value > 0 for value in weights):
            continue
        height3 = sum(weights[j] * columns[j][0] for j in range(3))
        height4 = sum(weights[j] * columns[j][1] for j in range(3))
        if height3 != height4 or height3 >= 1:
            continue
        lower_heights = [
            value for value in subset_sums(weights) if value < height3
        ]
        if len(lower_heights) < 2:
            continue
        key = canonical_four_row_columns(columns)
        orbits.setdefault(key, {
            "zero_and_outside_column_patterns": [list(column) for column in key],
            "normalized_nonfloor_weights": [str(value) for value in weights],
            "zero_floor_height": str(height3),
            "available_positive_floor_heights": [str(value) for value in lower_heights],
        })
    return list(orbits.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    three_plus_three = full_target_quotient(3)
    require(len(three_plus_three) == 4,
            "unexpected reduced 3+3 orbit count across one to three columns")
    require(max(record["max_distinct_subset_heights_below_zero_floor"]
                for record in three_plus_three) <= 1,
            "a 3+3 quotient permits three floor levels")

    four_plus_two_q3 = full_target_quotient(2)
    require(len(four_plus_two_q3) == 2,
            "unexpected reduced 4+2 q=3 orbit count")
    require(max(record["max_distinct_subset_heights_below_zero_floor"]
                for record in four_plus_two_q3) == 0,
            "the q=3 case unexpectedly permits a positive floor")

    short_count, short_maximum = q2_short_cases()
    require(short_count > 0, "short q=2 audit was vacuous")
    require(short_maximum <= 1,
            "a short q=2 quotient permits three floor levels")

    exceptional = q2_three_column_cases()
    require(len(exceptional) == 1,
            "the full q=2 quotient is not a unique orbit")
    record = exceptional[0]
    require(sorted(record["normalized_nonfloor_weights"])
            == ["1/3", "1/3", "2/3"], "wrong exceptional weights")
    require(record["zero_floor_height"] == "2/3",
            "wrong exceptional zero-floor height")
    require(record["available_positive_floor_heights"] == ["0", "1/3"],
            "wrong exceptional lower heights")

    reconstructed_columns = (
        (1, 1, 1, 1, 0, 0),  # S
        (1, 0, 0, 0, 0, 0),  # e1
        (0, 1, 0, 0, 0, 0),  # e2
        (0, 0, 1, 0, 1, 0),  # 35
        (1, 0, 1, 0, 0, 1),  # 136
        (0, 0, 0, 1, 1, 1),  # 456
    )
    reconstructed_weights = (1, 1, 2, 1, 1, 2)
    reconstructed_matrix = [
        [reconstructed_columns[column][player] for column in range(6)]
        for player in range(6)
    ]
    require(rank(reconstructed_matrix) == 6,
            "reconstructed balanced support is not minimal")
    require(all(
        sum(reconstructed_weights[column]
            * reconstructed_columns[column][player]
            for column in range(6)) == 3
        for player in range(6)
    ), "reconstructed balanced identity is false")

    payload = {
        "status": "compact exact matrix classification verified",
        "method": (
            "quotient by S and positive target singletons; classify equal "
            "subset sums of at most three positive weights"
        ),
        "three_plus_three": {
            "reduced_orbits_by_column_count": three_plus_three,
            "three_level_orbits": 0,
        },
        "four_plus_two": {
            "three_positive_floor_case": four_plus_two_q3,
            "two_floor_short_feasible_patterns": short_count,
            "two_floor_short_maximum_lower_height_count": short_maximum,
            "three_level_orbits": exceptional,
        },
        "reconstructed_balanced_identity": (
            "1_S + e_1 + 2e_2 + 1_35 + 1_136 + 2*1_456 = 3*1_N"
        ),
        "conclusion": (
            "no three-level eta-dual vertex exists in the 3+3 split; "
            "the displayed 4+2 support is unique up to target/outside permutations"
        ),
    }
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
