#!/usr/bin/env python3
"""Exact sparse-support attack on the corrected s=2 classification.

The universal classification is not assumed here.  The verifier freezes a
direct-packet-failing selector profile with the same saturated Lmin point as
PXC87, enumerates every strictly positive-top normalized over-cover on one
through five nonsingleton rows compatible with the selector comparison, and
lifts one representative of every exact symmetry orbit.

This is an exhaustive theorem for the stated selector-profile/minimal-lift
cell only.  It is a falsification gate for the universal conjecture, not a
proof of it.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_class_b_support_alternative import coalition_minimizer, mask
from audit_costar_saturation_dichotomy import coalition_sum
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet
from audit_menu_relaxed_root_exchange import ordered_saturated_roots
from audit_spectral_or_reserve import margins, selectors


N = 7
X = (F(6), F(4), F(2), F(2), F(2), F(2), F(2))
Z = (F(29, 7), F(29, 7), F(27, 7), F(27, 7), F(4, 7), F(12, 7), F(12, 7))
TARGET = F(7, 12)
R, H, A, B = 0, 1, 2, 3
OUTSIDERS = (4, 5, 6)
PAIR = mask(R, H)
HEAVY_BLOCK = mask(H, *OUTSIDERS)
DOUBLE_COSTARS = tuple(sorted({
    mask(R, H, other, outsider)
    for other in (A, B)
    for outsider in OUTSIDERS
}))
LMIN_ROWS = {
    mask(R, H, A): F(12),
    mask(R, H, B): F(12),
    mask(R, A, B): F(10),
}


def solve_overdetermined(
    matrix: list[list[F]], rhs: list[F], variable_count: int
):
    """Return the unique rational solution, if it exists."""
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    pivot_row = 0
    pivots = []
    for column in range(variable_count):
        pivot = next(
            (row for row in range(pivot_row, len(augmented))
             if augmented[row][column]),
            None,
        )
        if pivot is None:
            continue
        augmented[pivot_row], augmented[pivot] = (
            augmented[pivot], augmented[pivot_row]
        )
        scale = augmented[pivot_row][column]
        augmented[pivot_row] = [value / scale for value in augmented[pivot_row]]
        for row in range(len(augmented)):
            if row == pivot_row or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                left - scale * right
                for left, right in zip(augmented[row], augmented[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
    if any(
        not any(row[:variable_count]) and row[variable_count]
        for row in augmented
    ):
        return None
    if len(pivots) != variable_count:
        return None
    solution = [F(0)] * variable_count
    for row, column in enumerate(pivots):
        solution[column] = augmented[row][variable_count]
    return tuple(solution)


def normalized_cover(rows: tuple[int, ...]):
    """Solve for positive row weights and the common non-top load eta."""
    matrix = []
    rhs = []
    for player in range(2, N):
        matrix.append([
            *(F(int(bool(row >> player & 1))) for row in rows),
            F(-1),
        ])
        rhs.append(F(0))
    matrix.append([
        *(F(int(bool(row & 1)) + int(bool(row & 2))) for row in rows),
        F(-2),
    ])
    rhs.append(F(1))
    solution = solve_overdetermined(matrix, rhs, len(rows) + 1)
    if solution is None:
        return None
    weights = solution[:-1]
    eta = solution[-1]
    root_load = sum(
        (weight for weight, row in zip(weights, rows) if row >> R & 1), F(0)
    )
    heavy_load = sum(
        (weight for weight, row in zip(weights, rows) if row >> H & 1), F(0)
    )
    alpha = (root_load - eta, heavy_load - eta)
    if (
        min(weights) <= 0
        or eta < 0
        or min(alpha) < 0
        or sum(alpha, F(0)) != 1
    ):
        return None
    return weights, eta, alpha


def normalized_three_row_cover(rows: tuple[int, int, int]):
    """Backward-compatible wrapper used by the discovery replay."""
    return normalized_cover(rows)


def split_matching_tight(values, z) -> bool:
    for first in OUTSIDERS:
        for second in OUTSIDERS:
            if first == second:
                continue
            remaining = next(iter(set(OUTSIDERS) - {first, second}))
            rows = (
                mask(R, H, B, first),
                mask(R, H, A, second),
                mask(H, remaining),
            )
            if all(coalition_sum(z, row) == values[row] for row in rows):
                return True
    return False


def classify_lift(rows: tuple[int, ...]) -> dict:
    constraints = {row: coalition_sum(Z, row) for row in rows}
    constraints.update(LMIN_ROWS)
    minimize = coalition_minimizer(constraints)
    singletons = tuple(minimize(1 << player) for player in range(N))
    result = {
        "rows": list(rows),
        "singleton_values": [str(value) for value in singletons],
    }
    if any(singletons):
        result["status"] = "singleton normalization fails"
        return result
    values = tuple(minimize(coalition) for coalition in range(1 << N))
    x, z = selectors(values, N)
    roots = ordered_saturated_roots(values, x, z)
    result.update({
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "ordered_saturated_roots": len(roots),
    })
    if not roots:
        result["status"] = "ordered saturated root fails"
        return result
    packet_margin = margins(values, x, z)["packet_margin"]
    direct = has_direct_packet(x, z, TARGET)
    pair_tight = coalition_sum(z, PAIR) == values[PAIR]
    pxc78 = (
        coalition_sum(z, HEAVY_BLOCK) == values[HEAVY_BLOCK]
        and all(coalition_sum(z, row) == values[row] for row in DOUBLE_COSTARS)
    )
    matching = split_matching_tight(values, z)
    result.update({
        "status": "qualified",
        "packet_margin": str(packet_margin),
        "direct": direct,
        "top_pair_tight": pair_tight,
        "pxc78_full": pxc78,
        "split_matching": matching,
        "classification_escape": packet_margin < 0 and not (
            direct or pair_tight or pxc78 or matching
        ),
    })
    return result


def incidence_key(coalition: int) -> tuple[int, ...]:
    return tuple((coalition >> player) & 1 for player in range(2, N)) + (
        int(bool(coalition >> R & 1)) + int(bool(coalition >> H & 1)),
    )


def permute_mask(coalition: int, permutation: tuple[int, ...]) -> int:
    answer = 0
    for player in range(N):
        if coalition >> player & 1:
            answer |= 1 << permutation[player]
    return answer


SYMMETRIES = tuple(
    tuple(
        ({A: B, B: A}.get(player, player) if swap_sub else player)
        for player in range(N)
    )
    for swap_sub in (False, True)
)
SYMMETRIES = tuple(
    tuple(
        ({5: 6, 6: 5}.get(player, player) if swap_out else player)
        for player in permutation
    )
    for permutation in SYMMETRIES
    for swap_out in (False, True)
)


def canonical_rows(rows: tuple[int, ...]) -> tuple[int, ...]:
    return min(
        tuple(sorted(permute_mask(row, permutation) for row in rows))
        for permutation in SYMMETRIES
    )


def incidence_cover(rows: tuple[int, ...]):
    """Solve the top-summed incidence equations before choosing top labels."""
    integer_matrix = []
    integer_rhs = []
    for player in range(2, N):
        integer_matrix.append([
            *(int(bool(row >> player & 1)) for row in rows),
            -1,
        ])
        integer_rhs.append(0)
    integer_matrix.append([
        *(int(bool(row & 1)) + int(bool(row & 2)) for row in rows),
        -2,
    ])
    integer_rhs.append(1)

    # This filter only rejects systems that are visibly rank-deficient,
    # inconsistent, or sign-infeasible.  Every survivor is solved again over
    # Q below.  The matrices are 0/1/-1 with at most six rows; the generous
    # tolerance also sends every numerical boundary case to the exact path.
    float_matrix = np.asarray(integer_matrix, dtype=float)
    float_rhs = np.asarray(integer_rhs, dtype=float)
    approximate, _, rank, _ = np.linalg.lstsq(
        float_matrix, float_rhs, rcond=None
    )
    if rank != len(rows) + 1:
        return None
    residual = np.max(np.abs(float_matrix @ approximate - float_rhs))
    if residual > 1e-9:
        return None
    if min(approximate[:-1]) < -1e-9 or approximate[-1] < -1e-9:
        return None

    matrix = [[F(value) for value in row] for row in integer_matrix]
    rhs = [F(value) for value in integer_rhs]
    solution = solve_overdetermined(matrix, rhs, len(rows) + 1)
    if solution is None or min(solution[:-1]) <= 0 or solution[-1] < 0:
        return None
    return solution


def support_orbit_census(
    compatible: tuple[int, ...], support_size: int
) -> dict:
    """Exhaust one nonsingleton support size, quotienting exact symmetries."""
    columns: dict[tuple[int, ...], list[int]] = {}
    for coalition in compatible:
        if coalition.bit_count() >= 2:
            columns.setdefault(incidence_key(coalition), []).append(coalition)
    column_items = tuple(columns.items())
    positive_column_covers = 0
    row_covers = set()
    for indices in itertools.combinations(
        range(len(column_items)), support_size
    ):
        representatives = tuple(column_items[index][1][0] for index in indices)
        if incidence_cover(representatives) is None:
            continue
        positive_column_covers += 1
        for rows in itertools.product(
            *(column_items[index][1] for index in indices)
        ):
            rows = tuple(sorted(rows))
            cover = normalized_cover(rows)
            if cover is not None and min(cover[2]) > 0:
                row_covers.add(rows)

    orbits: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
    for rows in row_covers:
        orbits.setdefault(canonical_rows(rows), []).append(rows)
    results = []
    orbit_status = Counter()
    row_status = Counter()
    negative = []
    escapes = []
    qualified = []
    mechanism_counts = Counter()
    for representative, members in sorted(orbits.items()):
        result = classify_lift(representative)
        result["orbit_size"] = len(members)
        results.append(result)
        orbit_status[result["status"]] += 1
        row_status[result["status"]] += len(members)
        if result["status"] == "qualified":
            qualified.append(result)
            mechanisms = tuple(
                name for name in (
                    "direct", "top_pair_tight", "pxc78_full", "split_matching"
                ) if result[name]
            )
            mechanism_counts["+".join(mechanisms) or "none"] += 1
        if result["status"] == "qualified" and F(result["packet_margin"]) < 0:
            negative.append(result)
        if result.get("classification_escape"):
            escapes.append(result)
    if escapes:
        raise AssertionError({
            f"{support_size}-row classification escape": escapes
        })
    expected = {
        1: (1, 1, {"qualified": 1}, 0),
        2: (6, 2, {"qualified": 2}, 0),
        3: (
            66,
            20,
            {"singleton normalization fails": 16, "qualified": 4},
            0,
        ),
        4: (
            312,
            96,
            {"singleton normalization fails": 92, "qualified": 4},
            0,
        ),
        5: (
            2576,
            719,
            {"singleton normalization fails": 717, "qualified": 2},
            2,
        ),
    }
    expected_rows, expected_orbits, expected_status, expected_negative = (
        expected[support_size]
    )
    if (
        len(columns) != 52
        or len(row_covers) != expected_rows
        or len(orbits) != expected_orbits
        or orbit_status != expected_status
        or len(negative) != expected_negative
        or any(not (
            result["direct"]
            or result["top_pair_tight"]
            or result["pxc78_full"]
            or result["split_matching"]
        ) for result in qualified)
        or any(not result["top_pair_tight"] for result in negative)
    ):
        raise AssertionError({
            "support_size": support_size,
            "columns": len(columns),
            "positive_column_covers": positive_column_covers,
            "row_covers": len(row_covers),
            "orbits": len(orbits),
            "status": dict(orbit_status),
            "negative": len(negative),
            "qualified_unclassified": [
                result for result in qualified
                if not (
                    result["direct"]
                    or result["top_pair_tight"]
                    or result["pxc78_full"]
                    or result["split_matching"]
                )
            ],
        })
    return {
        "support_size": support_size,
        "incidence_columns": len(columns),
        "positive_column_covers": positive_column_covers,
        "expanded_row_covers": len(row_covers),
        "symmetry_orbits": len(orbits),
        "orbit_status_counts": dict(sorted(orbit_status.items())),
        "row_cover_status_counts": dict(sorted(row_status.items())),
        "qualified_mechanism_counts": dict(sorted(mechanism_counts.items())),
        "qualified_packet_violations": negative,
        "classification_escapes": 0,
    }


def direct_failing_matching_calibration() -> dict:
    matching_rows = (
        mask(R, H, B, 4),
        mask(R, H, A, 5),
        mask(H, 6),
    )
    constraints = {row: coalition_sum(Z, row) for row in matching_rows}
    constraints.update(LMIN_ROWS)
    constraints.update({
        mask(R, H, A, 6): coalition_sum(Z, mask(R, H, A, 6)),
        mask(R, H, B, 6): coalition_sum(Z, mask(R, H, B, 6)),
    })
    minimize = coalition_minimizer(constraints)
    values = tuple(minimize(coalition) for coalition in range(1 << N))
    x, z = selectors(values, N)
    packet_margin = margins(values, x, z)["packet_margin"]
    pair_gap = coalition_sum(z, PAIR) - values[PAIR]
    heavy_gap = coalition_sum(z, HEAVY_BLOCK) - values[HEAVY_BLOCK]
    double_gaps = tuple(
        coalition_sum(z, row) - values[row] for row in DOUBLE_COSTARS
    )
    if (
        x != X
        or z != Z
        or any(values[1 << player] for player in range(N))
        or packet_margin != F(-1, 7)
        or has_direct_packet(x, z, TARGET)
        or not split_matching_tight(values, z)
        or pair_gap != F(4, 7)
        or heavy_gap != F(16, 7)
        or double_gaps != (
            F(5, 7), F(0), F(0), F(13, 7), F(0), F(0)
        )
    ):
        raise AssertionError("direct-failing PXC87 calibration changed")
    return {
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "packet_margin": "-1/7",
        "direct": False,
        "split_matching": True,
        "top_pair_gap": str(pair_gap),
        "heavy_block_gap": str(heavy_gap),
        "double_costar_gaps": [str(value) for value in double_gaps],
        "pxc87_is_nonredundant": True,
        "overlap_target_margin": str(
            sum((min(left, right) for left, right in zip(x, z)), F(0))
            - TARGET * sum(x, F(0))
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    compatible = tuple(
        coalition
        for coalition in range(1, (1 << N) - 1)
        if coalition_sum(X, coalition) >= coalition_sum(Z, coalition)
    )
    censuses = {}
    for support_size in range(1, 6):
        print(f"auditing support size {support_size}", file=sys.stderr)
        censuses[str(support_size)] = support_orbit_census(
            compatible, support_size
        )

    payload = {
        "claim": "exact direct-failing sparse-support attack",
        "calibration": direct_failing_matching_calibration(),
        "compatible_rows": len(compatible),
        "support_censuses": censuses,
        "classification_escapes": 0,
        "scope": (
            "exhaustive for one- through five-row nonsingleton top covers "
            "compatible with the fixed direct-failing selector profile, with "
            "strictly positive weights on both top coordinates and exact "
            "minimal lifts of every symmetry orbit; not a universal support "
            "classification"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
