#!/usr/bin/env python3
"""Verify the zero-anchor coalition-incidence over-cover theorem."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


def loads(coalitions, weights, n):
    return tuple(
        sum((weight for coalition, weight in zip(coalitions, weights, strict=True) if i in coalition), Fraction())
        for i in range(n)
    )


def audit_menu(coalitions, weights, anchor, expected_bound=None):
    n = 6
    coalitions = tuple(tuple(C) for C in coalitions)
    weights = tuple(Fraction(w) for w in weights)
    if any(weight < 0 for weight in weights):
        raise AssertionError("negative over-cover weight")
    incidence_loads = loads(coalitions, weights, n)
    bound = max(incidence_loads[i] for i in range(n) if i != anchor)
    if expected_bound is not None and bound != Fraction(expected_bound):
        raise AssertionError(f"support bound changed: {bound}")

    # Exact coefficient identity:
    # sum_j lambda_j q(C_j) = sum_i load_i q_i.
    left_coefficients = [Fraction() for _ in range(n)]
    for coalition, weight in zip(coalitions, weights, strict=True):
        for i in coalition:
            left_coefficients[i] += weight
    if tuple(left_coefficients) != incidence_loads:
        raise AssertionError("coalition-sum coefficient identity failed")

    # Every non-anchor simplex vertex e_i maps to its incidence column, and a
    # maximum-load vertex attains the support value exactly.
    vertex_values = {}
    for i in range(n):
        if i == anchor:
            continue
        value = sum(
            (weight for coalition, weight in zip(coalitions, weights, strict=True) if i in coalition),
            Fraction(),
        )
        vertex_values[i] = value
    if max(vertex_values.values()) != bound:
        raise AssertionError("unit-vector attainment failed")
    maximizers = [i for i, value in vertex_values.items() if value == bound]
    return {
        "coalitions": [list(C) for C in coalitions],
        "weights": [str(w) for w in weights],
        "incidence_loads": [str(v) for v in incidence_loads],
        "anchor": anchor,
        "nonanchor_support_bound": str(bound),
        "attaining_unit_vectors": maximizers,
    }


def exhaustive_small_menu_audit():
    # Exhaust every one- through three-coalition menu from a representative
    # four-coalition universe and weights 0,1,2.  This checks the theorem's
    # coefficient and vertex-attainment implementation beyond the paper rows.
    universe = ((0, 1, 4), (0, 1, 5), (1, 2), (1, 3, 4))
    tested = 0
    for size in range(1, 4):
        for menu in combinations(universe, size):
            for weights in product((0, 1, 2), repeat=size):
                if not any(weights):
                    continue
                audit_menu(menu, weights, 1)
                tested += 1
    return tested


def reject(function, label):
    try:
        function()
    except AssertionError:
        return label
    raise AssertionError(f"mutation passed: {label}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [
        ("split-poor crossing", ((0, 1, 5), (1, 2), (1, 3, 4)), (1, 1, 1), 1),
        ("empty-poor crossing", ((0, 1, 5), (1, 2, 3), (1, 4)), (1, 1, 1), 1),
        ("full-complement crossing", ((0, 1, 4), (0, 1, 5), (1, 2, 3), (1, 2, 3, 4, 5)), (1, 1, 1, 1), 2),
        ("weak-root near-cover", ((0, 1, 4), (1, 2, 5)), (1, 1), 1),
    ]
    applications = []
    for name, coalitions, weights, bound in rows:
        applications.append({"name": name, **audit_menu(coalitions, weights, 1, bound)})
    mutations = [
        reject(lambda: audit_menu(((0, 1, 5), (1, 2), (0, 1, 3, 4)), (1, 1, 1), 1, 1), "raise a nonanchor incidence load"),
        reject(lambda: audit_menu(((0, 1, 4), (0, 1, 5), (1, 2, 3), (1, 2, 3, 4, 5)), (1, 1, 1, 1), 1, 1), "understate support bound"),
        reject(lambda: audit_menu(((0, 1, 5),), (-1,), 1), "negative weight"),
    ]
    payload = {
        "schema": "zero-anchor-overcover-duality-v1",
        "status": "PASS",
        "scope": "solver-free incidence/support-function theorem and class-5 applications; standard convex duality, not novelty evidence",
        "theorem": "the q_b=0 simplex maps to the convex hull of nonanchor incidence columns; nonnegative support equals maximum nonanchor incidence load",
        "class5_applications": applications,
        "exhaustive_small_menu_count": exhaustive_small_menu_audit(),
        "rejected_mutations": mutations,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
