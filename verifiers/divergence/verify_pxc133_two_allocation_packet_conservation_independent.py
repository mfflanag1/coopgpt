#!/usr/bin/env python3
"""Standalone coefficient audit of PXC133; imports no project code."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def load(rows, weights, n):
    return tuple(sum((w for s, w in zip(rows, weights) if s >> i & 1), F(0)) for i in range(n))


def coalition_sum(point, row):
    return sum((point[i] for i in range(len(point)) if row >> i & 1), F(0))


def replay(name, rows, exceptional, beta, ambient, x, z):
    weights = (F(1),) * len(rows)
    expected = tuple(ambient + beta * F(bool(exceptional >> i & 1)) for i in range(6))
    if load(rows, weights, 6) != expected:
        raise AssertionError((name, load(rows, weights, 6), expected))
    lhs = sum((coalition_sum(x, row) - coalition_sum(z, row) for row in rows), F(0))
    rhs = beta * (coalition_sum(x, exceptional) - coalition_sum(z, exceptional))
    if lhs != rhs:
        raise AssertionError((name, lhs, rhs))
    return {"name": name, "comparison_left": lhs, "exceptional_shear": rhs}


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = [
        replay("PXC101", (7, 17, 41), 1, F(2), F(1),
               tuple(F(v) for v in ("9/2", "9/2", 2, 2, 2, 2)),
               tuple(F(v) for v in (4, 4, 3, 3, 2, 1))),
        replay("PXC104", (11, 23, 35), 3, F(2), F(1),
               tuple(F(v) for v in ("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
               tuple(F(v) for v in (6, 6, 5, 4, 1, 1))),
        replay("PXC125", (39, 43, 51), 35, F(2), F(1),
               tuple(F(v) for v in ("13/2", "13/2", 1, 5, 1, 5)),
               tuple(F(v) for v in (6, 6, 0, "26/5", 2, "29/5"))),
    ]
    payload = {
        "claim": "standalone PXC133 incidence-dot-product conservation",
        "records": records,
        "scope": "coefficient and x-z arithmetic only; no game, exactness, LP, selector, cover, or catalogue code",
    }
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
