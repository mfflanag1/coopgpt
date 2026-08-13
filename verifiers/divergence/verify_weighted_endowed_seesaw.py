#!/usr/bin/env python3
"""Exact audit of the endowed two-flat four-role seesaw reduction.

The human theorem identifies weighted Lmin/Lmax with two max-min values of a
2x2 crossing-time matrix.  This script independently replays staged LPs on
fixed controls and exhausts a bounded exact grid only as falsification
evidence for the still-open general middle-gap inequality.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402


def atomic_target(n):
    return F(4 * n, n * n - (n % 2))


def clamp(value, width):
    return min(max(value, F(0)), F(width))


def crossing_matrix(weights, endowments, width):
    return {
        (rising, falling): F(
            weights[rising] * (endowments[falling] + width)
            - weights[falling] * endowments[rising],
            weights[rising] + weights[falling],
        )
        for rising in (0, 2)
        for falling in (1, 3)
    }


def selector_positions(weights, endowments, width):
    matrix = crossing_matrix(weights, endowments, width)
    lmin = max(min(matrix[r, f] for f in (1, 3)) for r in (0, 2))
    lmax = max(min(matrix[r, f] for r in (0, 2)) for f in (1, 3))
    ordered = sorted(clamp(value, width) for value in matrix.values())
    lmin, lmax = clamp(lmin, width), clamp(lmax, width)
    if sorted((lmin, lmax)) != ordered[1:3]:
        raise AssertionError((weights, endowments, width, matrix, lmin, lmax))
    return lmin, lmax, matrix


def affine(role, endowments, width):
    if role in (0, 2):
        return F(1), F(endowments[role])
    return F(-1), F(endowments[role] + width)


def exact_staged_selector(weights, endowments, width, mode):
    pinned, free, trace = {}, set(range(4)), []
    while free:
        aub = [[F(-1), F(0)], [F(1), F(0)]]
        bub = [F(0), F(width)]
        aeq, beq = [], []
        for role, payoff in pinned.items():
            slope, intercept = affine(role, endowments, width)
            aeq.append([slope, F(0)])
            beq.append(payoff - intercept)
        for role in free:
            slope, intercept = affine(role, endowments, width)
            if mode == "min":
                aub.append([-slope, F(weights[role])])
                bub.append(intercept)
            else:
                aub.append([slope, F(-weights[role])])
                bub.append(-intercept)
        objective = [F(0), F(-1 if mode == "min" else 1)]
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        if status != "optimal":
            raise AssertionError((mode, status))
        level = -optimum if mode == "min" else optimum
        aeq.append([F(0), F(1)])
        beq.append(level)
        newly = []
        for role in sorted(free):
            slope, intercept = affine(role, endowments, width)
            objective = [F(-slope if mode == "min" else slope), F(0)]
            status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
            if status != "optimal":
                raise AssertionError((mode, role, status))
            extreme = (-optimum if mode == "min" else optimum) + intercept
            if extreme == weights[role] * level:
                newly.append(role)
        if not newly:
            raise AssertionError((mode, "stage pinned nobody", level))
        for role in newly:
            pinned[role] = weights[role] * level
            free.remove(role)
        trace.append({"level": str(level), "newly_pinned_roles": newly})
    return tuple(pinned[i] for i in range(4)), trace


def controls():
    inputs = (
        ((1, 1, 1, 2), (0, 0, 0, 2), 1),
        ((1, 2, 1, 2), (0, 0, 0, 2), 1),
        ((1, 2, 1, 3), (0, 2, 0, 0), 1),
        ((5, 1, 1, 1), (0, 0, 0, 0), 6),
        ((1, 6, 14, 12), (9, 6, 7, 3), 15),
        ((8, 3, 2, 5), (2, 4, 1, 7), 11),
        ((2, 7, 9, 4), (5, 0, 3, 6), 13),
        ((6, 41, 263, 23), (31, 9, 2, 6), 59),
    )
    rows = []
    for weights, endowments, width in inputs:
        expected_lmin, expected_lmax, matrix = selector_positions(
            weights, endowments, width
        )
        lmin, lmin_trace = exact_staged_selector(weights, endowments, width, "min")
        lmax, lmax_trace = exact_staged_selector(weights, endowments, width, "max")
        if lmin[0] - endowments[0] != expected_lmin:
            raise AssertionError((weights, "Lmin", lmin, expected_lmin))
        if lmax[0] - endowments[0] != expected_lmax:
            raise AssertionError((weights, "Lmax", lmax, expected_lmax))
        total = F(sum(endowments) + 2 * width)
        overlap = total - 2 * abs(expected_lmin - expected_lmax)
        rows.append(
            {
                "weights": list(weights),
                "endowments": list(endowments),
                "width": width,
                "crossing_matrix": {
                    f"{r}{f}": str(value) for (r, f), value in matrix.items()
                },
                "lmin": [str(value) for value in lmin],
                "lmax": [str(value) for value in lmax],
                "overlap_ratio": str(overlap / total),
                "atomic_target": str(atomic_target(sum(weights))),
                "lmin_trace": lmin_trace,
                "lmax_trace": lmax_trace,
            }
        )
    return rows


def bounded_grid():
    checked = 0
    rows = []
    for n in range(5, 21):
        target = atomic_target(n)
        minimum = None
        minimizer = None
        for h0 in range(1, n - 2):
            for h1 in range(1, n - h0 - 1):
                for h2 in range(1, n - h0 - h1):
                    weights = (h0, h1, h2, n - h0 - h1 - h2)
                    for endowments in product(range(4), repeat=4):
                        if any(
                            weights[i] == 1 and endowments[i] != 0
                            for i in range(4)
                        ):
                            continue
                        for width in range(1, 5):
                            lmin, lmax, _ = selector_positions(
                                weights, endowments, width
                            )
                            total = F(sum(endowments) + 2 * width)
                            ratio = (total - 2 * abs(lmin - lmax)) / total
                            checked += 1
                            if minimum is None or ratio < minimum:
                                minimum = ratio
                                minimizer = (weights, endowments, width)
                            if n >= 6 and ratio < target:
                                raise AssertionError(
                                    (n, weights, endowments, width, ratio, target)
                                )
        rows.append(
            {
                "n": n,
                "target": str(target),
                "minimum_ratio": str(minimum),
                "margin": str(minimum - target),
                "first_minimizer": {
                    "weights": list(minimizer[0]),
                    "endowments": list(minimizer[1]),
                    "width": minimizer[2],
                },
            }
        )
    return checked, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    checked, grid_rows = bounded_grid()
    report = {
        "status": "weighted endowed seesaw reduction audited exactly",
        "selector_theorem": (
            "Lmin=max over rising rows of their minimum crossing time; "
            "Lmax=max over falling columns of their minimum crossing time; "
            "after clipping these are the two middle order statistics"
        ),
        "independent_exact_staged_lp_controls": controls(),
        "bounded_grid": {
            "atomic_weight_range": "5..20",
            "endowment_coordinates": "0..3",
            "widths": "1..4",
            "cases_checked": checked,
            "rows": grid_rows,
        },
        "scope": (
            "the 2x2 selector reduction is a human theorem; the bounded grid is "
            "falsification evidence only and does not prove the general middle-gap target"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
