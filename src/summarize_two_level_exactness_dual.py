"""Compress an exact endpoint LP dual into two-level coalition collections."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path


def members(mask, n):
    return [player for player in range(n) if mask >> player & 1]


def summarize(payload):
    n = payload["n"]
    dual = payload["exact_dual"]
    inequalities = dual["decoded_core_witness_inequalities"]
    equalities = dual["decoded_efficiency_tightness_multipliers"]
    grouped = defaultdict(dict)
    for row in inequalities:
        key = (row["game"], row["tight_coalition"])
        multiplier = -F(row["multiplier"])
        assert multiplier > 0
        grouped[key][row["core_coalition"]] = multiplier

    equality_map = {
        (row["game"], row["tight_coalition"], row["kind"]): F(row["multiplier"])
        for row in equalities
    }
    blocks = []
    for (game, tight), collection in sorted(grouped.items()):
        coverage = [
            sum((weight for coalition, weight in collection.items()
                 if coalition >> player & 1), F(0))
            for player in range(n)
        ]
        alpha = -equality_map.get((game, tight, "efficiency"), F(0))
        delta = -equality_map.get((game, tight, "tightness"), F(0))
        expected = [alpha + (delta if tight >> player & 1 else 0)
                    for player in range(n)]
        assert coverage == expected
        blocks.append({
            "game": game,
            "tight_coalition": tight,
            "tight_members": [player + 1 for player in members(tight, n)],
            "alpha": str(alpha),
            "delta": str(delta),
            "coverage": [str(value) for value in coverage],
            "collection": {
                str(coalition): str(weight)
                for coalition, weight in sorted(collection.items())
            },
            "balanced_block": delta == 0,
        })
    return {
        "status": "exact dual compressed into two-level collections",
        "n": n,
        "A_mask": payload["A_mask"],
        "B_mask": payload["B_mask"],
        "circuit_index": payload["circuit_index"],
        "dual_bound": dual["dual_bound"],
        "bump_nonnegativity_multipliers": dual["bump_nonnegativity_multipliers"],
        "block_count": len(blocks),
        "balanced_block_count": sum(block["balanced_block"] for block in blocks),
        "genuine_two_level_block_count": sum(not block["balanced_block"] for block in blocks),
        "blocks": blocks,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = summarize(json.loads(args.input.read_text()))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
