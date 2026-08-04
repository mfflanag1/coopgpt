"""Exact audit for the Lmin local-supermodularity uncrossing theorem."""
from __future__ import annotations

import argparse
import itertools
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


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def energy(n, coalition):
    size = coalition.bit_count()
    return size * (n - size)


def envelope(points):
    n = len(points[0])
    full = (1 << n) - 1
    values = [F(0)] * (1 << n)
    for coalition in range(1, full):
        values[coalition] = min(payoff(point, coalition) for point in points)
    values[full] = F(sum(points[0]))
    return values


def is_supermodular(values, left, right):
    return (
        values[left] + values[right]
        <= values[left & right] + values[left | right]
    )


def audit_energy(max_n=9):
    crossing_pairs = 0
    for n in range(2, max_n + 1):
        full = (1 << n) - 1
        for left in range(1, full):
            for right in range(left + 1, full):
                only_left = left & ~right
                only_right = right & ~left
                if not (left & right and only_left and only_right):
                    continue
                crossing_pairs += 1
                before = energy(n, left) + energy(n, right)
                after = energy(n, left & right) + energy(n, left | right)
                expected = 2 * only_left.bit_count() * only_right.bit_count()
                if before - after != expected or expected <= 0:
                    raise AssertionError("uncrossing energy identity failed")
                for player in range(n):
                    lhs = int(left >> player & 1) + int(right >> player & 1)
                    rhs = int((left & right) >> player & 1) + int(
                        (left | right) >> player & 1
                    )
                    if lhs != rhs:
                        raise AssertionError("uncrossing changed incidence load")
    return crossing_pairs


def audit_five_player_defect():
    game = Game(5, lower_envelope(BASE_GENERATORS))
    phi = tuple(leximin_core_exact(game))
    if phi != PHI_BASE:
        raise AssertionError("five-player Lmin changed")
    left = (1 << 0) | (1 << 2) | (1 << 4)
    right = (1 << 2) | (1 << 3) | (1 << 4)
    intersection = left & right
    union = left | right
    slacks = {
        coalition: payoff(phi, coalition) - game.v[coalition]
        for coalition in (left, right, intersection, union)
    }
    defect = (
        game.v[left] + game.v[right]
        - game.v[intersection] - game.v[union]
    )
    if slacks[left] or slacks[right]:
        raise AssertionError("protector pair is not tight")
    if slacks[intersection] != 1 or slacks[union] != 1 or defect != 2:
        raise AssertionError("unexpected sharp uncrossing defect")
    if defect != slacks[intersection] + slacks[union]:
        raise AssertionError("defect is not the sum of derived-set slacks")
    return {
        "lmin": [str(x) for x in phi],
        "tight_pair": [[1, 3, 5], [3, 4, 5]],
        "intersection": [3, 5],
        "union": [1, 3, 4, 5],
        "intersection_slack": "1",
        "union_slack": "1",
        "strict_supermodularity_defect": "2",
        "support_columns": 2,
        "support_incidence_is_balanced": True,
        "support_incidence_is_totally_balanced": True,
        "reason": "a forbidden cycle submatrix requires at least three columns",
    }


def audit_nonconvex_positive_domain():
    points = (
        (0, 4, 6, 5, 0),
        (5, 0, 2, 7, 1),
        (3, 0, 0, 11, 1),
        (2, 2, 6, 0, 5),
    )
    values = envelope(points)
    game = Game(5, values)
    phi = tuple(leximin_core_exact(game))
    expected = (F(5, 2), F(5, 2), F(10, 3), F(10, 3), F(10, 3))
    if phi != expected:
        raise AssertionError("nonconvex domain example has unexpected Lmin")
    full = (1 << 5) - 1
    tight = [
        coalition for coalition in range(1, full)
        if payoff(phi, coalition) == values[coalition]
    ]
    if tight != [28]:
        raise AssertionError(f"unexpected proper tight family: {tight}")
    if any(
        not is_supermodular(values, left, right)
        for left, right in itertools.combinations(tight, 2)
    ):
        raise AssertionError("local supermodularity failed")
    violations = [
        (left, right, values[left] + values[right]
         - values[left & right] - values[left | right])
        for left in range(full + 1)
        for right in range(left + 1, full + 1)
        if not is_supermodular(values, left, right)
    ]
    if not violations:
        raise AssertionError("example is unexpectedly convex")
    if payoff(phi, 28) != values[28]:
        raise AssertionError("richer suffix is not tight")
    for coalition in range(1, full + 1):
        if not any(payoff(point, coalition) == values[coalition] for point in points):
            raise AssertionError("lower-envelope game is not exactly attained")
    return {
        "generators": [list(point) for point in points],
        "lmin": [str(x) for x in phi],
        "proper_lmin_tight_coalitions": [[3, 4, 5]],
        "richer_suffix_tight": True,
        "exact_by_attained_lower_envelope": True,
        "globally_convex": False,
        "global_supermodularity_violations": len(violations),
        "maximum_global_defect": str(max(item[2] for item in violations)),
        "lmin_locally_supermodular": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-n", type=int, default=9)
    args = parser.parse_args()
    payload = {
        "status": "Lmin uncrossing theorem audited",
        "finite_audit_is_not_proof": True,
        "crossing_pairs_checked": audit_energy(args.max_n),
        "maximum_n_for_energy_audit": args.max_n,
        "sharp_five_player_obstruction": audit_five_player_defect(),
        "nonconvex_positive_domain_example": audit_nonconvex_positive_domain(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
