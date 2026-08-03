"""Record exact primal patterns in quotient-canonical extreme-set repairs."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from analyze_two_color_box_capacity import analyze, circuit_data
from audit_potential_guided_sources import CASES, type_i_payload


def relation(coalition, U, A, B):
    return {
        "coalition": coalition,
        "size": coalition.bit_count(),
        "intersection_U": (coalition & U).bit_count(),
        "contains_U": coalition & U == U,
        "contained_in_U": coalition & U == coalition,
        "is_A": coalition == A,
        "is_B": coalition == B,
    }


def repair_record(payload, index, extreme):
    n, A, B, aggregate, required_A, required_B = circuit_data(payload, index)
    U = extreme["coalition"]
    repair = analyze(payload, index, U)
    assert repair["primal_exact"] and repair["dual_exact"]
    selected = []
    for raw_coalition, raw_weight in repair["subcollection"].items():
        coalition, weight = int(raw_coalition), F(raw_weight)
        item = relation(coalition, U, A, B)
        item.update({
            "weight": str(weight),
            "aggregate_weight": str(aggregate[coalition]),
            "box_fraction": str(weight / aggregate[coalition]),
        })
        selected.append(item)
    fractions = Counter(item["box_fraction"] for item in selected)
    exclusive = []
    if aggregate[A] == required_A:
        exclusive.append("A")
    if aggregate[B] == required_B:
        exclusive.append("B")
    return {
        "kind": extreme["kind"],
        "n": n,
        "A": A,
        "B": B,
        "U": U,
        "U_size": U.bit_count(),
        "exclusive_arms": exclusive,
        "capacity": repair["capacity"],
        "alpha": repair["alpha"],
        "delta": repair["delta"],
        "selected_support_size": len(selected),
        "box_fraction_counts": dict(sorted(fractions.items())),
        "selected": selected,
    }


def audit(results_dir):
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
    cases = []
    for (label, payload, index), quotient_case in zip(circuits, quotient["cases"]):
        assert label == quotient_case["label"]
        cases.append({
            "label": label,
            "repairs": [
                repair_record(payload, index, extreme)
                for extreme in quotient_case["extreme_sets"]
            ],
        })
    repairs = [repair for case in cases for repair in case["repairs"]]
    fraction_profiles = Counter(
        tuple(repair["box_fraction_counts"].items()) for repair in repairs
    )
    return {
        "status": "exact quotient-canonical primal repair pattern audit",
        "case_count": len(cases),
        "repair_count": len(repairs),
        "negative_delta_count": sum(F(item["delta"]) < 0 for item in repairs),
        "positive_delta_count": sum(F(item["delta"]) > 0 for item in repairs),
        "maximum_negative_delta_count": sum(
            item["kind"] == "maximum" and F(item["delta"]) < 0
            for item in repairs
        ),
        "minimum_positive_delta_count": sum(
            item["kind"] == "minimum" and F(item["delta"]) > 0
            for item in repairs
        ),
        "fraction_profile_count": len(fraction_profiles),
        "fraction_profiles": [
            {"profile": dict(profile), "count": count}
            for profile, count in fraction_profiles.most_common()
        ],
        "cases": cases,
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
