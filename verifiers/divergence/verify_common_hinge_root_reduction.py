#!/usr/bin/env python3
"""Exact hostile controls for the common-hinge rooted reduction.

Replace every fixed Lmax support by its intersection with the complete fixed
Lmin support.  Thus the only retained Lmax tightness rows turn common tight
coalitions into x(S)=z(S)<=w^r(S) hinges.  Recompute every rooted one-witness
minimum on five hostile branches and two sharp-family orientations.

These are seven fixed-support controls, not an all-n theorem.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from verify_labelled_branch_duals import CASES, branch_system, one_witness_minimum


EXPECTED = {
    "optimized_label_free_spectral_failure": (
        (52, 57),
        (F(25, 34),) * 7,
    ),
    "actual_top_fixed_failure": (
        (21, 47, 79),
        (F(7, 10),) * 7,
    ),
    "top_and_bottom_fixed_failure": (
        (6, 12, 122),
        (F(2, 3),) * 7,
    ),
    "coefficient_two_congestion_failure": (
        (24, 44),
        (F(16, 25), F(16, 25), F(16, 25), F(9, 11), F(16, 25), F(9, 11), F(16, 25)),
    ),
    "primitive_coefficient_seven_failure": (
        (9, 70, 85, 90, 104, 151, 165, 176, 204),
        (F(113, 161), F(11, 19), F(11, 19), F(11, 19), F(3, 5), F(11, 19), F(181, 261), F(2, 3)),
    ),
    "sharp_family_p2_k4": (
        (22, 38, 57, 70, 89, 105, 113),
        (F(7, 12),) + (F(7, 15),) * 6,
    ),
    "sharp_family_p3_k3": (
        (46, 49, 78, 81, 97),
        (F(7, 12),) + (F(7, 16),) * 6,
    ),
}


def audit_case(case0):
    case = dict(case0)
    common = tuple(sorted(set(case["support_x"]).intersection(case["support_z"])))
    case["support_z"] = common
    system = branch_system(case)
    n = len(case["x"])
    bounds = tuple(one_witness_minimum(system, root) for root in range(n))
    expected_common, expected_bounds = EXPECTED[case["name"]]
    if common != expected_common or bounds != expected_bounds:
        raise AssertionError(f"common-hinge control changed for {case['name']}")

    coordinate_overlap = tuple(min(case["x"][i], case["z"][i]) for i in range(n))
    roots = tuple(
        i for i, value in enumerate(coordinate_overlap) if value == max(coordinate_overlap)
    )
    target = F(n, (n * n) // 4)
    if any(bounds[root] < target for root in roots):
        raise AssertionError(f"maximum-overlap common-hinge root failed for {case['name']}")
    return {
        "name": case["name"],
        "n": n,
        "common_support": list(common),
        "maximum_overlap_roots": list(roots),
        "all_root_bounds": [str(q) for q in bounds],
        "target": str(target),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact fixed-support common-hinge controls; all maximum-overlap roots pass",
        "cases": [audit_case(case) for case in CASES],
        "scope": (
            "five hostile fixed branches and two sharp-family orientations; exact rational "
            "falsification evidence only, not an all-n proof"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
