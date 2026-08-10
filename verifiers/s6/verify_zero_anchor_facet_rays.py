#!/usr/bin/env python3
"""Enumerate the exact finite ray system behind zero-anchor over-covers.

For an anchor i and a proposed maximizing non-anchor player k, the relevant
weight cone is

    lambda >= 0,
    lambda . (a^k-a^l) >= 0  for every l != i,k.

The cone has only n-2 non-coordinate inequalities.  Exact active-set
enumeration therefore finds every extreme ray, and every ray has support at
most n-1 (five when n=6).  This checker uses rational row reduction only; it
imports no solver, optimizer, production encoder, or frozen relay map.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path


def incidence_columns(coalitions, n):
    return tuple(
        tuple(Fraction(int(player in coalition)) for coalition in coalitions)
        for player in range(n)
    )


def rank(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    if not rows:
        return 0
    row = 0
    for column in range(len(rows[0])):
        pivot = next((r for r in range(row, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        scale = rows[row][column]
        rows[row] = [value / scale for value in rows[row]]
        for r in range(len(rows)):
            if r == row or not rows[r][column]:
                continue
            scale = rows[r][column]
            rows[r] = [a - scale * b for a, b in zip(rows[r], rows[row], strict=True)]
        row += 1
        if row == len(rows):
            break
    return row


def one_dimensional_null_vector(matrix, width):
    """Return one exact null vector when the nullity is one, else None."""
    rows = [list(map(Fraction, row)) for row in matrix]
    pivot_columns = []
    row = 0
    for column in range(width):
        pivot = next((r for r in range(row, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        scale = rows[row][column]
        rows[row] = [value / scale for value in rows[row]]
        for r in range(len(rows)):
            if r == row or not rows[r][column]:
                continue
            scale = rows[r][column]
            rows[r] = [a - scale * b for a, b in zip(rows[r], rows[row], strict=True)]
        pivot_columns.append(column)
        row += 1
    free = [column for column in range(width) if column not in pivot_columns]
    if len(free) != 1:
        return None
    vector = [Fraction() for _ in range(width)]
    vector[free[0]] = 1
    for r, column in reversed(list(enumerate(pivot_columns))):
        vector[column] = -sum(
            rows[r][j] * vector[j] for j in range(column + 1, width)
        )
    return tuple(vector)


def primitive_integer(vector):
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in vector]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def extreme_rays(coalitions, anchor, maximizer, n=6, support_cap=None):
    columns = incidence_columns(coalitions, n)
    comparisons = [
        tuple(a - b for a, b in zip(columns[maximizer], columns[player], strict=True))
        for player in range(n)
        if player not in (anchor, maximizer)
    ]
    m = len(coalitions)
    rays = set()
    cap = n - 1 if support_cap is None else support_cap
    for support_size in range(1, min(m, cap) + 1):
        for support in combinations(range(m), support_size):
            restricted = [tuple(row[j] for j in support) for row in comparisons]
            for active in combinations(range(len(comparisons)), support_size - 1):
                active_rows = [restricted[index] for index in active]
                if rank(active_rows) != support_size - 1:
                    continue
                vector = one_dimensional_null_vector(active_rows, support_size)
                if vector is None:
                    continue
                if all(value < 0 for value in vector):
                    vector = tuple(-value for value in vector)
                if not all(value > 0 for value in vector):
                    continue
                full = [Fraction() for _ in range(m)]
                for index, value in zip(support, vector, strict=True):
                    full[index] = value
                if any(
                    sum(a * b for a, b in zip(row, full, strict=True)) < 0
                    for row in comparisons
                ):
                    continue
                rays.add(primitive_integer(full))
    return tuple(sorted(rays))


def audit_menu(name, coalitions, n=6):
    coalitions = tuple(tuple(coalition) for coalition in coalitions)
    columns = incidence_columns(coalitions, n)
    rows = []
    all_rays = set()
    for anchor in range(n):
        anchor_rays = set()
        for maximizer in range(n):
            if maximizer == anchor:
                continue
            for ray in extreme_rays(coalitions, anchor, maximizer, n):
                loads = tuple(
                    sum(Fraction(weight) * columns[player][j]
                        for j, weight in enumerate(ray))
                    for player in range(n)
                )
                if loads[maximizer] != max(loads[player] for player in range(n) if player != anchor):
                    raise AssertionError("ray lies outside its maximizing cone")
                anchor_rays.add((ray, int(loads[maximizer])))
                all_rays.add(ray)
        rows.append({
            "anchor": anchor,
            "distinct_ray_inequality_count": len(anchor_rays),
            "maximum_support": max(sum(bool(value) for value in ray) for ray, _ in anchor_rays),
        })
    maximum_support = max(sum(bool(value) for value in ray) for ray in all_rays)
    if maximum_support > n - 1:
        raise AssertionError("n-1 support theorem failed")
    return {
        "name": name,
        "requirement_count": len(coalitions),
        "distinct_weight_ray_count": len(all_rays),
        "maximum_support": maximum_support,
        "maximum_coefficient": max(max(ray) for ray in all_rays),
        "anchors": rows,
    }


def exhaustive_representative_audit():
    universe = (
        (0, 1, 4),
        (0, 2, 5),
        (1, 2, 3),
        (1, 3, 4),
        (2, 4, 5),
        (0, 1, 2, 3),
    )
    tested = 0
    maximum_support = 0
    maximum_coefficient = 0
    for size in range(1, 5):
        for menu in combinations(universe, size):
            row = audit_menu("representative", menu)
            tested += 1
            maximum_support = max(maximum_support, row["maximum_support"])
            maximum_coefficient = max(maximum_coefficient, row["maximum_coefficient"])
    return {
        "menu_count": tested,
        "maximum_support": maximum_support,
        "maximum_coefficient": maximum_coefficient,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # The last menu makes the n-1 bound sharp.  For anchor 5 and maximizer 0,
    # the four comparison rows have positive null ray (1,1,1,1,1).
    menus = [
        ("crossing-three", ((0, 1, 5), (1, 2), (1, 3, 4))),
        ("mixed-four", ((0, 1, 4), (0, 1, 5), (1, 2, 3), (1, 2, 3, 4, 5))),
        ("sharp-five-circuit", (
            (0, 2, 3, 4),
            (0, 1, 3, 4),
            (0, 1, 2, 4),
            (0, 1, 2, 3),
            (1, 2, 3, 4),
        )),
    ]
    rows = [audit_menu(name, coalitions) for name, coalitions in menus]
    sharp = rows[-1]
    if sharp["maximum_support"] != 5:
        raise AssertionError("sharp support-five circuit was not detected")
    sharp_menu = menus[-1][1]
    sharp_ray = (1, 1, 1, 1, 1)
    if sharp_ray not in extreme_rays(sharp_menu, 5, 0):
        raise AssertionError("sharp primitive ray was not reconstructed")
    if sharp_ray in extreme_rays(sharp_menu, 5, 0, support_cap=4):
        raise AssertionError("support-cap mutation was not detected")

    payload = {
        "schema": "zero-anchor-facet-rays-v1",
        "status": "PASS",
        "scope": (
            "solver-free exact extreme-ray enumeration for the anchor/maximizer "
            "weight cones; no production encoder or relay map"
        ),
        "theorem": (
            "all zero-anchor witness inequalities are generated by rational rays "
            "supported on at most n-1 requirements; the bound is sharp at n=6"
        ),
        "exhaustive_representative_audit": exhaustive_representative_audit(),
        "rejected_mutations": ["cap extreme-ray support at n-2"],
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
