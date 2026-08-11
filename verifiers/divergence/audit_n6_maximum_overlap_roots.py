#!/usr/bin/env python3
"""Exact regression audit of the maximum-overlap root rule at n=6.

For every archived pair, extract one complete exact staged support for Lmin
and Lmax.  For each player maximizing min(Lmin_i,Lmax_i), solve the exact
three-generator rooted relaxation and test the sharp 2/3 threshold.

This is finite archive evidence only.  It is neither a census of all exact
games nor a proof of the maximum-overlap root conjecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import records  # noqa: E402
from audit_n6_equality_one_witness_roots import stage_support  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from verify_labelled_branch_duals import branch_system, one_witness_minimum  # noqa: E402


def audit_record(source, trail, values, x, z):
    n = len(x)
    total = sum(x, F(0))
    support_x, support_z = set(), set()
    for mode, point, support in (("min", x, support_x), ("max", z, support_z)):
        for stage, block in enumerate(payoff_blocks(point, mode)):
            for player in block:
                support.update(stage_support(values, point, mode, stage, player))
    case = {
        "x": x,
        "z": z,
        "g": (total,) + (F(0),) * (n - 1),
        "support_x": tuple(sorted(support_x)),
        "support_z": tuple(sorted(support_z)),
    }
    system = branch_system(case)
    coordinate_overlap = tuple(min(x[i], z[i]) for i in range(n))
    roots = tuple(
        i for i, value in enumerate(coordinate_overlap) if value == max(coordinate_overlap)
    )
    bounds = tuple(one_witness_minimum(system, root) for root in roots)
    target = F(2, 3)
    assert all(bound >= target for bound in bounds)
    actual_overlap = sum(coordinate_overlap, F(0)) / total
    return {
        "source": source.name,
        "trail": trail,
        "roots": roots,
        "bounds": bounds,
        "actual_overlap": actual_overlap,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for source in args.paths:
        data = json.loads(source.read_text())
        for parsed_source, trail, values, x, z in records(data, source):
            if len(x) == 6:
                rows.append(audit_record(parsed_source, trail, values, x, z))
    assert len(rows) == 374
    bounds = [bound for row in rows for bound in row["bounds"]]
    distribution = Counter(str(bound) for bound in bounds)
    target = F(2, 3)
    report = {
        "status": "exact rational regression audit; no maximum-overlap root failures",
        "archive_records": len(rows),
        "exact_root_lps": len(bounds),
        "failures": 0,
        "minimum_root_bound": str(min(bounds)),
        "sharp_target": str(target),
        "root_bound_distribution": dict(sorted(distribution.items())),
        "records_with_some_floor_root": sum(
            any(bound == target for bound in row["bounds"]) for row in rows
        ),
        "records_where_every_tested_root_matches_actual_overlap": sum(
            all(bound == row["actual_overlap"] for bound in row["bounds"])
            for row in rows
        ),
        "scope": (
            "374 archived n=6 pairs and one extracted basic staged-support system "
            "per pair; finite regression evidence only, not a domain theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
