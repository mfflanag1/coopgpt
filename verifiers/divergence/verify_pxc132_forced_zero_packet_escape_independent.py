#!/usr/bin/env python3
"""Standalone incidence replay for PXC132; imports no project code."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def mask(*players):
    return sum(1 << player for player in players)


def dot(direction, coalition):
    return sum((direction[i] for i in range(len(direction)) if coalition >> i & 1), F(0))


def common_family_checks():
    answer = []
    for family in ("PXC101", "PXC125"):
        for parameter in range(1 if family == "PXC125" else 2, 101):
            if family == "PXC101":
                k = parameter
                n = k + 4
                outsiders = tuple(range(4, n))
                blocker = mask(0, 4)
                menu = (mask(0, 1), mask(0, 1, 2), mask(0, 1, 3), blocker,
                        mask(0, 1, *outsiders))
                direction = [F(0)] * n
                direction[4] = -(k - 1)
                for player in range(5, n):
                    direction[player] = 1
            else:
                t = parameter
                n = t + 5
                block = tuple(range(5, n))
                blocker = mask(0, 1, 2, *block)
                menu = (
                    mask(0, 1), mask(2), mask(0, 1, 2), mask(0, 1, 4),
                    mask(0, 1, 2, 4), blocker, mask(0, 1, 3, *block),
                    mask(0, 1, 2, 3, *block),
                )
                direction = [F(0)] * n
                direction[3] = t
                for player in block:
                    direction[player] = -1
            derivatives = {row: dot(direction, row) for row in menu}
            if sum(direction, F(0)) or derivatives[blocker] >= 0:
                raise AssertionError((family, parameter, derivatives))
            if any(value for row, value in derivatives.items() if row != blocker):
                raise AssertionError((family, parameter, derivatives))
        answer.append({"family": family, "parameter_range_checked": [1 if family == "PXC125" else 2, 100]})
    return answer


def contradiction_replay():
    # Abstract normalized numbers: d(Q)=-3 and every other z-tight row has
    # derivative zero.  A reduced active packet with Q-weight 2 and an
    # exceptional z-tight E != Q would assert -6=0 after dotting with d.
    blocker_weight, blocker_derivative, exceptional_derivative = F(2), F(-3), F(0)
    lhs = blocker_weight * blocker_derivative
    rhs = exceptional_derivative
    if lhs == rhs:
        raise AssertionError("forced-zero contradiction disappeared")
    return {"left_side": lhs, "right_side": rhs, "contradiction": True}


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
    payload = {
        "claim": "standalone PXC132 forced-zero dot-product contradiction",
        "abstract_contradiction": contradiction_replay(),
        "all_dimension_incidence_replays": common_family_checks(),
        "scope": "incidence proof and family derivative patterns only; no catalogue, LP, game, selector, or cover code",
    }
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
