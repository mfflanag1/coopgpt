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

The script also checks the canonical saturation theorem.  For residual player
``i`` put ``a_i=min(x_i,z_i)`` and ``b_i=max(x_i,z_i)``.  Sorting the ``a``
values down and the ``b`` values up and pairing equal ranks gives the clipped
rectangles ``(b_[k],a_[k]]``.  Their unit occupancy is exactly
``min(|A_t|,|D_t|)`` at every threshold, so they recover all label currency.
The exact packing/cover LP is retained as an independent finite audit of the
named controls, together with its rooted-potential certificate.
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
from exactlp import exact_linprog  # noqa: E402
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
    sign_compatible_total = F(0)
    layers = []
    m = len(residual)
    for low, high in zip(levels, levels[1:]):
        if high == low:
            continue
        upper_x = {i for i in residual if x[i] >= high}
        upper_z = {i for i in residual if z[i] >= high}
        double_high = upper_x.intersection(upper_z)
        double_low = set(residual).difference(upper_x.union(upper_z))
        gainers = {i for i in residual if z[i] > x[i]}
        losers = {i for i in residual if x[i] > z[i]}
        frechet = max(0, len(upper_x) + len(upper_z) - m)
        excess = len(double_high) - frechet
        if excess < 0:
            raise AssertionError("Frechet lower bound failed")
        if excess != min(len(double_high), len(double_low)):
            raise AssertionError("high-high/low-low capacity identity failed")
        contribution = (high - low) * excess
        sign_compatible_capacity = (
            min(len(double_high & gainers), len(double_low & losers))
            + min(len(double_high & losers), len(double_low & gainers))
        )
        sign_compatible_contribution = (
            (high - low) * sign_compatible_capacity
        )
        total += contribution
        sign_compatible_total += sign_compatible_contribution
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
                    "sign_compatible_capacity": sign_compatible_capacity,
                    "contribution": str(contribution),
                    "sign_compatible_contribution": str(
                        sign_compatible_contribution
                    ),
                }
            )
    return total, sign_compatible_total, layers


