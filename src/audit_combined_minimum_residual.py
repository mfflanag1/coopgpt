"""Deduplicated exact evidence audit for the multilevel carrier conjecture."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def coalition_sum(values, mask):
    return sum(
        values[player] for player in range(len(values))
        if mask >> player & 1
    )


def normalize_record(record, source):
    if "v" in record:
        n = record["n"]
        worths = [F(value) for value in record["v"]]
        phi = [F(value) for value in record["phi"]]
        target = sum(1 << (player - 1) for player in record["S"])
        outside = ((1 << n) - 1) ^ target
        candidates = []
        for one_indexed in record["minimum_residual_players"]:
            player = one_indexed - 1
            face = 1 << player
            carrier = outside | face
            gain = phi[player] - worths[face]
            carrier_slack = coalition_sum(phi, carrier) - worths[carrier]
            candidates.append({
                "player": one_indexed,
                "margin": carrier_slack - gain,
                "certifies": carrier_slack <= gain,
            })
    else:
        payload = json.loads(Path(record["path"]).read_text())
        n = payload["n"]
        worths = [F(value) for value in payload["v"]]
        target = sum(1 << (player - 1) for player in record["S"])
        candidates = [
            {
                "player": item["player"],
                "margin": F(item["carrier_slack"]) - F(item["face_slack"]),
                "certifies": item["carrier_explains"],
            }
            for item in record["candidates"]
        ]
    return {
        "key": (tuple(worths), target),
        "n": n,
        "S": [player + 1 for player in range(n) if target >> player & 1],
        "source": source,
        "candidates": candidates,
    }


def audit(paths):
    deduplicated = {}
    raw_count = 0
    for path in paths:
        payload = json.loads(path.read_text())
        for record in payload.get("records", []):
            raw_count += 1
            normalized = normalize_record(record, str(path))
            key = normalized.pop("key")
            if key not in deduplicated:
                normalized["sources"] = [str(path)]
                deduplicated[key] = normalized
            elif str(path) not in deduplicated[key]["sources"]:
                deduplicated[key]["sources"].append(str(path))
    records = list(deduplicated.values())
    for record in records:
        record["some_carrier"] = any(
            item["certifies"] for item in record["candidates"]
        )
        record["all_carriers"] = all(
            item["certifies"] for item in record["candidates"]
        )
    candidates = [item for record in records for item in record["candidates"]]
    return {
        "status": "deduplicated exact multilevel minimum-residual audit",
        "arithmetic": (
            "all inputs are exact-certification outputs; carrier margins "
            "recomputed as Fractions"
        ),
        "input_files": [str(path) for path in paths],
        "raw_case_count": raw_count,
        "duplicate_case_count": raw_count - len(records),
        "unique_case_count": len(records),
        "n_counts": {
            str(n): sum(record["n"] == n for record in records)
            for n in sorted({record["n"] for record in records})
        },
        "minimum_residual_candidate_count": len(candidates),
        "candidate_carrier_count": sum(item["certifies"] for item in candidates),
        "some_minimum_residual_carrier_count": sum(
            record["some_carrier"] for record in records
        ),
        "all_minimum_residual_carriers_count": sum(
            record["all_carriers"] for record in records
        ),
        "violations": [record for record in records if not record["some_carrier"]],
        "records": [
            {
                **record,
                "candidates": [
                    {**item, "margin": str(item["margin"])}
                    for item in record["candidates"]
                ],
            }
            for record in records
        ],
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.output.write_text(json.dumps(audit(args.inputs), indent=2) + "\n")
