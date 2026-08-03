"""Fresh exact stress test of the multilevel tight-hypergraph selector.

Float LPs only screen candidates.  Every retained case is recomputed with the
certified leximin pipeline, and binding, star failure, and the carrier tests
are accepted only after exact rational primal-dual verification.
"""
from __future__ import annotations

import argparse
import json
import random
import time
from fractions import Fraction as F
from pathlib import Path

from certified_float_lp import certified_lp_min
from certified_leximin import leximin_core_certified
from classify_saved_capacity_frontier import residual_cover_float
from hunt_exact_points import game_from_points
from hunt_off_side_carrier import (
    core_matrices,
    generate_points,
    maximize_target,
)
from lemD import residual_cover, tight_coalitions, xS
from leximin import leximin_core_float


def members(mask, n):
    return [player + 1 for player in range(n) if mask >> player & 1]


def certified_core_maximum(game, target, lower=None):
    rows = [
        [-1 if coalition >> player & 1 else 0 for player in range(game.n)]
        for coalition in range(1, game.N)
    ]
    rhs = [-game.v[coalition] for coalition in range(1, game.N)]
    if lower is not None:
        for player in range(game.n):
            if target >> player & 1:
                row = [0] * game.n
                row[player] = -1
                rows.append(row)
                rhs.append(-lower[player])
    optimum, point, certificate = certified_lp_min(
        [-1 if target >> player & 1 else 0 for player in range(game.n)],
        rows,
        rhs,
        [[1] * game.n],
        [game.v[game.N]],
    )
    if optimum is None:
        raise RuntimeError(certificate)
    return -optimum, point


def certified_face_maximum(game, target, face):
    rows = [
        [-1 if coalition >> player & 1 else 0 for player in range(game.n)]
        for coalition in range(1, game.N)
    ]
    rhs = [-game.v[coalition] for coalition in range(1, game.N)]
    optimum, point, certificate = certified_lp_min(
        [-1 if target >> player & 1 else 0 for player in range(game.n)],
        rows,
        rhs,
        [
            [1] * game.n,
            [1 if face >> player & 1 else 0 for player in range(game.n)],
        ],
        [game.v[game.N], game.v[face]],
    )
    if optimum is None:
        raise RuntimeError(certificate)
    return -optimum, point, certificate


def exact_record(game, points, target, trial):
    phi, leximin_certificate = leximin_core_certified(game)
    if phi is None:
        raise RuntimeError(leximin_certificate)
    phi_target = xS(phi, target, game.n)
    core_maximum, _ = certified_core_maximum(game, target)
    if core_maximum <= phi_target:
        return None
    star_maximum, _ = certified_core_maximum(game, target, lower=phi)
    if star_maximum > phi_target:
        return None
    cover = residual_cover(game, phi, target)
    if cover is None:
        raise RuntimeError("exact star failure has no residual cover")
    levels = sorted(set(cover["r"].values()))
    if len(levels) < 3:
        return None

    minimum = levels[0]
    minimum_players = [
        player for player, residual in cover["r"].items()
        if residual == minimum
    ]
    gains = {
        player: phi[player] - game.v[1 << player]
        for player in minimum_players
    }
    maximum_gain = max(gains.values())
    highest = [
        player for player in minimum_players if gains[player] == maximum_gain
    ]
    tights = tight_coalitions(game, phi)
    centrality = {
        player: sum(
            coalition.bit_count() for coalition in tights
            if coalition >> player & 1
        )
        for player in highest
    }
    maximum_centrality = max(centrality.values())
    selected = [
        player for player in highest
        if centrality[player] == maximum_centrality
    ]
    adjacency = {
        player: sum(
            weight * sum(
                cover["r"][other] - 1
                for other in range(game.n)
                if coalition >> other & 1 and target >> other & 1
            )
            for coalition, weight in cover["lambda"].items()
            if coalition >> player & 1
        )
        for player in highest
    }
    maximum_adjacency = max(adjacency.values())
    adjacency_selected = [
        player for player in highest
        if adjacency[player] == maximum_adjacency
    ]
    outside = game.N ^ target
    minimum_carrier_records = []
    for player in minimum_players:
        face = 1 << player
        carrier = outside | face
        gain = phi[player] - game.v[face]
        carrier_slack = xS(phi, carrier, game.n) - game.v[carrier]
        minimum_carrier_records.append({
            "player": player + 1,
            "gain": str(gain),
            "carrier_slack": str(carrier_slack),
            "carrier_certifies": carrier_slack <= gain,
        })
    candidate_records = []
    for player in highest:
        face = 1 << player
        face_maximum, _face_point, _face_certificate = certified_face_maximum(
            game, target, face
        )
        carrier = outside | face
        face_slack = phi[player] - game.v[face]
        carrier_slack = xS(phi, carrier, game.n) - game.v[carrier]
        candidate_records.append({
            "player": player + 1,
            "gain": str(gains[player]),
            "tight_hypergraph_centrality": centrality[player],
            "selected": player in selected,
            "cover_adjacency_Q": str(adjacency[player]),
            "adjacency_selected": player in adjacency_selected,
            "face_slack": str(face_slack),
            "singleton_face_maximum": str(face_maximum),
            "singleton_face_certifies": face_maximum <= phi_target,
            "carrier_slack": str(carrier_slack),
            "carrier_certifies": carrier_slack <= face_slack,
        })

    return {
        "trial": trial,
        "n": game.n,
        "S": members(target, game.n),
        "points": points,
        "v": [str(value) for value in game.v],
        "phi": [str(value) for value in phi],
        "binding_margin": str(core_maximum - phi_target),
        "star_maximum_minus_phi_S": str(star_maximum - phi_target),
        "residual_levels": [str(value) for value in levels],
        "minimum_residual_players": [
            player + 1 for player in minimum_players
        ],
        "some_minimum_residual_carrier": any(
            item["carrier_certifies"] for item in minimum_carrier_records
        ),
        "all_minimum_residual_carriers": all(
            item["carrier_certifies"] for item in minimum_carrier_records
        ),
        "minimum_residual_carrier_candidates": minimum_carrier_records,
        "highest_gain_minimum_residual_players": [
            player + 1 for player in highest
        ],
        "selected_players": [player + 1 for player in selected],
        "adjacency_selected_players": [
            player + 1 for player in adjacency_selected
        ],
        "selected_all_certify": all(
            item["carrier_certifies"]
            for item in candidate_records if item["selected"]
        ),
        "adjacency_selected_all_certify": all(
            item["carrier_certifies"]
            for item in candidate_records if item["adjacency_selected"]
        ),
        "adjacency_selected_faces_all_certify": all(
            item["singleton_face_certifies"]
            for item in candidate_records if item["adjacency_selected"]
        ),
        "some_highest_gain_face_certifies": any(
            item["singleton_face_certifies"] for item in candidate_records
        ),
        "all_highest_gain_faces_certify": all(
            item["singleton_face_certifies"] for item in candidate_records
        ),
        "some_highest_gain_certifies": any(
            item["carrier_certifies"] for item in candidate_records
        ),
        "candidates": candidate_records,
    }


