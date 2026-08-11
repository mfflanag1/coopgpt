#!/usr/bin/env python3
"""Independent Z3 replay of rooted-completion decomposition counts.

The primary rooted-hinge verifier uses the project's exact rational LP
implementation.  This script reads only its emitted singleton-slack and
rooted-pair coalition supports and reformulates the Studeny--Kratochvil
exceptional-set test directly in Z3.
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


def sharp_pair_lift_support(p, k):
    n = 1 + p + k
    root = 1
    outside = tuple(range(1, p + 1))
    block = tuple(range(p + 1, n))
    hinges = []
    for omitted in block:
        coalition = root
        for player in block:
            if player != omitted:
                coalition |= 1 << player
        hinges.append(coalition)
    pairs = [root | (1 << player) for player in outside]
    return n, tuple(sorted(hinges + pairs + [root]))


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
                pair_lifted = completion["pair_lifted_completion"]
                pair_lifted_support = [
                    row["coalition"] for row in pair_lifted["coefficients"]
                ]
                pair_lifted_count = decomposition_count(
                    case["n"], pair_lifted_support
                )
                if pair_lifted_count != pair_lifted["decomposition_count"]:
                    raise AssertionError(
                        (
                            case["name"],
                            root["root"],
                            cut_number,
                            "pair_lifted",
                            pair_lifted_count,
                        )
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
                        "pair_lifted_support": pair_lifted_support,
                        "z3_pair_lifted_decomposition_count": pair_lifted_count,
                        "exact_lp_pair_lifted_decomposition_count": pair_lifted[
                            "decomposition_count"
                        ],
                        "pair_lifted_agreement": True,
                        "pair_lifted_exact_cone_facet": pair_lifted_count == 0,
                    }
                )
    sharp_grid = []
    for p in range(1, 4):
        for k in range(2, 5):
            n, support = sharp_pair_lift_support(p, k)
            count = decomposition_count(n, support)
            if count:
                raise AssertionError(("sharp_pair_lift", p, k, count))
            sharp_grid.append(
                {
                    "p": p,
                    "k": k,
                    "n": n,
                    "support": list(support),
                    "z3_decomposition_count": count,
                    "indecomposable": True,
                }
            )
    report = {
        "status": "independent Z3 decomposition replay",
        "arithmetic": "exact rational linear arithmetic",
        "cut_count": len(rows),
        "all_counts_agree": all(row["agreement"] for row in rows),
        "all_pair_lifted_counts_agree": all(
            row["pair_lifted_agreement"] for row in rows
        ),
        "all_completions_decomposable": all(
            row["z3_decomposition_count"] > 0 for row in rows
        ),
        "pair_lifted_facet_count": sum(
            row["pair_lifted_exact_cone_facet"] for row in rows
        ),
        "sharp_family_finite_bug_audit": sharp_grid,
        "sharp_family_grid_is_not_proof": True,
        "cuts": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
