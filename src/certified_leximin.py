"""Exact leximin computation via rationally certified floating LP proposals."""
from __future__ import annotations

from fractions import Fraction as F

from certified_float_lp import certified_lp_min


def leximin_core_certified(game):
    n, grand, worths = game.n, game.N, game.v
    floors = [worths[1 << player] for player in range(n)]
    fixed = {}
    rounds = []

    def core_rows(variable_count):
        rows, rhs = [], []
        for coalition in range(1, grand):
            row = [F(0)] * variable_count
            for player in range(n):
                if coalition >> player & 1:
                    row[player] = -1
            rows.append(row)
            rhs.append(-worths[coalition])
        return rows, rhs

    def solve_level(free):
        variable_count = n + 1
        level_index = n
        A_ub, b_ub = core_rows(variable_count)
        for player in free:
            row = [F(0)] * variable_count
            row[player] = -1
            row[level_index] = 1
            A_ub.append(row)
            b_ub.append(-floors[player])
        A_eq = [[F(1)] * n + [F(0)]]
        b_eq = [worths[grand]]
        for player, value in fixed.items():
            row = [F(0)] * variable_count
            row[player] = 1
            A_eq.append(row)
            b_eq.append(value)
        objective = [F(0)] * variable_count
        objective[level_index] = -1
        return certified_lp_min(objective, A_ub, b_ub, A_eq, b_eq)

    def maximize_player(player, free, level):
        A_ub, b_ub = core_rows(n)
        for other in free:
            row = [F(0)] * n
            row[other] = -1
            A_ub.append(row)
            b_ub.append(-(floors[other] + level))
        A_eq = [[F(1)] * n]
        b_eq = [worths[grand]]
        for other, value in fixed.items():
            row = [F(0)] * n
            row[other] = 1
            A_eq.append(row)
            b_eq.append(value)
        objective = [F(0)] * n
        objective[player] = -1
        optimum, _point, certificate = certified_lp_min(
            objective, A_ub, b_ub, A_eq, b_eq
        )
        if optimum is None:
            return None, certificate
        return -optimum, certificate

    free = list(range(n))
    while free:
        optimum, point, certificate = solve_level(free)
        if optimum is None:
            return None, {"status": "level certification failed", "detail": certificate}
        level = -optimum
        pinned = []
        player_certificates = {}
        for player in free:
            maximum, player_certificate = maximize_player(player, free, level)
            if maximum is None:
                return None, {
                    "status": "pinning certification failed",
                    "player": player,
                    "detail": player_certificate,
                }
            player_certificates[player] = player_certificate
            if maximum == floors[player] + level:
                pinned.append(player)
        if not pinned:
            return None, {"status": "certified level has no pinned player"}
        rounds.append({
            "level": level,
            "free_players": list(free),
            "pinned_players": pinned,
            "level_certificate": certificate,
            "pinning_certificates": player_certificates,
        })
        for player in pinned:
            fixed[player] = floors[player] + level
            free.remove(player)

    return [fixed[player] for player in range(n)], {
        "status": "exact certified leximin sequence",
        "rounds": rounds,
    }
