"""Exact audit of the two-column Lmin obstruction normal form.

The finite checks below are bug detectors for a dimension-free proof.  They
audit the abstract load-pattern implication, the exterior-slack conservation
identity in the sharp five-player game, and the generalized two-level
lower-envelope realization over an exact-rational parameter grid.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximin_core_exact
from tugame import Game
from verify_binary_broken_diamond_realization import instance
from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope,
)


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def abstract_normal_form(max_n=7):
    """Exhaustively check the two-column load-pattern implication."""
    checked = 0
    for n in range(4, max_n + 1):
        full = (1 << n) - 1
        for left in range(1, full):
            for right in range(left + 1, full):
                meet = left & right
                only_left = left & ~right
                only_right = right & ~left
                if not (meet and only_left and only_right):
                    continue
                for left_weight, right_weight in (
                    (F(1), F(1)),
                    (F(1), F(2)),
                    (F(2), F(1)),
                    (F(2, 3), F(5, 4)),
                ):
                    loads = [
                        left_weight * int(left >> i & 1)
                        + right_weight * int(right >> i & 1)
                        for i in range(n)
                    ]
                    alpha = max(loads)
                    target = sum(
                        1 << i for i, load in enumerate(loads) if load == alpha
                    )
                    if not (0 < target < full):
                        continue
                    checked += 1
                    if meet != target:
                        raise AssertionError(
                            "two-column strict cover is not in meet normal form"
                        )
    return checked


def sharp_five_player_budget():
    values = lower_envelope(BASE_GENERATORS)
    game = Game(5, values)
    phi = tuple(leximin_core_exact(game))
    if phi != PHI_BASE:
        raise AssertionError("sharp five-player Lmin changed")
    left = sum(1 << i for i in (0, 2, 4))
    right = sum(1 << i for i in (2, 3, 4))
    target = left & right
    exterior = ((1 << 5) - 1) & ~(left | right)
    target_slack = payoff(phi, target) - values[target]
    exterior_slack = payoff(phi, exterior) - values[exterior]
    if target_slack != 1 or exterior_slack != 1:
        raise AssertionError("sharp exterior-slack budget is not saturated")
    identity = [
        int(left >> i & 1)
        + int(right >> i & 1)
        + int(exterior >> i & 1)
        - int(target >> i & 1)
        for i in range(5)
    ]
    if identity != [1] * 5:
        raise AssertionError("exact-balanced two-column identity failed")
    return {
        "lmin": [str(value) for value in phi],
        "target": [3, 5],
        "exterior": [2],
        "target_slack": str(target_slack),
        "exterior_slack": str(exterior_slack),
        "budget_saturated": True,
    }


def generalized_realizations():
    levels = ((F(3, 2), F(1)), (F(2), F(1)), (F(3), F(1)), (F(4), F(3)))
    sizes = ((1, 1, 1, 2), (1, 1, 1, 3), (2, 1, 1, 1), (2, 1, 2, 1))
    cases = []
    for rich, poor in levels:
        for c, x, y, r in sizes:
            if c == 1 and poor * r < rich:
                continue
            detail = instance(c, x, y, r, rich, poor)
            target_slack = F(detail["intersection_slack"])
            exterior_slack = F(detail["exterior_slack"])
            if target_slack > exterior_slack:
                raise AssertionError("realization violates exterior-slack budget")
            detail["target_budget_saturated"] = target_slack == exterior_slack
            cases.append(detail)
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-n", type=int, default=7)
    args = parser.parse_args()
    payload = {
        "status": "two-column Lmin obstruction audited",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "abstract_strict_cover_instances": abstract_normal_form(args.max_n),
        "maximum_n_for_abstract_audit": args.max_n,
        "sharp_five_player_budget": sharp_five_player_budget(),
        "generalized_realizations": generalized_realizations(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
