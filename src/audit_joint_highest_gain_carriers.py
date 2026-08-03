"""Exact audit of common off-side carrier faces for the Bet 1 frontier.

The input records already contain exactly certified leximin gains and a chosen
star-failure cover.  For each record, this script asks whether one core point
can simultaneously attain v(P union {k}) for every highest-gain player among
the minimum-residual class.  Floating LP solutions are used only as proposals;
``certified_lp_min`` accepts them only after exact rational primal-dual checks.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from certified_float_lp import certified_lp_min
from tugame import Game


def joint_face_point(game, faces):
    rows = [
        [-1 if coalition >> player & 1 else 0 for player in range(game.n)]
        for coalition in range(1, game.N)
    ]
    rhs = [-game.v[coalition] for coalition in range(1, game.N)]
    equalities = [[1] * game.n]
    equality_rhs = [game.v[game.N]]
    for face in faces:
        equalities.append([
            1 if face >> player & 1 else 0 for player in range(game.n)
        ])
        equality_rhs.append(game.v[face])
    optimum, point, certificate = certified_lp_min(
        [0] * game.n, rows, rhs, equalities, equality_rhs
    )
    return point, certificate if optimum is None else None


def audit_record(record):
    payload = json.loads(Path(record["path"]).read_text())
    game = Game(payload["n"], [F(value) for value in payload["v"]])
    target = sum(1 << (player - 1) for player in record["S"])
    outside = game.N ^ target
    minimum_players = [player - 1 for player in record["minimum_residual_players"]]
    highest_players = [
        item["player"] - 1
        for item in record["candidates"]
        if item["maximum_gain_in_minimum_residual_class"]
    ]
    highest_faces = [outside | (1 << player) for player in highest_players]
    minimum_faces = [outside | (1 << player) for player in minimum_players]
    highest_point, highest_error = joint_face_point(game, highest_faces)
    minimum_point, minimum_error = joint_face_point(game, minimum_faces)
    return {
        "path": record["path"],
        "case": record["case"],
        "S": record["S"],
        "highest_gain_minimum_residual_players": [
            player + 1 for player in highest_players
        ],
        "all_minimum_residual_players": [
            player + 1 for player in minimum_players
        ],
        "highest_gain_carrier_faces_have_common_point": highest_point is not None,
        "all_minimum_carrier_faces_have_common_point": minimum_point is not None,
        "highest_gain_common_point": (
            None if highest_point is None else [str(value) for value in highest_point]
        ),
        "highest_gain_failure": highest_error,
        "all_minimum_failure": minimum_error,
    }


def audit(paths):
    records = []
    for path in paths:
        records.extend(json.loads(path.read_text())["records"])
    results = [audit_record(record) for record in records]
    return {
        "status": "exact common-carrier-face audit",
        "arithmetic": (
            "floating LP proposals accepted only after exact rational "
            "primal-dual verification"
        ),
        "case_count": len(results),
        "tied_highest_gain_case_count": sum(
            len(record["highest_gain_minimum_residual_players"]) > 1
            for record in results
        ),
        "highest_gain_common_point_count": sum(
            record["highest_gain_carrier_faces_have_common_point"]
            for record in results
        ),
        "all_minimum_common_point_count": sum(
            record["all_minimum_carrier_faces_have_common_point"]
            for record in results
        ),
        "records": results,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.output.write_text(json.dumps(audit(args.inputs), indent=2) + "\n")
