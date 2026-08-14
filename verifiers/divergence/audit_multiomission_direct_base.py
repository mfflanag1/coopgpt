#!/usr/bin/env python3
r"""Exact arithmetic controls for the multi-omission direct-base lemma.

The dimension-free result is the human monotonicity and quadratic argument
recorded as (PXC57).  This driver checks the formulas, the complete n=6,7
exception list, the unique n>=8 equality cell in a wide exact regression,
and every admissible parameter cell through a configurable cutoff.  The
finite cutoff is a regression, not the proof of the all-n assertion.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402


def target(n: int) -> F:
    return F(4 * n, n * n - (n % 2))


def direct_base(n: int, g: int, h: int, s: int) -> F:
    p = n - g - h
    if not (g >= 2 and h >= 1 and p >= 1 and 0 <= s <= g - 2):
        raise ValueError("inadmissible multi-omission cell")
    return F(1) - F(g * p, (g + h) * (p + g - s))


def worst_base(n: int, g: int) -> F:
    """The h=1, s=g-2 endpoint after the two monotonicity reductions."""
    return F(n + g + 1, (g + 1) * (n - g + 1))


def cells(n: int):
    for g in range(2, n - 1):
        for h in range(1, n - g):
            p = n - g - h
            for s in range(g - 1):
                yield g, h, p, s, direct_base(n, g, h, s)


def hostile_upper_budget_control():
    """Show that PXC57's remaining upper-budget gate is genuinely necessary."""
    case = next(
        row for row in CASES if row["name"] == "primitive_coefficient_seven_failure"
    )
    x, z = tuple(case["x"]), tuple(case["z"])
    gainers = tuple(i for i in range(len(x)) if z[i] > x[i])
    nongainers = tuple(i for i in range(len(x)) if i not in gainers)
    root = 6
    rows = []
    for coalition in case["support_x"]:
        if not (coalition >> root & 1):
            continue
        j_set = tuple(i for i in gainers if coalition >> i & 1)
        if len(j_set) > len(gainers) - 2:
            continue
        h_set = tuple(i for i in nongainers if coalition >> i & 1)
        p_set = tuple(i for i in nongainers if not (coalition >> i & 1))
        certificate = master_identity(x, z, p_set, gainers, h_set, j_set)
        base = F(certificate["base_bound_ratio"])
        if base < target(len(x)):
            raise AssertionError("hostile multi-omission row lost its base bound")
        if certificate["packet_hits_interval"]:
            raise AssertionError("hostile upper-budget obstruction disappeared")
        rows.append(
            {
                "coalition": coalition,
                "base": str(base),
                "gainer_packet": certificate["gainer_packet"],
                "upper_budget": certificate["residual_budget"],
                "lower_comparison_slack": certificate["comparison_slack"],
                "upper_budget_holds": False,
            }
        )
    expected_coalitions = [70, 85, 90, 104, 204]
    if [row["coalition"] for row in rows] != expected_coalitions:
        raise AssertionError(("hostile multi-omission support changed", rows))
    return {
        "name": case["name"],
        "n": len(x),
        "root": root,
        "tight_multiomission_rows": rows,
        "interpretation": (
            "all five Lmin-tight multi-omission rows clear the PXC57 base and "
            "lower comparison sign but fail the upper labelled budget"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=64)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_n < 8:
        raise ValueError("the regression cutoff must be at least eight")

    low_failures = []
    for n in (6, 7):
        for g, h, p, s, base in cells(n):
            if base < target(n):
                low_failures.append(
                    {
                        "n": n,
                        "g": g,
                        "h": h,
                        "p": p,
                        "s": s,
                        "base": str(base),
                        "target": str(target(n)),
                    }
                )
    expected_low = [
        {"n": 6, "g": 2, "h": 1, "p": 3, "s": 0,
         "base": "3/5", "target": "2/3"},
        {"n": 6, "g": 3, "h": 1, "p": 2, "s": 1,
         "base": "5/8", "target": "2/3"},
        {"n": 7, "g": 2, "h": 1, "p": 4, "s": 0,
         "base": "5/9", "target": "7/12"},
        {"n": 7, "g": 3, "h": 1, "p": 3, "s": 1,
         "base": "11/20", "target": "7/12"},
    ]
    if low_failures != expected_low:
        raise AssertionError(("low-dimensional exception list changed", low_failures))

    checked_cells = 0
    equality_cells = []
    endpoint_checks = 0
    for n in range(8, args.max_n + 1):
        for g in range(2, n - 1):
            endpoint = worst_base(n, g)
            if endpoint != direct_base(n, g, 1, g - 2):
                raise AssertionError(("endpoint simplification failed", n, g))
            if endpoint < target(n):
                raise AssertionError(("endpoint violates PXC57", n, g, endpoint))
            if n % 2 == 0:
                k = n // 2
                cross = k * (2 * k + g + 1) - 2 * (g + 1) * (2 * k - g + 1)
                continuous_min = F((k - 4) * (7 * k + 4), 8)
            else:
                k = (n - 1) // 2
                cross = (
                    k * (k + 1) * (2 * k + g + 2)
                    - (2 * k + 1) * (g + 1) * (2 * k - g + 2)
                )
                t = k - 4
                continuous_min = F(
                    7 * t**4 + 102 * t**3 + 505 * t**2 + 898 * t + 239,
                    4 * (2 * k + 1),
                )
            if cross < continuous_min or continuous_min < 0:
                raise AssertionError(("quadratic minimum formula failed", n, g))
            endpoint_checks += 1
        for g, h, p, s, base in cells(n):
            checked_cells += 1
            endpoint = worst_base(n, g)
            if base < endpoint or base < target(n):
                raise AssertionError(
                    ("multi-omission cell violates PXC57", n, g, h, p, s, base)
                )
            if base == target(n):
                equality_cells.append(
                    {"n": n, "g": g, "h": h, "p": p, "s": s}
                )
    expected_equality = [{"n": 8, "g": 3, "h": 1, "p": 4, "s": 1}]
    if equality_cells != expected_equality:
        raise AssertionError(("PXC57 equality cells changed", equality_cells))

    report = {
        "status": "exact multi-omission direct-base controls verified",
        "human_theorem": (
            "for n>=8, every direct-gluing cardinality cell with g>=2, "
            "h>=1, p>=1, and s<=g-2 has base at least "
            "4n/[n^2-(n mod 2)]"
        ),
        "endpoint_formula": "(n+g+1)/[(g+1)(n-g+1)]",
        "monotonicity_reduction": (
            "the base is minimized first at h=1 and then at s=g-2"
        ),
        "all_n_proof": {
            "even_n_2k_continuous_min_numerator": "(k-4)(7k+4)/8",
            "odd_n_2k_plus_1_continuous_min_numerator": (
                "[7(k-4)^4+102(k-4)^3+505(k-4)^2+898(k-4)+239]"
                "/[4(2k+1)]"
            ),
        },
        "low_dimensional_failures": low_failures,
        "unique_regression_equality_cell": equality_cells,
        "hostile_upper_budget_control": hostile_upper_budget_control(),
        "regression": {
            "minimum_n": 8,
            "maximum_n": args.max_n,
            "endpoint_checks": endpoint_checks,
            "parameter_cells": checked_cells,
        },
        "scope": (
            "human algebra proves the all-n base bound; this does not prove "
            "the comparison interval or select a tight multi-omission row"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