def complete_carrier_interval_packing(x, z, residual):
    """Audit all high--low rectangles and the canonical rank pairing."""
    levels = sorted({F(0)} | {x[i] for i in residual} | {z[i] for i in residual})
    layers = tuple((low, high) for low, high in zip(levels, levels[1:]) if low < high)
    capacities = []
    for _low, high in layers:
        upper_x = {i for i in residual if x[i] >= high}
        upper_z = {i for i in residual if z[i] >= high}
        double_high = upper_x & upper_z
        double_low = set(residual) - (upper_x | upper_z)
        capacities.append(F(min(len(double_high), len(double_low))))

    intervals = []
    for high_player in residual:
        ceiling = min(x[high_player], z[high_player])
        for low_player in residual:
            floor = max(x[low_player], z[low_player])
            if floor < ceiling:
                intervals.append(
                    ("clipped", high_player, low_player, floor, ceiling)
                )

    high_order = sorted(residual, key=lambda i: (min(x[i], z[i]), -i), reverse=True)
    low_order = sorted(residual, key=lambda i: (max(x[i], z[i]), i))
    canonical = []
    for high_player, low_player in zip(high_order, low_order):
        floor = max(x[low_player], z[low_player])
        ceiling = min(x[high_player], z[high_player])
        if floor < ceiling:
            canonical.append(
                ("canonical", high_player, low_player, floor, ceiling)
            )

    if not intervals:
        prices = [F(0)] * len(layers)
        weights = []
        optimum = F(0)
    else:
        incidence = []
        lengths = []
        for _kind, _i, _j, start, end in intervals:
            column = [F(int(start <= low and high <= end)) for low, high in layers]
            if sum(column, F(0)) == 0:
                raise AssertionError("nonempty carrier interval has no threshold layer")
            incidence.append(column)
            lengths.append(end - start)
            if lengths[-1] != sum(
                (high - low) * column[k] for k, (low, high) in enumerate(layers)
            ):
                raise AssertionError("carrier length/incidence mismatch")

        width = len(intervals)
        primal_rows = [
            [incidence[e][layer] for e in range(width)]
            for layer in range(len(layers))
        ]
        primal_rhs = capacities[:]
        for e in range(width):
            row = [F(0)] * width
            row[e] = F(-1)
            primal_rows.append(row)
            primal_rhs.append(F(0))
        status, negative_optimum, weights = exact_linprog(
            [-length for length in lengths], primal_rows, primal_rhs
        )
        if status != "optimal":
            raise AssertionError(f"carrier packing primal is {status}")
        optimum = -negative_optimum

        layer_count = len(layers)
        dual_rows = []
        dual_rhs = []
        for e in range(width):
            dual_rows.append([-entry for entry in incidence[e]])
            dual_rhs.append(-lengths[e])
        for layer in range(layer_count):
            row = [F(0)] * layer_count
            row[layer] = F(-1)
            dual_rows.append(row)
            dual_rhs.append(F(0))
        dual_status, dual_optimum, prices = exact_linprog(
            capacities, dual_rows, dual_rhs
        )
        if dual_status != "optimal" or dual_optimum != optimum:
            raise AssertionError("exact carrier packing primal/dual mismatch")

    support = []
    for interval, weight in zip(intervals, weights):
        if weight > 0:
            support.append(
                {
                    "kind": interval[0],
                    "high_player": interval[1],
                    "low_player": interval[2],
                    "start": str(interval[3]),
                    "end": str(interval[4]),
                    "weight": str(weight),
                }
            )
    dual_value = sum(
        (capacity * price for capacity, price in zip(capacities, prices)), F(0)
    )
    if dual_value != optimum:
        raise AssertionError("carrier cover value mismatch")

    cumulative_price = F(0)
    potential = [F(0)]
    for k, price in enumerate(prices, start=1):
        cumulative_price += price
        potential.append(cumulative_price - levels[k])
    for _kind, _i, _j, start, end in intervals:
        s = levels.index(start)
        t = levels.index(end)
        if potential[t] < potential[s]:
            raise AssertionError("shifted carrier potential is not monotone")
    full_currency = sum(
        capacity * (high - low)
        for capacity, (low, high) in zip(capacities, layers)
    )
    canonical_value = sum((end - start for _, _, _, start, end in canonical), F(0))
    canonical_occupancy = []
    for low, high in layers:
        occupancy = sum(
            F(int(start <= low and high <= end))
            for _, _, _, start, end in canonical
        )
        canonical_occupancy.append(occupancy)
    if canonical_occupancy != capacities:
        raise AssertionError("canonical rank pairing does not saturate every layer")
    if canonical_value != full_currency or optimum != full_currency:
        raise AssertionError("complete clipped rectangles do not recover label currency")
    potential_correction = sum(
        capacities[k] * (potential[k + 1] - potential[k])
        for k in range(len(layers))
    )
    if dual_value != full_currency + potential_correction:
        raise AssertionError("shifted-potential objective identity failed")

    parent = list(range(len(levels)))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left, right):
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    tight_edges = []
    for layer, price in enumerate(prices, start=1):
        if price == 0:
            union(layer - 1, layer)
            tight_edges.append({"kind": "path", "left": layer - 1, "right": layer})
    for kind, i, j, start, end in intervals:
        s = levels.index(start)
        t = levels.index(end)
        if potential[t] == potential[s]:
            union(s, t)
            tight_edges.append(
                {
                    "kind": f"carrier_{kind}",
                    "left": s,
                    "right": t,
                    "high_player": i,
                    "low_player": j,
                }
            )
    tight_graph_connected = len({find(node) for node in range(len(levels))}) == 1
    if not tight_graph_connected:
        raise AssertionError("exact cover solution lacks a tight spanning tree")

    return {
        "optimum": optimum,
        "dual_value": dual_value,
        "support": support,
        "layer_count": len(layers),
        "interval_count": len(intervals),
        "dual_prices": prices,
        "shifted_potential": potential,
        "full_currency": full_currency,
        "canonical_value": canonical_value,
        "canonical_rectangles": [
            {
                "high_player": high_player,
                "low_player": low_player,
                "start": str(start),
                "end": str(end),
                "weight": "1",
            }
            for _, high_player, low_player, start, end in canonical
        ],
        "canonical_layer_occupancy": canonical_occupancy,
        "potential_correction": potential_correction,
        "dual_tight_graph_connected": tight_graph_connected,
        "dual_tight_edges": tight_edges,
    }


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
    threshold, sign_compatible_currency, layers = threshold_currency(
        x, z, tuple(i for i in range(n) if i not in actual_top)
    )
    packing_audit = complete_carrier_interval_packing(
        x, z, tuple(i for i in range(n) if i not in actual_top)
    )
    packing = packing_audit["optimum"]
    packing_dual = packing_audit["dual_value"]
    if top_currency < 0 or label_currency < 0 or threshold != label_currency:
        raise AssertionError("currency decomposition failed")
    if overlap != spectral + top_currency + label_currency:
        raise AssertionError("currency sum does not recover overlap")
    if packing != packing_dual or packing != label_currency:
        raise AssertionError("canonical saturation audit failed")

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
        "sign_compatible_currency_ratio": str(sign_compatible_currency / total),
        "overlap_ratio": str(overlap / total),
        "target_ratio": str(target / total),
        "spectral_deficit_ratio": str(max(F(0), target - spectral) / total),
        "post_top_deficit_ratio": str(
            max(F(0), target - actual_top_bound) / total
        ),
        "sign_compatible_currency_covers_post_top_deficit": (
            sign_compatible_currency >= max(F(0), target - actual_top_bound)
        ),
        "complete_carrier_packing_ratio": str(packing / total),
        "canonical_rectangle_value_ratio": str(
            packing_audit["canonical_value"] / total
        ),
        "canonical_rectangles": packing_audit["canonical_rectangles"],
        "canonical_layer_occupancy": [
            str(value) for value in packing_audit["canonical_layer_occupancy"]
        ],
        "complete_carrier_packing_layer_count": packing_audit["layer_count"],
        "complete_carrier_packing_interval_count": packing_audit["interval_count"],
        "complete_carrier_packing_covers_post_top_deficit": (
            packing >= max(F(0), target - actual_top_bound)
        ),
        "complete_carrier_packing_support": packing_audit["support"],
        "complete_carrier_packing_dual_prices": [
            str(value) for value in packing_audit["dual_prices"]
        ],
        "complete_carrier_packing_shifted_potential": [
            str(value) for value in packing_audit["shifted_potential"]
        ],
        "complete_carrier_packing_potential_correction_ratio": str(
            packing_audit["potential_correction"] / total
        ),
        "complete_carrier_packing_dual_tight_graph_connected": (
            packing_audit["dual_tight_graph_connected"]
        ),
        "complete_carrier_packing_dual_tight_edges": packing_audit[
            "dual_tight_edges"
        ],
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
            "pairs are exact structural controls, not proof of the all-n disjunction; "
            "the canonical rank-pairing theorem proves for every pair that all "
            "label currency is recovered by clipped high--low rectangles; these "
            "named cases are exact controls of that human identity, not evidence "
            "for the unresolved hybrid-overlap inequality"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
