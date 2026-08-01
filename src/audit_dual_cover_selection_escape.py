"""Explore whether selecting another exact star-failure cover restores escape.

This is a proof-directed finite audit, not a completeness claim.  It exposes
extreme covers by minimizing every positive cost vector in a finite grid over
the residual coordinates, deduplicates the resulting exact residual vectors,
and checks the residual-gap escape criterion on every minimum-residual carrier
face of each discovered cover.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from audit_min_residual_singletons import certified_face_linear_min
from lemD import tight_coalitions, xS
from tugame import Game, exact_lp_min


def cover_with_cost(
        game, phi, target, residual_cost, anchor=None, residual_sum_bound=None):
    tights = tight_coalitions(game, phi)
    members = [player for player in range(game.n) if target >> player & 1]
    count = len(tights)
    variable_count = count + 1 + len(members)
    residual_index = {
        player: count + 1 + index for index, player in enumerate(members)
    }
    A_eq, b_eq = [], []
    for player in range(game.n):
        row = [F(0)] * variable_count
        for index, coalition in enumerate(tights):
            if coalition >> player & 1:
                row[index] = F(-1)
        row[count] = F(1)
        if target >> player & 1:
            row[residual_index[player]] = F(-1)
        A_eq.append(row)
        b_eq.append(F(0))
    A_ub, b_ub = [], []
    for index in range(count):
        row = [F(0)] * variable_count
        row[index] = F(-1)
        A_ub.append(row)
        b_ub.append(F(0))
    for player in members:
        row = [F(0)] * variable_count
        row[residual_index[player]] = F(-1)
        A_ub.append(row)
        b_ub.append(F(-1))
    if residual_sum_bound is not None:
        row = [F(0)] * variable_count
        for player in members:
            row[residual_index[player]] = F(1)
        A_ub.append(row)
        b_ub.append(F(residual_sum_bound))
    if anchor is not None:
        row = [F(0)] * variable_count
        row[residual_index[anchor]] = F(1)
        A_eq.append(row)
        b_eq.append(F(1))
    objective = [F(0)] * variable_count
    for player, cost in zip(members, residual_cost):
        objective[residual_index[player]] = F(cost)
    optimum, point = exact_lp_min(
        objective, A_ub, b_ub, A_eq, b_eq
    )
    if optimum is None or optimum == "unbounded":
        return None
    return {
        "r": tuple(point[residual_index[player]] for player in members),
        "members": tuple(members),
        "lambda": {
            tights[index]: point[index]
            for index in range(count) if point[index]
        },
    }


def audit_record(raw, source, costs, anchor_bound=None):
    game = Game(int(raw["n"]), [F(value) for value in raw["v"]])
    phi = tuple(F(value) for value in raw["phi"])
    target = sum(1 << (player - 1) for player in raw["S"])
    covers = {}
    objectives = tuple(itertools.product(costs, repeat=len(raw["S"])))
    anchors = (
        [player - 1 for player in raw["S"]]
        if anchor_bound is not None else [None]
    )
    for anchor in anchors:
        for residual_cost in objectives:
            if not any(residual_cost):
                continue
            cover = cover_with_cost(
                game, phi, target, residual_cost, anchor, anchor_bound
            )
            if cover is not None:
                covers.setdefault(cover["r"], cover)

    outside = game.N ^ target
    cover_records = []
    for residuals, cover in covers.items():
        r0 = min(residuals)
        gaps = tuple(value - r0 for value in residuals)
        gap_mass = sum(gaps, F(0))
        minimum_players = tuple(
            player for player, value in zip(cover["members"], residuals)
            if value == r0
        )
        faces = []
        if gap_mass:
            weights = {
                player: gap / gap_mass
                for player, gap in zip(cover["members"], gaps)
            }
            vector = tuple(weights.get(player, F(0)) for player in range(game.n))
            base = sum(vector[player] * phi[player] for player in range(game.n))
            for player in minimum_players:
                singleton = 1 << player
                carrier = outside | singleton
                maximum = -certified_face_linear_min(
                    game, [-value for value in vector], carrier
                ) - base
                singleton_slack = phi[player] - game.v[singleton]
                carrier_slack = xS(phi, carrier, game.n) - game.v[carrier]
                faces.append({
                    "player": player + 1,
                    "carrier_margin": str(carrier_slack - singleton_slack),
                    "carrier": carrier_slack <= singleton_slack,
                    "maximum_residual_gap_displacement": str(maximum),
                    "escape": maximum >= 0,
                })
        cover_records.append({
            "residuals": [str(value) for value in residuals],
            "minimum_residual_players": [player + 1 for player in minimum_players],
            "gap_mass": str(gap_mass),
            "faces": faces,
            "some_escape": any(face["escape"] for face in faces),
            "some_carrier": any(face["carrier"] for face in faces),
        })

    return {
        "status": "exact finite extreme-cover selection audit",
        "source": str(source),
        "trial": raw.get("trial"),
        "cost_grid": list(costs),
        "anchor_bound": anchor_bound,
        "objective_count": len(anchors) * sum(
            any(objective) for objective in objectives
        ),
        "distinct_cover_count": len(cover_records),
        "cover_with_escape_count": sum(item["some_escape"] for item in cover_records),
        "cover_with_carrier_count": sum(item["some_carrier"] for item in cover_records),
        "some_discovered_cover_escapes": any(item["some_escape"] for item in cover_records),
        "covers": cover_records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--record", type=int, default=0)
    parser.add_argument("--costs", default="1,2,4")
    parser.add_argument("--anchor-bound", type=int)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    payload = json.loads(args.input.read_text())
    costs = tuple(int(value) for value in args.costs.split(","))
    result = audit_record(
        payload["records"][args.record], args.input, costs, args.anchor_bound
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
