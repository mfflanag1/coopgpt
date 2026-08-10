#!/usr/bin/env python3
"""Compress retained labeled equality directions by sign-preserving orbits."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def signature(item, positive, negative):
    direction = item["direction"]
    first = positive
    second = positive + negative
    return (
        item["side"],
        tuple(sorted(direction[:first])),
        tuple(sorted(direction[first:second])),
        tuple(sorted(direction[second:])),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=HERE / "equality_exchange_direction_cores.json",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    audit = json.loads(args.input.read_text())
    rows = []
    all_signatures = set()
    for row in audit["rows"]:
        counts = Counter(
            signature(item, row["positive_count"], row["negative_count"])
            for item in row["retained_menu"]
        )
        all_signatures.update(counts)
        rows.append(
            {
                "case": row["case"],
                "labeled_direction_count": row["retained_direction_count"],
                "sign_preserving_orbit_count": len(counts),
                "orbits": [
                    {
                        "side": key[0],
                        "positive_coefficients": list(key[1]),
                        "negative_coefficients": list(key[2]),
                        "tie_coefficients": list(key[3]),
                        "retained_labeled_count": count,
                    }
                    for key, count in sorted(counts.items())
                ],
            }
        )
    payload = {
        "schema": "equality-exchange-sign-orbits-v1",
        "scope": "combinatorial summary only; the certified formulas use the labeled menus",
        "status": "PASS",
        "case_count": len(rows),
        "distinct_cross_case_signature_count": len(all_signatures),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
