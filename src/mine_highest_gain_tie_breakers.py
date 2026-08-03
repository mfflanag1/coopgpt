"""Mine noncircular tie-breakers for the multilevel singleton selector."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from certified_leximin import leximin_core_certified
from lemD import residual_cover, tight_coalitions, xS
from tugame import Game


def audit(paths):
    raw_records = []
    for path in paths:
        raw_records.extend(json.loads(path.read_text())["records"])
    tied_records = []
    for record in raw_records:
        highest = [
            dict(item) for item in record["candidates"]
            if item["maximum_gain_in_minimum_residual_class"]
        ]
        if len(highest) < 2:
            continue
        payload = json.loads(Path(record["path"]).read_text())
        game = Game(payload["n"], [F(value) for value in payload["v"]])
        phi, certificate = leximin_core_certified(game)
        if phi is None:
            raise RuntimeError(certificate)
        target = sum(1 << (player - 1) for player in record["S"])
        outside = game.N ^ target
        tights = tight_coalitions(game, phi)
        cover = residual_cover(game, phi, target)
        if cover is None:
            raise RuntimeError("saved star failure has no exact cover")
        gains = {
            player: phi[player] - game.v[1 << player]
            for player in range(game.n) if target >> player & 1
        }
        for item in highest:
            player = item["player"] - 1
            containing = [face for face in tights if face >> player & 1]
            cover_containing = [
                (face, weight) for face, weight in cover["lambda"].items()
                if face >> player & 1
            ]
            crossing = [
                face for face in containing
                if face & target and face & outside
            ]
            inside = [face for face in containing if face & outside == 0]
            item["features"] = {
                "singleton_value": game.v[1 << player],
                "carrier_value": game.v[outside | (1 << player)],
                "tight_count": F(len(containing)),
                "tight_crossing_count": F(len(crossing)),
                "tight_inside_count": F(len(inside)),
                "tight_size_sum": F(sum(face.bit_count() for face in containing)),
                "minimum_tight_size": F(min(face.bit_count() for face in containing)),
                "maximum_tight_size": F(max(face.bit_count() for face in containing)),
                "cover_weighted_size_sum": sum(
                    weight * face.bit_count()
                    for face, weight in cover_containing
                ),
                "cover_weighted_inside_size_sum": sum(
                    weight * (face & target).bit_count()
                    for face, weight in cover_containing
                ),
                "cover_weighted_residual_mass": sum(
                    weight * sum(
                        cover["r"][other] - 1
                        for other in range(game.n)
                        if face >> other & 1 and target >> other & 1
                    )
                    for face, weight in cover_containing
                ),
                "cover_weighted_gain_mass": sum(
                    weight * sum(
                        gains[other]
                        for other in range(game.n)
                        if face >> other & 1 and target >> other & 1
                    )
                    for face, weight in cover_containing
                ),
            }
        tied_records.append({
            "path": record["path"],
            "case": record["case"],
            "candidates": highest,
        })

    feature_names = list(tied_records[0]["candidates"][0]["features"])
    selectors = {}
    for feature in feature_names:
        for direction in ("minimum", "maximum"):
            success = 0
            pruned = 0
            all_selected_certify = 0
            unique_selection = 0
            for record in tied_records:
                candidates = record["candidates"]
                values = [item["features"][feature] for item in candidates]
                extreme = min(values) if direction == "minimum" else max(values)
                selected = [
                    item for item in candidates
                    if item["features"][feature] == extreme
                ]
                success += any(item["carrier_explains"] for item in selected)
                pruned += len(selected) < len(candidates)
                all_selected_certify += all(
                    item["carrier_explains"] for item in selected
                )
                unique_selection += len(selected) == 1
            selectors[f"{direction}_{feature}"] = {
                "retains_a_certificate": success,
                "prunes_at_least_one_candidate": pruned,
                "all_selected_candidates_certify": all_selected_certify,
                "unique_selection": unique_selection,
            }
    return {
        "status": "exact highest-gain tie-breaker screen",
        "case_count": len(tied_records),
        "selectors": selectors,
        "tight_hypergraph_centrality_selector": {
            "definition": "D_k=sum{|T|: phi(T)=v(T), k in T}",
            "rule": "maximize D_k among tied highest-gain minimum-residual players",
            **selectors["maximum_tight_size_sum"],
        },
        "records": [
            {
                **record,
                "candidates": [
                    {
                        "player": item["player"],
                        "carrier_explains": item["carrier_explains"],
                        "features": {
                            key: str(value) for key, value in item["features"].items()
                        },
                    }
                    for item in record["candidates"]
                ],
            }
            for record in tied_records
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
