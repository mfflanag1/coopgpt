#!/usr/bin/env python3
"""Independent Z3 replay of mixed-packet decomposition counts.

The primary cutting-plane verifier uses the project's exact rational simplex.
This script reads only its emitted coalition supports and reformulates every
Studeny--Kratochvil exceptional-set feasibility test in exact Z3 linear real
arithmetic.  Agreement is a finite cross-check, not a proof of the human
mixed-witness projection theorem.
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
        weights = [z3.Real(f"w_{n}_{exceptional}_{j}") for j in range(len(support))]
        common = z3.Real(f"c_{n}_{exceptional}")
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
        count += solver.check() == z3.sat
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=HERE / "mixed_witness_projection.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    primary = json.loads(args.input.read_text())
    rows = []
    for case in primary["cases"]:
        for root in case["roots"]:
            for cut_number, cut in enumerate(root["cuts"], start=1):
                projected = [row["coalition"] for row in cut["projected_completion"]]
                projected_count = decomposition_count(case["n"], projected)
                if projected_count != cut["projected_decomposition_count"]:
                    raise AssertionError(
                        (case["name"], root["root"], cut_number, "projected", projected_count)
                    )
                pair = [
                    row["coalition"]
                    for row in cut["rooted_pair_shear"]["completion"]
                ]
                pair_count = decomposition_count(case["n"], pair)
                if pair_count != cut["rooted_pair_shear"]["decomposition_count"]:
                    raise AssertionError(
                        (case["name"], root["root"], cut_number, "pair", pair_count)
                    )
                rows.append(
                    {
                        "case": case["name"],
                        "root": root["root"],
                        "cut": cut_number,
                        "uses_both_colours": len(
                            {row["selection"] for row in cut["tagged_support"]}
                        )
                        > 1,
                        "projected_support": projected,
                        "z3_projected_decomposition_count": projected_count,
                        "exact_lp_projected_decomposition_count": cut[
                            "projected_decomposition_count"
                        ],
                        "pair_support": pair,
                        "z3_pair_decomposition_count": pair_count,
                        "exact_lp_pair_decomposition_count": cut["rooted_pair_shear"][
                            "decomposition_count"
                        ],
                        "pair_exact_cone_facet": pair_count == 0,
                        "agreement": True,
                    }
                )
    mixed = [row for row in rows if row["uses_both_colours"]]
    if len(mixed) != 1 or not mixed[0]["pair_exact_cone_facet"]:
        raise AssertionError("expected unique mixed-colour facet control changed")
    report = {
        "status": "independent exact-LRA mixed-packet decomposition replay",
        "cut_count": len(rows),
        "all_counts_agree": all(row["agreement"] for row in rows),
        "pair_exact_cone_facet_count": sum(row["pair_exact_cone_facet"] for row in rows),
        "mixed_colour_cut_count": len(mixed),
        "mixed_colour_pair_lift_is_facet": True,
        "scope": "finite decomposition cross-check only",
        "cuts": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
