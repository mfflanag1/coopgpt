#!/usr/bin/env python3
"""Exact counterexample to the corrected four-arm split-top classification."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_class_b_support_alternative import coalition_minimizer, mask
from audit_class_b_three_row_supports import (
    DOUBLE_COSTARS,
    HEAVY_BLOCK,
    PAIR,
    TARGET,
    split_matching_tight,
)
from audit_costar_saturation_dichotomy import coalition_sum
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet
from audit_menu_relaxed_root_exchange import ordered_saturated_roots
from audit_spectral_or_reserve import margins, selectors


N = 7
X = (F(6), F(4), F(2), F(2), F(2), F(2), F(2))
Z = tuple(F(value, 7) for value in (29, 29, 28, 28, 8, 9, 9))
TOP_ROWS = (23, 27, 39, 75, 114)
TOP_BOUNDS = (F(94, 7), F(94, 7), F(95, 7), F(95, 7), F(55, 7))
TOP_WEIGHTS = (F(1, 7), F(1, 7), F(2, 7), F(2, 7), F(1, 7))
CONSTRAINTS = dict(zip(TOP_ROWS, TOP_BOUNDS))
CONSTRAINTS.update({mask(0, 1, 2): F(12), mask(0, 1, 3): F(12), mask(0, 2, 3): F(10)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    minimize = coalition_minimizer(CONSTRAINTS)
    values = tuple(minimize(coalition) for coalition in range(1 << N))
    if any(values[1 << player] for player in range(N)):
        raise AssertionError("counterexample lost singleton normalization")
    x, z = selectors(values, N)
    if x != X or z != Z:
        raise AssertionError(("counterexample selectors changed", x, z))
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1 or roots[0][:3] != (0, (1, 2, 3), (4, 5, 6)):
        raise AssertionError(("counterexample root changed", roots))

    packet_margin = margins(values, x, z)["packet_margin"]
    direct = has_direct_packet(x, z, TARGET)
    pair_gap = coalition_sum(z, PAIR) - values[PAIR]
    heavy_gap = coalition_sum(z, HEAVY_BLOCK) - values[HEAVY_BLOCK]
    double_gaps = tuple(
        coalition_sum(z, row) - values[row] for row in DOUBLE_COSTARS
    )
    matching = split_matching_tight(values, z)
    if (
        packet_margin != F(-2, 7)
        or direct
        or pair_gap != F(29, 28)
        or heavy_gap != 0
        or double_gaps != (F(0), F(0), F(0), F(11, 7), F(11, 7), F(0))
        or matching
    ):
        raise AssertionError("counterexample classification changed")

    loads = tuple(
        sum(
            (weight for row, weight in zip(TOP_ROWS, TOP_WEIGHTS) if row >> player & 1),
            F(0),
        )
        for player in range(N)
    )
    if loads != (F(6, 7), F(1), F(3, 7), F(3, 7), F(3, 7), F(3, 7), F(3, 7)):
        raise AssertionError(("forked cover loads changed", loads))
    weighted_bound = sum(
        (weight * bound for weight, bound in zip(TOP_WEIGHTS, TOP_BOUNDS)), F(0)
    )
    if weighted_bound != F(89, 7):
        raise AssertionError("forked cover top bound changed")

    overlap = sum((min(left, right) for left, right in zip(x, z)), F(0))
    target = TARGET * sum(x, F(0))
    payload = {
        "claim": "exact refutation of the corrected four-arm classification",
        "defining_constraints": {str(row): str(bound) for row, bound in sorted(CONSTRAINTS.items())},
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "singleton_normalized": True,
        "ordered_saturated_single_heavy_s2": True,
        "packet_margin": str(packet_margin),
        "direct_packet_exists": False,
        "top_pair_gap": str(pair_gap),
        "heavy_block_gap": str(heavy_gap),
        "double_costar_gaps": [str(value) for value in double_gaps],
        "full_pxc78": False,
        "split_matching": False,
        "forked_cover": {
            "rows": list(TOP_ROWS),
            "weights": [str(value) for value in TOP_WEIGHTS],
            "eta": "3/7",
            "alpha": ["3/7", "4/7"],
            "weighted_bound": str(weighted_bound),
        },
        "classification_escape": True,
        "overlap": str(overlap),
        "hybrid_target": str(target),
        "hybrid_margin": str(overlap - target),
        "scope": (
            "refutes selection of top pair, full PXC78, PXC87 split matching, "
            "or direct packet; it does not refute the hybrid-overlap bound"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
