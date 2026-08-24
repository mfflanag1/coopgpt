#!/usr/bin/env python3
"""Independent finite combinatorial replay of the PXC126 square bound.

This implementation uses only integer endpoint pairs and an explicit
threshold integral.  It imports no project, PXC125, label-currency, selector,
cover, or primary-verifier code.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def layer_value(a, b):
    cuts = sorted(set((0, *a, *b)))
    answer = 0
    for lo, hi in zip(cuts, cuts[1:]):
        high = sum(value >= hi for value in a)
        low = sum(value < hi for value in b)
        answer += (hi - lo) * min(high, low)
    return answer


def canonical_value(a, b):
    return sum(max(0, high - low) for high, low in zip(
        sorted(a, reverse=True), sorted(b)
    ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    endpoints = tuple((a, b) for a in range(4) for b in range(a, 4))
    permutations = tuple(itertools.permutations(range(4)))
    checked = 0
    positive = 0
    equality = 0
    for profile in itertools.product(endpoints, repeat=4):
        a = tuple(item[0] for item in profile)
        b = tuple(item[1] for item in profile)
        layer = layer_value(a, b)
        canonical = canonical_value(a, b)
        if layer != canonical:
            raise AssertionError((profile, layer, canonical))
        for u11, u01, u10, u00 in permutations:
            price = max(0, a[u11] - b[u01]) + max(0, a[u10] - b[u00])
            if price > layer:
                raise AssertionError((profile, (u11, u01, u10, u00), price, layer))
            checked += 1
            positive += price > 0
            equality += price == layer

    duplicated = 2 * (5 - 1)
    fail_currency = layer_value((5, 0), (5, 1))
    if duplicated <= fail_currency:
        raise AssertionError((duplicated, fail_currency))

    payload = {
        "claim": "independent exhaustive endpoint replay of PXC126a-b",
        "endpoint_pairs": len(endpoints),
        "four_player_profiles": len(endpoints) ** 4,
        "cell_permutations_per_profile": len(permutations),
        "square_assignments_checked": checked,
        "positive_square_assignments": positive,
        "equality_assignments": equality,
        "all_square_prices_at_most_layer_currency": True,
        "canonical_formula_equals_threshold_integral": True,
        "drop_disjointness_control": {
            "duplicated_price": duplicated,
            "layer_currency": fail_currency,
            "violates_bound": duplicated > fail_currency,
        },
        "independence": (
            "standalone exhaustive integer endpoint and threshold enumeration; "
            "no project or primary-verifier imports"
        ),
        "scope": "finite audit of the dimension-free hand lemma, not evidence for PXC126?",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
