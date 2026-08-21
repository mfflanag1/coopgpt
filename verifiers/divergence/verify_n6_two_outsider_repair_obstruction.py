#!/usr/bin/env python3
"""Exact arithmetic audit of the n=6 obstruction to the PXC88 repair menu.

This proves only the stated incidence/comparison lemma.  It does not exclude
all six-player faithful-lift counterexamples.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


N = 6
R, H, A, B, J, K = range(N)
MATCHED = ((R, H, B, J), (R, H, A, K))
CROSSED = ((R, H, A, J), (R, H, B, K))


def load(rows, weights):
    return tuple(
        sum((weight for row, weight in zip(rows, weights) if i in row), F(0))
        for i in range(N)
    )


def normalized_cover(rows):
    weights = (F(1, 2), F(1, 2))
    eta = F(1, 2)
    alpha = (F(1, 2), F(1, 2))
    expected = tuple(
        eta + (alpha[0] if i == R else alpha[1] if i == H else F(0))
        for i in range(N)
    )
    actual = load(rows, weights)
    if actual != expected or sum(alpha, F(0)) != 1:
        raise AssertionError((rows, actual, expected))
    return {
        "rows": ["".join(str(i) for i in row) for row in rows],
        "weights": [str(q) for q in weights],
        "eta": str(eta),
        "alpha": [str(q) for q in alpha],
        "load": [str(q) for q in actual],
    }


def comparison_identity():
    # delta=z-x=(-ell, d_h,d_a,d_b,-L_j,-L_k), with
    # d_h+d_a+d_b=ell+L_j+L_k.  The two rows below contain all
    # gainers and one outsider, so their z-x gaps are strictly positive.
    # Coefficient-vector proof in variables (ell,d_h,d_a,d_b,L_j,L_k).
    balance = (-1, 1, 1, 1, -1, -1)
    gap_j = (0, 1, 1, 1, -1, 0)
    rhs_j = (1, 0, 0, 0, 0, 1)
    gap_k = (0, 1, 1, 1, 0, -1)
    rhs_k = (1, 0, 0, 0, 1, 0)
    if tuple(a - b for a, b in zip(gap_j, rhs_j)) != balance:
        raise AssertionError("j comparison identity failed symbolically")
    if tuple(a - b for a, b in zip(gap_k, rhs_k)) != balance:
        raise AssertionError("k comparison identity failed symbolically")
    samples = []
    for ell in range(1, 5):
        for loss_j in range(0, 5):
            for loss_k in range(0, 5):
                total_gain = ell + loss_j + loss_k
                for d_h in range(1, total_gain):
                    for d_a in range(1, total_gain - d_h):
                        d_b = total_gain - d_h - d_a
                        if d_b <= 0:
                            continue
                        delta = (-ell, d_h, d_a, d_b, -loss_j, -loss_k)
                        gap_j = sum(delta[i] for i in (H, A, B, J))
                        gap_k = sum(delta[i] for i in (H, A, B, K))
                        if gap_j != ell + loss_k or gap_k != ell + loss_j:
                            raise AssertionError((delta, gap_j, gap_k))
                        if gap_j <= 0 or gap_k <= 0:
                            raise AssertionError((gap_j, gap_k))
                        samples.append((delta, gap_j, gap_k))
    if not samples:
        raise AssertionError("comparison identity received no positive-gain tests")
    return {
        "balance_coefficients": list(balance),
        "identities": ["gap(HABj)=ell+L_k", "gap(HABk)=ell+L_j"],
        "positive_integer_controls": len(samples),
    }


def singleton_budget_identity():
    # If either Q_j={r,a,b,j} or Q_k={r,a,b,k} is z-tight, a core point
    # with y_r=0 is impossible.  The matched cover gives y_r+y_h>=2M.
    # The remaining budget is at most 2q+z_j+z_k, strictly below the
    # corresponding row bound M+2q+z_j (or M+2q+z_k).
    # Coefficients in (M,q,z_j,z_k).  The row bound minus the remaining
    # budget is M-z_k for Q_j and M-z_j for Q_k.
    row_j = (1, 2, 1, 0)
    row_k = (1, 2, 0, 1)
    remaining = (0, 2, 1, 1)
    if tuple(a - b for a, b in zip(row_j, remaining)) != (1, 0, 0, -1):
        raise AssertionError("Q_j budget identity failed symbolically")
    if tuple(a - b for a, b in zip(row_k, remaining)) != (1, 0, -1, 0):
        raise AssertionError("Q_k budget identity failed symbolically")
    samples = 0
    for M in range(2, 8):
        for q in range(1, M):
            for z_j in range(q):
                for z_k in range(q):
                    remaining = 2 * q + z_j + z_k
                    if not remaining < M + 2 * q + z_j:
                        raise AssertionError((M, q, z_j, z_k, "Q_j"))
                    if not remaining < M + 2 * q + z_k:
                        raise AssertionError((M, q, z_j, z_k, "Q_k"))
                    samples += 1
    return {
        "identities": [
            "z(Q_j)-(T-2M)=M-z_k",
            "z(Q_k)-(T-2M)=M-z_j",
        ],
        "strict_order_controls": samples,
    }


def direct_specialization():
    # At (n,g,h,p,s)=(6,3,2,1,2), the direct master identity has
    # base 1-gp/((g+h)(p+g-s))=7/10.  Its residual budget is
    # [-x(G)-3x_p-(M+z_u)+(8/5)(T-z_p)]/3.
    n, g, h, p, s = 6, 3, 2, 1, 2
    base = F(1) - F(g * p, (g + h) * (p + g - s))
    mu = F((g - 1) * n, g * (n - g))
    cardinality_slack = F(n, g * (n - g)) - F(2, 3)
    if base != F(7, 10) or mu != F(4, 3) or cardinality_slack:
        raise AssertionError((base, mu, cardinality_slack))
    # Coefficients of (xG,xp,M,zu,T,zp) after division by three.
    coefficients = tuple(q / 3 for q in (F(-1), F(-3), F(-1), F(-1), F(8, 5), F(-8, 5)))
    return {
        "sizes": {"n": n, "g": g, "h": h, "p": p, "s": s},
        "base": str(base),
        "reserve_mu": str(mu),
        "cardinality_slack": str(cardinality_slack),
        "budget_variables": ["xG", "xp", "M", "zu", "T", "zp"],
        "budget_coefficients": [str(q) for q in coefficients],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "exact n=6 two-outsider obstruction to the PXC88 zero-weight repair",
        "matched_cover": normalized_cover(MATCHED),
        "crossed_cover": normalized_cover(CROSSED),
        "comparison_identity_tests": comparison_identity(),
        "singleton_budget_tests": singleton_budget_identity(),
        "direct_specialization": direct_specialization(),
        "conclusion": (
            "with only two outsiders, the two opposite-omission repair rows "
            "either duplicate the matched cover or themselves form a positive "
            "normalized top cover; the two natural all-gainer repair rows are "
            "excluded respectively by x-feasibility and singleton normalization"
        ),
        "scope": (
            "rules out the literal PXC88 split-matching plus zero-cover repair "
            "mechanism at n=6; it is not a universal n=6 fidelity theorem"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
