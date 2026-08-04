"""Exact audit of the terminal slack-cut theorem on three mechanisms.

The theorem has a short human proof.  This script only recomputes interval
maxima, the neighbor inequalities that force every exactifier's signs,
displayed defining exactifiers, and deficit transport from the defining exact
games; it is not independent proof evidence.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope as five_lower_envelope,
)
from verify_three_trace_half_integral_family import (
    lower_envelope as three_lower_envelope,
    mask,
    vertices as three_vertices,
)
from verify_two_poorer_rich_family import (
    generators as cosingleton_generators,
    lower_envelope as cosingleton_lower_envelope,
)


def coalition_sum(point, coalition):
    return sum(
        (point[i] for i in range(len(point)) if coalition >> i & 1), F(0)
    )


def members(n, coalition):
    return [i + 1 for i in range(n) if coalition >> i & 1]


def audit_terminal_cut(name, points, values, phi, root, poor_loads):
    points = [tuple(F(value) for value in point) for point in points]
    phi = tuple(F(value) for value in phi)
    n = len(phi)
    full = (1 << n) - 1
    poor = [i for i in range(n) if not (root >> i & 1)]
    if set(poor_loads) != set(poor):
        raise AssertionError(f"{name}: poor-load map has wrong support")
    loads = {i: F(poor_loads[i]) for i in poor}
    if any(not (F(0) <= load < F(1)) for load in loads.values()):
        raise AssertionError(f"{name}: cover is not strictly underloaded")

    def slack(coalition):
        return coalition_sum(phi, coalition) - values[coalition]

    root_slack = slack(root)
    if root_slack <= 0:
        raise AssertionError(f"{name}: root is not slack")
    interval = [
        coalition
        for coalition in range(1 << n)
        if coalition & root == root
    ]
    maximum = max(slack(coalition) for coalition in interval)
    terminals = [coalition for coalition in interval if slack(coalition) == maximum]
    if maximum <= root_slack:
        raise AssertionError(f"{name}: strict ascent was not recovered")

    terminal_records = []
    for terminal in terminals:
        if terminal in (root, full):
            raise AssertionError(f"{name}: terminal cut is degenerate")
        losing_side = [i for i in poor if terminal >> i & 1]
        gaining_side = [i for i in poor if not (terminal >> i & 1)]
        if not losing_side or not gaining_side:
            raise AssertionError(f"{name}: terminal cut does not puncture poor side")

        for i in losing_side:
            marginal = values[terminal] - values[terminal ^ (1 << i)]
            if marginal > phi[i]:
                raise AssertionError(f"{name}: deletion marginal has wrong sign")
        for i in gaining_side:
            marginal = values[terminal | (1 << i)] - values[terminal]
            if marginal < phi[i]:
                raise AssertionError(f"{name}: addition marginal has wrong sign")

        defining_exactifiers = [
            point
            for point in points
            if coalition_sum(point, terminal) == values[terminal]
        ]
        if not defining_exactifiers:
            raise AssertionError(f"{name}: no defining exactifier found")
        witness_records = []
        for point in defining_exactifiers:
            delta = tuple(point[i] - phi[i] for i in range(n))
            if coalition_sum(delta, terminal) != -maximum:
                raise AssertionError(f"{name}: terminal deficit identity failed")
            if sum((delta[i] for i in gaining_side), F(0)) != maximum:
                raise AssertionError(f"{name}: exterior gain identity failed")
            if any(delta[i] > 0 for i in losing_side):
                raise AssertionError(f"{name}: included poor player gains")
            if any(delta[i] < 0 for i in gaining_side):
                raise AssertionError(f"{name}: excluded poor player loses")
            losers = [i for i in losing_side if delta[i] < 0]
            gainers = [i for i in gaining_side if delta[i] > 0]
            if not losers or not gainers:
                raise AssertionError(f"{name}: strict transfer signs missing")
            if not any(phi[d] <= phi[e] for d in losers for e in gainers):
                raise AssertionError(f"{name}: payoff inversion missing")

            left = sum(
                (F(1) - loads[i]) * (-delta[i]) for i in losing_side
            )
            right = sum(
                (F(1) - loads[i]) * delta[i] for i in gaining_side
            )
            if left < right or right <= 0:
                raise AssertionError(f"{name}: deficit transport failed")
            minimum_exterior_deficit = min(
                F(1) - loads[i] for i in gaining_side
            )
            singleton_budget = sum(
                (F(1) - loads[i]) * (phi[i] - values[1 << i])
                for i in losing_side
            )
            required_budget = minimum_exterior_deficit * maximum
            if required_budget > singleton_budget:
                raise AssertionError(f"{name}: singleton sacrifice budget failed")
            witness_records.append(
                {
                    "delta": [str(value) for value in delta],
                    "strict_losers": members(n, sum(1 << i for i in losers)),
                    "strict_gainers": members(n, sum(1 << i for i in gainers)),
                    "weighted_loss": str(left),
                    "weighted_gain": str(right),
                    "transport_saturated": left == right,
                    "minimum_exterior_deficit": str(minimum_exterior_deficit),
                    "required_singleton_budget": str(required_budget),
                    "available_singleton_budget": str(singleton_budget),
                    "singleton_budget_saturated": required_budget == singleton_budget,
                }
            )

        terminal_records.append(
            {
                "coalition": members(n, terminal),
                "slack": str(maximum),
                "included_poorer_players": [i + 1 for i in losing_side],
                "excluded_poorer_players": [i + 1 for i in gaining_side],
                "defining_exactifiers": witness_records,
            }
        )

    return {
        "name": name,
        "player_count": n,
        "root": members(n, root),
        "root_slack": str(root_slack),
        "normalized_poor_loads": {
            str(i + 1): str(loads[i]) for i in poor
        },
        "terminal_slack": str(maximum),
        "terminals": terminal_records,
    }


def audits():
    five_points = BASE_GENERATORS
    five_values = five_lower_envelope(five_points)
    five = audit_terminal_cut(
        "five_player_pure_star",
        five_points,
        five_values,
        PHI_BASE,
        mask((2, 4)),
        {0: F(1, 2), 1: F(0), 3: F(1, 2)},
    )

    three_points = three_vertices(1, 2, 2)
    three_game = three_lower_envelope(three_points)
    three = audit_terminal_cut(
        "seven_player_three_trace",
        three_points,
        three_game.v,
        tuple([F(1), F(1)] + [F(2)] * 5),
        mask(range(2, 7)),
        {0: F(0), 1: F(1, 2)},
    )

    m, h = 2, 4
    scale = (h - 2) * (h - 3)
    cosingleton_points = cosingleton_generators(m, h)
    cosingleton_values = cosingleton_lower_envelope(cosingleton_points)
    cosingleton = audit_terminal_cut(
        "six_player_four_cosingleton",
        cosingleton_points,
        cosingleton_values,
        tuple([F(scale)] * m + [F(2 * scale)] * h),
        mask(range(m, m + h)),
        {0: F(2, 3), 1: F(0)},
    )
    return [five, three, cosingleton]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "status": "terminal slack cuts audited",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "audits": audits(),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
