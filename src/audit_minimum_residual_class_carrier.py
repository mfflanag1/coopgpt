"""Exact audit of the whole minimum-residual class as an off-side carrier.

For each stored genuinely multilevel star-failure record, let K be the full
minimum-residual class, S the target, and P=N\S.  The audited inequality is

    slack_phi(P union K) <= slack_phi(K),

equivalently v(P union K)-v(K) >= phi(P).  By the off-side carrier
proposition, this single class inequality gives the required capacity face
certificate without selecting an individual member of K.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def mask(players):
    return sum(1 << (player - 1) for player in players)


def normalize_record(raw, audit_path):
    if "v" in raw:
        n = int(raw["n"])
        worths = tuple(F(value) for value in raw["v"])
        phi = tuple(F(value) for value in raw["phi"])
        phi_target = sum(phi[player - 1] for player in raw["S"])
        source = str(audit_path)
        case = raw.get("trial")
    else:
        payload = json.loads(Path(raw["path"]).read_text())
        n = int(payload["n"])
        worths = tuple(F(value) for value in payload["v"])
        phi = None
        phi_target = F(raw["phi_S"])
        source = raw["path"]
        case = raw.get("case")
    target = mask(raw["S"])
    minimum_class = mask(raw["minimum_residual_players"])
    if not minimum_class or minimum_class & target != minimum_class:
        raise ValueError("minimum-residual class must be a nonempty subset of S")
    if minimum_class == target:
        raise ValueError("audit inputs must be genuinely multilevel")
    return {
        "n": n,
        "worths": worths,
        "phi": phi,
        "phi_target": phi_target,
        "target": target,
        "minimum_class": minimum_class,
        "S": list(raw["S"]),
        "K": list(raw["minimum_residual_players"]),
        "source": source,
        "case": case,
    }


def audit(paths):
    normalized = {}
    duplicate_count = 0
    for audit_path in paths:
        payload = json.loads(audit_path.read_text())
        for raw in payload.get("records", []):
            record = normalize_record(raw, audit_path)
            key = (record["n"], record["target"], record["worths"])
            if key in normalized:
                duplicate_count += 1
                continue
            normalized[key] = record

    records = []
    for record in normalized.values():
        n = record["n"]
        grand = (1 << n) - 1
        outside = grand ^ record["target"]
        class_carrier = outside | record["minimum_class"]
        worths = record["worths"]
        phi_outside = (
            sum(
                record["phi"][player]
                for player in range(n) if outside >> player & 1
            )
            if record["phi"] is not None else
            worths[grand] - record["phi_target"]
        )
        game_marginal = worths[class_carrier] - worths[record["minimum_class"]]
        margin = phi_outside - game_marginal
        records.append({
            "source": record["source"],
            "case": record["case"],
            "n": n,
            "S": record["S"],
            "minimum_residual_class": record["K"],
            "phi_outside": str(phi_outside),
            "class_game_marginal": str(game_marginal),
            "class_carrier_margin": str(margin),
            "class_carrier_certifies": margin <= 0,
        })

    margins = [F(record["class_carrier_margin"]) for record in records]
    return {
        "status": "exact minimum-residual-class carrier audit",
        "input_record_count": len(records) + duplicate_count,
        "duplicate_count": duplicate_count,
        "distinct_game_coalition_count": len(records),
        "class_carrier_certificate_count": sum(
            record["class_carrier_certifies"] for record in records
        ),
        "violation_count": sum(
            not record["class_carrier_certifies"] for record in records
        ),
        "strict_certificate_count": sum(value < 0 for value in margins),
        "boundary_certificate_count": sum(value == 0 for value in margins),
        "minimum_margin": str(min(margins)),
        "maximum_margin": str(max(margins)),
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.output.write_text(json.dumps(audit(args.inputs), indent=2) + "\n")
