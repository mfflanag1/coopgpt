"""Test whether failed carrier faces separate along higher-residual players.

For every saved multilevel record with at least one failed minimum-residual
candidate, recompute the exact common face separator under three support
restrictions.  The main branch forces w to S\K, where the star-failure
residual is strictly above its minimum on K.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from analyze_carrier_face_separator_dual import analyze


def audit(paths):
    records = []
    seen = set()
    for audit_path in paths:
        payload = json.loads(audit_path.read_text())
        for raw in payload.get("records", []):
            K = tuple(item["player"] for item in raw["candidates"])
            failed = tuple(
                item["player"] for item in raw["candidates"]
                if not item["carrier_explains"]
            )
            if not failed:
                continue
            source_path = Path(raw["path"])
            S = tuple(raw["S"])
            key = (str(source_path), S, K, failed)
            if key in seen:
                continue
            seen.add(key)
            game_payload = json.loads(source_path.read_text())
            higher_residual = tuple(player for player in S if player not in K)
            carrier_candidates = tuple(player for player in K if player not in failed)
            nonfailed_coordinates = tuple(
                player for player in S if player not in failed
            )
            branches = {}
            for name, support in (
                    ("higher_residual", higher_residual),
                    ("carrier_candidates", carrier_candidates),
                    ("all_nonfailed", nonfailed_coordinates)):
                if not support:
                    branches[name] = {
                        "support": [], "epsilon": None,
                        "strict_separator": False, "exact": True,
                    }
                    continue
                result = analyze(
                    game_payload, list(S), list(failed), list(support)
                )
                branches[name] = {
                    "support": list(support),
                    "epsilon": result.get("epsilon"),
                    "strict_separator": result.get("strict_separator", False),
                    "exact": result.get("exact", False),
                    "w": result.get("w"),
                }
            records.append({
                "path": str(source_path),
                "S": list(S),
                "minimum_residual_players": list(K),
                "failed_carrier_players": list(failed),
                "branches": branches,
            })

    def branch_summary(name):
        available = [
            record["branches"][name]
            for record in records if record["branches"][name]["support"]
        ]
        epsilons = [F(branch["epsilon"]) for branch in available]
        return {
            "available_count": len(available),
            "all_exact": all(branch["exact"] for branch in available),
            "strict_count": sum(value > 0 for value in epsilons),
            "zero_count": sum(value == 0 for value in epsilons),
            "negative_count": sum(value < 0 for value in epsilons),
            "minimum_epsilon": str(min(epsilons)) if epsilons else None,
            "maximum_epsilon": str(max(epsilons)) if epsilons else None,
        }

    return {
        "status": "exact residual-gap carrier-separator support audit",
        "record_count": len(records),
        "higher_residual_support": branch_summary("higher_residual"),
        "carrier_candidate_support": branch_summary("carrier_candidates"),
        "all_nonfailed_support": branch_summary("all_nonfailed"),
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.output.write_text(json.dumps(audit(args.inputs), indent=2)+"\n")
