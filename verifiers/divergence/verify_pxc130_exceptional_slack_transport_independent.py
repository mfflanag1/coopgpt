#!/usr/bin/env python3
"""Standalone coefficient audit for PXC130.

This implementation shares no project game, selector, cover, catalogue, or
PXC130-primary code.  It checks the generic coefficient cancellation on an
exhaustive finite family of incidence identities and the two named primitive
relations directly.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def vector(mask, n):
    return tuple(F((mask >> i) & 1) for i in range(n))


def add(*vectors):
    return tuple(sum(items, F(0)) for items in zip(*vectors))


def scale(c, values):
    return tuple(c * value for value in values)


def independent_identity_checks():
    checked = 0
    # Exhaust all two-block and three-block ordered partitions of up to four
    # residual labels.  These are coefficient checks, not a game census.
    for residual_size in range(2, 5):
        n = residual_size + 2
        pair = 3
        residual = tuple(range(2, n))
        for labels in itertools.product(range(3), repeat=residual_size):
            used = set(labels)
            if used not in ({0, 1}, {0, 1, 2}):
                continue
            m = len(used)
            blocks = tuple(
                sum(1 << residual[q] for q, label in enumerate(labels) if label == block)
                for block in range(m)
            )
            rows = tuple(pair | block for block in blocks)
            left = add(*(vector(row, n) for row in rows))
            right = add(tuple(F(1) for _ in range(n)), scale(F(m - 1), vector(pair, n)))
            if left != right:
                raise AssertionError((n, blocks, left, right))
            checked += 1
    return checked


def relation(rows, coefficients, exceptional, beta, ambient, n):
    left = add(*(scale(F(c), vector(row, n)) for row, c in zip(rows, coefficients)))
    right = add(scale(F(ambient), tuple(F(1) for _ in range(n))),
                scale(F(beta), vector(exceptional, n)))
    if left != right:
        raise AssertionError((left, right))
    return left


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    partition_checks = independent_identity_checks()
    pxc101 = relation((7, 11, 51), (1, 1, 1), 3, 2, 1, 6)
    type41 = relation((37, 38, 56, 43, 51), (2, 2, 3, 1, 1), 32, 5, 4, 6)
    payload = {
        "claim": "standalone PXC130 coefficient cancellation",
        "ordered_partition_identity_checks": partition_checks,
        "pxc101_partition_star_loads": pxc101,
        "catalogue_type41_loads": type41,
        "scope": (
            "incidence and coefficient cancellation only; exactness supplies the attaining "
            "witness and the manuscript supplies the inequality proof"
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
