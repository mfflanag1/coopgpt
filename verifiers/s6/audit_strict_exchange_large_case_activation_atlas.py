#!/usr/bin/env python3
"""Audit the 19-schema activation atlas for the three large strict cases.

This is a solver-free combinatorial check.  It expands the selected role
orbits directly, enumerates every labelled weak payoff order, and compares
the first-affected-level definition with the min/max support test.  It does
not inspect or validate any blocker consequent.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
CASE_META = {
    "p3_n2_t1": (3, 2, 1, "A"),
    "p3_n3_t0": (3, 3, 0, "B"),
    "p4_n2_t0": (4, 2, 0, "C"),
}
EXPECTED_COUNTS = {
    "p3_n2_t1": [2, 3, 6, 3, 3, 6, 3, 3],
    "p3_n3_t0": [9, 9, 9, 6, 6],
    "p4_n2_t0": [8, 24, 12, 6, 12, 6],
}


def weak_orders(size: int):
    """Return canonical rank vectors for all labelled total preorders."""
    for ranks in itertools.product(range(size), repeat=size):
        if set(ranks) == set(range(max(ranks) + 1)):
            yield ranks


def unique_permutations(values):
    return sorted(set(itertools.permutations(values)))


def expand_orbit(orbit, positive_count, negative_count, tie_count):
    blocks = (
        unique_permutations(orbit["P"]),
        unique_permutations(orbit["M"]),
        unique_permutations(orbit["E"]),
    )
    if any(len(values) == 0 for values in blocks):
        raise AssertionError("empty permutation block")
    directions = []
    for positive, negative, tied in itertools.product(*blocks):
        direction = (*positive, *negative, *tied)
        if len(direction) != positive_count + negative_count + tie_count:
            raise AssertionError(direction)
        if sum(direction) != 0 or not any(direction):
            raise AssertionError(direction)
        directions.append(direction)
    return directions


def first_affected_level(ranks, direction, side):
    affected = [index for index, value in enumerate(direction) if value]
    if side == "min":
        level = min(ranks[index] for index in affected)
        signs = [direction[index] for index in affected if ranks[index] == level]
        return any(value > 0 for value in signs) and not any(value < 0 for value in signs)
    if side == "max":
        level = max(ranks[index] for index in affected)
        signs = [direction[index] for index in affected if ranks[index] == level]
        return any(value < 0 for value in signs) and not any(value > 0 for value in signs)
    raise ValueError(side)


def extreme_support_test(ranks, direction, side, strict=True):
    positive = [ranks[index] for index, value in enumerate(direction) if value > 0]
    negative = [ranks[index] for index, value in enumerate(direction) if value < 0]
    if not positive or not negative:
        raise AssertionError(direction)
    if side == "min":
        return min(positive) < min(negative) if strict else min(positive) <= min(negative)
    if side == "max":
        return max(negative) > max(positive) if strict else max(negative) >= max(positive)
    raise ValueError(side)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = json.loads((HERE / "strict_exchange_large_case_orbit_cores.json").read_text())
    source_rows = {row["case"]: row for row in payload["rows"]}
    orders = tuple(weak_orders(6))
    if len(orders) != 4683:
        raise AssertionError(f"unexpected weak-order count: {len(orders)}")

    rows = []
    total_directions = 0
    total_comparisons = 0
    mutation_detected = False
    for case, (positive_count, negative_count, tie_count, prefix) in CASE_META.items():
        source = source_rows[case]
        expected = EXPECTED_COUNTS[case]
        orbits = source["selected_orbits"]
        if len(orbits) != len(expected):
            raise AssertionError(f"{case}: unexpected schema count")
        schemas = []
        case_directions = 0
        for offset, (orbit, expected_count) in enumerate(zip(orbits, expected, strict=True), 1):
            directions = expand_orbit(orbit, positive_count, negative_count, tie_count)
            if len(directions) != expected_count:
                raise AssertionError(
                    f"{case} {prefix}{offset}: {len(directions)} != {expected_count}"
                )
            for direction in directions:
                for ranks in orders:
                    direct = first_affected_level(ranks, direction, orbit["side"])
                    extreme = extreme_support_test(ranks, direction, orbit["side"])
                    if direct != extreme:
                        raise AssertionError(
                            f"{case} {prefix}{offset}: activation mismatch for "
                            f"{direction} at {ranks}"
                        )
                    if direct != extreme_support_test(
                        ranks, direction, orbit["side"], strict=False
                    ):
                        mutation_detected = True
            comparisons = len(directions) * len(orders)
            total_comparisons += comparisons
            case_directions += len(directions)
            schemas.append(
                {
                    "schema": f"{prefix}{offset}",
                    "side": orbit["side"],
                    "labelled_direction_count": len(directions),
                    "weak_order_comparisons": comparisons,
                }
            )
        if case_directions != source["selected_labeled_direction_count"]:
            raise AssertionError(f"{case}: labelled selected-core count changed")
        total_directions += case_directions
        rows.append(
            {
                "case": case,
                "schema_count": len(schemas),
                "labelled_direction_count": case_directions,
                "schemas": schemas,
            }
        )

    if total_directions != 136 or not mutation_detected:
        raise AssertionError("activation atlas coverage or strictness mutation failed")
    report = {
        "schema": "strict-exchange-large-case-activation-atlas-v1",
        "status": "PASS",
        "scope": (
            "solver-free expansion of the 19 selected role orbits and exhaustive "
            "activation equivalence on labelled weak orders; blocker consequents excluded"
        ),
        "weak_order_count": len(orders),
        "selected_schema_count": sum(row["schema_count"] for row in rows),
        "selected_labeled_direction_count": total_directions,
        "activation_comparison_count": total_comparisons,
        "nonstrict_mutation_detected": mutation_detected,
        "rows": rows,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    # Keep the per-schema rows compact while preserving deterministic JSON.
    schema_block = re.compile(
        r'(?m)^(?P<indent>\s*)\{\n'
        r'(?P=indent)  "labelled_direction_count": (?P<count>[0-9]+),\n'
        r'(?P=indent)  "schema": "(?P<schema>[ABC][0-9]+)",\n'
        r'(?P=indent)  "side": "(?P<side>min|max)",\n'
        r'(?P=indent)  "weak_order_comparisons": (?P<comps>[0-9]+)\n'
        r'(?P=indent)\}'
    )
    rendered = schema_block.sub(
        lambda match: (
            f'{match.group("indent")}{{"labelled_direction_count": '
            f'{match.group("count")}, "schema": "{match.group("schema")}", '
            f'"side": "{match.group("side")}", "weak_order_comparisons": '
            f'{match.group("comps")}}}'
        ),
        rendered,
    )
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
