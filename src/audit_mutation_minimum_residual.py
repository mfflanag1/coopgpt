"""Exact post-audit of minimum-residual carriers in mutation corpora."""
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


def audit(paths):
    records = []
    source_summaries = []
    for path in paths:
        payload = json.loads(path.read_text())
        source_summaries.append({
            "path": str(path),
            "status": payload["status"],
            "arithmetic": payload["arithmetic"],
            "exact_multilevel_cases": payload["exact_multilevel_cases"],
        })
        records.extend(payload["records"])

    output = []
    for record in records:
        n = record["n"]
        worths = [F(value) for value in record["v"]]
        phi = [F(value) for value in record["phi"]]
        target = sum(1 << (player - 1) for player in record["S"])
        outside = ((1 << n) - 1) ^ target
        highest = set(record["highest_gain_minimum_residual_players"])
        candidates = []
        for one_indexed in record["minimum_residual_players"]:
            player = one_indexed - 1
            face = 1 << player
            carrier = outside | face
            gain = phi[player] - worths[face]
            carrier_slack = coalition_sum(phi, carrier) - worths[carrier]
            candidates.append({
                "player": one_indexed,
                "highest_gain": one_indexed in highest,
                "gain": str(gain),
                "carrier_slack": str(carrier_slack),
                "carrier_margin": str(carrier_slack - gain),
                "carrier_certifies": carrier_slack <= gain,
            })
        highest_face_data = {
            item["player"]: item["singleton_face_certifies"]
            for item in record["candidates"]
        }
        output.append({
            "trial": record["trial"],
            "n": n,
            "S": record["S"],
            "points": record["points"],
            "some_minimum_residual_carrier": any(
                item["carrier_certifies"] for item in candidates
            ),
            "all_minimum_residual_carriers": all(
                item["carrier_certifies"] for item in candidates
            ),
            "some_highest_gain_carrier": any(
                item["highest_gain"] and item["carrier_certifies"]
                for item in candidates
            ),
            "some_highest_gain_singleton_face_certifies": any(
                highest_face_data.values()
            ),
            "candidates": candidates,
        })

    candidates = [item for record in output for item in record["candidates"]]
    return {
        "status": "exact minimum-residual mutation audit",
        "arithmetic": (
            "all source cases were retained only after exact rational "
            "primal-dual certification; carrier comparisons recomputed as Fractions"
        ),
        "sources": source_summaries,
        "case_count": len(output),
        "minimum_residual_candidate_count": len(candidates),
        "candidate_carrier_count": sum(
            item["carrier_certifies"] for item in candidates
        ),
        "some_minimum_residual_carrier_count": sum(
            record["some_minimum_residual_carrier"] for record in output
        ),
        "all_minimum_residual_carriers_count": sum(
            record["all_minimum_residual_carriers"] for record in output
        ),
        "some_highest_gain_carrier_count": sum(
            record["some_highest_gain_carrier"] for record in output
        ),
        "some_highest_gain_singleton_face_certifies_count": sum(
            record["some_highest_gain_singleton_face_certifies"]
            for record in output
        ),
        "highest_gain_face_counterexamples": [
            record for record in output
            if not record["some_highest_gain_singleton_face_certifies"]
        ],
        "records": output,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.output.write_text(json.dumps(audit(args.inputs), indent=2) + "\n")
