#!/usr/bin/env python3
"""Exact controls for PXC134 endpoint-congested threshold transport.

The conventional theorem is the layer-cake argument in the manuscript.  For
residual player ``i`` put a_i=min(x_i,z_i) and b_i=max(x_i,z_i).  Every
oriented edge i->j with b_j<a_i represents the interval (b_j,a_i].  If
nonnegative edge weights use every player with outgoing weight at most one
and incoming weight at most one, their total interval value is at most the
residual label currency O-B_H.  The two capacities are separate: a player
can be a high endpoint below a_i and a low endpoint above b_i, and these
ranges are disjoint because a_i<=b_i.  The LP computes the best fractional
bipartite matching and its source/sink-potential dual.

This is an aggregation interface, not an existence theorem saying that the
staged blockers or packet supports supply a target-reaching edge family.
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


def q(values):
    return tuple(F(value) for value in values)


def opposite_residual(x, z, residual):
    xs = sorted(x[i] for i in residual)
    zs = sorted((z[i] for i in residual), reverse=True)
    return sum((min(left, right) for left, right in zip(xs, zs)), F(0))


def spectral_terms(x, z):
    n = len(x)
    total = sum(x, F(0))
    if total != sum(z, F(0)):
        raise AssertionError("efficiency mismatch")
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    residual = tuple(i for i in range(n) if i not in top)
    bound = sum((min(x[i], maximum) for i in top), F(0))
    bound += opposite_residual(x, z, residual)
    overlap = sum((min(left, right) for left, right in zip(x, z)), F(0))
    target = F(n, (n * n) // 4) * total
    return {
        "total": total,
        "top": top,
        "residual": residual,
        "B_H": bound,
        "overlap": overlap,
        "label_currency": overlap - bound,
        "D_H": max(F(0), target - bound),
    }


def clipped_edges(x, z, residual, allowed=None):
    edges = []
    allowed_set = None if allowed is None else set(allowed)
    for high in residual:
        ceiling = min(x[high], z[high])
        for low in residual:
            if high == low:
                continue
            floor = max(x[low], z[low])
            if floor < ceiling and (
                allowed_set is None or (high, low) in allowed_set
            ):
                edges.append((high, low, floor, ceiling, ceiling - floor))
    return tuple(edges)


def fractional_endpoint_matching(x, z, residual, allowed=None):
    edges = clipped_edges(x, z, residual, allowed)
    if not edges:
        return {
            "edges": (),
            "optimum": F(0),
            "primal_support": (),
            "dual_source_prices": tuple((i, F(0)) for i in residual),
            "dual_sink_prices": tuple((i, F(0)) for i in residual),
        }

    width = len(edges)
    primal_rows = []
    primal_rhs = []
    for player in residual:
        primal_rows.append(
            [F(int(player == edge[0])) for edge in edges]
        )
        primal_rhs.append(F(1))
    for player in residual:
        primal_rows.append(
            [F(int(player == edge[1])) for edge in edges]
        )
        primal_rhs.append(F(1))
    for edge_index in range(width):
        row = [F(0)] * width
        row[edge_index] = F(-1)
        primal_rows.append(row)
        primal_rhs.append(F(0))
    status, negative_optimum, weights = exact_linprog(
        [-edge[4] for edge in edges], primal_rows, primal_rhs
    )
    if status != "optimal":
        raise AssertionError(("fractional matching", status))
    optimum = -negative_optimum

    players = tuple(residual)
    dual_width = 2 * len(players)
    dual_rows = []
    dual_rhs = []
    for high, low, _floor, _ceiling, length in edges:
        row = [F(0)] * dual_width
        row[players.index(high)] = F(-1)
        row[len(players) + players.index(low)] = F(-1)
        dual_rows.append(row)
        dual_rhs.append(-length)
    for index in range(dual_width):
        row = [F(0)] * dual_width
        row[index] = F(-1)
        dual_rows.append(row)
        dual_rhs.append(F(0))
    dual_status, dual_optimum, prices = exact_linprog(
        [F(1)] * dual_width, dual_rows, dual_rhs
    )
    if dual_status != "optimal" or dual_optimum != optimum:
        raise AssertionError(("fractional matching dual", dual_status, dual_optimum, optimum))

    primal_support = tuple(
        (edge[0], edge[1], edge[2], edge[3], weight)
        for edge, weight in zip(edges, weights)
        if weight > 0
    )
    for high, low, _floor, _ceiling, length in edges:
        if (
            prices[players.index(high)]
            + prices[len(players) + players.index(low)]
            < length
        ):
            raise AssertionError("dual edge uncovered")
    return {
        "edges": edges,
        "optimum": optimum,
        "primal_support": primal_support,
        "dual_source_prices": tuple(zip(players, prices[: len(players)])),
        "dual_sink_prices": tuple(zip(players, prices[len(players) :])),
    }


def threshold_layers(x, z, residual):
    levels = sorted({F(0)} | {x[i] for i in residual} | {z[i] for i in residual})
    layers = []
    currency = F(0)
    for low, high in zip(levels, levels[1:]):
        if low == high:
            continue
        double_high = {
            i for i in residual if min(x[i], z[i]) >= high
        }
        double_low = {
            i for i in residual if max(x[i], z[i]) <= low
        }
        capacity = min(len(double_high), len(double_low))
        contribution = F(capacity) * (high - low)
        currency += contribution
        if capacity:
            layers.append((low, high, tuple(sorted(double_high)), tuple(sorted(double_low)), capacity))
    return currency, tuple(layers)


def audit_case(name, x, z, allowed=None):
    terms = spectral_terms(x, z)
    matching = fractional_endpoint_matching(x, z, terms["residual"], allowed)
    layer_value, layers = threshold_layers(x, z, terms["residual"])
    if layer_value != terms["label_currency"]:
        raise AssertionError((name, "layer currency", layer_value, terms["label_currency"]))
    if matching["optimum"] > layer_value:
        raise AssertionError((name, "endpoint transport exceeded label currency"))
    return {
        "name": name,
        **terms,
        "allowed_edges": "all" if allowed is None else tuple(allowed),
        "transport_optimum": matching["optimum"],
        "transport_covers_D_H": matching["optimum"] >= terms["D_H"],
        "primal_support": matching["primal_support"],
        "dual_source_prices": matching["dual_source_prices"],
        "dual_sink_prices": matching["dual_sink_prices"],
        "threshold_layers": layers,
    }


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    controls = [
        audit_case(
            "PXC101_zero_demand",
            q(("9/2", "9/2", 2, 2, 2, 2)),
            q((4, 4, 3, 3, 2, 1)),
        ),
        audit_case(
            "PXC104_reciprocal_zero_demand",
            q(("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            q((6, 6, 5, 4, 1, 1)),
        ),
        audit_case(
            "PXC125_positive_demand_two_rungs",
            q(("13/2", "13/2", 1, 5, 1, 5)),
            q((6, 6, 0, "26/5", 2, "29/5")),
            ((3, 2), (5, 4)),
        ),
        audit_case(
            "PXC125_empty_graph_fail_open",
            q(("13/2", "13/2", 1, 5, 1, 5)),
            q((6, 6, 0, "26/5", 2, "29/5")),
            (),
        ),
        audit_case(
            "PXC127_common_cut",
            q(("32/5", "32/5", 1, "51/10", 1, "51/10")),
            q((6, 6, "1/5", "26/5", "9/5", "29/5")),
            ((3, 2), (3, 4), (5, 2), (5, 4)),
        ),
        audit_case(
            "PXC90_faithful_full_rank",
            q((6, 4, 2, 2, 2, 2, 2)),
            q(("29/7", "29/7", 4, 4, "8/7", "9/7", "9/7")),
        ),
        audit_case(
            "orientation_split_chain_control",
            q((5, 5, 4, 2, 1)),
            q((5, 5, 3, "5/2", "3/2")),
            ((2, 3), (3, 4)),
        ),
        audit_case(
            "complete_graph_saturation_chain_control",
            q((5, 5, 4, 2, 1)),
            q((5, 5, 3, "5/2", "3/2")),
        ),
    ]
    by_name = {record["name"]: record for record in controls}
    if by_name["PXC101_zero_demand"]["D_H"] != 0:
        raise AssertionError("PXC101 demand changed")
    if by_name["PXC104_reciprocal_zero_demand"]["D_H"] != 0:
        raise AssertionError("PXC104 demand changed")
    pxc125 = by_name["PXC125_positive_demand_two_rungs"]
    if pxc125["D_H"] != F(2, 3) or pxc125["transport_optimum"] != F(7):
        raise AssertionError(("PXC125 transport", pxc125))
    fail_open = by_name["PXC125_empty_graph_fail_open"]
    if fail_open["D_H"] != F(2, 3) or fail_open["transport_covers_D_H"]:
        raise AssertionError(("PXC125 fail-open graph", fail_open))
    pxc127 = by_name["PXC127_common_cut"]
    if pxc127["D_H"] != F(2, 3) or pxc127["transport_optimum"] != F(37, 5):
        raise AssertionError(("PXC127 transport", pxc127))
    chain = by_name["orientation_split_chain_control"]
    if chain["transport_optimum"] != F(1):
        raise AssertionError(("orientation-split chain", chain))
    complete_chain = by_name["complete_graph_saturation_chain_control"]
    if (
        complete_chain["transport_optimum"] != F(3, 2)
        or complete_chain["transport_optimum"] != complete_chain["label_currency"]
    ):
        raise AssertionError(("complete chain saturation", complete_chain))

    payload = {
        "claim": "PXC134 endpoint-congested threshold-transport theorem",
        "symbolic_statement": (
            "every nonnegative clipped-rectangle weighting with outgoing and "
            "incoming weight separately at most one per residual player has "
            "value at most O-B_H; the restricted optimum equals its fractional "
            "bipartite source/sink-cover dual"
        ),
        "controls": controls,
        "scope": {
            "proved_conventionally": (
                "dimension-free layer-cake upper bound and exact fractional "
                "bipartite matching/cover duality for every predeclared edge family"
            ),
            "not_proved": (
                "that PXC114 blockers, cover comparison shears, or staged Farkas "
                "supports always generate an allowed family whose optimum reaches D_H"
            ),
            "falsifier": (
                "any positive-demand instance whose structurally admissible edge graph "
                "has a dual source/sink cover of value below D_H"
            ),
        },
    }
    rendered = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
