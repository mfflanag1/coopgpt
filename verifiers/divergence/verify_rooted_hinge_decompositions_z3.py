#!/usr/bin/env python3
"""Independent Z3 replay of rooted-completion decomposition counts.

The primary rooted-hinge verifier uses the project's exact rational LP
implementation.  This script reads only its emitted coalition supports and
reformulates the Studeny--Kratochvil exceptional-set test directly in Z3.
Agreement is a cross-check of the finite audit, not a proof of the human
singleton-slack completion theorem.
"""

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
        solver = z3.Solver()
        weights = [z3.Real(f"w_{exceptional}_{j}") for j in range(len(support))]
        common = z3.Real(f"c_{exceptional}")
        solver.add(*(weight >= 0 for weight in weights))
        for player in range(n):
            load = z3.Sum(
                [
                    weight
                    for coalition, weight in zip(support, weights)
                    if coalition >> player & 1
                ]
            )
            solver.add(
                load - (1 if exceptional >> player & 1 else 0) == common
            )
        count += solver.check() == z3.sat
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=HERE / "rooted_hinge_projection.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    primary = json.loads(args.input.read_text())
    rows = []
    for case in primary["cases"]:
        for root in case["roots"]:
            for cut_number, cut in enumerate(root["cuts"], start=1):
                completion = cut["semi_balanced_completion"]
                support = [
                    row["coalition"]
                    for row in completion["completion_coefficients"]
                ]
                count = decomposition_count(case["n"], support)
                if count != completion["decomposition_count"]:
                    raise AssertionError(
                        (case["name"], root["root"], cut_number, count)
                    )
                rows.append(
                    {
                        "case": case["name"],
                        "root": root["root"],
                        "cut": cut_number,
                        "support": support,
                        "z3_decomposition_count": count,
                        "exact_lp_decomposition_count": completion[
                            "decomposition_count"
                        ],
                        "agreement": True,
                    }
                )
    report = {
        "status": "independent Z3 decomposition replay",
        "arithmetic": "exact rational linear arithmetic",
        "cut_count": len(rows),
        "all_counts_agree": all(row["agreement"] for row in rows),
        "all_completions_decomposable": all(
            row["z3_decomposition_count"] > 0 for row in rows
        ),
        "cuts": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
