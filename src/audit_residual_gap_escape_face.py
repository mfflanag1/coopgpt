"""Exact audit for an escape face from the residual-gap separator.

For every star-failure record, form the normalized residual-gap functional

    w_i = (r_i-r_0) / sum_j (r_j-r_0).

For each minimum-residual player k, maximize w.(x-phi) over the core face
tight on (N\S) union {k}.  A nonnegative maximum escapes the strict
separator and, by the residual-gap separator theorem, certifies that k's
carrier inequality cannot fail.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

from audit_min_residual_singletons import certified_face_linear_min
from certified_leximin import leximin_core_certified
from lemD import residual_cover, star_holds
from tugame import Game


def solve_record(raw):
    if "v" in raw:
        payload = raw
        source_label = raw["_audit_source"]
    else:
        source_path = Path(raw["path"])
        payload = json.loads(source_path.read_text())
        source_label = str(source_path)
    n = int(payload["n"])
    game = Game(n, [F(value) for value in payload["v"]])
    if payload.get("phi") is not None:
        phi = tuple(F(value) for value in payload["phi"])
    else:
        phi, certificate = leximin_core_certified(game)
        if phi is None:
            raise RuntimeError(certificate)
    target = sum(1 << (player - 1) for player in raw["S"])
    holds, _value, _point = star_holds(game, phi, target)
    assert not holds
    cover = residual_cover(game, phi, target)
    assert cover is not None

    r0 = min(cover["r"].values())
    minimum_players = tuple(
        player for player, value in cover["r"].items() if value == r0
    )
    gaps = tuple(
        cover["r"].get(player, F(0)) - r0
        if target >> player & 1 else F(0)
        for player in range(n)
    )
    gap_mass = sum(gaps, F(0))
    assert gap_mass > 0
    w = tuple(value / gap_mass for value in gaps)
    base = sum(w[player] * phi[player] for player in range(n))
    outside = game.N ^ target

    faces = []
    for player in minimum_players:
        singleton = 1 << player
        carrier = outside | singleton
        maximum = -certified_face_linear_min(
            game, [-value for value in w], carrier
        ) - base
        singleton_slack = phi[player] - game.v[singleton]
        carrier_slack = sum(
            phi[index] for index in range(n) if carrier >> index & 1
        ) - game.v[carrier]
        gamma = carrier_slack - singleton_slack
        faces.append({
            "player": player + 1,
            "carrier_failure_margin": str(gamma),
            "maximum_residual_gap_displacement": str(maximum),
            "escapes_separator": maximum >= 0,
            "carrier_explains": gamma <= 0,
            "escape_implies_carrier": maximum < 0 or gamma <= 0,
        })

    return {
        "source": source_label,
        "case": raw.get("case", raw.get("trial")),
        "S": raw["S"],
        "minimum_residual": str(r0),
        "minimum_residual_players": [player + 1 for player in minimum_players],
        "normalized_residual_gap_separator": [str(value) for value in w],
        "some_face_escapes": any(face["escapes_separator"] for face in faces),
        "some_carrier_explains": any(face["carrier_explains"] for face in faces),
        "faces": faces,
    }


def audit(paths, jobs):
    raw_records = []
    seen = set()
    for path in paths:
        payload = json.loads(path.read_text())
        for raw in payload["records"]:
            raw = dict(raw)
            raw["_audit_source"] = str(path)
            key = (
                (raw["path"], raw["case"])
                if "path" in raw else
                (raw["n"], tuple(raw["S"]), tuple(raw["v"]))
            )
            if key not in seen:
                seen.add(key)
                raw_records.append(raw)
    if jobs == 1:
        records = [solve_record(raw) for raw in raw_records]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            records = list(pool.map(solve_record, raw_records))

    faces = [face for record in records for face in record["faces"]]
    escape_values = [
        F(face["maximum_residual_gap_displacement"])
        for face in faces if face["escapes_separator"]
    ]
    return {
        "status": "exact residual-gap escape-face audit",
        "record_count": len(records),
        "face_count": len(faces),
        "record_escape_count": sum(record["some_face_escapes"] for record in records),
        "record_carrier_count": sum(record["some_carrier_explains"] for record in records),
        "escape_face_count": sum(face["escapes_separator"] for face in faces),
        "carrier_face_count": sum(face["carrier_explains"] for face in faces),
        "all_escapes_imply_carriers": all(face["escape_implies_carrier"] for face in faces),
        "escape_equivalent_to_carrier_at_record_level": all(
            record["some_face_escapes"] == record["some_carrier_explains"]
            for record in records
        ),
        "minimum_nonnegative_escape": str(min(escape_values)),
        "maximum_escape": str(max(escape_values)),
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.output.write_text(json.dumps(audit(args.inputs, args.jobs), indent=2) + "\n")
