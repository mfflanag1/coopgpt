"""Audit one canonical representative of every ratio-five leaf orbit."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import audit_ratio5_bad_leaf_gluing_n7 as gluing


def audit(orbit_payload):
    records = []
    for orbit in orbit_payload["orbits"]:
        collection = {
            int(mask):F(weight) for mask,weight in orbit["canonical_collection"]
        }
        singleton_weight = collection.pop(1 << gluing.A_PLAYER)
        assert singleton_weight > 0
        arm_ratio = collection[gluing.A]/singleton_weight
        gluing.BAD_FIRST_CORE = {
            mask:weight/singleton_weight for mask,weight in collection.items()
        }
        gluing.BAD_FIRST_MONO = F(1)
        result = gluing.audit()
        records.append({
            "orbit_index": orbit["orbit_index"],
            "orbit_record_count": orbit["record_count"],
            "arm_to_singleton_ratio": str(arm_ratio),
            "minimum_fixed_witness_capacity": result[
                "minimum_fixed_witness_capacity"
            ],
            "below_nine_eighths": result["below_nine_eighths"],
            "below_one": result["below_one"],
            "best_record": result["best_record"],
        })
    records.sort(key=lambda item:F(item["minimum_fixed_witness_capacity"]))
    return {
        "status": "exact canonical ratio-five leaf-orbit gluing audit",
        "leaf_orbit_count": len(records),
        "global_circuits_checked": 168*len(records),
        "minimum_fixed_witness_capacity": records[0][
            "minimum_fixed_witness_capacity"
        ],
        "orbits_below_nine_eighths": sum(
            F(record["minimum_fixed_witness_capacity"]) < F(9,8)
            for record in records
        ),
        "orbits_below_one": sum(
            F(record["minimum_fixed_witness_capacity"]) < 1
            for record in records
        ),
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",type=Path)
    parser.add_argument("--output",type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(audit(json.loads(args.input.read_text())),indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered,end="")
