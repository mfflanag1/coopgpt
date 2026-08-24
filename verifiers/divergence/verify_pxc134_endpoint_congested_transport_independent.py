#!/usr/bin/env python3
"""Standalone arithmetic controls for PXC134.

This companion imports no project LP, selector, cover, spectral, or packet
code.  It checks the layer-cake endpoint bound directly on the named payoff
pairs and exhausts the two nonzero restricted matchings combinatorially.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def q(values):
    return tuple(F(value) for value in values)


def interval(x, z, high, low):
    start = max(x[low], z[low])
    end = min(x[high], z[high])
    return max(F(0), end - start)


def label_currency(x, z, top):
    residual = tuple(i for i in range(len(x)) if i not in top)
    levels = sorted({F(0)} | {x[i] for i in residual} | {z[i] for i in residual})
    value = F(0)
    layers = []
    for low, high in zip(levels, levels[1:]):
        high_set = {i for i in residual if min(x[i], z[i]) >= high}
        low_set = {i for i in residual if max(x[i], z[i]) <= low}
        capacity = min(len(high_set), len(low_set))
        contribution = F(capacity) * (high - low)
        value += contribution
        if contribution:
            layers.append((low, high, capacity, contribution))
    return value, tuple(layers)


def maximum_integral_bipartite_matching(x, z, allowed):
    best = F(0)
    best_edges = ()
    allowed = tuple(allowed)
    for size in range(len(allowed) + 1):
        for selected in itertools.combinations(allowed, size):
            sources = [edge[0] for edge in selected]
            sinks = [edge[1] for edge in selected]
            if len(sources) != len(set(sources)) or len(sinks) != len(set(sinks)):
                continue
            value = sum((interval(x, z, *edge) for edge in selected), F(0))
            if value > best:
                best = value
                best_edges = selected
    return best, best_edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    zero_cases = [
        (
            "PXC101",
            q(("9/2", "9/2", 2, 2, 2, 2)),
            q((4, 4, 3, 3, 2, 1)),
        ),
        (
            "PXC104",
            q(("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            q((6, 6, 5, 4, 1, 1)),
        ),
        (
            "PXC90",
            q((6, 4, 2, 2, 2, 2, 2)),
            q(("29/7", "29/7", 4, 4, "8/7", "9/7", "9/7")),
        ),
    ]
    records = []
    for name, x, z in zero_cases:
        top_value = max(z)
        top = tuple(i for i, value in enumerate(z) if value == top_value)
        currency, layers = label_currency(x, z, top)
        if currency != 0 or layers:
            raise AssertionError((name, currency, layers))
        records.append({"name": name, "label_currency": currency, "matching": F(0)})

    nonzero = [
        (
            "PXC125",
            q(("13/2", "13/2", 1, 5, 1, 5)),
            q((6, 6, 0, "26/5", 2, "29/5")),
            ((3, 2), (5, 4)),
            F(7),
        ),
        (
            "PXC127",
            q(("32/5", "32/5", 1, "51/10", 1, "51/10")),
            q((6, 6, "1/5", "26/5", "9/5", "29/5")),
            ((3, 2), (3, 4), (5, 2), (5, 4)),
            F(37, 5),
        ),
    ]
    for name, x, z, allowed, expected in nonzero:
        currency, layers = label_currency(x, z, (0, 1))
        optimum, support = maximum_integral_bipartite_matching(x, z, allowed)
        if currency != expected or optimum != expected:
            raise AssertionError((name, currency, optimum, expected))
        # These two allowed graphs are bipartite forests/K2,2, so their
        # fractional matching polytopes are integral.  Exhausting integral
        # matchings therefore independently checks the primary LP optimum.
        records.append(
            {
                "name": name,
                "label_currency": currency,
                "matching": optimum,
                "support": support,
                "layers": layers,
            }
        )

    # A positive-demand empty admissible graph must remain a genuine failure
    # rather than silently falling back to the complete rectangle family.
    pxc125_x, pxc125_z = nonzero[0][1], nonzero[0][2]
    empty_optimum, empty_support = maximum_integral_bipartite_matching(
        pxc125_x, pxc125_z, ()
    )
    if empty_optimum != 0 or empty_support:
        raise AssertionError("empty graph did not fail open")
    records.append(
        {
            "name": "PXC125_empty_graph_fail_open",
            "label_currency": F(7),
            "matching": empty_optimum,
            "target_demand": F(2, 3),
        }
    )

    chain_x = q((5, 5, 4, 2, 1))
    chain_z = q((5, 5, 3, "5/2", "3/2"))
    chain_allowed = ((2, 3), (3, 4))
    chain_currency, chain_layers = label_currency(chain_x, chain_z, (0, 1))
    chain_optimum, chain_support = maximum_integral_bipartite_matching(
        chain_x, chain_z, chain_allowed
    )
    if chain_currency != F(3, 2) or chain_optimum != F(1):
        raise AssertionError(("orientation-split chain", chain_currency, chain_optimum))
    records.append(
        {
            "name": "orientation_split_chain_control",
            "label_currency": chain_currency,
            "matching": chain_optimum,
            "support": chain_support,
            "layers": chain_layers,
        }
    )
    complete_allowed = tuple(
        (high, low)
        for high in (2, 3, 4)
        for low in (2, 3, 4)
        if high != low and interval(chain_x, chain_z, high, low) > 0
    )
    complete_optimum, complete_support = maximum_integral_bipartite_matching(
        chain_x, chain_z, complete_allowed
    )
    if complete_optimum != chain_currency:
        raise AssertionError(("complete graph saturation", complete_optimum, chain_currency))
    records.append(
        {
            "name": "complete_graph_saturation_chain_control",
            "label_currency": chain_currency,
            "matching": complete_optimum,
            "support": complete_support,
        }
    )

    payload = {
        "claim": "standalone PXC134 threshold and matching controls",
        "records": records,
        "scope": (
            "exact payoff/layer arithmetic and exhaustive integral bipartite "
            "matchings on the named controls only; no project LP or "
            "structural-existence code"
        ),
    }

    def encode(value):
        if isinstance(value, F):
            return str(value)
        if isinstance(value, tuple):
            return [encode(item) for item in value]
        if isinstance(value, list):
            return [encode(item) for item in value]
        if isinstance(value, dict):
            return {key: encode(item) for key, item in value.items()}
        return value

    rendered = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
