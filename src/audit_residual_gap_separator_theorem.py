"""Exact audit of the residual-gap separator theorem.

For a star-failure cover r on S, let r0=min r, K={i:r_i=r0}, and
Delta_i=r_i-r0.  If a minimum-residual candidate k fails its carrier
inequality by gamma_k>0, every displacement d from phi on the exact carrier
face F_{P union {k}} satisfies

    Delta . d_{S\K} <= -r0 d(S) <= -r0 gamma_k.

After normalizing Delta, this is an explicit strict common separator on the
higher-residual coordinates.  The audit recomputes every quantity exactly and
checks the face maximum independently.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from audit_min_residual_singletons import certified_face_linear_min
from certified_leximin import leximin_core_certified
from lemD import residual_cover, star_holds, xS
from tugame import Game


def audit(paths):
    records = []
    seen = set()
    for audit_path in paths:
        payload = json.loads(audit_path.read_text())
        for raw in payload.get("records", []):
            failed = tuple(
                item["player"] for item in raw["candidates"]
                if not item["carrier_explains"]
            )
            if not failed:
                continue
            source_path = Path(raw["path"])
            S_players = tuple(raw["S"])
            key = (str(source_path), S_players, failed)
            if key in seen:
                continue
            seen.add(key)
            game_payload = json.loads(source_path.read_text())
            n = int(game_payload["n"])
            game = Game(n, [F(value) for value in game_payload["v"]])
            phi, leximin_certificate = leximin_core_certified(game)
            if phi is None:
                raise RuntimeError(leximin_certificate)
            S = sum(1 << (player-1) for player in S_players)
            holds, _value, _point = star_holds(game, phi, S)
            assert not holds
            cover = residual_cover(game, phi, S)
            assert cover is not None
            r0 = min(cover["r"].values())
            K = tuple(
                player for player, value in cover["r"].items()
                if value == r0
            )
            delta = tuple(
                cover["r"].get(player, F(0))-r0
                if S >> player & 1 else F(0)
                for player in range(n)
            )
            delta_mass = sum(delta, F(0))
            assert delta_mass > 0
            w = tuple(value/delta_mass for value in delta)
            outside = game.N ^ S
            face_records = []
            for player_one_based in failed:
                player = player_one_based-1
                assert player in K
                singleton = 1 << player
                carrier = outside | singleton
                singleton_slack = phi[player]-game.v[singleton]
                carrier_slack = xS(phi,carrier,n)-game.v[carrier]
                gamma = carrier_slack-singleton_slack
                assert gamma > 0
                maximum_wx = -certified_face_linear_min(
                    game, [-value for value in w], carrier
                )
                maximum_displacement = maximum_wx-sum(
                    w[index]*phi[index] for index in range(n)
                )
                theorem_bound = -r0*gamma/delta_mass
                face_records.append({
                    "player": player_one_based,
                    "carrier": carrier,
                    "carrier_failure_margin": str(gamma),
                    "maximum_normalized_residual_gap_displacement": str(
                        maximum_displacement
                    ),
                    "theorem_upper_bound": str(theorem_bound),
                    "strictly_separated": maximum_displacement < 0,
                    "bound_verified": maximum_displacement <= theorem_bound,
                })
            records.append({
                "path": str(source_path),
                "S": list(S_players),
                "minimum_residual": str(r0),
                "minimum_residual_players": [player+1 for player in K],
                "failed_carrier_players": list(failed),
                "residual_gap_mass": str(delta_mass),
                "normalized_residual_gap_separator": [str(value) for value in w],
                "cover_tightness_verified": all(
                    xS(phi,coalition,n) == game.v[coalition]
                    for coalition in cover["lambda"]
                ),
                "cover_identity_verified": all(
                    cover["mu"]-sum(
                        weight for coalition,weight in cover["lambda"].items()
                        if coalition >> player & 1
                    ) == (cover["r"][player] if S >> player & 1 else 0)
                    for player in range(n)
                ),
                "faces": face_records,
            })

    faces = [face for record in records for face in record["faces"]]
    ratios = [
        -F(face["maximum_normalized_residual_gap_displacement"])
        / F(face["carrier_failure_margin"])
        for face in faces
    ]
    return {
        "status": "exact residual-gap separator theorem audit",
        "record_count": len(records),
        "failed_face_count": len(faces),
        "all_cover_identities_exact": all(
            record["cover_tightness_verified"]
            and record["cover_identity_verified"]
            for record in records
        ),
        "all_faces_strictly_separated": all(
            face["strictly_separated"] for face in faces
        ),
        "all_theorem_bounds_verified": all(
            face["bound_verified"] for face in faces
        ),
        "minimum_observed_separation_to_carrier_margin_ratio": str(
            min(ratios)
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
    args.output.write_text(json.dumps(audit(args.inputs), indent=2)+"\n")
