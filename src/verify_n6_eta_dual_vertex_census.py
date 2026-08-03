"""Independent structural checks for the complete n=6 eta-dual census."""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path

if not __debug__:
    raise RuntimeError("certificate verification must not run with Python -O")


N = 6
EXPECTED_RAW_COUNTS = {3: 21_695, 4: 19_501}
EXPECTED_ORBIT_COUNTS = {3: 870, 4: 619}


def player_permutations(s_size):
    for inside in itertools.permutations(range(s_size)):
        for outside in itertools.permutations(range(s_size, N)):
            yield inside + outside


def permute_mask(mask, permutation):
    return sum(
        1 << permutation[player]
        for player in range(N)
        if mask >> player & 1
    )


def canonical(terms, s_size):
    return min(
        tuple(sorted(
            (permute_mask(mask, permutation), weight)
            for mask, weight in terms.items()
            if weight
        ))
        for permutation in player_permutations(s_size)
    )


def rational_rank(matrix):
    matrix = [[F(value) for value in row] for row in matrix]
    height = len(matrix)
    width = len(matrix[0]) if matrix else 0
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (row for row in range(pivot_row, height)
             if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
        for row in range(height):
            if row == pivot_row or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == height:
            break
    return pivot_row


def verify_shape(shape, sample_path):
    s_size = int(shape["S_size"])
    target = (1 << s_size) - 1
    expected_checked = sum(math.comb(61, size - 1) for size in range(2, 7))
    assert shape["supports_checked"] == expected_checked == 6_508_883
    assert sum(shape["raw_count_by_support_size"].values()) == (
        shape["raw_minimal_balanced_collections"]
    )
    if shape["raw_minimal_balanced_collections"] != EXPECTED_RAW_COUNTS[s_size]:
        raise ValueError("raw minimal-balanced count differs from the pinned census")
    if shape["orbit_count"] != EXPECTED_ORBIT_COUNTS[s_size]:
        raise ValueError("orbit count differs from the pinned census")

    census_keys = set()
    for orbit in shape["orbits"]:
        terms = {
            int(term["mask"]): F(term["weight"])
            for term in orbit["balanced_support"]
        }
        assert terms[target] == 1
        assert 2 <= len(terms) <= N
        degrees = [
            sum(weight for mask, weight in terms.items() if mask >> player & 1)
            for player in range(N)
        ]
        assert len(set(degrees)) == 1 and degrees[0] == F(orbit["degree"])
        incidence = [
            [int(mask >> player & 1) for mask in terms]
            for player in range(N)
        ]
        # Linear independence is equivalent to minimality for a positive
        # balanced support.
        assert rational_rank(incidence) == len(terms)
        key = canonical(terms, s_size)
        assert key not in census_keys
        census_keys.add(key)
    assert len(census_keys) == shape["orbit_count"]

    sample = json.loads(sample_path.read_text())
    sample_keys = set()
    for orbit in sample["orbits"]:
        terms = {target: F(1)}
        for term in orbit["lambda_support"]:
            mask = sum(1 << (player - 1) for player in term["coalition"])
            terms[mask] = terms.get(mask, F(0)) + F(term["coefficient"])
        for player, weight in enumerate(orbit["floor_weights"]):
            if F(weight):
                mask = 1 << player
                terms[mask] = terms.get(mask, F(0)) + F(weight)
        sample_keys.add(canonical(terms, s_size))
    assert len(sample_keys) == sample["distinct_sampled_orbits"]
    assert sample_keys <= census_keys
    return {
        "S_size": s_size,
        "supports_checked": expected_checked,
        "pinned_raw_minimal_balanced_collections": EXPECTED_RAW_COUNTS[s_size],
        "verified_orbit_count": len(census_keys),
        "previous_sample_orbits_all_recovered": len(sample_keys),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    census = json.loads(args.census.read_text())
    assert census["n"] == N
    if {int(shape["S_size"]) for shape in census["shapes"]} != {3, 4}:
        raise ValueError("census must contain exactly the 3+3 and 4+2 splits")
    records = []
    for shape in census["shapes"]:
        s_size = int(shape["S_size"])
        records.append(verify_shape(
            shape,
            args.results_dir / f"n6_s{s_size}_eta_dual_orbit_sample.json",
        ))
    payload = {
        "status": "independent structural verification passed",
        "checks": [
            "complete bounded-support combination count",
            "exact balancing equations",
            "exact incidence rank and minimality",
            "symmetry-orbit uniqueness",
            "recovery of every previously sampled orbit",
        ],
        "shapes": records,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
