"""Merge exact circuit enumeration/classification batches for the supplement."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build(enumeration_paths, classification_paths):
    assert len(enumeration_paths) == len(classification_paths)
    batches = []
    all_records = []
    shape = None
    rank = None
    maximum_support = None
    coefficient_floor = None
    for enum_path, class_path in zip(enumeration_paths, classification_paths):
        enumeration = json.loads(enum_path.read_text())
        classification = json.loads(class_path.read_text())
        assert enumeration["n"] == classification["n"]
        assert enumeration["A_mask"] == classification["A_mask"]
        assert enumeration["B_mask"] == classification["B_mask"]
        assert len(enumeration["circuits"]) == len(classification["orbits"])
        batch_shape = (
            enumeration["n"], enumeration["A_mask"], enumeration["B_mask"]
        )
        if shape is None:
            shape = batch_shape
            rank = enumeration["rank"]
            maximum_support = enumeration["circuit_support_bound"]
            coefficient_floor = enumeration["exact_epsilon"]
        assert batch_shape == shape
        assert enumeration["rank"] == rank
        assert enumeration["circuit_support_bound"] <= maximum_support
        assert enumeration["exact_epsilon"] == coefficient_floor
        records = []
        for index, (circuit, classified) in enumerate(
            zip(enumeration["circuits"], classification["orbits"]), 1
        ):
            assert classified["orbit_index"] == index
            assert circuit["support_size"] == classified["support_size"]
            assert circuit["orbit_size"] == classified["orbit_size"]
            record = dict(circuit)
            record["classification"] = classified["classification"]
            records.append(record)
        batches.append({
            "enumeration_file": enum_path.name,
            "classification_file": class_path.name,
            "enumeration_status": enumeration["status"],
            "seeded_both_sensitive_orbits": enumeration.get(
                "seeded_both_sensitive_orbits", 0
            ),
            "circuits": records,
        })
        all_records.extend(records)

    balanced = [
        record for record in all_records
        if record["classification"]["class"] == "balancedness-neutralized"
    ]
    bump_nonnegative = [
        record for record in all_records
        if record["classification"]["class"]
        == "balancedness-plus-bump-nonnegativity-neutralized"
    ]
    counterexamples = [
        record for record in all_records
        if record["classification"]["class"] == "balanced-counterexample"
    ]
    return {
        "status": "exact circuit and coefficientwise neutralization bundle",
        "n": shape[0],
        "A_mask": shape[1],
        "B_mask": shape[2],
        "rank": rank,
        "maximum_circuit_support": maximum_support,
        "normalized_positive_coefficient_floor": coefficient_floor,
        "enumeration_complete": batches[-1]["enumeration_status"]
        == "exact exhaustive enumeration completed",
        "exhaustive_through_support": maximum_support,
        "summary": {
            "circuit_orbits": len(all_records),
            "transported_supports": sum(record["orbit_size"] for record in all_records),
            "balancedness_neutralized_orbits": len(balanced),
            "balancedness_neutralized_supports": sum(
                record["orbit_size"] for record in balanced
            ),
            "balancedness_plus_bump_nonnegativity_neutralized_orbits": len(
                bump_nonnegative
            ),
            "balancedness_plus_bump_nonnegativity_neutralized_supports": sum(
                record["orbit_size"] for record in bump_nonnegative
            ),
            "balanced_counterexample_orbits": len(counterexamples),
            "balanced_counterexample_supports": sum(
                record["orbit_size"] for record in counterexamples
            ),
            "orbits_by_support": {
                str(support): sum(
                    record["support_size"] == support for record in all_records
                )
                for support in sorted({record["support_size"] for record in all_records})
            },
            "transported_supports_by_support": {
                str(support): sum(
                    record["orbit_size"] for record in all_records
                    if record["support_size"] == support
                )
                for support in sorted({record["support_size"] for record in all_records})
            },
        },
        "batches": batches,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--enumeration", type=Path, action="append", required=True)
    parser.add_argument("--classification", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    payload = build(args.enumeration, args.classification)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["summary"], indent=2))
