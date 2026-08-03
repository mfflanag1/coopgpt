"""Audit generalized recoloring capacities at the two arm-potential top sets."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from analyze_single_witness_capacity import analyze
from audit_potential_guided_sources import CASES, type_i_payload


def top_set(capacity_detail, game):
    vector = [F(value) for value in
              capacity_detail["dual_obstruction"]["game_player_potentials"][game]]
    maximum = max(vector)
    return sum(1 << player for player, value in enumerate(vector)
               if value == maximum)


def record(label, circuit, capacity, index):
    detail = capacity["circuits"][index - 1]
    tops = []
    for game in (1, 2):
        U = top_set(detail, game)
        grand = (1 << circuit["n"]) - 1
        if U in (0, grand):
            tops.append({
                "game": game,
                "coalition": None,
                "capacity": None,
                "repairs_full_bumps": False,
                "block_count": None,
            })
            continue
        result = analyze(circuit, index, U)
        assert result["primal_exact"] and result["dual_exact"]
        two_bumped = analyze(circuit, index, U, exclude_base=True)
        if two_bumped.get("capacity") is not None:
            assert two_bumped["primal_exact"] and two_bumped["dual_exact"]
        zero_sum = analyze(
            circuit, index, U, exclude_base=True, zero_total_defect=True,
        )
        if zero_sum.get("capacity") is not None:
            assert zero_sum["primal_exact"] and zero_sum["dual_exact"]
        tops.append({
            "game": game,
            "coalition": U,
            "capacity": result["capacity"],
            "repairs_full_bumps": result["repairs_full_bumps"],
            "block_count": len(result["blocks"]),
            "blocks": [
                {
                    "game": block["game"],
                    "alpha": block["alpha"],
                    "delta": block["delta"],
                    "support_size": len(block["collection"]),
                }
                for block in result["blocks"]
            ],
            "two_bumped_games_capacity": two_bumped.get("capacity"),
            "two_bumped_games_repair": two_bumped.get("repairs_full_bumps", False),
            "two_bumped_games_blocks": [
                {
                    "game": block["game"],
                    "alpha": block["alpha"],
                    "delta": block["delta"],
                    "support_size": len(block["collection"]),
                }
                for block in two_bumped.get("blocks", ())
            ],
            "zero_sum_two_bumped_games_capacity": zero_sum.get("capacity"),
            "zero_sum_two_bumped_games_repair": zero_sum.get(
                "repairs_full_bumps", False
            ),
        })
    capacities = [F(item["capacity"]) for item in tops
                  if item["capacity"] is not None]
    assert capacities
    return {
        "label": label,
        "ordinary_capacity": detail["capacity"],
        "top_sets": tops,
        "maximum_top_capacity": str(max(capacities)),
        "sum_top_capacities": str(sum(capacities, F(0))),
        "top_capacity_excess_sum": str(sum(
            (value - 1 for value in capacities), F(0)
        )),
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
        "status": "exact two-top-set generalized capacity audit",
        "case_count": len(records),
        "all_exact": True,
        "all_maximum_top_capacities_at_least_one": all(
            F(item["maximum_top_capacity"]) >= 1 for item in records
        ),
        "minimum_maximum_top_capacity": str(min(
            F(item["maximum_top_capacity"]) for item in records
        )),
        "minimum_sum_top_capacities": str(min(
            F(item["sum_top_capacities"]) for item in records
        )),
        "full_repair_top_sets_using_two_bumped_games_only": sum(
            set(block["game"] for block in top.get("blocks", ())) == {1, 2}
            for item in records for top in item["top_sets"]
            if top["repairs_full_bumps"]
        ),
        "full_repair_top_set_count": sum(
            top["repairs_full_bumps"]
            for item in records for top in item["top_sets"]
        ),
        "cases_with_two_bumped_games_top_set_repair": sum(
            any(top.get("two_bumped_games_repair", False)
                for top in item["top_sets"])
            for item in records
        ),
        "all_two_bumped_top_repairs_have_zero_total_defect": all(
            sum(F(block["delta"])
                for block in top.get("two_bumped_games_blocks", ())) == 0
            for item in records for top in item["top_sets"]
            if top.get("two_bumped_games_repair", False)
        ),
        "cases_with_zero_sum_two_bumped_games_top_set_repair": sum(
            any(top.get("zero_sum_two_bumped_games_repair", False)
                for top in item["top_sets"])
            for item in records
        ),
        "minimum_maximum_zero_sum_two_bumped_games_capacity": str(min(
            max(F(top["zero_sum_two_bumped_games_capacity"])
                for top in item["top_sets"]
                if top.get("zero_sum_two_bumped_games_capacity") is not None)
            for item in records
        )),
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
