"""Audit common carrier-face separator margins on saved hard cases."""
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
            candidates = tuple(item["player"] for item in raw["candidates"])
            failed = tuple(
                item["player"] for item in raw["candidates"]
                if not item["carrier_explains"]
            )
            if not failed:
                continue
            source_path = Path(raw["path"])
            target = tuple(raw["S"])
            key = (str(source_path), target, candidates)
            if key in seen:
                continue
            seen.add(key)
            game_payload = json.loads(source_path.read_text())
            failed_result = analyze(game_payload, list(target), list(failed))
            full_result = analyze(game_payload, list(target), list(candidates))
            records.append({
                "path": str(source_path),
                "S": list(target),
                "minimum_residual_players": list(candidates),
                "failed_carrier_players": list(failed),
                "failed_only": {
                    "epsilon": failed_result.get("epsilon"),
                    "strict_separator": failed_result.get("strict_separator"),
                    "exact": failed_result.get("exact"),
                    "w": failed_result.get("w"),
                },
                "full_class": {
                    "epsilon": full_result.get("epsilon"),
                    "strict_separator": full_result.get("strict_separator"),
                    "exact": full_result.get("exact"),
                    "w": full_result.get("w"),
                },
            })
    failed_eps = [F(record["failed_only"]["epsilon"]) for record in records]
    full_eps = [F(record["full_class"]["epsilon"]) for record in records]
    failed_support_sizes = [
        sum(F(value) != 0 for value in record["failed_only"]["w"])
        for record in records
    ]
    return {
        "status": "exact carrier-face separator boundary audit",
        "input_files": [str(path) for path in paths],
        "record_count": len(records),
        "all_certificates_exact": all(
            record[branch]["exact"]
            for record in records
            for branch in ("failed_only", "full_class")
        ),
        "failed_only_strict_count": sum(value > 0 for value in failed_eps),
        "full_class_strict_count": sum(value > 0 for value in full_eps),
        "full_class_zero_count": sum(value == 0 for value in full_eps),
        "minimum_failed_only_margin": str(min(failed_eps)) if failed_eps else None,
        "maximum_full_class_margin": str(max(full_eps)) if full_eps else None,
        "failed_only_unit_separator_count": sum(
            size == 1 for size in failed_support_sizes
        ),
        "maximum_failed_only_separator_support": (
            max(failed_support_sizes) if failed_support_sizes else None
        ),
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
