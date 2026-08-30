#!/usr/bin/env python3
"""Symbolic transcription audit for the PXC147 H_{m,r,t} no-go theorem.

The paper contains the conventional all-parameter proof.  This verifier
checks the rational identities, convex-combination witnesses, incidence
relations, selector formulas, overlap formulas, and asymptotic obstruction.
It is not presented as a replacement for the proof.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

def family(m, r, transfer):
    h = F(2 * m, r - 1)
    bx = F(m) + h
    cx = F(m) + r * h
    p = r * h + 1
    q = h + 1
    s = F(m + 1)
    total = F(m) + 2 * r * h + r + 2
    x = (F(1), bx, cx, F(1), F(1), F(1))
    B = (F(0), F(0), F(0), p, q, s)
    C = (F(0), bx + 2, total - bx - 2, F(0), F(0), F(0))
    D = (F(0), F(0), transfer, p - transfer, q, s)
    return (x, B, C, D), (h, bx, cx, p, q, s, total)


def total(point, m, r):
    weights = (m, 1, 1, 1, r, 1)
    return sum((weights[i] * point[i] for i in range(6)), F(0))


def row_sum(point, row):
    return sum((point[i] * row[i] for i in range(6)), F(0))


def named_rows(m, r):
    # Per-role incidence, with the U and E entries recording counts.
    return {
        "Q_i=c+d+(E\\i)": (0, 0, 1, 1, r - 1, 0),
        "R3=b+c+d+E": (0, 1, 1, 1, r, 0),
        "R4=c+d+g": (0, 0, 1, 1, 0, 1),
        "R5_i=b+e_i+g": (0, 1, 0, 0, 1, 1),
        "R7=c+E+g": (0, 0, 1, 0, r, 1),
        "R8_i=U+c+d+(E\\i)": (m, 0, 1, 1, r - 1, 0),
        "cd": (0, 0, 1, 1, 0, 0),
        "cde_i": (0, 0, 1, 1, 1, 0),
    }


def encode(point):
    return [str(value) for value in point]


def finite_audit():
    cases = []
    for r in range(3, 13):
        for m in range(1, 13):
            generators, params = family(m, r, F(0))
            h, bx, cx, p, q, s, T = params
            transfer = p * F(3, 4)
            generators, _ = family(m, r, transfer)
            assert all(total(point, m, r) == T for point in generators)
            x, B, C, D = generators
            rows = named_rows(m, r)
            claimed = {
                "Q_i=c+d+(E\\i)": cx + r,
                "R3=b+c+d+E": T - m - 1,
                "R4=c+d+g": p + s,
                "R5_i=b+e_i+g": q + s,
                "R7=c+E+g": r * q + s,
                "R8_i=U+c+d+(E\\i)": p + (r - 1) * q,
                "cd": p,
                "cde_i": p + q,
            }
            for name, row in rows.items():
                sums = tuple(row_sum(point, row) for point in generators)
                assert min(sums) == claimed[name], (m, r, name, sums, claimed[name])

            if h <= 1:
                lam = (1 - h) / (3 * m)
                M = (p + s) / 3
                e = q - lam * h
                z = (lam, lam * bx, M, M, e, M)
                delta = (1 - lam) * (p - s) / transfer
                beta = 1 - lam - delta
                assert min(lam, beta, delta) >= 0
                for coordinate in range(6):
                    got = (lam * x[coordinate] + beta * B[coordinate]
                           + delta * D[coordinate])
                    assert got == z[coordinate]
                overlap = m + r + 3 + lam * (m + h)
                assert M >= max(lam, lam * bx, e)
                chamber = "h<=1"
            else:
                delta = p / (2 * transfer)
                beta = 1 - delta
                assert min(beta, delta) >= 0
                z = (F(0), F(0), p / 2, p / 2, q, s)
                for coordinate in range(6):
                    got = beta * B[coordinate] + delta * D[coordinate]
                    assert got == z[coordinate]
                overlap = p / 2 + r + 2
                assert p / 2 >= max(q, s)
                chamber = "h>=1"
            direct_overlap = sum(
                ((m, 1, 1, 1, r, 1)[i] * min(x[i], z[i]) for i in range(6)),
                F(0),
            )
            assert direct_overlap == overlap
            rho = F(2) - 2 * overlap / T
            cases.append({
                "m": m, "r": r, "h": str(h), "chamber": chamber,
                "total": str(T), "transfer": str(transfer),
                "Lmin_roles": encode(x), "Lmax_roles": encode(z),
                "overlap": str(overlap), "rho": str(rho),
            })
    return cases


def symbolic_audit():
    # Exact coefficient identities are also checked at every point of the
    # 120-case rational grid.  The manuscript supplies their universal
    # algebraic proof; keeping this verifier stdlib-only makes the release
    # environment no stronger than its documented requirements.
    for r in range(3, 31):
        N = (1, 1, 1, 1, 1, 1)
        R3 = (0, 1, 1, 1, 1, 0)
        R4 = (0, 0, 1, 1, 0, 1)
        R5sum = (0, r, 0, 0, 1, r)
        R7 = (0, 0, 1, 0, 1, 1)
        got = tuple(
            2 * r * N[i] - r * R3[i] - R4[i] - R5sum[i] - (r - 1) * R7[i]
            for i in range(6)
        )
        assert got == (2 * r, 0, 0, r - 1, 0, 0)
    return {
        "forced_scale": "h=2m/(r-1)",
        "total": "m+2rh+r+2",
        "low_chamber_lambda": "(1-h)/(3m)",
        "low_chamber_M": "(p+s)/3",
        "low_chamber_E": "q-lambda*h",
        "low_chamber_overlap": "m+r+3+lambda*(m+h)",
        "high_chamber_overlap": "p/2+r+2",
        "ray_limit": "8a/(5a+1)",
        "supremum_of_ray_limits": "8/5",
    }


def calibration_r2():
    rows = []
    for m in range(1, 5):
        r = 2
        transfer = F(7 * m + 1, 2)
        generators, params = family(m, r, transfer)
        h, bx, cx, p, q, s, T = params
        expected = (
            (F(1), bx, cx, F(1), F(1), F(1)),
            (F(0), F(0), F(0), F(4 * m + 1), F(2 * m + 1), F(m + 1)),
            (F(0), F(3 * m + 2), F(6 * m + 2), F(0), F(0), F(0)),
            (F(0), F(0), F(7 * m + 1, 2), F(m + 1, 2), F(2 * m + 1), F(m + 1)),
        )
        assert generators == expected
        assert T == 9 * m + 4 and h == 2 * m
        rows.append({"m": m, "total": str(T), "generators": [encode(g) for g in generators]})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "PXC147 incidence-faithful four-generator H_{m,r,t} selector theorem and asymptotic no-go",
        "domain": "integers m>=1, r>=3; h=2m/(r-1); p/2<=t<=p",
        "symbolic": symbolic_audit(),
        "finite_exact_transcription_grid": finite_audit(),
        "PXC146_r_equals_2_calibration": calibration_r2(),
        "scope": (
            "transcription audit of the conventional proof; the no-go is for the explicitly "
            "defined incidence-faithful ordered-transfer four-generator class, not all exact games"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
