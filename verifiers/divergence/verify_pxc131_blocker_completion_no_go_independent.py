#!/usr/bin/env python3
"""Standalone active-set replay of the three PXC131 irredundancy controls."""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def solve_square(matrix, rhs):
    n = len(rhs)
    aug = [[F(value) for value in row] + [F(value)] for row, value in zip(matrix, rhs)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col]), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [value / scale for value in aug[col]]
        for r in range(n):
            if r == col or not aug[r][col]:
                continue
            scale = aug[r][col]
            aug[r] = [a - scale * b for a, b in zip(aug[r], aug[col])]
    return tuple(row[-1] for row in aug)


def vertices(constraints, total, n=6):
    inequalities = []
    for i in range(n):
        inequalities.append((tuple(F(int(q == i)) for q in range(n)), F(0)))
    for mask, bound in constraints.items():
        inequalities.append((tuple(F((mask >> i) & 1) for i in range(n)), F(bound)))
    answer = set()
    for active in itertools.combinations(inequalities, n - 1):
        point = solve_square(
            [tuple(F(1) for _ in range(n)), *(normal for normal, _ in active)],
            [F(total), *(bound for _, bound in active)],
        )
        if point is None or any(value < 0 for value in point):
            continue
        if any(sum(normal[i] * point[i] for i in range(n)) < bound
               for normal, bound in inequalities):
            continue
        answer.add(point)
    if not answer:
        raise AssertionError("empty vertex set")
    return tuple(sorted(answer))


def csum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def lower_envelope(constraints, total):
    points = vertices(constraints, total)
    return tuple(min(csum(point, mask) for point in points) for mask in range(64)), points


def check_control(name, constraints, total, exceptional, candidate, dual_rows,
                  dual_weights, ambient):
    values, points = lower_envelope(constraints, total)
    if csum(candidate, exceptional) >= values[exceptional]:
        raise AssertionError((name, "candidate does not violate blocker"))
    bad = tuple(mask for mask in range(1, 63)
                if mask != exceptional and csum(candidate, mask) < values[mask])
    if bad:
        raise AssertionError((name, bad))
    loads = tuple(
        sum((weight for row, weight in zip(dual_rows, dual_weights) if row >> i & 1), F(0))
        for i in range(6)
    )
    expected = tuple(ambient + F((exceptional >> i) & 1) for i in range(6))
    if loads != expected:
        raise AssertionError((name, loads, expected))
    lower_bound = sum((weight * values[row]
                       for row, weight in zip(dual_rows, dual_weights)), F(0)) - ambient * total
    if lower_bound != csum(candidate, exceptional):
        raise AssertionError((name, lower_bound, candidate))
    return {
        "name": name,
        "defining_polytope_vertex_count": len(points),
        "blocker": exceptional,
        "blocker_worth": values[exceptional],
        "deleted_row_minimum": lower_bound,
        "deleted_row_minimizer": candidate,
        "dual_rows": dual_rows,
        "dual_weights": dual_weights,
        "dual_ambient": ambient,
        "dual_loads": loads,
        "all_other_proper_core_rows_checked": True,
    }


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
    p101 = {7: F(11), 11: F(11), 17: F(6), 51: F(11)}
    p104 = {7: F(16), 11: F(16), 19: F(13), 23: F(18), 35: F(13), 39: F(18)}
    controls = [
        check_control(
            "PXC101_rj", p101, F(17), 17,
            (F(3), F(5), F(3), F(3), F(0), F(3)),
            (21, 25, 51), (F(1, 2),) * 3, F(1, 2),
        ),
        check_control(
            "PXC104_rhaj", p104, F(23), 23,
            (F(16), F(0), F(0), F(5), F(0), F(2)),
            (7, 16), (F(1), F(1)), F(0),
        ),
        check_control(
            "PXC104_rhak", p104, F(23), 39,
            (F(16), F(0), F(0), F(5), F(2), F(0)),
            (7, 32), (F(1), F(1)), F(0),
        ),
    ]
    payload = {
        "claim": "standalone PXC131 blocker irredundancy replay",
        "controls": controls,
        "scope": (
            "independent rational active-set lower envelopes, explicit primal minimizers, "
            "and explicit dual lower bounds; no project LP or selector code"
        ),
    }
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
