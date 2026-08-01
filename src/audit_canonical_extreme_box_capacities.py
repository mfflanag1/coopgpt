"""Audit the reduced dual potential's maximum/minimum sets on all cases."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from analyze_two_color_box_capacity import analyze
from audit_potential_guided_sources import CASES, type_i_payload


def record(label, circuit, three_color_capacity, index):
    reduced = analyze(circuit, index)
    assert reduced["primal_exact"] and reduced["dual_exact"]
    ordinary = three_color_capacity["circuits"][index - 1]["capacity"]
    extrema = []
    for kind, U in (
        ("maximum", reduced["maximum_set"]),
        ("minimum", reduced["minimum_set"]),
    ):
        result = analyze(circuit, index, U)
        assert result["primal_exact"] and result["dual_exact"]
        extrema.append({
            "kind": kind,
            "coalition": U,
            "capacity": result["capacity"],
            "repairs_full_bumps": result["repairs_full_bumps"],
            "alpha": result["alpha"],
            "delta": result["delta"],
            "support_size": len(result["subcollection"]),
        })
    return {
        "label": label,
        "three_color_capacity": ordinary,
        "reduced_two_color_capacity": reduced["capacity"],
        "capacities_match": F(ordinary) == F(reduced["capacity"]),
        "ordinary_dual_potential": reduced["player_potential"],
        "ordinary_dual_potential_sum": reduced["potential_sum"],
        "extreme_sets": extrema,
        "maximum_extreme_capacity": str(max(F(item["capacity"]) for item in extrema)),
    }


def audit(results_dir):
    records = []
    circuit, capacity, index = type_i_payload(results_dir)
    records.append(record("n5-Type-I", circuit, capacity, index))
    for label, circuit_name, capacity_name, index in CASES:
        circuit = json.loads((results_dir / circuit_name).read_text())
        capacity = json.loads((results_dir / capacity_name).read_text())
        records.append(record(label, circuit, capacity, index))
    return {
        "status": "exact canonical extreme-set box-capacity audit",
        "case_count": len(records),
        "all_reduced_capacities_match_three_color_capacities": all(
            item["capacities_match"] for item in records
        ),
        "all_extreme_set_pairs_repair": all(
            F(item["maximum_extreme_capacity"]) >= 1 for item in records
        ),
        "minimum_maximum_extreme_capacity": str(min(
            F(item["maximum_extreme_capacity"]) for item in records
        )),
        "all_maximum_extreme_capacities_equal_one": all(
            F(item["maximum_extreme_capacity"]) == 1 for item in records
        ),
        "successful_cases_by_extreme": {
            kind: sum(
                next(extreme for extreme in item["extreme_sets"]
                     if extreme["kind"] == kind)["repairs_full_bumps"]
                for item in records
            )
            for kind in ("maximum", "minimum")
        },
        "all_extreme_capacities_are_ordinary_or_one": all(
            F(extreme["capacity"]) in {F(item["reduced_two_color_capacity"]), F(1)}
            for item in records for extreme in item["extreme_sets"]
        ),
        "failed_extreme_set_count": sum(
            not extreme["repairs_full_bumps"]
            for item in records for extreme in item["extreme_sets"]
        ),
        "cases": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(args.results_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
