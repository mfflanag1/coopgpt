"""Exact audit of the exact-balanced slack budget in the five-player game.

This checks the concrete identity used in
paper3/GENERAL_BOUNDARY_OBSTRUCTION.md.  It is an audit of the application,
not a substitute for the general two-line exact-balancedness proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from exactlp import exact_linprog
from leximin import leximin_core_exact
from tugame import Game
from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope,
    members,
)


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


def coalition_sum(vector, coalition):
    return sum(
        vector[player]
        for player in range(len(vector))
        if coalition >> player & 1
    )


def boundary_defect(game, phi, richer):
    """Minimize the boundary-cover RHS with alpha-beta normalized to one."""
    tight = [
        coalition
        for coalition in range(1, game.N)
        if coalition_sum(phi, coalition) == game.v[coalition]
    ]
    # Variables are the tight-coalition weights followed by beta.  The exact
    # LP solver treats variables as free, so append explicit nonnegativity rows.
    variable_count = len(tight) + 1
    beta_index = len(tight)
    objective = [
        -coalition_sum(phi, coalition)
        for coalition in tight
    ] + [game.v[game.N]]
    A_ub, b_ub = [], []
    for player in range(game.n):
        row = [int(coalition >> player & 1) for coalition in tight] + [-1]
        A_ub.append(row)
        b_ub.append(1 if richer >> player & 1 else 0)
    for index in range(variable_count):
        row = [0] * variable_count
        row[index] = -1
        A_ub.append(row)
        b_ub.append(0)
    status, optimum, solution = exact_linprog(
        objective, A_ub=A_ub, b_ub=b_ub
    )
    if status != "optimal":
        raise RuntimeError(f"boundary-defect LP returned {status}")
    defect = coalition_sum(phi, richer) + optimum
    weights = {
        tight[index]: solution[index]
        for index in range(len(tight))
        if solution[index]
    }
    return defect, solution[beta_index], weights


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    game = Game(5, lower_envelope(BASE_GENERATORS))
    phi = tuple(leximin_core_exact(game))
    if phi != PHI_BASE:
        raise RuntimeError(f"unexpected base Lmin allocation: {phi}")

    richer = (1 << 2) | (1 << 4)            # {3,5}
    protector_1 = (1 << 0) | richer         # {1,3,5}
    protector_4 = (1 << 3) | richer         # {3,4,5}
    singleton_2 = 1 << 1                    # {2}
    weights = {
        protector_1: 1,
        protector_4: 1,
        singleton_2: 1,
        richer: -1,
    }

    coverage = [
        sum(weight for coalition, weight in weights.items()
            if coalition >> player & 1)
        for player in range(5)
    ]
    if coverage != [1] * 5:
        raise RuntimeError(f"not an exact-balanced incidence identity: {coverage}")

    weighted_value = sum(
        weight * game.v[coalition]
        for coalition, weight in weights.items()
    )
    if weighted_value != game.v[game.N]:
        raise RuntimeError(
            "the five-player exact-balanced inequality is not attained at equality"
        )

    slack = {
        coalition: coalition_sum(phi, coalition) - game.v[coalition]
        for coalition in weights
    }
    weighted_slack = sum(
        weight * slack[coalition]
        for coalition, weight in weights.items()
    )
    if weighted_slack != 0:
        raise RuntimeError(f"slack budget does not balance: {weighted_slack}")
    if slack[protector_1] != 0 or slack[protector_4] != 0:
        raise RuntimeError("the two claimed protectors are not tight")
    if slack[singleton_2] != 1 or slack[richer] != 1:
        raise RuntimeError("the positive and negative slack budgets are not one")

    protector_coverage = [
        int(protector_1 >> player & 1)
        + int(protector_4 >> player & 1)
        for player in range(5)
    ]
    alpha, beta = 2, 1
    left = (alpha - beta) * slack[richer]
    right = sum(
        (alpha - protector_coverage[player]) * phi[player]
        for player in range(5)
        if richer >> player & 1
    ) + sum(
        (beta - protector_coverage[player]) * phi[player]
        for player in range(5)
        if not richer >> player & 1
    )
    if left != 1 or right != 1:
        raise RuntimeError(f"boundary-cover equality failed: {left} != {right}")

    defect, optimal_beta, optimal_weights = boundary_defect(game, phi, richer)
    if defect != slack[richer]:
        raise RuntimeError(
            f"canonical boundary defect is not sharp: {defect} != {slack[richer]}"
        )

    payload = {
        "status": "exact-balanced five-player slack budget verified",
        "arithmetic": "exact rational",
        "lmin": [str(value) for value in phi],
        "negative_coalition": members(richer),
        "exact_balanced_identity": {
            "positive": [
                members(protector_1),
                members(protector_4),
                members(singleton_2),
            ],
            "negative": members(richer),
            "player_coverage": coverage,
            "weighted_game_value": str(weighted_value),
            "grand_coalition_value": str(game.v[game.N]),
        },
        "slack_budget": {
            "positive_protector_slacks": [
                str(slack[protector_1]),
                str(slack[protector_4]),
            ],
            "positive_singleton_slack": str(slack[singleton_2]),
            "negative_suffix_slack": str(slack[richer]),
            "weighted_total": str(weighted_slack),
        },
        "boundary_cover": {
            "alpha": alpha,
            "beta": beta,
            "protector_player_loads": protector_coverage,
            "left_side": str(left),
            "right_side": str(right),
            "attained_at_equality": True,
            "exact_lp_optimum_defect": str(defect),
            "exact_lp_beta": str(optimal_beta),
            "exact_lp_positive_tight_weights": [
                {
                    "coalition": members(coalition),
                    "weight": str(weight),
                }
                for coalition, weight in sorted(optimal_weights.items())
            ],
        },
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
