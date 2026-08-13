#!/usr/bin/env python3
"""Exact scope control for common-face versus singleton endowments.

The role game is singleton-normalized and exact, and both weighted selectors
lie on the same two pair-slab endpoints.  Nevertheless the maximal
nonnegative extension of their common line has positive effective endowment
on a unit-weight role.  This refutes only the inference from role singleton
normalization to face normalization; its overlap is safely above the atomic
target.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from lexsimplex import lex_point_with_trace  # noqa: E402

import explore_weighted_four_role_faces as faces  # noqa: E402

WEIGHTS = (3, 1, 1, 1)
GENERATORS = (
    (F(0), F(5), F(3), F(4)),
    (F(0), F(3), F(5), F(4)),
    (F(2), F(4), F(3), F(3)),
    (F(5), F(0), F(7), F(0)),
    (F(0), F(5), F(0), F(7)),
)
EXPECTED_VALUES = tuple(
    map(F, (0, 0, 0, 3, 0, 0, 5, 5, 0, 4, 0, 5, 6, 7, 7, 12))
)
EXPECTED_ROLE_LMIN = (F(9, 2), F(3, 2), F(7, 2), F(5, 2))
EXPECTED_ROLE_LMAX = (F(4), F(2), F(3), F(3))
BLOCKS = ((0, 1, 2), (3,), (4,), (5,))


def completed_role_mask(coalition):
    return sum(
        1 << role
        for role, block in enumerate(BLOCKS)
        if all(coalition >> player & 1 for player in block)
    )


def clone_witness(role_point, coalition):
    allocation = [F(0)] * 6
    for role, block in enumerate(BLOCKS):
        if all(coalition >> player & 1 for player in block):
            allocation[block[0]] = role_point[role]
        elif any(coalition >> player & 1 for player in block):
            outside = next(player for player in block if not (coalition >> player & 1))
            allocation[outside] = role_point[role]
        else:
            allocation[block[0]] = role_point[role]
    return tuple(allocation)


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def encode_atomic_trace(trace):
    return [
        {
            "level": str(row["level"]),
            "newly_pinned": list(row["newly_pinned"]),
        }
        for row in trace
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values = faces.role_values(GENERATORS)
    if values != EXPECTED_VALUES or not faces.exact_role_game(values):
        raise AssertionError(("role exactness", values))
    if any(values[1 << role] != 0 for role in range(4)):
        raise AssertionError("role game is not singleton-normalized")

    role_lmin, lmin_trace = faces.weighted_lex_point(values, WEIGHTS, "min")
    role_lmax, lmax_trace = faces.weighted_lex_point(values, WEIGHTS, "max")
    if role_lmin != EXPECTED_ROLE_LMIN or role_lmax != EXPECTED_ROLE_LMAX:
        raise AssertionError((role_lmin, role_lmax))
    active_lmin = faces.active_pair_endpoints(values, role_lmin)
    active_lmax = faces.active_pair_endpoints(values, role_lmax)
    common = active_lmin & active_lmax
    labels = [(0, "U"), (2, "U")]
    if not set(labels).issubset(common):
        raise AssertionError(("common face", active_lmin, active_lmax))
    direction, endowments, width = faces.common_face_ambient_endowments(
        role_lmin, labels
    )
    if direction != (1, -1, 1, -1) or endowments != tuple(map(F, (1, 0, 0, 1))):
        raise AssertionError((direction, endowments, width))
    if endowments[3] == 0 or WEIGHTS[3] != 1:
        raise AssertionError("missing unit-role face-endowment obstruction")

    clone_values = tuple(values[completed_role_mask(S)] for S in range(1 << 6))
    for coalition in range(1 << 6):
        mask = completed_role_mask(coalition)
        role_point = next(
            point for point in GENERATORS if faces.coalition_sum(point, mask) == values[mask]
        )
        witness = clone_witness(role_point, coalition)
        if coalition_sum(witness, coalition) != clone_values[coalition]:
            raise AssertionError(("clone attainment", coalition))
        if any(
            coalition_sum(witness, other) < clone_values[other]
            for other in range(1 << 6)
        ):
            raise AssertionError(("clone core witness", coalition))

    atomic_lmin, atomic_lmin_trace = lex_point_with_trace(6, clone_values, "min")
    atomic_lmax, atomic_lmax_trace = lex_point_with_trace(6, clone_values, "max")
    expected_atomic_lmin = (F(3, 2),) * 4 + (F(7, 2), F(5, 2))
    expected_atomic_lmax = (F(4, 3),) * 3 + (F(2), F(3), F(3))
    if tuple(atomic_lmin) != expected_atomic_lmin:
        raise AssertionError(("atomic Lmin", atomic_lmin))
    if tuple(atomic_lmax) != expected_atomic_lmax:
        raise AssertionError(("atomic Lmax", atomic_lmax))
    overlap = sum(min(a, b) for a, b in zip(role_lmin, role_lmax))
    if overlap != 11 or overlap / values[15] != F(11, 12):
        raise AssertionError(("overlap", overlap))

    report = {
        "status": "common-face endowment scope control verified exactly",
        "role_weights": list(WEIGHTS),
        "lower_envelope_generators": [[str(value) for value in row] for row in GENERATORS],
        "role_values_binary_order": [str(value) for value in values],
        "role_singletons_zero": True,
        "weighted_lmin_role_totals": [str(value) for value in role_lmin],
        "weighted_lmax_role_totals": [str(value) for value in role_lmax],
        "common_pair_endpoints": [list(label) for label in labels],
        "common_line_direction": list(direction),
        "ambient_nonnegative_endowments": [str(value) for value in endowments],
        "ambient_nonnegative_width": str(width),
        "unit_role_with_positive_face_endowment": 3,
        "role_lmin_trace": faces.encode_trace(lmin_trace),
        "role_lmax_trace": faces.encode_trace(lmax_trace),
        "clone_coalitions_and_witnesses_checked": 1 << 6,
        "atomic_lmin": [str(value) for value in atomic_lmin],
        "atomic_lmax": [str(value) for value in atomic_lmax],
        "atomic_lmin_trace": encode_atomic_trace(atomic_lmin_trace),
        "atomic_lmax_trace": encode_atomic_trace(atomic_lmax_trace),
        "total": str(values[15]),
        "overlap": str(overlap),
        "overlap_ratio": str(overlap / values[15]),
        "six_player_target": "2/3",
        "scope": (
            "refutes automatic passage from zero role singletons to zero "
            "unit-role endowments on a common face; does not refute the target"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
