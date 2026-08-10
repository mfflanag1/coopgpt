#!/usr/bin/env python3
"""Differentially audit the symbolic lex-improvement condition.

The production predicate is pivot-based.  This audit compares its Boolean
semantics with a separately formulated first-affected-stratum criterion on
every labeled weak order of six players and every bound-two direction.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from search_positive_handover_directions import direction_pool  # noqa: E402


def weak_orders():
    for ranks in itertools.product(range(6), repeat=6):
        values = set(ranks)
        if values == set(range(max(values) + 1)):
            yield ranks


def pivot_predicate(ranks, direction, side):
    if side == "min":
        return any(
            value > 0
            and all(
                direction[player] == 0 or ranks[player] >= ranks[pivot]
                for player in range(6)
            )
            and all(
                direction[player] >= 0 or ranks[player] > ranks[pivot]
                for player in range(6)
            )
            for pivot, value in enumerate(direction)
        )
    return any(
        value < 0
        and all(
            direction[player] == 0 or ranks[player] <= ranks[pivot]
            for player in range(6)
        )
        and all(
            direction[player] <= 0 or ranks[player] < ranks[pivot]
            for player in range(6)
        )
        for pivot, value in enumerate(direction)
    )


def first_affected_stratum(ranks, direction, side):
    levels = sorted(set(ranks), reverse=(side == "max"))
    for level in levels:
        coefficients = [
            direction[player]
            for player in range(6)
            if ranks[player] == level
        ]
        if not any(coefficients):
            continue
        if side == "min":
            return min(coefficients) >= 0 and max(coefficients) > 0
        return max(coefficients) <= 0 and min(coefficients) < 0
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    orders = tuple(weak_orders())
    directions = direction_pool(2)
    mismatches = []
    comparison_count = 0
    accepted = {"min": 0, "max": 0}
    for ranks in orders:
        for direction in directions:
            for side in ("min", "max"):
                pivot = pivot_predicate(ranks, direction, side)
                direct = first_affected_stratum(ranks, direction, side)
                comparison_count += 1
                accepted[side] += int(pivot)
                if pivot != direct and len(mismatches) < 20:
                    mismatches.append(
                        {
                            "ranks": list(ranks),
                            "direction": list(direction),
                            "side": side,
                            "pivot": pivot,
                            "first_affected_stratum": direct,
                        }
                    )
    payload = {
        "schema": "lex-improvement-predicate-differential-audit-v1",
        "scope": "complete finite combinatorial truth-table audit",
        "status": "PASS" if not mismatches else "FAIL",
        "weak_order_count": len(orders),
        "direction_count": len(directions),
        "side_count": 2,
        "comparison_count": comparison_count,
        "accepted_count": accepted,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
