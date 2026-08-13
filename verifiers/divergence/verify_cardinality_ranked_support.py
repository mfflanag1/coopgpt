#!/usr/bin/env python3
"""Exact audit of the cardinality-ranked carrier-support identity.

For a fixed gainer set G and a nongainer block H of fixed size h, the
comparison--residual budget U_(g-1)-L_H is affine in the five block sums.
After simplification, the only H-dependent payoff sum is z(H), with strictly
positive coefficient n/(g+h).  Thus among any equal-cardinality family of
admissible blocks, maximizing the direct budget is exactly maximizing z(H).

The coefficient calculation is the dimension-free proof.  The finite grid
and seven-player control below are exact regression/falsification evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402


LMIN = (F(3), F(7, 2), F(1), F(3), F(2), F(7, 2), F(1))
LMAX = (F(14, 5), F(16, 5), F(2, 5), F(13, 5), F(16, 5), F(16, 5), F(8, 5))
GENERATORS = (
    (F(6), F(7), F(1), F(0), F(2), F(0), F(1)),
    (F(7), F(0), F(0), F(0), F(0), F(10), F(0)),
    (F(0), F(0), F(0), F(5), F(4), F(6), F(2)),
)


def source_coefficients(p, g, h):
    """Coefficients in the defining formula for U_(g-1)-L_H."""

    a = p - g + 1
    # Coordinate order: X_P, X_H, X_G, Z_H, Z_G.
    # high_z=(Z_G+Z_H)/(g+h).
    high_coefficient = F(g * (g - 1) - a * h, g * (g + h))
    return (
        F(-1),
        F(-1),
        F(a, g),
        F(a, g) + F(1) + high_coefficient,
        high_coefficient,
    )


def ranked_coefficients(p, g, h):
    n = p + g + h
    return (
        F(-1),
        F(-1),
        F(p - g + 1, g),
        F(n, g + h),
        F((g - 1) * (g + h) - h * p, g * (g + h)),
    )


def block_sum(point, players):
    return sum((point[i] for i in players), F())


def control_rows():
    values = tuple(
        min(coalition_sum(row, coalition) for row in GENERATORS)
        for coalition in range(1 << 7)
    )
    tight = full_tight_support(values, LMIN)
    gainers = (4, 6)
    nongainers = (0, 1, 2, 3, 5)
    cycle = {1, 5}
    rows = []
    for coalition in tight:
        h_set = tuple(i for i in nongainers if coalition >> i & 1)
        if not cycle <= set(h_set) or len(h_set) == len(nongainers):
            continue
        p_set = tuple(i for i in nongainers if i not in h_set)
        row = master_identity(LMIN, LMAX, p_set, gainers, h_set, gainers[:-1])
        rows.append(
            {
                "coalition": coalition,
                "H": list(h_set),
                "h": len(h_set),
                "z_H": str(block_sum(LMAX, h_set)),
                "budget_margin": row["normalized_budget_margin"],
                "closes": row["budget_closes_direct"],
            }
        )
    rows.sort(key=lambda row: (row["h"], F(row["z_H"]), row["coalition"]))

    # Equal-cardinality ordering must agree exactly with z(H) ordering.
    for left in rows:
        for right in rows:
            if left["h"] != right["h"]:
                continue
            z_order = F(left["z_H"]) <= F(right["z_H"])
            budget_order = F(left["budget_margin"]) <= F(right["budget_margin"])
            if z_order != budget_order:
                raise AssertionError(("rank ordering mismatch", left, right))
    if [row["coalition"] for row in rows if row["closes"]] != [59, 123]:
        raise AssertionError(("unexpected closing controls", rows))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    checked = 0
    for n in range(3, 101):
        for p in range(1, n - 1):
            for g in range(1, n - p):
                h = n - p - g
                if source_coefficients(p, g, h) != ranked_coefficients(p, g, h):
                    raise AssertionError(("coefficient identity failure", p, g, h))
                if ranked_coefficients(p, g, h)[3] <= 0:
                    raise AssertionError("z(H) coefficient is not positive")
                checked += 1

    report = {
        "status": "cardinality-ranked carrier-support identity verified exactly",
        "theorem": (
            "for L=N\\G, H subset L, P=L\\H, |P|=p, |G|=g, "
            "|H|=h, and n=p+g+h, the maximal-proper-packet budget is "
            "U_(g-1)-L_H = n z(H)/(g+h) - x(L) + "
            "(p-g+1)x(G)/g + "
            "[(g-1)(g+h)-hp]z(G)/[g(g+h)]"
        ),
        "consequence": (
            "within every fixed-cardinality admissible support family, a "
            "block maximizes the direct budget if and only if it maximizes z(H)"
        ),
        "coefficient_rows_checked": checked,
        "parameter_range": "all positive p,g,h with 3<=p+g+h<=100",
        "n7_rbb_counterexample_tight_support_rows": control_rows(),
        "scope": (
            "the coefficient simplification is the dimension-free proof; "
            "the finite parameter grid and n=7 tight-support ordering are "
            "regression controls and do not prove existence of an admissible "
            "support at the required threshold"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
