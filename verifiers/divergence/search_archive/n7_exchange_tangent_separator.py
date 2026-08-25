#!/usr/bin/env python3
"""Exact staged tangent separator for a scratch n=7 lower-envelope model."""

from __future__ import annotations

import importlib.util
import argparse
import json
import math
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("exactlp", ROOT / "src/exactlp.py")
exactlp = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(exactlp)


def csum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def primitive(direction):
    denominator = math.lcm(*(value.denominator for value in direction))
    integers = [value.numerator * (denominator // value.denominator) for value in direction]
    divisor = math.gcd(*(abs(value) for value in integers))
    return tuple(value // divisor for value in integers)


def blocks(point, side):
    levels = sorted(set(point), reverse=(side == "max"))
    return tuple(tuple(i for i, value in enumerate(point) if value == level) for level in levels)


def separate(reference, generators, side):
    n = len(reference)
    full = (1 << n) - 1
    values = tuple(min(csum(point, mask) for point in generators) for mask in range(1 << n))
    active = tuple(mask for mask in range(1, full) if csum(reference, mask) == values[mask])
    aub = []
    bub = []
    # Active core rows require d(S)>=0.
    for mask in active:
        aub.append([-F((mask >> i) & 1) for i in range(n)])
        bub.append(F(0))
    # Active nonnegativity is already the active singleton row, but retain the
    # explicit guard so the separator remains faithful if zero rows are elided.
    for i, value in enumerate(reference):
        if value == 0:
            row = [F(0)] * n
            row[i] = F(-1)
            aub.append(row)
            bub.append(F(0))
    earlier = []
    attempts = []
    for block_index, block in enumerate(blocks(reference, side)):
        for designated in block:
            cell_aub = list(aub)
            cell_bub = list(bub)
            for j in block:
                row = [F(0)] * n
                if side == "min":
                    row[j] = F(-1)  # d_j>=0
                else:
                    row[j] = F(1)   # d_j<=0
                cell_aub.append(row)
                cell_bub.append(F(0))
            row = [F(0)] * n
            if side == "min":
                row[designated] = F(-1)  # d_i>=1
            else:
                row[designated] = F(1)   # d_i<=-1
            cell_aub.append(row)
            cell_bub.append(F(-1))
            aeq = [[F(1)] * n]
            beq = [F(0)]
            for j in earlier:
                row = [F(0)] * n
                row[j] = F(1)
                aeq.append(row)
                beq.append(F(0))
            status, _value, direction = exactlp.exact_linprog(
                [F(0)] * n, cell_aub, cell_bub, aeq, beq
            )
            attempts.append((block_index, designated, status))
            if status == "optimal":
                return {
                    "side": side,
                    "active_row_count": len(active),
                    "block_index": block_index,
                    "block": block,
                    "designated": designated,
                    "direction": tuple(direction),
                    "primitive_direction": primitive(direction),
                    "attempts": attempts,
                }
        earlier.extend(block)
    return {
        "side": side,
        "active_row_count": len(active),
        "direction": None,
        "attempts": attempts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    model = payload["rows"][0]["model"]
    x = tuple(map(F, model["x"]))
    z = tuple(map(F, model["z"]))
    witnesses = tuple(tuple(map(F, row)) for row in model["witnesses"])
    generators = (x, z) + witnesses
    result = [separate(x, generators, "min"), separate(z, generators, "max")]
    print(
        json.dumps(
            result,
            indent=2,
            default=lambda item: list(item) if isinstance(item, tuple) else str(item),
        )
    )


if __name__ == "__main__":
    main()
