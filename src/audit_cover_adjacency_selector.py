"""Exact audit of the cover-adjacency refinement of the Bet 1 selector.

For a normalized star-failure cover (lambda,r), put

    Q_k = sum_{T contains k} lambda_T sum_{i in T intersect S} (r_i-1).

Thus Q_k is positive exactly when k co-occurs, in a positively weighted tight
coalition, with a player from a higher residual level.  The audit tests Q only
inside the highest-gain part of the minimum-residual class.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from certified_leximin import leximin_core_certified
from lemD import residual_cover
from tugame import Game


def adjacency(cover, target, player, n):
    return sum(
        weight * sum(
            cover["r"][other] - 1
            for other in range(n)
            if coalition >> other & 1 and target >> other & 1
        )
        for coalition, weight in cover["lambda"].items()
        if coalition >> player & 1
    )


def audit(paths):
    raw_records = []
    for path in paths:
        raw_records.extend(json.loads(path.read_text())["records"])
    output = []
    for record in raw_records:
        payload = json.loads(Path(record["path"]).read_text())
        game = Game(payload["n"], [F(value) for value in payload["v"]])
        phi, certificate = leximin_core_certified(game)
        if phi is None:
            raise RuntimeError(certificate)
        target = sum(1 << (player - 1) for player in record["S"])
        cover = residual_cover(game, phi, target)
        if cover is None:
            raise RuntimeError("saved star failure has no exact cover")
        candidates = []
        for item in record["candidates"]:
            if not item["maximum_gain_in_minimum_residual_class"]:
                continue
            player = item["player"] - 1
            candidates.append({
                "player": player + 1,
                "Q": adjacency(cover, target, player, game.n),
                "carrier_explains": item["carrier_explains"],
            })
        maximum = max(item["Q"] for item in candidates)
        selected = [item for item in candidates if item["Q"] == maximum]
        output.append({
            "path": record["path"],
            "case": record["case"],
            "maximum_Q": maximum,
            "selected_all_certify": all(
                item["carrier_explains"] for item in selected
            ),
            "selected_retains_certificate": any(
                item["carrier_explains"] for item in selected
            ),
            "candidates": candidates,
        })

    candidate_records = [
        item for record in output for item in record["candidates"]
    ]
    return {
        "status": "exact cover-adjacency selector audit",
        "definition": (
            "Q_k=sum_{T contains k} lambda_T "
            "sum_{i in T intersect S}(r_i-1)"
        ),
        "case_count": len(output),
        "cases_with_positive_maximum_Q": sum(
            record["maximum_Q"] > 0 for record in output
        ),
        "selected_all_certify_count": sum(
            record["selected_all_certify"] for record in output
        ),
        "selected_retains_certificate_count": sum(
            record["selected_retains_certificate"] for record in output
        ),
        "positive_Q_candidate_count": sum(
            item["Q"] > 0 for item in candidate_records
        ),
        "positive_Q_carrier_count": sum(
            item["Q"] > 0 and item["carrier_explains"]
            for item in candidate_records
        ),
        "zero_Q_candidate_count": sum(
            item["Q"] == 0 for item in candidate_records
        ),
        "zero_Q_carrier_count": sum(
            item["Q"] == 0 and item["carrier_explains"]
            for item in candidate_records
        ),
        "records": [
            {
                **record,
                "maximum_Q": str(record["maximum_Q"]),
                "candidates": [
                    {**item, "Q": str(item["Q"])}
                    for item in record["candidates"]
                ],
            }
            for record in output
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
