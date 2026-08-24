#!/usr/bin/env python3
"""Standalone incidence audit for PXC129, sharing no project selector code."""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def bit(mask, player):
    return F((mask >> player) & 1)


def load(rows, weights, player):
    return sum((weight * bit(row, player) for row, weight in zip(rows, weights)), F(0))


def check(rows, weights, source=2, sink=4):
    forward = sum((w for row, w in zip(rows, weights)
                   if bit(row, source) == 1 and bit(row, sink) == 0), F(0))
    reverse = sum((w for row, w in zip(rows, weights)
                   if bit(row, source) == 0 and bit(row, sink) == 1), F(0))
    if load(rows, weights, source) != load(rows, weights, sink):
        raise AssertionError("support is not outsider-balanced")
    if forward != reverse:
        raise AssertionError((rows, weights, forward, reverse))
    tangent = forward == 0
    if tangent != all(bit(row, source) == bit(row, sink) for row in rows):
        raise AssertionError((rows, tangent))
    return {"rows": rows, "weights": weights, "forward": forward,
            "reverse": reverse, "classification": "tangent" if tangent else "charged"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    # Exhaust every positive integer-weight multiset of the four two-player
    # incidence types.  Equal outsider loads force 10 and 01 weights to match.
    abstract = []
    patterns = ((0, 0), (0, 1), (1, 0), (1, 1))
    for weights in itertools.product(range(1, 5), repeat=4):
        source_load = sum(F(w * p[0]) for w, p in zip(weights, patterns))
        sink_load = sum(F(w * p[1]) for w, p in zip(weights, patterns))
        if source_load != sink_load:
            continue
        forward = F(weights[2])
        reverse = F(weights[1])
        if forward != reverse:
            raise AssertionError((weights, forward, reverse))
        abstract.append(weights)
    half, quarter = F(1, 2), F(1, 4)
    controls = {
        "PXC104_pair": check((3,), (half,)),
        "PXC104_charged": check((11, 19, 39), (quarter,) * 3),
        "PXC104_other_cover": check((11, 23, 35), (quarter,) * 3),
        "PXC118_pair": check((3,), (half,)),
        "PXC118_balanced_pair": check((11, 55), (half, half)),
        "PXC118_charged": check((11, 19, 39), (quarter,) * 3),
        "PXC118_other_cover": check((11, 23, 35), (quarter,) * 3),
    }
    if {item["classification"] for item in controls.values()} != {"tangent", "charged"}:
        raise AssertionError("controls do not exercise both PXC129 outcomes")
    payload = {
        "claim": "standalone PXC129 outsider-balance incidence dichotomy",
        "abstract_balanced_positive_weight_controls": len(abstract),
        "abstract_weight_range": [1, 4],
        "controls": controls,
        "scope": (
            "incidence/load implication and reciprocal calibrations only; the staged-tangent "
            "and cover-comparison identities are proved symbolically in the manuscript"
        ),
    }
    def encode(value):
        if isinstance(value, F):
            return str(value)
        if isinstance(value, tuple):
            return [encode(item) for item in value]
        if isinstance(value, dict):
            return {key: encode(item) for key, item in value.items()}
        return value
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
