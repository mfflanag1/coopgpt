"""Exactify the finite dual of a common carrier-face separator.

Given an exact game, a target coalition S, and candidate players K subset S,
solve the joint system in Proposition ``lx-carrier-separator-dual``.  The LP
maximizes a normalized strict separation margin epsilon.  Every reported
certificate is rechecked with ``Fraction`` arithmetic after the floating-point
discovery solve.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from certified_leximin import leximin_core_certified
from tugame import Game


def rat(value):
    return F(float(value)).limit_denominator(1_000_000)


def coalition_sum(values, coalition):
    return sum(
        value for player, value in enumerate(values)
        if coalition >> player & 1
    )


def mask_from_players(players):
    return sum(1 << (player - 1) for player in players)


def analyze(payload, target_players, candidate_players, separator_players=None):
    n = int(payload["n"])
    grand = (1 << n) - 1
    worths = tuple(F(value) for value in payload["v"])
    game = Game(n, list(worths))
    if payload.get("phi") is None:
        phi, certificate = leximin_core_certified(game)
        if phi is None:
            raise RuntimeError(certificate)
    else:
        phi = tuple(F(value) for value in payload["phi"])

    target = mask_from_players(target_players)
    candidates = tuple(player - 1 for player in candidate_players)
    separator_support = tuple(
        player - 1 for player in (
            target_players if separator_players is None else separator_players
        )
    )
    if not target or target == grand:
        raise ValueError("S must be a nonempty proper coalition")
    if not candidates or any(not (target >> player & 1) for player in candidates):
        raise ValueError("K must be a nonempty subset of S")
    if (not separator_support
            or any(not (target >> player & 1)
                   for player in separator_support)):
        raise ValueError("separator support must be a nonempty subset of S")
    outside = grand ^ target
    coalitions = tuple(range(1, grand))
    slacks = {
        coalition: coalition_sum(phi, coalition) - worths[coalition]
        for coalition in coalitions
    }
    if any(value < 0 for value in slacks.values()):
        raise ValueError("phi is not in the core")

    # Variables: w_0,...,w_{n-1}; for each k, theta_U, a_k, b_k;
    # and the common strict margin epsilon.
    cursor = n
    blocks = {}
    for player in candidates:
        theta = {coalition: cursor + index for index, coalition in enumerate(coalitions)}
        cursor += len(coalitions)
        a_index, b_index = cursor, cursor + 1
        cursor += 2
        blocks[player] = (theta, a_index, b_index)
    epsilon_index = cursor
    variable_count = cursor + 1

    objective = np.zeros(variable_count)
    objective[epsilon_index] = -1.0
    A_eq, b_eq = [], []
    normalization = np.zeros(variable_count)
    for player in range(n):
        if target >> player & 1:
            normalization[player] = 1.0
    A_eq.append(normalization)
    b_eq.append(1.0)

    for player in candidates:
        carrier = outside | (1 << player)
        theta, a_index, b_index = blocks[player]
        for coordinate in range(n):
            row = np.zeros(variable_count)
            row[coordinate] = 1.0
            row[a_index] = -1.0
            if carrier >> coordinate & 1:
                row[b_index] = -1.0
            for coalition in coalitions:
                if coalition >> coordinate & 1:
                    row[theta[coalition]] = 1.0
            A_eq.append(row)
            b_eq.append(0.0)

    A_ub, b_ub = [], []
    for player in candidates:
        carrier = outside | (1 << player)
        theta, _a_index, b_index = blocks[player]
        row = np.zeros(variable_count)
        for coalition in coalitions:
            row[theta[coalition]] = float(slacks[coalition])
        row[b_index] = -float(slacks[carrier])
        row[epsilon_index] = 1.0
        A_ub.append(row)
        b_ub.append(0.0)

    bounds = []
    for player in range(n):
        bounds.append(
            (0.0, None) if player in separator_support else (0.0, 0.0)
        )
    for _player in candidates:
        bounds.extend([(0.0, None)] * len(coalitions))
        bounds.extend([(None, None), (None, None)])
    bounds.append((None, None))

    result = linprog(
        objective,
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq),
        b_eq=np.asarray(b_eq),
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        return {
            "status": result.message,
            "n": n,
            "S": target_players,
            "K": candidate_players,
        }

    solution = tuple(rat(value) for value in result.x)
    w = solution[:n]
    epsilon = solution[epsilon_index]
    exact = sum(w) == 1 and all(
        value >= 0 if target >> player & 1 else value == 0
        for player, value in enumerate(w)
    )
    certificates = []
    for player in candidates:
        carrier = outside | (1 << player)
        theta_index, a_index, b_index = blocks[player]
        theta = {
            coalition: solution[index]
            for coalition, index in theta_index.items()
            if solution[index]
        }
        a_value, b_value = solution[a_index], solution[b_index]
        stationarity = []
        for coordinate in range(n):
            rhs = a_value + b_value * int(carrier >> coordinate & 1)
            rhs -= sum(
                value for coalition, value in theta.items()
                if coalition >> coordinate & 1
            )
            stationarity.append(rhs)
        slack_left = sum(
            value * slacks[coalition] for coalition, value in theta.items()
        )
        slack_right = b_value * slacks[carrier]
        certificate_exact = (
            tuple(stationarity) == w
            and all(value >= 0 for value in theta.values())
            and slack_left + epsilon <= slack_right
        )
        exact &= certificate_exact
        singleton = 1 << player
        certificates.append({
            "player": player + 1,
            "carrier_mask": carrier,
            "carrier_margin": str(
                slacks[carrier] - slacks[singleton]
            ),
            "a": str(a_value),
            "b": str(b_value),
            "carrier_slack": str(slacks[carrier]),
            "weighted_slack": str(slack_left),
            "strict_gap": str(slack_right - slack_left),
            "theta": {
                str(coalition): str(value)
                for coalition, value in theta.items()
            },
            "exact": certificate_exact,
        })

    return {
        "status": "exact common carrier-face separator dual certificate",
        "n": n,
        "S": target_players,
        "K": candidate_players,
        "separator_support": [player+1 for player in separator_support],
        "phi": [str(value) for value in phi],
        "epsilon": str(epsilon),
        "strict_separator": epsilon > 0,
        "w": [str(value) for value in w],
        "certificates": certificates,
        "exact": exact,
    }


def player_list(value):
    return [int(item) for item in value.split(",") if item]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--S", type=player_list)
    parser.add_argument("--K", type=player_list, required=True)
    parser.add_argument("--W", type=player_list)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    payload = json.loads(args.input.read_text())
    target_players = args.S or [player + 1 for player in payload["S"]]
    rendered = json.dumps(
        analyze(payload, target_players, args.K, args.W), indent=2
    ) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