def audit(n, trials, seed, mode, generators, exact_case_limit):
    rng = random.Random(seed)
    started = time.time()
    float_binding_star_failures = 0
    float_multilevel_candidates = 0
    exact_records = []
    seen = set()
    for trial in range(trials):
        points = generate_points(n, rng, mode, generators)
        game = game_from_points(n, points)
        phi_screen = leximin_core_float(n, game.v, tol=1e-9)
        if phi_screen is None:
            continue
        rows, rhs = core_matrices(game)
        coalitions = [
            target for target in range(1, game.N)
            if target.bit_count() >= 2
        ]
        rng.shuffle(coalitions)
        for target in coalitions:
            phi_target = xS(phi_screen, target, n)
            maximum = maximize_target(game, target, rows, rhs)
            if maximum is None or maximum <= phi_target + 1e-7:
                continue
            star_maximum = maximize_target(
                game, target, rows, rhs, lower=phi_screen
            )
            if star_maximum is None or star_maximum > phi_target + 1e-7:
                continue
            float_binding_star_failures += 1
            residuals = residual_cover_float(game, phi_screen, target)
            if residuals is None:
                continue
            if len({round(value, 7) for value in residuals.values()}) < 3:
                continue
            float_multilevel_candidates += 1
            key = (tuple(game.v), target)
            if key in seen:
                continue
            seen.add(key)
            record = exact_record(game, points, target, trial)
            if record is None:
                continue
            exact_records.append(record)
            if not record["some_minimum_residual_carrier"]:
                return {
                    "status": "exact selector counterexample found",
                    "arithmetic": "exact rational primal-dual certification",
                    "n": n,
                    "mode": mode,
                    "generators": generators,
                    "seed": seed,
                    "trials_requested": trials,
                    "trials_completed": trial + 1,
                    "float_binding_star_failures": float_binding_star_failures,
                    "float_multilevel_candidates": float_multilevel_candidates,
                    "exact_multilevel_cases": len(exact_records),
                    "records": exact_records,
                }
            if len(exact_records) >= exact_case_limit:
                break
        if len(exact_records) >= exact_case_limit:
            break

    tied = [
        record for record in exact_records
        if len(record["highest_gain_minimum_residual_players"]) > 1
    ]
    mixed = [
        record for record in tied
        if len({item["carrier_certifies"] for item in record["candidates"]}) > 1
    ]
    return {
        "status": "no exact selector counterexample found",
        "arithmetic": "exact rational primal-dual certification",
        "n": n,
        "mode": mode,
        "generators": generators,
        "seed": seed,
        "trials_requested": trials,
        "trials_completed": trial + 1 if trials else 0,
        "exact_case_limit": exact_case_limit,
        "float_binding_star_failures": float_binding_star_failures,
        "float_multilevel_candidates": float_multilevel_candidates,
        "exact_multilevel_cases": len(exact_records),
        "tied_highest_gain_cases": len(tied),
        "mixed_tie_cases": len(mixed),
        "selected_all_certify_count": sum(
            record["selected_all_certify"] for record in exact_records
        ),
        "adjacency_selected_all_certify_count": sum(
            record["adjacency_selected_all_certify"]
            for record in exact_records
        ),
        "adjacency_selected_faces_all_certify_count": sum(
            record["adjacency_selected_faces_all_certify"]
            for record in exact_records
        ),
        "some_highest_gain_face_certifies_count": sum(
            record["some_highest_gain_face_certifies"]
            for record in exact_records
        ),
        "all_highest_gain_faces_certify_count": sum(
            record["all_highest_gain_faces_certify"]
            for record in exact_records
        ),
        "some_highest_gain_certifies_count": sum(
            record["some_highest_gain_certifies"] for record in exact_records
        ),
        "some_minimum_residual_carrier_count": sum(
            record["some_minimum_residual_carrier"]
            for record in exact_records
        ),
        "all_minimum_residual_carriers_count": sum(
            record["all_minimum_residual_carriers"]
            for record in exact_records
        ),
        "elapsed_seconds": time.time() - started,
        "records": exact_records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument(
        "--mode", choices=["composition", "signed", "nearby"],
        default="nearby",
    )
    parser.add_argument("--generators", type=int, default=3)
    parser.add_argument("--exact-case-limit", type=int, default=100)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(
        args.n,
        args.trials,
        args.seed,
        args.mode,
        args.generators,
        args.exact_case_limit,
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
