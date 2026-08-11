#!/usr/bin/env python3
"""Exact controls for the spectral/top-selection/label-currency decomposition.

For the actual Lmax top block H, write B_H for the spectral expression with
that block fixed and the remaining spectra oppositely paired.  If B_* is the
minimum over every top block allowed by the sharpened over-cover anchor, then

    O = B_* + (B_H-B_*) + (O-B_H).

The last term is label currency.  The script independently recomputes it as
the threshold integral of the excess intersection of the residual upper
contour sets over their Frechet lower bound.  This identity is a human
layer-cake/rearrangement theorem; the named cases are exact controls only.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_effective_bipartition import characteristic_function  # noqa: E402
from audit_lmax_overcover import top_certificate  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_n7_effective_bipartition_counterexample import (  # noqa: E402
    G as CEB_G,
    H as CEB_H,
    VALUES as CEB_VALUES,
    X as CEB_X,
    Z as CEB_Z,
)


def opposite_residual(x, z, removed):
    remaining_x = sorted(x[i] for i in range(len(x)) if i not in removed)
    remaining_z = sorted((z[i] for i in range(len(z)) if i not in removed), reverse=True)
    return sum((min(a, b) for a, b in zip(remaining_x, remaining_z)), F(0))


def threshold_currency(x, z, residual):
    levels = sorted({F(0)} | {x[i] for i in residual} | {z[i] for i in residual})
    total = F(0)
    layers = []
    m = len(residual)
    for low, high in zip(levels, levels[1:]):
        if high == low:
            continue
        upper_x = {i for i in residual if x[i] >= high}
        upper_z = {i for i in residual if z[i] >= high}
        double_high = upper_x.intersection(upper_z)
        double_low = set(residual).difference(upper_x.union(upper_z))
        frechet = max(0, len(upper_x) + len(upper_z) - m)
        excess = len(double_high) - frechet
        if excess < 0:
            raise AssertionError("Frechet lower bound failed")
        if excess != min(len(double_high), len(double_low)):
            raise AssertionError("high-high/low-low capacity identity failed")
        contribution = (high - low) * excess
        total += contribution
        if contribution:
            layers.append(
                {
                    "low": str(low),
                    "high": str(high),
                    "upper_x": sorted(upper_x),
                    "upper_z": sorted(upper_z),
                    "double_high": sorted(double_high),
                    "double_low": sorted(double_low),
                    "frechet": frechet,
                    "excess_intersection": excess,
                    "threshold_capacity": min(len(double_high), len(double_low)),
                    "contribution": str(contribution),
                }
            )
    return total, layers


def spectral_decomposition(name, values, x, z):
    n = len(x)
    total = sum(x, F(0))
    if total != sum(z, F(0)) or total <= 0:
        raise AssertionError("invalid common total")
    certificate = top_certificate(values, z)
    alpha = certificate["alpha"]
    theta = certificate["theta"]
    minimum = min(x)
    maximum = max(z)
    actual_top = tuple(i for i, value in enumerate(z) if value == maximum)
    lower_z = sorted((value for value in z if value < maximum), reverse=True)
    surplus = sum((alpha[i] * x[i] for i in range(n)), F(0)) - maximum
    required = (maximum + surplus - minimum) / theta

    candidates = []
    for chosen in itertools.combinations(range(n), len(actual_top)):
        if sum((x[i] - minimum for i in chosen), F(0)) < required:
            continue
        residual_x = sorted(x[i] for i in range(n) if i not in chosen)
        bound = sum((min(x[i], maximum) for i in chosen), F(0))
        bound += sum((min(a, b) for a, b in zip(residual_x, lower_z)), F(0))
        candidates.append((bound, chosen))
    if not candidates:
        raise AssertionError("actual top block must satisfy the sharpened anchor")
    spectral, minimizing_top = min(candidates)

    actual_top_bound = sum((min(x[i], maximum) for i in actual_top), F(0))
    actual_top_bound += opposite_residual(x, z, set(actual_top))
    overlap = sum((min(x[i], z[i]) for i in range(n)), F(0))
    top_currency = actual_top_bound - spectral
    label_currency = overlap - actual_top_bound
    threshold, layers = threshold_currency(
        x, z, tuple(i for i in range(n) if i not in actual_top)
    )
    if top_currency < 0 or label_currency < 0 or threshold != label_currency:
        raise AssertionError("currency decomposition failed")
    if overlap != spectral + top_currency + label_currency:
        raise AssertionError("currency sum does not recover overlap")

    target = F(n, (n * n) // 4) * total
    return {
        "name": name,
        "n": n,
        "theta": str(theta),
        "hinge_surplus": str(surplus),
        "actual_top": list(actual_top),
        "spectral_minimizing_top": list(minimizing_top),
        "sharpened_spectral_bound_ratio": str(spectral / total),
        "actual_top_bound_ratio": str(actual_top_bound / total),
        "top_selection_currency_ratio": str(top_currency / total),
        "label_currency_ratio": str(label_currency / total),
        "overlap_ratio": str(overlap / total),
        "target_ratio": str(target / total),
        "spectral_deficit_ratio": str(max(F(0), target - spectral) / total),
        "currency_identity_verified": True,
        "nonzero_threshold_layers": layers,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for case in CASES:
        g = tuple(map(F, case["g"]))
        h = tuple(map(F, case["h"]))
        rows.append(
            spectral_decomposition(
                case["name"], characteristic_function(g, h),
                tuple(case["x"]), tuple(case["z"]),
            )
        )
    rows.append(
        spectral_decomposition(
            "effective_bipartition_counterexample",
            CEB_VALUES, CEB_X, CEB_Z,
        )
    )
    report = {
        "status": "exact spectral/top-selection/label-currency controls",
        "identity": "O=B_spectral+C_top+C_label",
        "cases": rows,
        "scope": (
            "the layer-cake currency identity is a human theorem; these eight named "
            "pairs are exact structural controls, not proof of the all-n disjunction"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
