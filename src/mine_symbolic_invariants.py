"""Exact invariant extractor for the proper-coalition leximin frontier.

This is theorem-discovery infrastructure rather than a frequency counter.  For
one exact pair (v,S), it emits only proof-relevant symbolic data:

  * leximin gain strata and tight-coalition crossing types;
  * the exact star test and a residual-cover dual when star fails;
  * exact capacity d*(S), every limiting face, and all capacity certificates;
  * whether the smallest certificate is a singleton or a same-stratum pair.
  * off-side slack comparisons and the face bound each carrier induces.

The default instance is the six-player lower-envelope game that disproves the
tempting stronger claim that a singleton in S always certifies.  Its canonical
certificate is the same-stratum pair {3,4} (one-indexed).
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from hunt_exact_points import game_from_points
from lemD import residual_cover, star_holds, tight_coalitions, xS
from leximin import leximin_core_exact
from tugame import Game, exact_lp_min


PAIR_WITNESS_V = [
    0, 4, 6, 11, 1, 5, 8, 12, 7, 11, 13, 18, 13, 19, 19, 25,
    0, 4, 7, 11, 1, 5, 8, 12, 7, 11, 14, 18, 14, 20, 20, 26,
    1, 5, 8, 12, 2, 6, 9, 13, 8, 12, 15, 19, 15, 21, 21, 27,
    1, 5, 8, 12, 2, 6, 9, 13, 8, 12, 15, 19, 16, 21, 22, 28,
]
PAIR_WITNESS_S = (1 << 0) | (1 << 2) | (1 << 3)
PAIR_WITNESS_POINTS = [
    (4, 7, 1, 15, 0, 1),
    (6, 6, 6, 7, 1, 2),
    (4, 7, 9, 7, 0, 1),
]


def members(mask, n):
    return [i + 1 for i in range(n) if mask >> i & 1]


def face_max(game, objective, face):
    """max x(objective) over core(v) with x(face)=v(face), exactly."""
    n, grand, worths = game.n, game.N, game.v
    a_ub = []
    b_ub = []
    for coalition in range(1, grand):
        a_ub.append([-1 if coalition >> i & 1 else 0 for i in range(n)])
        b_ub.append(-worths[coalition])
    a_eq = [
        [1] * n,
        [1 if face >> i & 1 else 0 for i in range(n)],
    ]
    b_eq = [worths[grand], worths[face]]
    objective_vector = [-1 if objective >> i & 1 else 0 for i in range(n)]
    optimum, _ = exact_lp_min(objective_vector, a_ub, b_ub, a_eq, b_eq)
    if optimum is None or optimum == "unbounded":
        return None
    return -optimum


def face_upper_dual(game, objective, face, phi_tights):
    """Exact dual certificate for max_{core, x(face)=v(face)} x(objective).

    It finds alpha_T >= 0 and free beta,gamma with

      1_objective = beta 1_N + gamma 1_face - sum_T alpha_T 1_T.

    Hence x(objective) <= beta v(N)+gamma v(face)-sum_T alpha_T v(T).
    """
    n, grand, worths = game.n, game.N, game.v
    coalitions = list(range(1, grand))
    p = len(coalitions)
    beta_index = p
    gamma_index = p + 1
    variable_count = p + 2

    a_eq = []
    b_eq = []
    for player in range(n):
        row = [F(0)] * variable_count
        for index, coalition in enumerate(coalitions):
            if coalition >> player & 1:
                row[index] = F(-1)
        row[beta_index] = F(1)
        if face >> player & 1:
            row[gamma_index] = F(1)
        a_eq.append(row)
        b_eq.append(F(1) if objective >> player & 1 else F(0))

    a_ub = []
    b_ub = []
    for index in range(p):
        row = [F(0)] * variable_count
        row[index] = F(-1)
        a_ub.append(row)
        b_ub.append(F(0))

    cost = [-worths[coalition] for coalition in coalitions]
    cost.extend([worths[grand], worths[face]])
    optimum, solution = exact_lp_min(cost, a_ub, b_ub, a_eq, b_eq)
    if optimum is None or optimum == "unbounded":
        return None

    support = []
    for index, coalition in enumerate(coalitions):
        if solution[index] != 0:
            support.append(
                {
                    "coalition": members(coalition, n),
                    "mask": coalition,
                    "weight": solution[index],
                    "phi_tight": coalition in phi_tights,
                    "type": crossing_type(coalition, objective),
                }
            )
    return {
        "bound": optimum,
        "beta": solution[beta_index],
        "gamma": solution[gamma_index],
        "support": support,
    }


def gain_strata(game, phi):
    gains = [phi[i] - game.v[1 << i] for i in range(game.n)]
    levels = sorted(set(gains))
    return gains, [
        [i + 1 for i, gain in enumerate(gains) if gain == level]
        for level in levels
    ]


def crossing_type(coalition, target):
    inside = coalition & target
    outside = coalition & ~target
    if inside and outside:
        return "crossing"
    if inside:
        return "inside_S"
    return "outside_S"


def stringify(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    return value


def extract(game, target):
    phi = leximin_core_exact(game)
    if phi is None:
        raise RuntimeError("exact leximin solver failed")
    gains, strata = gain_strata(game, phi)
    stratum_of = {
        player: level
        for level, group in enumerate(strata)
        for player in group
    }
    phi_target = xS(phi, target, game.n)
    slack = phi_target - game.v[target]
    holds, star_value, _ = star_holds(game, phi, target)
    cover = None if holds else residual_cover(game, phi, target)

    tights = tight_coalitions(game, phi)
    off_side = game.N ^ target
    carrier_comparisons = []
    for carrier_face in range(1, game.N):
        if carrier_face & target != carrier_face or carrier_face == target:
            continue
        carrier = off_side | carrier_face
        face_slack = xS(phi, carrier_face, game.n) - game.v[carrier_face]
        carrier_slack = xS(phi, carrier, game.n) - game.v[carrier]
        bound = game.v[game.N] + game.v[carrier_face] - game.v[carrier]
        carrier_comparisons.append(
            {
                "carrier": members(carrier, game.n),
                "carrier_mask": carrier,
                "face": members(carrier_face, game.n),
                "face_mask": carrier_face,
                "carrier_slack": carrier_slack,
                "face_slack": face_slack,
                "slack_difference": carrier_slack - face_slack,
                "carrier_is_phi_tight": carrier in tights,
                "bound": bound,
                "phiS": phi_target,
                "certifies": bound <= phi_target,
            }
        )
    tight_data = [
        {
            "coalition": members(coalition, game.n),
            "mask": coalition,
            "type": crossing_type(coalition, target),
        }
        for coalition in tights
    ]

    faces = []
    for coalition in range(1, game.N):
        if coalition == target:
            continue
        maximum = face_max(game, target, coalition)
        if maximum is None:
            continue
        faces.append(
            {
                "coalition": members(coalition, game.n),
                "mask": coalition,
                "max_xS": maximum,
                "capacity": maximum - game.v[target],
                "certifies": maximum <= phi_target,
                "subset_of_S": coalition & target == coalition,
                "single_stratum": len(
                    {stratum_of[i + 1] for i in range(game.n) if coalition >> i & 1}
                ) == 1,
            }
        )

    capacity = min(item["capacity"] for item in faces)
    limiters = [item for item in faces if item["capacity"] == capacity]
    certificates = [item for item in faces if item["certifies"]]
    minimum_size = min(len(item["coalition"]) for item in certificates)
    smallest = [item for item in certificates if len(item["coalition"]) == minimum_size]
    in_target = [item for item in certificates if item["subset_of_S"]]
    minimum_in_target_size = min(len(item["coalition"]) for item in in_target)
    smallest_in_target = [
        item for item in in_target if len(item["coalition"]) == minimum_in_target_size
    ]
    for item in smallest_in_target:
        item["upper_bound_dual"] = face_upper_dual(
            game, target, item["mask"], set(tights)
        )

    cover_payload = None
    residual_levels = []
    minimum_residual_class = []
    if cover is not None:
        residual_levels = sorted(set(cover["r"].values()))
        minimum_residual = residual_levels[0]
        minimum_residual_class = [
            player + 1
            for player, residual in cover["r"].items()
            if residual == minimum_residual
        ]
        cover_payload = {
            "mu": cover["mu"],
            "weights": [
                {
                    "coalition": members(coalition, game.n),
                    "mask": coalition,
                    "weight": weight,
                    "type": crossing_type(coalition, target),
                }
                for coalition, weight in cover["lambda"].items()
            ],
            "residuals_on_S": {
                str(player + 1): residual for player, residual in cover["r"].items()
            },
            "residual_levels": residual_levels,
            "minimum_residual_class": minimum_residual_class,
        }

    two_level_face = None
    if cover is not None and len(residual_levels) <= 2:
        predicted_mask = sum(1 << (player - 1) for player in minimum_residual_class)
        predicted = next(item for item in faces if item["mask"] == predicted_mask)
        two_level_face = {
            "coalition": minimum_residual_class,
            "mask": predicted_mask,
            "max_xS": predicted["max_xS"],
            "certifies": predicted["certifies"],
            "theorem": "Proposition two-level dual certificate",
        }

    return stringify(
        {
            "n": game.n,
            "S": members(target, game.n),
            "vS": game.v[target],
            "phi": phi,
            "gains": gains,
            "gain_strata": strata,
            "phiS": phi_target,
            "slack": slack,
            "star_holds": holds,
            "star_max": star_value,
            "residual_cover": cover_payload,
            "residual_level_count": len(residual_levels),
            "two_level_predicted_face": two_level_face,
            "tight_coalitions": tight_data,
            "off_side": members(off_side, game.n),
            "off_side_carrier_comparisons": carrier_comparisons,
            "capacity_dstar": capacity,
            "capacity_minus_slack": capacity - slack,
            "limiting_faces": limiters,
            "minimum_certificate_size_global": minimum_size,
            "smallest_certificates_global": smallest,
            "minimum_certificate_size_inside_S": minimum_in_target_size,
            "smallest_certificates_inside_S": smallest_in_target,
            "all_certificates": certificates,
        }
    )


def load_game(path):
    payload = json.loads(path.read_text())
    worths = payload["v"] if isinstance(payload, dict) else payload
    n = (len(worths)).bit_length() - 1
    return Game(n, [F(value) for value in worths])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-json", type=Path)
    parser.add_argument("--coalition", type=lambda value: int(value, 0))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.game_json:
        if args.coalition is None:
            raise SystemExit("--coalition is required with --game-json")
        selected_game = load_game(args.game_json)
        selected_coalition = args.coalition
    else:
        selected_game = game_from_points(6, PAIR_WITNESS_POINTS)
        assert selected_game.v == [F(value) for value in PAIR_WITNESS_V]
        selected_coalition = PAIR_WITNESS_S
    rendered = json.dumps(extract(selected_game, selected_coalition), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
