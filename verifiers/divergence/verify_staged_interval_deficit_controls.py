#!/usr/bin/env python3
"""Exact staged-availability controls for canonical label rectangles.

For each hostile named pair whose spectral/top terms leave a deficit, this
verifier forms every clipped high--low rectangle ``(b_j,a_i]``, where
``a_i=min(x_i,z_i)`` and
``b_j=max(x_j,z_j)``.  It independently finds an exact normalized Lmin
relation with positive auxiliary coefficient on ``j`` and solves the full
rectangle packing and threshold-cover dual.  The optimum must equal label
currency exactly, as proved by the human canonical rank-pairing theorem.

The checks are finite controls of the staged identities and arithmetic.  The
universal saturation statement is the human sorting proof, and saturation is
an identity rather than evidence for the unresolved hybrid-overlap bound.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from audit_effective_bipartition import characteristic_function  # noqa: E402
from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def normalized_relation(values, point, mode, player, required_aux=None):
    """Return one exact normalized relation, optionally with a_j >= 1."""
    n = len(point)
    full = (1 << n) - 1
    blocks = payoff_blocks(point, mode)
    stage = next(k for k, block in enumerate(blocks) if player in block)
    cumulative = tuple(j for block in blocks[: stage + 1] for j in block)
    if required_aux is not None and required_aux not in cumulative:
        return None
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(point, coalition) == values[coalition]
    )
    m = len(tight)
    auxiliary_index = {j: m + k for k, j in enumerate(cumulative)}
    c_index = m + len(cumulative)
    width = c_index + 1
    side = F(1 if mode == "min" else -1)
    rhs_side = F(-1 if mode == "min" else 1)

    aeq = []
    beq = []
    for coordinate in range(n):
        row = [F(0)] * width
        for k, coalition in enumerate(tight):
            if coalition >> coordinate & 1:
                row[k] = F(1)
        if coordinate in auxiliary_index:
            row[auxiliary_index[coordinate]] = side
        row[c_index] = F(-1)
        aeq.append(row)
        beq.append(rhs_side * F(int(coordinate == player)))

    aub = []
    bub = []
    for index in (*range(m), *auxiliary_index.values()):
        row = [F(0)] * width
        row[index] = F(-1)
        aub.append(row)
        bub.append(F(0))
    if required_aux is not None:
        row = [F(0)] * width
        row[auxiliary_index[required_aux]] = F(-1)
        aub.append(row)
        bub.append(F(-1))

    status, _objective, solution = exact_linprog(
        [F(0)] * width, aub, bub, aeq, beq
    )
    if status != "optimal":
        return None
    return {
        "mode": mode,
        "player": player,
        "stage": stage,
        "cumulative": cumulative,
        "tight": tight,
        "auxiliary": {
            j: solution[index] for j, index in auxiliary_index.items()
        },
        "coalition_support": {
            coalition: solution[k]
            for k, coalition in enumerate(tight)
            if solution[k]
        },
        "auxiliary_support": {
            j: solution[index]
            for j, index in auxiliary_index.items()
            if solution[index]
        },
        "constant": solution[c_index],
    }


def available_carriers(values, x, z, actual_top):
    residual = tuple(i for i in range(len(x)) if i not in actual_top)
    edges = []
    for high_player in residual:
        end = min(x[high_player], z[high_player])
        for low_player in residual:
            start = max(x[low_player], z[low_player])
            if start >= end:
                continue
            relation = normalized_relation(
                values, x, "min", high_player, required_aux=low_player
            )
            if relation is None:
                raise AssertionError(
                    {
                        "error": "complete strict Lmin support failed",
                        "high_player": high_player,
                        "low_player": low_player,
                    }
                )
            edges.append(
                {
                    "mode": "min",
                    "high_player": high_player,
                    "low_player": low_player,
                    "start": start,
                    "end": end,
                    "availability_witness": relation,
                }
            )
    return residual, edges


def exact_complete_carrier_packing(x, z, residual, edges):
    levels = sorted({F(0)} | {x[i] for i in residual} | {z[i] for i in residual})
    layers = tuple(zip(levels, levels[1:]))
    capacities = []
    for _low, high in layers:
        upper_x = {i for i in residual if x[i] >= high}
        upper_z = {i for i in residual if z[i] >= high}
        capacities.append(
            F(
                min(
                    len(upper_x & upper_z),
                    len(set(residual) - (upper_x | upper_z)),
                )
            )
        )
    if not edges:
        return F(0), [], [F(0)] * len(layers)

    incidence = [
        [F(int(edge["start"] <= low and high <= edge["end"])) for low, high in layers]
        for edge in edges
    ]
    lengths = [edge["end"] - edge["start"] for edge in edges]
    width = len(edges)
    aub = [
        [incidence[e][layer] for e in range(width)]
        for layer in range(len(layers))
    ]
    bub = capacities[:]
    for e in range(width):
        row = [F(0)] * width
        row[e] = F(-1)
        aub.append(row)
        bub.append(F(0))
    status, negative_optimum, weights = exact_linprog(
        [-length for length in lengths], aub, bub
    )
    if status != "optimal":
        raise AssertionError(f"complete carrier packing is {status}")
    optimum = -negative_optimum

    layer_count = len(layers)
    dual_aub = []
    dual_bub = []
    for e in range(width):
        dual_aub.append([-entry for entry in incidence[e]])
        dual_bub.append(-lengths[e])
    for layer in range(layer_count):
        row = [F(0)] * layer_count
        row[layer] = F(-1)
        dual_aub.append(row)
        dual_bub.append(F(0))
    dual_status, dual_optimum, prices = exact_linprog(
        capacities, dual_aub, dual_bub
    )
    if dual_status != "optimal" or dual_optimum != optimum:
        raise AssertionError("complete carrier packing/cover mismatch")
    return optimum, weights, prices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for case in CASES:
        g = tuple(map(F, case["g"]))
        h = tuple(map(F, case["h"]))
        values = characteristic_function(g, h)
        x = tuple(case["x"])
        z = tuple(case["z"])
        decomposition = spectral_decomposition(case["name"], values, x, z)
        total = sum(x, F(0))
        deficit = F(decomposition["post_top_deficit_ratio"]) * total
        if deficit == 0:
            rows.append(
                {
                    "name": case["name"],
                    "status": "not needed: spectral plus top contribution meets target",
                    "deficit": "0",
                }
            )
            continue
        actual_top = set(decomposition["actual_top"])
        residual, edges = available_carriers(values, x, z, actual_top)
        support_optimum, support_weights, cover_prices = exact_complete_carrier_packing(
            x, z, residual, edges
        )
        label_currency = F(decomposition["label_currency_ratio"]) * total
        if support_optimum != label_currency:
            raise AssertionError(
                {
                    "name": case["name"],
                    "support_optimum": str(support_optimum),
                    "label_currency": str(label_currency),
                }
            )
        edge_output = []
        for edge, weight in zip(edges, support_weights):
            edge_output.append(
                {
                    "mode": edge["mode"],
                    "high_player": edge["high_player"],
                    "low_player": edge["low_player"],
                    "interval": [str(edge["start"]), str(edge["end"])],
                    "packing_weight": str(weight),
                    "availability_witness": {
                        "stage": edge["availability_witness"]["stage"],
                        "coalition_support": {
                            str(coalition): str(value)
                            for coalition, value in edge["availability_witness"][
                                "coalition_support"
                            ].items()
                        },
                        "auxiliary_support": {
                            str(player): str(value)
                            for player, value in edge["availability_witness"][
                                "auxiliary_support"
                            ].items()
                        },
                        "constant": str(
                            edge["availability_witness"]["constant"]
                        ),
                    },
                }
            )
        rows.append(
            {
                "name": case["name"],
                "target_deficit": str(deficit),
                "label_currency": str(label_currency),
                "complete_clipped_rectangles": edge_output,
                "all_high_low_rectangles_lmin_available": True,
                "complete_rectangle_packing_optimum": str(support_optimum),
                "complete_rectangle_cover_prices": [
                    str(price) for price in cover_prices
                ],
                "complete_rectangle_optimum_equals_label_currency": True,
            }
        )

    report = {
        "status": "exact rational canonical-rectangle saturation controls",
        "scope": (
            "finite hostile controls only; the universal saturation theorem is the "
            "human rank-pairing proof, and it is an identity rather than a proof of H"
        ),
        "human_theorem_audited": (
            "normalized auxiliary coefficients are either unavailable or "
            "unbounded, and every strict order-compatible edge is available, so "
            "every clipped high-low rectangle is Lmin-available; canonical rank "
            "pairing saturates label currency"
        ),
        "cases": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
