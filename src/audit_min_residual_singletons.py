"""Exact audit of minimum-residual singleton capacity certificates."""
from __future__ import annotations

import argparse
import glob
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

from lemD import residual_cover, star_holds, xS
from certified_float_lp import certified_lp_min
from certified_leximin import leximin_core_certified
from tugame import Game


def members(mask, n):
    return [i + 1 for i in range(n) if mask >> i & 1]


def certified_face_linear_min(game, coefficients, face):
    n, grand, worths = game.n, game.N, game.v
    A_ub, b_ub = [], []
    for coalition in range(1, grand):
        A_ub.append([
            -1 if coalition >> player & 1 else 0 for player in range(n)
        ])
        b_ub.append(-worths[coalition])
    A_eq = [
        [1] * n,
        [1 if face >> player & 1 else 0 for player in range(n)],
    ]
    b_eq = [worths[grand], worths[face]]
    cost = list(coefficients)
    optimum, _point, certificate = certified_lp_min(
        cost, A_ub, b_ub, A_eq, b_eq
    )
    if optimum is None:
        raise RuntimeError(certificate)
    return optimum


def certified_face_max(game, objective, face):
    coefficients = [
        -1 if objective >> player & 1 else 0
        for player in range(game.n)
    ]
    return -certified_face_linear_min(game, coefficients, face)


def audit_path(path_string):
    path = Path(path_string)
    payload = json.loads(path.read_text())
    n = payload["n"]
    game = Game(n, [F(value) for value in payload["v"]])
    raw_cases = payload.get("cases") or [{"S": payload["S"]}]
    phi, leximin_certificate = leximin_core_certified(game)
    if phi is None:
        raise RuntimeError(leximin_certificate)
    records = []
    for case_index, raw_case in enumerate(raw_cases):
        target = sum(1 << player for player in raw_case["S"])
        holds, _value, _point = star_holds(game, phi, target)
        if holds:
            continue
        cover = residual_cover(game, phi, target)
        assert cover is not None
        minimum = min(cover["r"].values())
        minimum_players = [
            player for player, value in cover["r"].items() if value == minimum
        ]
        gains = {
            player: phi[player] - game.v[1 << player]
            for player in minimum_players
        }
        minimum_gain = min(gains.values())
        maximum_gain = max(gains.values())
        phi_target = xS(phi, target, n)
        outside = game.N ^ target
        candidates = []
        for player in minimum_players:
            face = 1 << player
            maximum = certified_face_max(game, target, face)
            correction_coefficients = [
                cover["r"].get(other, F(0)) - 1
                if target >> other & 1 and other != player else F(0)
                for other in range(n)
            ]
            correction_constant = sum(
                correction_coefficients[other] * phi[other]
                for other in range(n)
            )
            correction_minimum = (
                certified_face_linear_min(
                    game, correction_coefficients, face
                ) - correction_constant
            )
            correction_maximum = -certified_face_linear_min(
                game,
                [-coefficient for coefficient in correction_coefficients],
                face,
            ) - correction_constant
            face_slack = phi[player] - game.v[face]
            carrier = outside | face
            carrier_slack = xS(phi, carrier, n) - game.v[carrier]
            candidates.append({
                "player": player + 1,
                "residual": str(cover["r"][player]),
                "gain": str(gains[player]),
                "minimum_gain_in_minimum_residual_class": (
                    gains[player] == minimum_gain
                ),
                "maximum_gain_in_minimum_residual_class": (
                    gains[player] == maximum_gain
                ),
                "face_maximum": str(maximum),
                "certifies": maximum <= phi_target,
                "carrier": members(carrier, n),
                "face_slack": str(face_slack),
                "carrier_slack": str(carrier_slack),
                "carrier_explains": carrier_slack <= face_slack,
                "weighted_correction_minimum_on_face": str(correction_minimum),
                "weighted_correction_maximum_on_face": str(correction_maximum),
                "weighted_correction_nonnegative_on_face": (
                    correction_minimum >= 0
                ),
                "weighted_correction_nonpositive_on_face": (
                    correction_maximum <= 0
                ),
            })
        records.append({
            "path": path_string,
            "case": case_index,
            "S": members(target, n),
            "phi_S": str(phi_target),
            "residual_level_count": len(set(cover["r"].values())),
            "minimum_residual": str(minimum),
            "minimum_residual_players": [player + 1 for player in minimum_players],
            "unique_minimum": len(minimum_players) == 1,
            "candidates": candidates,
            "some_minimum_certifies": any(item["certifies"] for item in candidates),
            "all_minimum_certify": all(item["certifies"] for item in candidates),
            "some_minimum_carrier_explains": any(
                item["carrier_explains"] for item in candidates
            ),
            "some_lowest_gain_minimum_carrier_explains": any(
                item["carrier_explains"]
                and item["minimum_gain_in_minimum_residual_class"]
                for item in candidates
            ),
            "some_highest_gain_minimum_carrier_explains": any(
                item["carrier_explains"]
                and item["maximum_gain_in_minimum_residual_class"]
                for item in candidates
            ),
        })
    return records


