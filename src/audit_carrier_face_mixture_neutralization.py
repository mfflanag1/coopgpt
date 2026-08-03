"""Exact audit of higher-residual neutralization by carrier-face mixtures.

For a star-failure residual cover, let K be the minimum-residual players and
H the strictly higher-residual players in S.  For every k in K, write F_k for
the core face tight on (N\S) union {k}.  This audit maximizes eta subject to a
convex mixture of points x^k in F_k whose average displacement from the
leximin point is at least eta in every coordinate of H.

The products alpha_k x^k are linearized as z^k.  All reported optima and
points have exact rational primal-dual certificates.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

from certified_float_lp import certified_lp_min
from certified_leximin import leximin_core_certified
from lemD import residual_cover, star_holds
from tugame import Game


def solve_record(raw):
    source_path = Path(raw["path"])
    payload = json.loads(source_path.read_text())
    n = int(payload["n"])
    game = Game(n, [F(value) for value in payload["v"]])
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
    higher_players = tuple(
        player for player, value in cover["r"].items() if value > r0
    )
    assert minimum_players and higher_players

    # Variables are alpha_k, z^k_1,...,z^k_n for k in K, followed by eta.
    block_size = n + 1
    eta_index = len(minimum_players) * block_size
    variable_count = eta_index + 1
    c = [F(0)] * variable_count
    c[eta_index] = F(-1)
    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    def alpha_index(block):
        return block * block_size

    def z_index(block, player):
        return block * block_size + 1 + player

    for block, player in enumerate(minimum_players):
        alpha = alpha_index(block)
        # alpha_k >= 0.
        row = [F(0)] * variable_count
        row[alpha] = F(-1)
        A_ub.append(row)
        b_ub.append(F(0))

        # z^k(U) >= alpha_k v(U): the homogenized core constraints.
        for coalition in range(1, game.N):
            row = [F(0)] * variable_count
            row[alpha] = game.v[coalition]
            for coordinate in range(n):
                if coalition >> coordinate & 1:
                    row[z_index(block, coordinate)] = F(-1)
            A_ub.append(row)
            b_ub.append(F(0))

        # Efficiency and carrier-face tightness.
        row = [F(0)] * variable_count
        row[alpha] = -game.v[game.N]
        for coordinate in range(n):
            row[z_index(block, coordinate)] = F(1)
        A_eq.append(row)
        b_eq.append(F(0))

        carrier = (game.N ^ target) | (1 << player)
        row = [F(0)] * variable_count
        row[alpha] = -game.v[carrier]
        for coordinate in range(n):
            if carrier >> coordinate & 1:
                row[z_index(block, coordinate)] = F(1)
        A_eq.append(row)
        b_eq.append(F(0))

    # Convex weights.
    row = [F(0)] * variable_count
    for block in range(len(minimum_players)):
        row[alpha_index(block)] = F(1)
    A_eq.append(row)
    b_eq.append(F(1))

    # Average higher-residual displacement is coordinatewise at least eta.
    for player in higher_players:
        row = [F(0)] * variable_count
        for block in range(len(minimum_players)):
            row[z_index(block, player)] = F(-1)
        row[eta_index] = F(1)
        A_ub.append(row)
        b_ub.append(-phi[player])

    optimum, point, lp_certificate = certified_lp_min(
        c, A_ub, b_ub, A_eq, b_eq
    )
    if optimum is None:
        return {
            "path": str(source_path),
            "case": raw["case"],
            "S": raw["S"],
            "status": lp_certificate["status"],
        }

    eta = -optimum
    weights = tuple(
        point[alpha_index(block)]
        for block in range(len(minimum_players))
    )
    average = tuple(
        sum(
            point[z_index(block, player)]
            for block in range(len(minimum_players))
        )
        for player in range(n)
    )
    displacements = tuple(average[player] - phi[player] for player in range(n))
    carrier_margins = []
    for player in minimum_players:
        singleton = 1 << player
        carrier = (game.N ^ target) | singleton
        singleton_slack = phi[player] - game.v[singleton]
        carrier_slack = sum(
            phi[index] for index in range(n) if carrier >> index & 1
        ) - game.v[carrier]
        carrier_margins.append(carrier_slack - singleton_slack)

    return {
        "path": str(source_path),
        "case": raw["case"],
        "S": raw["S"],
        "status": "exact rational primal-dual certificate",
        "minimum_residual_players": [player + 1 for player in minimum_players],
        "higher_residual_players": [player + 1 for player in higher_players],
        "carrier_failure_margins": [str(value) for value in carrier_margins],
        "some_carrier_explains": any(value <= 0 for value in carrier_margins),
        "optimal_neutralization_margin": str(eta),
        "higher_residual_neutralization": eta >= 0,
        "strict_higher_residual_improvement": eta > 0,
        "weights": [str(value) for value in weights],
        "average_displacement": [str(value) for value in displacements],
        "exact_point_checks": {
            "weights_nonnegative": all(value >= 0 for value in weights),
            "weights_sum_to_one": sum(weights, F(0)) == 1,
            "higher_coordinates_meet_margin": all(
                displacements[player] >= eta for player in higher_players
            ),
        },
    }


def audit(paths, jobs, limit=None):
    raw_records = []
    seen = set()
    for path in paths:
        payload = json.loads(path.read_text())
        for raw in payload["records"]:
            key = (raw["path"], raw["case"])
            if key not in seen:
                seen.add(key)
                raw_records.append(raw)
    if limit is not None:
        raw_records = raw_records[:limit]
    if jobs == 1:
        records = [solve_record(raw) for raw in raw_records]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            records = list(pool.map(solve_record, raw_records))

    certified = [
        record for record in records
        if record["status"] == "exact rational primal-dual certificate"
    ]
    margins = [F(record["optimal_neutralization_margin"]) for record in certified]
    return {
        "status": "exact carrier-face mixture neutralization audit",
        "record_count": len(records),
        "certified_count": len(certified),
        "all_exact_point_checks": all(
            all(record["exact_point_checks"].values()) for record in certified
        ),
        "some_carrier_explains_count": sum(
            record["some_carrier_explains"] for record in certified
        ),
        "higher_residual_neutralization_count": sum(
            record["higher_residual_neutralization"] for record in certified
        ),
        "strict_higher_residual_improvement_count": sum(
            record["strict_higher_residual_improvement"] for record in certified
        ),
        "minimum_optimal_neutralization_margin": str(min(margins)),
        "maximum_optimal_neutralization_margin": str(max(margins)),
        "carrier_explanation_equivalent_to_neutralization": all(
            record["some_carrier_explains"]
            == record["higher_residual_neutralization"]
            for record in certified
        ),
        "records": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(args.inputs, args.jobs, args.limit)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
