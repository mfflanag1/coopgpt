#!/usr/bin/env python3
"""Exact audit of the carrier-cycle direct-cardinality theorem.

The proof is the monotonic reduction and discriminant calculation recorded in
the paper.  The finite grid is an exact arithmetic regression, not the proof.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def target(n: int) -> F:
    return F(4 * n, n * n - (n % 2))


def base(p: int, g: int, h: int, s: int) -> F:
    return F(1) - F(g * p, (g + h) * (p + g - s))


def full_grid(max_n: int) -> tuple[int, list[dict[str, object]]]:
    checked = 0
    equalities = []
    for n in range(6, max_n + 1):
        for h in range(2, n - 1):
            for g in range(1, n - h):
                p = n - h - g
                for s in range(g):
                    checked += 1
                    value = base(p, g, h, s)
                    if value < target(n):
                        raise AssertionError((n, p, g, h, s, value, target(n)))
                    if value == target(n):
                        equalities.append(
                            {"n": n, "p": p, "g": g, "h": h, "s": s}
                        )
    return checked, equalities


def reduced_grid(max_n: int) -> int:
    checked = 0
    for n in range(6, max_n + 1):
        for p in range(1, n - 2):
            g = n - p - 2
            reduced = F(n + p, (n - p) * (p + 1))
            if reduced < target(n):
                raise AssertionError((n, p, reduced, target(n)))
            checked += 1
    return checked


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--full-max-n", type=int, default=60)
    parser.add_argument("--reduced-max-n", type=int, default=500)
    args = parser.parse_args()

    full_checks, equalities = full_grid(args.full_max_n)
    reduced_checks = reduced_grid(args.reduced_max_n)
    if equalities != [{"n": 6, "p": 2, "g": 2, "h": 2, "s": 1}]:
        raise AssertionError(equalities)

    even_discriminant_at_8 = -7 * 8**2 + 40 * 8 + 16
    odd_cubic_at_7 = 7 * 7**3 - 47 * 7**2 + 9 * 7 - 1
    if even_discriminant_at_8 >= 0 or odd_cubic_at_7 <= 0:
        raise AssertionError((even_discriminant_at_8, odd_cubic_at_7))

    report = {
        "status": "carrier-cycle proper-packet cardinality theorem audited exactly",
        "theorem": (
            "for n=p+g+h>=6, h>=2, p,g>=1, and 0<=s<g, "
            "1-gp/[(g+h)(p+g-s)] >= 4n/[n^2-(n mod 2)]"
        ),
        "monotone_worst_case": "s=g-1 and h=2",
        "reduced_base": "(n+p)/[(n-p)(p+1)]",
        "even_cross_product_quadratic": (
            "n[4p^2+(4-3n)p+n^2-4n], with discriminant "
            "-7n^2+40n+16<0 for even n>=8; n=6 checked directly"
        ),
        "odd_cross_product_quadratic": (
            "4np^2+(-3n^2+4n-1)p+n^3-4n^2-n, with discriminant "
            "-(n+1)(7n^3-47n^2+9n-1)<0 for odd n>=7"
        ),
        "full_parameter_rows_checked": full_checks,
        "full_parameter_n_range": [6, args.full_max_n],
        "reduced_worst_case_rows_checked": reduced_checks,
        "reduced_n_range": [6, args.reduced_max_n],
        "unique_equality_parameters": equalities,
        "scope": (
            "the displayed monotonicity and discriminant argument is the "
            "dimension-free proof; the exact grids are regression controls"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
