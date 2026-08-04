"""Exact audit of the quantitative uncrossing-defect budget."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

from tugame import Game
from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope as five_envelope,
)
from verify_three_trace_half_integral_family import (
    defining_coalitions,
    lower_envelope as trace_envelope,
    mask,
    vertices,
)


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def crossing(left, right):
    return bool(left & right and left & ~right and right & ~left)


def loads(n, weights):
    return tuple(
        sum(weight for coalition, weight in weights.items()
            if coalition >> player & 1)
        for player in range(n)
    )


def uncross(game, phi, richer, initial):
    n = game.n
    weights = defaultdict(F, {coalition: F(weight)
                              for coalition, weight in initial.items()})
    initial_loads = loads(n, weights)
    history = []

    while True:
        support = sorted(coalition for coalition, weight in weights.items()
                         if weight > 0)
        pair = next(
            ((left, right) for index, left in enumerate(support)
             for right in support[index + 1:] if crossing(left, right)),
            None,
        )
        if pair is None:
            break
        left, right = pair
        intersection, union = left & right, left | right
        delta = min(weights[left], weights[right])
        before_energy = sum(
            weight * coalition.bit_count() * (n - coalition.bit_count())
            for coalition, weight in weights.items()
        )
        defect = (
            game.v[left] + game.v[right]
            - game.v[intersection] - game.v[union]
        )
        weights[left] -= delta
        weights[right] -= delta
        weights[intersection] += delta
        weights[union] += delta
        for coalition in (left, right, intersection):
            if coalition == 0 or weights[coalition] == 0:
                weights.pop(coalition, None)
        after_energy = sum(
            weight * coalition.bit_count() * (n - coalition.bit_count())
            for coalition, weight in weights.items()
        )
        expected_drop = (
            2 * delta * (left & ~right).bit_count()
            * (right & ~left).bit_count()
        )
        if before_energy - after_energy != expected_drop or expected_drop <= 0:
            raise AssertionError("wrong uncrossing energy drop")
        if loads(n, weights) != initial_loads:
            raise AssertionError("uncrossing changed player loads")
        history.append({
            "left": left,
            "right": right,
            "intersection": intersection,
            "union": union,
            "multiplicity": delta,
            "defect": defect,
            "weighted_defect": delta * defect,
            "energy_drop": expected_drop,
        })

    support = tuple(sorted(weights))
    if any(crossing(left, right) for i, left in enumerate(support)
           for right in support[i + 1:]):
        raise AssertionError("final support is not laminar")

    minimal = []
    for player in range(n):
        if not richer >> player & 1:
            continue
        containing = [coalition for coalition in support
                      if coalition >> player & 1]
        member = min(containing, key=lambda coalition: coalition.bit_count())
        if member & ~richer:
            raise AssertionError("minimal rich set meets the outside")
        minimal.append(member)
    blocks = tuple(sorted(
        member for member in set(minimal)
        if not any(member != other and member & ~other == 0
                   for other in set(minimal))
    ))
    if any(left & right for i, left in enumerate(blocks)
           for right in blocks[i + 1:]) or sum(blocks) != richer:
        raise AssertionError("extracted sets do not partition the target")

    slack = lambda coalition: payoff(phi, coalition) - game.v[coalition]
    minimum_block_multiplicity = min(weights[block] for block in blocks)
    target_bound = minimum_block_multiplicity * slack(richer)
    final_weighted_slack = sum(
        weight * slack(coalition) for coalition, weight in weights.items()
    )
    cumulative_defect = sum(item["weighted_defect"] for item in history)
    block_slack = minimum_block_multiplicity * sum(slack(block) for block in blocks)
    if not (F(0) <= target_bound <= block_slack <= final_weighted_slack):
        raise AssertionError("uncrossing-defect inequalities failed")
    if final_weighted_slack != cumulative_defect:
        raise AssertionError("weighted slack is not conserved")
    if any(slack(coalition) != 0 for coalition in initial):
        raise AssertionError("initial cover is not tight")

    def members(coalition):
        return [player + 1 for player in range(n) if coalition >> player & 1]

    return {
        "initial_loads": [str(x) for x in initial_loads],
        "target": members(richer),
        "target_slack": str(slack(richer)),
        "uncrossing_steps": [
            {
                "left": members(item["left"]),
                "right": members(item["right"]),
                "intersection": members(item["intersection"]),
                "union": members(item["union"]),
                "multiplicity": str(item["multiplicity"]),
                "defect": str(item["defect"]),
                "weighted_defect": str(item["weighted_defect"]),
                "energy_drop": str(item["energy_drop"]),
            }
            for item in history
        ],
        "final_weights": [
            {"coalition": members(coalition), "multiplicity": str(weight)}
            for coalition, weight in sorted(weights.items())
        ],
        "extracted_partition": [members(block) for block in blocks],
        "minimum_partition_block_multiplicity": str(minimum_block_multiplicity),
        "scaled_target_slack": str(target_bound),
        "scaled_partition_slack": str(block_slack),
        "final_weighted_slack": str(final_weighted_slack),
        "cumulative_weighted_defect": str(cumulative_defect),
        "budget_verified": True,
    }


def five_player_case():
    game = Game(5, five_envelope(BASE_GENERATORS))
    richer = (1 << 2) | (1 << 4)
    initial = {
        (1 << 0) | richer: 1,
        (1 << 3) | richer: 1,
    }
    return uncross(game, PHI_BASE, richer, initial)


def three_column_case():
    (_, _), _, _, _, constraints = defining_coalitions(1, 2, 2)
    game = trace_envelope(vertices(1, 2, 2))
    phi = (F(1), F(1)) + (F(2),) * 5
    richer = mask(range(2, 7))
    initial = {mask(coalition): 1 for coalition, _ in constraints}
    return uncross(game, phi, richer, initial)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "status": "quantitative uncrossing-defect budget verified",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "five_player_crossing_pair": five_player_case(),
        "seven_player_three_column": three_column_case(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