def audit(paths, jobs):
    if jobs == 1:
        nested = [audit_path(path) for path in paths]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            nested = list(pool.map(audit_path, paths))
    records = [record for group in nested for record in group]
    multilevel = [record for record in records if record["residual_level_count"] >= 3]
    unique = [record for record in records if record["unique_minimum"]]
    candidates = [item for record in records for item in record["candidates"]]
    return {
        "status": "exact minimum-residual singleton capacity audit",
        "arithmetic": (
            "floating LP proposals accepted only after exact rational "
            "primal-dual verification"
        ),
        "file_count": len(paths),
        "star_failure_count": len(records),
        "three_plus_level_count": len(multilevel),
        "some_minimum_certifies_count": sum(
            record["some_minimum_certifies"] for record in records
        ),
        "all_minimum_certify_count": sum(
            record["all_minimum_certify"] for record in records
        ),
        "minimum_singleton_failure_count": sum(
            not record["some_minimum_certifies"] for record in records
        ),
        "some_minimum_carrier_explains_count": sum(
            record["some_minimum_carrier_explains"] for record in records
        ),
        "some_lowest_gain_minimum_carrier_explains_count": sum(
            record["some_lowest_gain_minimum_carrier_explains"]
            for record in records
        ),
        "some_highest_gain_minimum_carrier_explains_count": sum(
            record["some_highest_gain_minimum_carrier_explains"]
            for record in records
        ),
        "unique_minimum_count": len(unique),
        "unique_minimum_certifies_count": sum(
            record["some_minimum_certifies"] for record in unique
        ),
        "minimum_residual_candidate_count": len(candidates),
        "candidate_singleton_certificate_count": sum(
            item["certifies"] for item in candidates
        ),
        "candidate_carrier_certificate_count": sum(
            item["carrier_explains"] for item in candidates
        ),
        "candidate_carrier_false_positive_count": sum(
            item["carrier_explains"] and not item["certifies"]
            for item in candidates
        ),
        "candidate_weighted_correction_nonnegative_count": sum(
            item["weighted_correction_nonnegative_on_face"]
            for item in candidates
        ),
        "highest_gain_weighted_correction_nonnegative_case_count": sum(
            any(
                item["maximum_gain_in_minimum_residual_class"]
                and item["weighted_correction_nonnegative_on_face"]
                for item in record["candidates"]
            )
            for record in records
        ),
        "three_plus_level_some_minimum_certifies_count": sum(
            record["some_minimum_certifies"] for record in multilevel
        ),
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "patterns", nargs="*", default=[
            "results/WITNESS_KEY_CX_n6*.json",
            "results/WITNESS_KEY_CX_n7*.json",
            "results/WITNESS_KEY_FALSE_n6.json",
        ]
    )
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    paths = sorted({path for pattern in args.patterns for path in glob.glob(pattern)})
    result = audit(paths, args.jobs)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
