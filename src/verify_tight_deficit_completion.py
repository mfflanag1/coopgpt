"""Exact audit of the tight deficit-completion theorem's equality cases."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximin_core_exact
from tugame import Game
from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope,
)
from verify_three_trace_half_integral_family import (
    defining_coalitions,
    lower_envelope as three_trace_envelope,
    mask,
    vertices,
)


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def slack(game, phi, coalition):
    return payoff(phi, coalition) - game.v[coalition]


def audit_identity(n, target, cover, completion, alpha, beta):
    loads = [F(0)] * n
    for coalition, weight in cover + completion:
        for player in range(n):
            if coalition >> player & 1:
                loads[player] += weight
    for player in range(n):
        if target >> player & 1:
            loads[player] -= alpha - beta
    if loads != [beta] * n:
        raise AssertionError("deficit-completion incidence identity failed")


def five_player_case():
    game = Game(5, lower_envelope(BASE_GENERATORS))
    phi = tuple(leximin_core_exact(game))
    if phi != PHI_BASE:
        raise AssertionError("five-player Lmin changed")
    left = mask((0, 2, 4))
    right = mask((2, 3, 4))
    target = left & right
    exterior = ((1 << 5) - 1) & ~(left | right)
    cover = [(left, F(1)), (right, F(1))]
    completion = [(exterior, F(1))]
    audit_identity(5, target, cover, completion, F(2), F(1))
    lhs = slack(game, phi, target)
    rhs = slack(game, phi, exterior)
    deficit_price = payoff(phi, exterior)
    completion_worth = game.v[exterior]
    if lhs != 1 or rhs != lhs or rhs != deficit_price - completion_worth:
        raise AssertionError("five-player completion budget is not saturated")
    return {
        "alpha": "2",
        "beta": "1",
        "target_slack": str(lhs),
        "completion_cost": str(rhs),
        "deficit_phi_price": str(deficit_price),
        "maximum_fractional_completion_worth": str(completion_worth),
        "gap_identity_verified": True,
        "completion": "exterior singleton",
        "equality": True,
    }


def seven_player_case():
    t, u, w = 1, 2, 2
    (poor_a, poor_b), C, A, B, constraints = defining_coalitions(t, u, w)
    game = three_trace_envelope(vertices(t, u, w))
    phi = tuple([F(1), F(1)] + [F(2)] * (t + u + w))
    if tuple(leximin_core_exact(game)) != phi:
        raise AssertionError("seven-player Lmin changed")
    target = mask(range(2, 7))
    cover = [(mask(coalition), F(1, 2)) for coalition, _ in constraints]
    completion = [(1 << poor_a, F(1, 2))]
    audit_identity(7, target, cover, completion, F(1), F(1, 2))
    target_slack = slack(game, phi, target)
    singleton_slack = slack(game, phi, 1 << poor_a)
    lhs = F(1, 2) * target_slack
    rhs = F(1, 2) * singleton_slack
    deficit_price = F(1, 2) * phi[poor_a]
    completion_worth = F(1, 2) * game.v[1 << poor_a]
    if (
        target_slack != 1
        or singleton_slack != 1
        or lhs != rhs
        or rhs != deficit_price - completion_worth
    ):
        raise AssertionError("seven-player completion budget is not saturated")
    return {
        "alpha": "1",
        "beta": "1/2",
        "poor_loads": {str(poor_a + 1): "0", str(poor_b + 1): "1/2"},
        "target_slack": str(target_slack),
        "completion_cost": str(rhs),
        "deficit_phi_price": str(deficit_price),
        "maximum_fractional_completion_worth": str(completion_worth),
        "gap_identity_verified": True,
        "completion": "half of losing poorer singleton",
        "equality": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "status": "tight deficit completion audited",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "five_player_two_column_equality": five_player_case(),
        "seven_player_three_trace_equality": seven_player_case(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
