#!/usr/bin/env python3
"""Independent exact-LRA replay of the PXC46 aggregate facet filters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent


def decomposition_count(n, support):
    full = (1 << n) - 1
    count = 0
    for exceptional in range(1, full):
        if exceptional in support:
            continue
        weights = [z3.Real(f"w_{exceptional}_{j}") for j in range(len(support))]
        common = z3.Real(f"c_{exceptional}")
        solver = z3.Solver()
        solver.add(*(weight >= 0 for weight in weights))
        for player in range(n):
            load = z3.Sum(
                [
                    weight
                    for coalition, weight in zip(support, weights)
                    if coalition >> player & 1
                ]
            )
            solver.add(load - (1 if exceptional >> player & 1 else 0) == common)
        status = solver.check()
        if status == z3.unknown:
            raise AssertionError("Z3 returned unknown on decomposition test")
        count += status == z3.sat
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=HERE / "marked_hinge_deficiency_transfer_audit.json",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    primary = json.loads(args.input.read_text())
    rows = []
    for row in primary["aggregate_mixed_rooted_pair_facets"]:
        count = decomposition_count(6, row["support"])
        if count != row["decomposition_count"] or count:
            raise AssertionError((row["source"], row["trail"], count))
        rows.append(
            {
                "source": row["source"],
                "trail": row["trail"],
                "common_hinge": row["common_hinge"],
                "support": row["support"],
                "z3_decomposition_count": count,
                "primary_exact_lp_decomposition_count": row[
                    "decomposition_count"
                ],
                "agreement": True,
                "exact_cone_facet": True,
            }
        )
    report = {
        "status": "independent exact-LRA decomposition replay",
        "z3_version": z3.get_version_string(),
        "facet_count": len(rows),
        "all_counts_agree": all(row["agreement"] for row in rows),
        "all_supports_indecomposable": all(
            row["exact_cone_facet"] for row in rows
        ),
        "scope": "finite facet-filter cross-check; not a universal pricing theorem",
        "facets": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
