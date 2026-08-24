#!/usr/bin/env python3
"""Standalone named-control replay for PXC135.

This file uses exhaustive residual assignment rather than the primary
rank-pair implementation and imports no project code.  It checks the exact
canonical transport values and common-row labels on the nonvacuous controls.
The all-dimensional attribution theorem remains the written PXC129+PXC134
argument.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def q(values):
    return tuple(F(value) for value in values)


def cut(mask, left, right):
    return ((mask >> left) & 1) != ((mask >> right) & 1)


def exhaustive_assignment(x, z, top=(0, 1)):
    residual = tuple(i for i in range(len(x)) if i not in top)
    low = {i: min(x[i], z[i]) for i in residual}
    high = {i: max(x[i], z[i]) for i in residual}
    best = F(-1)
    supports = []
    for sinks in itertools.permutations(residual):
        edges = tuple(
            (source, sink, low[source] - high[sink])
            for source, sink in zip(residual, sinks)
            if low[source] > high[sink]
        )
        value = sum((edge[2] for edge in edges), F(0))
        if value > best:
            best = value
            supports = [edges]
        elif value == best:
            supports.append(edges)
    return best, tuple(supports)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    cases = (
        (
            "PXC116",
            q(("25/4", "25/4", "1/2", "9/4", "1/2", "9/4")),
            q((6, 6, 0, 2, 1, 3)),
            (19, 43),
            F(11, 4),
        ),
        (
            "PXC125",
            q(("13/2", "13/2", 1, 5, 1, 5)),
            q((6, 6, 0, "26/5", 2, "29/5")),
            (19, 43),
            F(7),
        ),
        (
            "PXC127",
            q(("32/5", "32/5", 1, "51/10", 1, "51/10")),
            q((6, 6, "1/5", "26/5", "9/5", "29/5")),
            (19, 43),
            F(37, 5),
        ),
    )
    records = []
    for name, x, z, rows, expected in cases:
        optimum, supports = exhaustive_assignment(x, z)
        if optimum != expected:
            raise AssertionError((name, optimum, expected))
        labelled_supports = []
        for support in supports:
            labels = tuple(
                tuple(row for row in rows if cut(row, source, sink))
                for source, sink, _length in support
            )
            if support and all(labels):
                labelled_supports.append((support, labels))
        if not labelled_supports:
            raise AssertionError((name, "no fully common-labelled optimum"))
        records.append(
            {
                "name": name,
                "assignment_optimum": optimum,
                "optimal_assignment_count": len(supports),
                "common_labelled_optimal_support": labelled_supports[0],
            }
        )

    payload = {
        "claim": "standalone PXC135 named canonical-assignment controls",
        "records": records,
        "scope": (
            "exhaustive residual permutations and direct row-incidence labels on "
            "three named controls; no project selector, spectral, cover, or LP code"
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
