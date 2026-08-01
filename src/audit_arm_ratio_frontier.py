"""Audit arm ratios, scalar recoloring, and exact-capacity arm ceilings."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from analyze_two_color_box_capacity import analyze, circuit_data
from audit_potential_guided_sources import CASES, type_i_payload
from audit_support_nullspace_structure import REPRESENTATIVE_FILES


def normalized_payload(payload):
    if "circuits" in payload:
        return payload
    if "deficient_records" in payload:
        geometry = payload["geometry"]
        return {
            "n": payload.get("n", geometry["n"]),
            "A_mask": payload.get("A_mask", geometry["A_mask"]),
            "B_mask": payload.get("B_mask", geometry["B_mask"]),
            "circuits": [
                {
                    "active_rows": item["active_rows"],
                    "circuit_weights": item["circuit_weights"],
                }
                for item in payload["deficient_records"]
            ],
        }
    circuits = [
        circuit
        for batch in payload["batches"]
        for circuit in batch["circuits"]
    ]
    return {
        "n": payload["n"],
        "A_mask": payload["A_mask"],
        "B_mask": payload["B_mask"],
        "circuits": circuits,
    }


def circuit_record(payload, index):
    _n, A, B, aggregate, required_A, required_B = circuit_data(payload, index)
    ratio_A = aggregate[A] / required_A
    ratio_B = aggregate[B] / required_B
    extra_A = aggregate[A] - required_A
    extra_B = aggregate[B] - required_B
    product_gap = extra_A * extra_B - required_A * required_B
    detail = payload["circuits"][index - 1]
    extra_A_games = set()
    extra_B_games = set()
    mono_A_count = 0
    mono_B_count = 0
    for meta, raw_weight in zip(detail["active_rows"], detail["circuit_weights"]):
        if not F(raw_weight):
            continue
        if meta[0] == "mono":
            mono_A_count += meta[-1] == A
            mono_B_count += meta[-1] == B
            continue
        game, coalition = int(meta[1]), int(meta[2])
        if coalition == A and game != 1:
            extra_A_games.add(game)
        if coalition == B and game != 2:
            extra_B_games.add(game)
    scalar_capacity = 1 / (1 / ratio_A + 1 / ratio_B)
    capacity = analyze(payload, index)
    assert capacity["primal_exact"] and capacity["dual_exact"]
    rho = F(capacity["capacity"])
    return {
        "required_A": required_A,
        "required_B": required_B,
        "ratio_A": ratio_A,
        "ratio_B": ratio_B,
        "scalar_capacity": scalar_capacity,
        "rho": rho,
        "deficient": rho < 1,
        "exclusive_arm": ratio_A == 1 or ratio_B == 1,
        "extra_A": extra_A,
        "extra_B": extra_B,
        "product_gap": product_gap,
        "extra_A_games": tuple(sorted(extra_A_games)),
        "extra_B_games": tuple(sorted(extra_B_games)),
        "mono_A_count": mono_A_count,
        "mono_B_count": mono_B_count,
    }


def source_record(path, exhaustive):
    payload = normalized_payload(json.loads(path.read_text()))
    records = [
        circuit_record(payload, index)
        for index in range(1, len(payload["circuits"]) + 1)
    ]
    ratios = Counter((item["ratio_A"], item["ratio_B"]) for item in records)
    copy_patterns = Counter(
        (
            item["extra_A_games"], item["extra_B_games"],
            "boundary" if item["product_gap"] == 0 else "strict",
        )
        for item in records if not item["exclusive_arm"]
    )
    return {
        "source": path.name,
        "exhaustive": exhaustive,
        "circuit_count": len(records),
        "scalar_recoloring_certifies_one": sum(
            item["scalar_capacity"] >= 1 for item in records
        ),
        "deficient_count": sum(item["deficient"] for item in records),
        "deficient_with_exclusive_arm": sum(
            item["deficient"] and item["exclusive_arm"] for item in records
        ),
        "deficient_without_exclusive_arm": sum(
            item["deficient"] and not item["exclusive_arm"] for item in records
        ),
        "one_monotonicity_row_per_arm": sum(
            item["mono_A_count"] == item["mono_B_count"] == 1
            for item in records
        ),
        "nonexclusive_product_boundary": sum(
            not item["exclusive_arm"] and item["product_gap"] == 0
            for item in records
        ),
        "nonexclusive_strict_product_success": sum(
            not item["exclusive_arm"] and item["product_gap"] > 0
            for item in records
        ),
        "nonexclusive_forbidden_product_gap": sum(
            not item["exclusive_arm"] and item["product_gap"] < 0
            for item in records
        ),
        "nonexclusive_cross_A_gap_nonnegative": sum(
            not item["exclusive_arm"]
            and item["extra_A"] >= item["required_B"]
            for item in records
        ),
        "nonexclusive_cross_B_gap_nonnegative": sum(
            not item["exclusive_arm"]
            and item["extra_B"] >= item["required_A"]
            for item in records
        ),
        "nonexclusive_both_cross_gaps_nonnegative": sum(
            not item["exclusive_arm"]
            and item["extra_A"] >= item["required_B"]
            and item["extra_B"] >= item["required_A"]
            for item in records
        ),
        "nonexclusive_cross_gap_violation": sum(
            not item["exclusive_arm"]
            and (
                item["extra_A"] < item["required_B"]
                or item["extra_B"] < item["required_A"]
            )
            for item in records
        ),
        "ratio_pairs": [
            {"ratio_A": str(left), "ratio_B": str(right), "count": count}
            for (left, right), count in sorted(ratios.items())
        ],
        "nonexclusive_copy_patterns": [
            {
                "extra_A_games": list(games_A),
                "extra_B_games": list(games_B),
                "product_gap_kind": kind,
                "count": count,
            }
            for (games_A, games_B, kind), count in sorted(copy_patterns.items())
        ],
    }


def canonical_ceiling_audit(results_dir):
    quotient = json.loads(
        (results_dir / "quotient_canonical_extreme_audit.json").read_text()
    )
    circuits = []
    payload, _capacity, index = type_i_payload(results_dir)
    circuits.append(("n5-Type-I", payload, index))
    circuits.extend(
        (label, json.loads((results_dir / circuit_name).read_text()), index)
        for label, circuit_name, _capacity_name, index in CASES
    )
    assert [label for label, _payload, _index in circuits] == [
        item["label"] for item in quotient["cases"]
    ]

    records = []
    for (label, payload, index), quotient_case in zip(circuits, quotient["cases"]):
        _n, A, B, aggregate, required_A, required_B = circuit_data(payload, index)
        exclusive = []
        if aggregate[A] == required_A:
            exclusive.append(A)
        if aggregate[B] == required_B:
            exclusive.append(B)
        extrema = [item["coalition"] for item in quotient_case["extreme_sets"]]
        records.append({
            "label": label,
            "exclusive_arms": exclusive,
            "extreme_sets": extrema,
            "each_extreme_has_unit_arm_ceiling": all(
                any(extreme != arm for arm in exclusive) for extreme in extrema
            ),
        })
    return {
        "case_count": len(records),
        "all_have_exclusive_arm": all(item["exclusive_arms"] for item in records),
        "all_extremes_have_unit_arm_ceiling": all(
            item["each_extreme_has_unit_arm_ceiling"] for item in records
        ),
        "records": records,
    }


def audit(results_dir, supplement_dir):
    sources = [
        source_record(supplement_dir / "circuit_frontier.json", True),
        source_record(supplement_dir / "circuit_frontier_221.json", True),
    ]
    sources.extend(
        source_record(results_dir / filename, False)
        for filename in REPRESENTATIVE_FILES
    )
    sources.append(
        source_record(
            results_dir / "forbidden_ratio_glued_circuit_n6.json", False
        )
    )
    sources.append(
        source_record(
            results_dir / "glued_local_circuit_hunt_n6_321.json", False
        )
    )
    return {
        "status": "exact arm-ratio and fixed-witness ceiling audit",
        "circuit_count": sum(item["circuit_count"] for item in sources),
        "scalar_recoloring_certifies_one": sum(
            item["scalar_recoloring_certifies_one"] for item in sources
        ),
        "deficient_count": sum(item["deficient_count"] for item in sources),
        "deficient_with_exclusive_arm": sum(
            item["deficient_with_exclusive_arm"] for item in sources
        ),
        "deficient_without_exclusive_arm": sum(
            item["deficient_without_exclusive_arm"] for item in sources
        ),
        "one_monotonicity_row_per_arm": sum(
            item["one_monotonicity_row_per_arm"] for item in sources
        ),
        "nonexclusive_product_boundary": sum(
            item["nonexclusive_product_boundary"] for item in sources
        ),
        "nonexclusive_strict_product_success": sum(
            item["nonexclusive_strict_product_success"] for item in sources
        ),
        "nonexclusive_forbidden_product_gap": sum(
            item["nonexclusive_forbidden_product_gap"] for item in sources
        ),
        "nonexclusive_cross_A_gap_nonnegative": sum(
            item["nonexclusive_cross_A_gap_nonnegative"] for item in sources
        ),
        "nonexclusive_cross_B_gap_nonnegative": sum(
            item["nonexclusive_cross_B_gap_nonnegative"] for item in sources
        ),
        "nonexclusive_both_cross_gaps_nonnegative": sum(
            item["nonexclusive_both_cross_gaps_nonnegative"] for item in sources
        ),
        "nonexclusive_cross_gap_violation": sum(
            item["nonexclusive_cross_gap_violation"] for item in sources
        ),
        "canonical_deficient_ceiling_audit": canonical_ceiling_audit(results_dir),
        "sources": sources,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--supplement-dir", type=Path, default=Path("paper/supplement")
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(args.results_dir, args.supplement_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
