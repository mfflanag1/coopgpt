"""Exact audit for the defect-to-uncertainty stability theorem.

The computation checks the sharp five-state obstruction and an inert positive
binding-defect example.  It is a bug audit, not a proof of the theorem.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from leximin import leximax_core_exact, leximin_core_exact
from tugame import Game
from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    lower_envelope,
)


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def envelope(points):
    n = len(points[0])
    full = (1 << n) - 1
    values = [F(0)] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(payoff(point, coalition) for point in points)
    values[full] = F(sum(points[0]))
    return values


def lower_curve(point):
    total = F(0)
    curve = []
    for value in sorted(point):
        total += value
        curve.append(total)
    return tuple(curve)


def upper_curve(point):
    total = F(0)
    curve = [F(0)]
    for value in sorted(point, reverse=True):
        total += value
        curve.append(total)
    return tuple(curve)


def richer_suffixes(point):
    order = sorted(range(len(point)), key=lambda i: (-point[i], i))
    result = []
    for size in range(1, len(point)):
        if point[order[size - 1]] > point[order[size]]:
            coalition = sum(1 << player for player in order[:size])
            result.append((size, coalition))
    return result


def steepen_sorted(point, mass):
    result = list(sorted(point))
    remaining = mass
    for i in range(len(result) - 1):
        removed = min(result[i], remaining)
        result[i] -= removed
        remaining -= removed
        if remaining == 0:
            break
    if remaining:
        raise AssertionError("insufficient lower-tail mass to steepen")
    result[-1] += mass
    if result != sorted(result):
        raise AssertionError("steepening destroyed sorted order")
    return tuple(result)


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def audit_rational_grid(max_n, total):
    pairs_checked = 0
    for n in range(2, max_n + 1):
        points = [tuple(F(value, total) for value in point)
                  for point in compositions(total, n)]
        for phi, point in itertools.product(points, repeat=2):
            suffixes = richer_suffixes(phi)
            epsilon = max(
                (max(F(0), payoff(phi, coalition) - payoff(point, coalition))
                 for _, coalition in suffixes),
                default=F(0),
            )
            regrets = [b - a for a, b in zip(lower_curve(phi), lower_curve(point))]
            if max(regrets[:-1], default=F(0)) > epsilon:
                raise AssertionError("rational-grid Lorenz regret bound failed")
            phi_upper = upper_curve(phi)
            point_upper = upper_curve(point)
            eta = max(F(0), *(a - b for a, b in zip(phi_upper, point_upper)))
            if eta > epsilon:
                raise AssertionError("rational-grid majorization radius bound failed")
            steepened = steepen_sorted(point, eta)
            if any(a < b for a, b in zip(lower_curve(phi), lower_curve(steepened))):
                raise AssertionError("rational-grid steepening failed")
            if sum(abs(a - b) for a, b in zip(sorted(point), steepened)) != 2 * eta:
                raise AssertionError("rational-grid L1 distance identity failed")
            pairs_checked += 1
    return pairs_checked


def audit_sharp_obstruction():
    game = Game(5, lower_envelope(BASE_GENERATORS))
    phi = tuple(leximin_core_exact(game))
    psi = tuple(leximax_core_exact(game))
    total = F(sum(phi))
    suffix_data = []
    for size, coalition in richer_suffixes(phi):
        slack = payoff(phi, coalition) - game.v[coalition]
        suffix_data.append(
            {
                "richest_coordinates": size,
                "coalition": [
                    i + 1 for i in range(5) if coalition >> i & 1
                ],
                "normalized_slack": str(slack / total),
            }
        )
    epsilon = max(
        payoff(phi, coalition) - game.v[coalition]
        for _, coalition in richer_suffixes(phi)
    ) / total
    normalized_phi = tuple(value / total for value in phi)
    normalized_psi = tuple(value / total for value in psi)
    phi_lower = lower_curve(normalized_phi)
    psi_lower = lower_curve(normalized_psi)
    regrets = tuple(b - a for a, b in zip(phi_lower, psi_lower))
    if max(regrets) != epsilon or regrets[2] != epsilon:
        raise AssertionError("sharp Lorenz-coordinate regret is no longer tight")
    phi_upper = upper_curve(normalized_phi)
    psi_upper = upper_curve(normalized_psi)
    eta = max(F(0), *(a - b for a, b in zip(phi_upper, psi_upper)))
    if eta != epsilon:
        raise AssertionError("approximate-majorization distance changed")
    steepened = steepen_sorted(normalized_psi, eta)
    if any(a < b for a, b in zip(lower_curve(normalized_phi), lower_curve(steepened))):
        raise AssertionError("inc-max does not Lorenz-dominate steepened point")
    l1_distance = sum(abs(a - b) for a, b in zip(sorted(normalized_psi), steepened))
    if l1_distance != 2 * epsilon:
        raise AssertionError("sharp L1 approximate-majorization radius changed")
    return {
        "normalized_incmax": [str(value) for value in normalized_phi],
        "normalized_decmin": [str(value) for value in normalized_psi],
        "strict_richer_suffixes": suffix_data,
        "epsilon": str(epsilon),
        "incmax_lower_lorenz_curve": [str(value) for value in phi_lower],
        "decmin_lower_lorenz_curve": [str(value) for value in psi_lower],
        "decmin_coordinate_regrets": [str(value) for value in regrets],
        "maximum_regret_equals_epsilon": True,
        "steepened_decmin": [str(value) for value in steepened],
        "l1_distance_to_dominated_point": str(l1_distance),
        "distance_equals_two_epsilon": True,
    }


def audit_inert_binding_defect():
    points = (
        (F(1, 10), F(1, 10), F(2, 5), F(2, 5), F(0)),
        (F(3, 10), F(3, 10), F(0), F(0), F(2, 5)),
        (F(0), F(2, 5), F(1, 5), F(1, 5), F(1, 5)),
        (F(2, 5), F(0), F(1, 5), F(1, 5), F(1, 5)),
    )
    values = envelope(points)
    game = Game(5, values)
    phi = tuple(leximin_core_exact(game))
    decmin = tuple(leximax_core_exact(game))
    expected = (F(1, 5),) * 5
    if phi != expected or decmin != expected:
        raise AssertionError("inert-defect example lost its universal selector")
    if any(values[1 << i] for i in range(5)):
        raise AssertionError("inert-defect example is not atom-vacuous")
    left = 0b00111
    right = 0b01011
    if payoff(phi, left) != values[left] or payoff(phi, right) != values[right]:
        raise AssertionError("displayed broken-diamond events are not binding")
    defect = values[left] + values[right] - values[left & right] - values[left | right]
    if defect != F(2, 5):
        raise AssertionError("inert binding defect changed")
    if richer_suffixes(phi):
        raise AssertionError("uniform selector unexpectedly has a strict boundary")
    return {
        "generators": [[str(value) for value in point] for point in points],
        "universal_selector": [str(value) for value in phi],
        "binding_pair": [[1, 2, 3], [1, 2, 4]],
        "intersection": [1, 2],
        "union": [1, 2, 3, 4],
        "positive_binding_defect": str(defect),
        "strict_payoff_boundaries": 0,
        "suffix_slack_epsilon": "0",
        "lesson": "raw positive binding defects need not create uncertainty regret",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-n", type=int, default=5)
    parser.add_argument("--grid-total", type=int, default=6)
    args = parser.parse_args()
    payload = {
        "status": "credal defect-to-uncertainty stability audited",
        "finite_audit_is_not_proof": True,
        "rational_grid_pairs_checked": audit_rational_grid(
            args.max_n, args.grid_total
        ),
        "rational_grid_maximum_n": args.max_n,
        "rational_grid_common_denominator": args.grid_total,
        "sharp_five_state_obstruction": audit_sharp_obstruction(),
        "inert_positive_binding_defect": audit_inert_binding_defect(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
