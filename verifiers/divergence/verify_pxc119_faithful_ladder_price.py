#!/usr/bin/env python3
"""Exact algebraic audit for the PXC119 faithful-ladder price theorem.

The proof in the paper is symbolic.  This verifier checks its two polynomial
identities, the parity reduction to the hybrid constant, the named faithful
spectral-deficit control, the equality branch point, and a fail-open point
obtained by deleting the Lmax top-order inequality.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

from verify_labelled_branch_duals import CASES  # noqa: E402


def target(n: int) -> F:
    return F(n, (n * n) // 4)


def denominator(n: int, s: int) -> F:
    g = n - s - 2
    if not (n >= 6 and s >= 2 and g >= 1):
        raise ValueError((n, s, g))
    return F(n + 1) + F(2 * (s - 1), g)


def ladder_profile(n: int, s: int, *, A, B, C, Dtop, m, ell, p, q, T):
    """Check the two common-row equations and return the price identity."""
    g = n - s - 2
    values = tuple(map(F, (A, B, C, Dtop, m, ell, p, q, T)))
    A, B, C, Dtop, m, ell, p, q, T = values
    if s * A + g * B + C + Dtop != T:
        raise AssertionError("x efficiency")
    if 2 * m + g * ell + p + (s - 1) * q != T:
        raise AssertionError("z efficiency")
    if C + Dtop + A != 2 * m + p:
        raise AssertionError("large common row")
    if 2 * A != p + q:
        raise AssertionError("small common row")
    delta = A - q
    D = denominator(n, s)
    overlap = 2 * m + g * B + A + (s - 1) * q
    slack = 2 * (m - ell) + (g + 2) * (B - A) + n * q
    if T - D * delta != slack:
        raise AssertionError(("price identity", T - D * delta, slack))
    if overlap - (1 - F(s, 1) / D) * T != F(s, 1) / D * slack:
        raise AssertionError("overlap slack identity")
    return {
        "delta": delta,
        "denominator": D,
        "overlap": overlap,
        "slack": slack,
        "bound": (1 - F(s, 1) / D) * T,
    }


def parity_certificate(n: int, s: int):
    """Return the exact cleared numerator for ladder bound minus c_n."""
    g = n - s - 2
    floor = (n * n) // 4
    # D=[g(n-1)+2(n-3)]/g.  Cross multiplication gives this numerator.
    cleared = (
        (floor - n) * (g * (n - 1) + 2 * (n - 3))
        - floor * g * (n - g - 2)
    )
    D = denominator(n, s)
    margin = 1 - F(s, 1) / D - target(n)
    expected = F(cleared, floor * (g * (n - 1) + 2 * (n - 3)))
    if margin != expected or cleared < 0:
        raise AssertionError((n, s, margin, expected, cleared))
    return cleared, margin


def actual_control():
    case = next(q for q in CASES if q["name"] == "actual_top_fixed_failure")
    x, z = tuple(case["x"]), tuple(case["z"])
    # Labels: u=0,v=2, G={1,3}, c=4, Q={5,6}.
    result = ladder_profile(
        7, 3,
        A=x[4], B=x[1], C=x[0], Dtop=x[2],
        m=z[0], ell=z[1], p=z[4], q=z[5], T=sum(x, F(0)),
    )
    if result["bound"] != F(7, 10) * sum(x, F(0)):
        raise AssertionError("actual-control bound changed")
    if result["overlap"] != sum((min(a, b) for a, b in zip(x, z)), F(0)):
        raise AssertionError("actual-control overlap labels changed")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    margins = []
    for n in range(6, 257):
        for s in range(2, n - 2):
            cleared, margin = parity_certificate(n, s)
            margins.append((n, s, cleared, margin))

    control = actual_control()
    # The normalized branch minimizer from verify_labelled_branch_duals.
    equality = ladder_profile(
        7, 3, A=F(1, 10), B=F(1, 10), C=F(1, 4), Dtop=F(1, 4),
        m=F(1, 5), ell=F(1, 5), p=F(1, 5), q=F(0), T=F(1),
    )
    if equality["overlap"] != F(7, 10) or equality["slack"] != 0:
        raise AssertionError("faithful ladder equality control changed")

    # Delete m>=ell.  The two common equations and all x-side orders remain,
    # but the overlap falls below the seven-player target.
    fail_open = ladder_profile(
        7, 3, A=F(1, 7), B=F(1, 7), C=F(1, 7), Dtop=F(1, 7),
        m=F(1, 14), ell=F(2, 7), p=F(2, 7), q=F(0), T=F(1),
    )
    if not (fail_open["overlap"] == F(4, 7) < target(7)
            and fail_open["slack"] < 0):
        raise AssertionError("fail-open top-order control closed")

    payload = {
        "claim": "PXC119 dimension-free two-top labelled-ladder price theorem",
        "formula": {
            "D": "n+1+2(s-1)/g",
            "overlap_identity": (
                "O-(1-s/D)T=(s/D)[2(m-ell)+(g+2)(B-A)+nq]"
            ),
            "hybrid_bound": "1-s/D >= n/floor(n^2/4) for n>=6",
        },
        "actual_top_fixed_control": {key: str(value) for key, value in control.items()},
        "equality_control": {key: str(value) for key, value in equality.items()},
        "fail_open_without_m_ge_ell": {
            key: str(value) for key, value in fail_open.items()
        },
        "finite_parity_regression": {
            "n_min": 6,
            "n_max": 256,
            "cells": len(margins),
            "minimum_margin": str(min(q[3] for q in margins)),
            "zero_margin_cells": [[n, s] for n, s, _c, margin in margins if margin == 0],
        },
        "scope": (
            "the all-n assertion is the displayed human parity proof; the finite "
            "loop, named exact branch, equality point, and fail-open point are audits"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
