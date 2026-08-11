#!/usr/bin/env python3
"""Exact n=7 control exposing neutral endpoints in label rectangles.

The two-generator lower-envelope game has an exactly recomputed Lmin/Lmax
pair for which the old opposite-sign carrier family is empty even though
label currency is positive.  Neutral endpoints repair the omission, and the
canonical sorted high--low rectangles recover label currency exactly.  This
is not a counterexample to the hybrid-overlap conjecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import coalition_sum, top_certificate  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from verify_labelled_branch_duals import verify_complete_selection  # noqa: E402


N = 7
FULL = (1 << N) - 1
G = tuple(F(q, 178) for q in (90, 87, 0, 0, 1, 0, 0))
H = tuple(F(q, 107) for q in (0, 0, 46, 54, 0, 5, 2))
X = tuple(F(q, 38092) for q in (8901, 8295, 8295, 10323, 214, 1566, 498))
Z = tuple(F(q, 38092) for q in (9612, 9006, 7584, 9612, 214, 1566, 498))
VALUES = tuple(
    min(coalition_sum(G, coalition), coalition_sum(H, coalition))
    for coalition in range(1 << N)
)


# (stage, player, coalition multipliers, old-pin coefficients,
#  other-current-block coefficients, constant).  Lmax old coefficients are
# stored with their actual negative sign.
LMIN_CERTIFICATES = (
    (0, 4, ((111, F(1)),), (), (), F(1)),
    (1, 6, ((9, F(1)), (38, F(1))), ((4, F(1)),), (), F(1)),
    (2, 5, ((9, F(1)), (70, F(1))), ((4, F(1)),), (), F(1)),
    (
        3, 1, ((9, F(1)),),
        ((4, F(1)), (6, F(1)), (5, F(1))), ((2, F(1)),), F(1),
    ),
    (
        3, 2, ((9, F(1)),),
        ((4, F(1)), (6, F(1)), (5, F(1))), ((1, F(1)),), F(1),
    ),
    (
        4, 0, ((10, F(1)),),
        ((4, F(1)), (6, F(1)), (5, F(1)), (2, F(1))), (), F(1),
    ),
    (
        5, 3, ((38, F(1)),),
        ((4, F(1)), (6, F(1)), (0, F(1))), (), F(1),
    ),
)

LMAX_CERTIFICATES = (
    (0, 0, ((9, F(1)),), (), ((3, F(1)),), F(0)),
    (0, 3, ((9, F(1)),), (), ((0, F(1)),), F(0)),
    (1, 1, ((10, F(1)),), ((3, F(-1)),), (), F(0)),
    (
        2, 2,
        ((9, F(1)), (26, F(1)), (38, F(1)), (70, F(1))),
        ((3, F(-1)), (1, F(-2))), (), F(1),
    ),
    (3, 5, ((38, F(1)),), ((1, F(-1)), (2, F(-1))), (), F(0)),
    (4, 6, ((70, F(1)),), ((1, F(-1)), (2, F(-1))), (), F(0)),
    (5, 4, ((26, F(1)),), ((3, F(-1)), (1, F(-1))), (), F(0)),
)


def tight_support(point):
    return tuple(
        coalition
        for coalition in range(1, FULL)
        if coalition_sum(point, coalition) == VALUES[coalition]
    )


def audit_staged_identity(point, mode, entry):
    stage, player, coalitions, old, current, constant = entry
    blocks = payoff_blocks(point, mode)
    expected_old = {i for block in blocks[:stage] for i in block}
    expected_current = set(blocks[stage])
    if player not in expected_current:
        raise AssertionError("forced player is not in the asserted stage")
    if any(i not in expected_old for i, _ in old):
        raise AssertionError("old-pin coefficient has the wrong stage label")
    if any(i not in expected_current - {player} for i, _ in current):
        raise AssertionError("current coefficient has the wrong stage label")
    if any(weight < 0 for _coalition, weight in coalitions + current):
        raise AssertionError("negative coalition/current coefficient")
    if mode == "min" and any(weight < 0 for _i, weight in old):
        raise AssertionError("Lmin old-pin coefficient has the wrong sign")
    if mode == "max" and any(weight > 0 for _i, weight in old):
        raise AssertionError("Lmax old-pin coefficient has the wrong sign")
    if any(
        coalition_sum(point, coalition) != VALUES[coalition]
        for coalition, _ in coalitions
    ):
        raise AssertionError("certificate uses a coalition not tight at the selection")

    side = F(1 if mode == "min" else -1)
    for coordinate in range(N):
        lhs = sum(
            (weight for coalition, weight in coalitions if coalition >> coordinate & 1),
            F(0),
        )
        lhs += sum(weight for i, weight in old if i == coordinate)
        lhs += side * sum(weight for i, weight in current if i == coordinate)
        lhs += side * F(coordinate == player)
        if lhs != constant:
            raise AssertionError((mode, stage, player, coordinate, lhs, constant))


def audit_exact_game():
    if sum(G, F(0)) != 1 or sum(H, F(0)) != 1:
        raise AssertionError("generator totals changed")
    if any(VALUES[1 << player] != 0 for player in range(N)):
        raise AssertionError("singleton normalization failed")
    for generator in (G, H):
        if any(
            coalition_sum(generator, coalition) < VALUES[coalition]
            for coalition in range(1 << N)
        ):
            raise AssertionError("displayed generator is outside the core")
    for point in (X, Z):
        if sum(point, F(0)) != 1:
            raise AssertionError("selection total changed")
        if any(
            coalition_sum(point, coalition) < VALUES[coalition]
            for coalition in range(1 << N)
        ):
            raise AssertionError("selection is outside the core")


def canonical_rectangles(residual):
    high_order = sorted(residual, key=lambda i: (min(X[i], Z[i]), -i), reverse=True)
    low_order = sorted(residual, key=lambda i: (max(X[i], Z[i]), i))
    rectangles = []
    for high_player, low_player in zip(high_order, low_order):
        start = max(X[low_player], Z[low_player])
        end = min(X[high_player], Z[high_player])
        if start < end:
            rectangles.append((high_player, low_player, start, end))
    return rectangles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    audit_exact_game()
    for entry in LMIN_CERTIFICATES:
        audit_staged_identity(X, "min", entry)
    for entry in LMAX_CERTIFICATES:
        audit_staged_identity(Z, "max", entry)
    verify_complete_selection(VALUES, X, "min", tight_support(X))
    verify_complete_selection(VALUES, Z, "max", tight_support(Z))

    top = top_certificate(VALUES, Z)
    if top["theta"] != F(1, 2):
        raise AssertionError("top-certificate value changed")
    actual_top = tuple(i for i, value in enumerate(Z) if value == max(Z))
    residual = tuple(i for i in range(N) if i not in actual_top)
    if actual_top != (0, 3):
        raise AssertionError("actual top block changed")

    overlap = sum((min(X[i], Z[i]) for i in range(N)), F(0))
    target = F(7, 12)
    maximum = max(Z)
    residual_x = sorted(X[i] for i in residual)
    residual_z = sorted((Z[i] for i in residual), reverse=True)
    actual_top_bound = sum((min(X[i], maximum) for i in actual_top), F(0))
    actual_top_bound += sum(
        (min(left, right) for left, right in zip(residual_x, residual_z)), F(0)
    )
    label_currency = overlap - actual_top_bound
    if (
        overlap != F(18335, 19046)
        or actual_top_bound != F(21503, 38092)
        or label_currency != F(15167, 38092)
    ):
        raise AssertionError("overlap decomposition changed")

    gainers = tuple(i for i in residual if Z[i] > X[i])
    losers = tuple(i for i in residual if X[i] > Z[i])
    sign_intervals = []
    for i in gainers:
        for j in losers:
            if X[j] < X[i]:
                sign_intervals.append(("min", i, j, X[j], X[i]))
            if Z[i] < Z[j]:
                sign_intervals.append(("max", i, j, Z[i], Z[j]))
    if gainers != (1,) or losers != (2,) or sign_intervals:
        raise AssertionError("opposite-sign obstruction changed")

    rectangles = canonical_rectangles(residual)
    rectangle_value = sum((end - start for _, _, start, end in rectangles), F(0))
    if rectangle_value != label_currency:
        raise AssertionError("canonical rectangles miss label currency")

    levels = sorted({F(0)} | {X[i] for i in residual} | {Z[i] for i in residual})
    layer_audit = []
    for low, high in zip(levels, levels[1:]):
        high_high = sum(F(min(X[i], Z[i]) >= high) for i in residual)
        low_low = sum(F(max(X[i], Z[i]) <= low) for i in residual)
        capacity = min(high_high, low_low)
        occupancy = sum(
            F(start <= low and high <= end)
            for _, _, start, end in rectangles
        )
        if occupancy != capacity:
            raise AssertionError("canonical occupancy/capacity mismatch")
        if capacity:
            layer_audit.append(
                {
                    "interval": [str(low), str(high)],
                    "capacity": str(capacity),
                    "canonical_occupancy": str(occupancy),
                }
            )

    report = {
        "status": "exact rational neutral-endpoint rectangle control",
        "scope": (
            "refutes only the opposite-sign carrier restriction; it does not "
            "refute the hybrid-overlap conjecture"
        ),
        "game": {
            "n": N,
            "generators": [[str(value) for value in generator] for generator in (G, H)],
            "singleton_normalized": True,
            "exact_from_lower_envelope_definition": True,
        },
        "selections": {
            "lmin": [str(value) for value in X],
            "lmax": [str(value) for value in Z],
            "lmin_blocks": [list(block) for block in payoff_blocks(X, "min")],
            "lmax_blocks": [list(block) for block in payoff_blocks(Z, "max")],
            "tight_support": list(tight_support(X)),
            "solver_free_staged_identities": 14,
            "independent_generic_exact_staged_checks": 14,
        },
        "top_certificate": {
            "theta": str(top["theta"]),
            "alpha": [str(value) for value in top["alpha"]],
            "actual_top": list(actual_top),
        },
        "currency": {
            "overlap": str(overlap),
            "actual_top_spectral_bound": str(actual_top_bound),
            "label_currency": str(label_currency),
            "target": str(target),
            "main_target_margin": str(overlap - target),
        },
        "old_opposite_sign_family": {
            "gainers": list(gainers),
            "losers": list(losers),
            "strict_intervals": [],
            "packing_value": "0",
        },
        "canonical_rectangles": [
            {
                "high_player": i,
                "low_player": j,
                "interval": [str(start), str(end)],
                "weight": "1",
                "length": str(end - start),
            }
            for i, j, start, end in rectangles
        ],
        "canonical_rectangle_value": str(rectangle_value),
        "canonical_value_equals_label_currency": True,
        "nonzero_layers": layer_audit,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
