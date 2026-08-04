"""Exact audit of the rooted deficit-completion equality cases.

The general rooted theorem is proved symbolically in the manuscript.  This
script reconstructs the five- and seven-player games, recomputes Lmin, checks
their rooted identities and marginal-cost equalities, verifies circuit
minimality, and applies the published exceptional-set decomposition test.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximin_core_exact
from probe_lmin_atom_indecomposability import decompositions
from tugame import Game, is_balanced_game
from verify_atomic_lmin_obstruction import audit_circuit
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


def marginal_factorization(game, phi, target):
    outside = [i for i in range(game.n) if not (target >> i & 1)]
    values = [F(0)] * (1 << len(outside))
    for local in range(1 << len(outside)):
        coalition = target
        for j, player in enumerate(outside):
            if local >> j & 1:
                coalition |= 1 << player
        values[local] = game.v[coalition] - game.v[target]
    marginal = Game(len(outside), values)
    restricted_phi = tuple(phi[player] for player in outside)
    target_slack = slack(game, phi, target)
    if not is_balanced_game(marginal):
        raise AssertionError("H-marginal game is not balanced")
    if marginal.v[marginal.N] - sum(restricted_phi) != target_slack:
        raise AssertionError("marginal efficiency deficit is not target slack")
    for local in range(1 << len(outside)):
        coalition = target
        for j, player in enumerate(outside):
            if local >> j & 1:
                coalition |= 1 << player
        lhs = payoff(restricted_phi, local) - marginal.v[local]
        rhs = slack(game, phi, coalition) - target_slack
        if lhs != rhs:
            raise AssertionError("marginal slack factorization failed")
    if marginal.in_core(restricted_phi):
        raise AssertionError("slack target unexpectedly gave a marginal-core allocation")
    marginal_lmin = tuple(leximin_core_exact(marginal))
    floors = tuple(marginal.v[1 << i] for i in range(marginal.n))
    residual_values = [
        marginal.v[coalition]
        - sum(floors[i] for i in range(marginal.n) if coalition >> i & 1)
        for coalition in range(1 << marginal.n)
    ]
    residual_lmin = tuple(leximin_core_exact(Game(marginal.n, residual_values)))
    normalized_marginal_lmin = tuple(
        floors[i] + residual_lmin[i] for i in range(marginal.n)
    )
    uniform_repair = tuple(
        value + target_slack / len(outside) for value in restricted_phi
    )
    return {
        "marginal_players": len(outside),
        "marginal_game_balanced": True,
        "efficiency_deficit": str(target_slack),
        "slack_factorization_all_coalitions": True,
        "restricted_lmin_in_marginal_core": False,
        "marginal_lmin": [str(value) for value in marginal_lmin],
        "normalized_marginal_lmin": [str(value) for value in normalized_marginal_lmin],
        "uniform_efficiency_repair": [str(value) for value in uniform_repair],
        "uniform_repair_equals_marginal_lmin": uniform_repair == marginal_lmin,
        "uniform_repair_equals_normalized_marginal_lmin": (
            uniform_repair == normalized_marginal_lmin
        ),
    }


def five_player_case():
    game = Game(5, lower_envelope(BASE_GENERATORS))
    phi = tuple(leximin_core_exact(game))
    if phi != PHI_BASE:
        raise AssertionError("five-player Lmin changed")
    left = mask((0, 2, 4))
    right = mask((2, 3, 4))
    target = left & right
    exterior = ((1 << 5) - 1) & ~(left | right)
    rooted = target | exterior
    support = [left, right, rooted, target]
    coefficients = [F(1), F(1), F(1), F(-2)]
    circuit = audit_circuit(5, support, coefficients, target)
    target_slack = slack(game, phi, target)
    rooted_slack = slack(game, phi, rooted)
    exterior_slack = slack(game, phi, exterior)
    rooted_cost = rooted_slack - target_slack
    surplus = target_slack + exterior_slack - rooted_slack
    if (target_slack, rooted_slack, rooted_cost, surplus) != (F(1), F(2), F(1), F(0)):
        raise AssertionError("five-player rooted equality changed")
    witnesses = decompositions(5, support)
    if witnesses:
        raise AssertionError("five-player rooted atom is no longer indecomposable")
    return {
        **circuit,
        "marginal_core_factorization": marginal_factorization(game, phi, target),
        "target_slack": str(target_slack),
        "rooted_extension_slack": str(rooted_slack),
        "rooted_marginal_cost": str(rooted_cost),
        "superadditivity_surplus": str(surplus),
        "rooted_budget_equality": True,
        "indecomposable": True,
        "decomposition_count": 0,
    }


def seven_player_case():
    t, u, w = 1, 2, 2
    (poor_a, _), _, A, B, constraints = defining_coalitions(t, u, w)
    game = three_trace_envelope(vertices(t, u, w))
    phi = tuple([F(1), F(1)] + [F(2)] * (t + u + w))
    if tuple(leximin_core_exact(game)) != phi:
        raise AssertionError("seven-player Lmin changed")
    traces = [mask(coalition) for coalition, _ in constraints]
    target = mask(range(2, 7))
    singleton = 1 << poor_a
    rooted = target | singleton
    support = traces + [rooted, target]
    coefficients = [F(1, 2)] * 4 + [F(-1)]
    circuit = audit_circuit(7, support, coefficients, target)
    target_slack = slack(game, phi, target)
    rooted_slack = slack(game, phi, rooted)
    singleton_slack = slack(game, phi, singleton)
    rooted_cost = F(1, 2) * (rooted_slack - target_slack)
    surplus = target_slack + singleton_slack - rooted_slack
    if (target_slack, rooted_slack, rooted_cost, surplus) != (F(1), F(2), F(1, 2), F(0)):
        raise AssertionError("seven-player rooted equality changed")
    witnesses = decompositions(7, support)
    if len(witnesses) != 1:
        raise AssertionError("seven-player rooted decomposition count changed")
    middle = mask(A + B)
    middle_slack = slack(game, phi, middle)
    internal_support = [traces[0], traces[1], middle, target]
    internal_circuit = audit_circuit(
        7, internal_support, [F(1), F(1), F(1), F(-2)], target
    )
    complementary_support = [traces[2], rooted, middle]
    complementary_circuit = audit_circuit(
        7, complementary_support, [F(1), F(1), F(-1)], middle
    )
    if middle_slack != 2:
        raise AssertionError("seven-player middle-face slack changed")
    if decompositions(7, internal_support) or decompositions(7, complementary_support):
        raise AssertionError("seven-player facet factor became decomposable")
    return {
        **circuit,
        "marginal_core_factorization": marginal_factorization(game, phi, target),
        "target_slack": str(target_slack),
        "rooted_extension_slack": str(rooted_slack),
        "weighted_rooted_marginal_cost": str(rooted_cost),
        "superadditivity_surplus": str(surplus),
        "rooted_budget_equality": True,
        "indecomposable": False,
        "decomposition_count": 1,
        "decomposition": witnesses[0],
        "middle_face_slack": str(middle_slack),
        "two_facet_slack_sandwich": "2*s(H) <= s(A union B) <= s(rooted extension)",
        "internal_triangle_factor": {**internal_circuit, "indecomposable": True},
        "complementary_diamond_factor": {
            **complementary_circuit,
            "indecomposable": True,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "status": "rooted deficit-completion examples audited",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "five_player_rooted_facet_atom": five_player_case(),
        "seven_player_rooted_residual_decomposition": seven_player_case(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
