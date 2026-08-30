#!/usr/bin/env python3
"""Exact symbolic/transcription audit for the PXC151 two-block family."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import sympy as sp


ROLES = ("U", "b", "c", "d", "E", "g")


def dot(point, counts):
    return sum((point[i] * counts[i] for i in range(6)), F(0))


def enc(xs):
    return [str(x) for x in xs]


def family(m, r, bad=False):
    """Roles are U^m,b,c,d,E^r,g; bad undercuts H by one."""
    assert m >= 2 and r >= 3
    q = 2*m + 1
    y = m*(2*r - 1)
    T = 2*m*r + m + r + 1
    X = (F(1), F(m-1), F(y), F(1), F(1), F(1))
    B = (F(0), F(0), F(0), F(1 if bad else 0),
         F(q), F(m if bad else m+1))
    C = (F(0), F(m+1), F(r*q), F(0), F(0), F(0))
    mult = (m, 1, 1, 1, r, 1)
    assert all(dot(P, mult) == T and min(P) >= 0 for P in (X, B, C))
    assert all(min(P[i] for P in (X, B, C)) == 0 for i in range(6))
    return (X, B, C), mult, F(T)


def check_case(m, r):
    points, mult, T = family(m, r)
    X, B, C = points
    q = F(2*m+1)
    y = F(m*(2*r-1))
    H = F(2*m*r-m+r)
    R = F(r*(2*m+1))
    rows = {
        "N_minus_U": ((0, 1, 1, 1, r, 1), T-m),
        "R3_bcdE": ((0, 1, 1, 1, r, 0), R),
        "bdg": ((0, 1, 0, 1, 0, 1), F(m+1)),
        "R5_beg": ((0, 1, 0, 0, 1, 1), F(m+1)),
        "H_cEminusg": ((0, 0, 1, 0, r-1, 1), H),
        "Ubg": ((1, 1, 0, 0, 0, 1), F(m+1)),
        "UcE": ((m, 0, 1, 0, r, 0), R),
        "Uminus_cdE": ((m-1, 0, 1, 1, r, 0), R),
    }
    row_audit = {}
    for name, (counts, value) in rows.items():
        sums = tuple(dot(P, counts) for P in points)
        assert min(sums) == value and value in sums, (m, r, name, sums, value)
        row_audit[name] = {"value": str(value), "generator_sums": enc(sums)}

    # The hand Lmin chain after the N\U floor cap.
    assert T - rows["N_minus_U"][1] == m
    assert T - rows["R3_bcdE"][1] == m+1
    assert rows["bdg"][1] - 1 == m
    assert rows["R5_beg"][1] - 1 == m
    upper_bde = (T-m-1) - (H-1)
    assert upper_bde == m+1
    # b+d>=m, b+e>=m, b+d+e<=m+1, d,e>=1 force b=m-1.
    assert 2*m - (m+1) == m-1
    assert upper_bde - 2 == m-1
    assert H-r == y

    lam = F(2*m+1, m*(2*r+1))
    Z = tuple(lam*X[i] + (1-lam)*B[i] for i in range(6))
    M = lam*y
    assert Z[2] == Z[4] == M == max(Z)
    assert M-Z[5] == F(2*m*r-m-1, 2*r+1) > 0
    assert M-Z[1] == lam*F(2*m*(r-1)+1) > 0
    assert M-Z[0] == lam*F(m*(2*r-1)-1) > 0
    assert Z == (
        lam, lam*(m-1), M, lam, M,
        lam+(1-lam)*(m+1),
    )

    # Reduced symmetric minimax dual. Equal weight eta goes on H_i, R3,
    # and U^m cE. Its incidence is eta*efficiency plus excess on c,E.
    eta = F(1, 2*r+1)
    alpha_c, alpha_E = 2*eta, (2*r-1)*eta
    assert alpha_c + alpha_E == 1
    loads = (eta*m, eta, 3*eta, eta, (3*r-1)*eta, eta)
    assert loads == (eta*m, eta, eta+alpha_c, eta,
                     eta*r+alpha_E, eta)
    dual = eta*(H+R+R-T)
    assert dual == M

    # Equality in the dual plus four tight rows uniquely recovers Z.
    fixed_g = H-r*M
    fixed_U = (R-(r+1)*M)/m
    fixed_b = F(m+1)-fixed_U-fixed_g
    fixed_d = F(m+1)-fixed_b-fixed_g
    assert (fixed_U, fixed_b, fixed_d, fixed_g) == (Z[0], Z[1], Z[3], Z[5])
    # U_j b g gives U_j>=d after the dual equalities; the U\j c d E row
    # gives d>=U_j. Thus all U_j=d, and their fixed sum pins both at lambda.
    assert rows["Ubg"][1]-fixed_b-fixed_g == fixed_d
    assert rows["Uminus_cdE"][1]-(m-1)*fixed_U-(r+1)*M == fixed_d

    overlap = sum((F(mult[i])*min(X[i], Z[i]) for i in range(6)), F(0))
    assert overlap == 2*m+r+2
    rho = F(2)-2*overlap/T
    closed = F(2*(2*m*r-m-1), 2*m*r+m+r+1)
    assert rho == closed
    n = m+r+4
    benchmark = F(2)-F(8*n, n*n-(n % 2))
    return {
        "m": m, "r": r, "n": n, "total": str(T),
        "generators": [enc(P) for P in points],
        "Lmin_roles": enc(X), "Lmax_roles": enc(Z),
        "lambda": str(lam), "ceiling": str(M),
        "overlap": str(overlap), "rho": str(rho),
        "balanced_G_benchmark": str(benchmark),
        "benchmark_margin": str(rho-benchmark),
        "tight_rows": row_audit,
        "minimax_dual": {
            "common_weight": str(eta),
            "support": ["H_i", "R3", "U^m cE"],
            "alpha_c": str(alpha_c), "alpha_E": str(alpha_E),
            "objective": str(dual),
        },
    }


def symbolic_audit():
    m, r, a, k = sp.symbols("m r a k", positive=True)
    T = 2*m*r+m+r+1
    O = 2*m+r+2
    n = m+r+4
    rho = sp.factor(2-2*O/T)
    assert sp.simplify(rho-2*(2*m*r-m-1)/(2*m*r+m+r+1)) == 0
    C = sp.factor(sp.limit((n*(2-rho)).subs(m, a*r), r, sp.oo))
    assert C == (a+1)*(2*a+1)/a
    diagonal_rho = sp.factor(rho.subs({m: k, r: k}))
    diagonal_benchmark = 2-4/(k+2)
    diagonal_margin = sp.factor(diagonal_rho-diagonal_benchmark)
    expected_margin = 2*(k**2-4*k-2)/((k+2)*(2*k**2+2*k+1))
    assert sp.simplify(diagonal_margin-expected_margin) == 0
    # k^2-4k-2 is negative through k=4 and strictly increasing thereafter.
    assert all((j*j-4*j-2 < 0) for j in range(2, 5))
    assert 5*5-4*5-2 > 0
    # C(a)-(3+2sqrt(2)) = (sqrt(2)*a-1)^2/a.
    minimum_gap = sp.factor(C-(3+2*sp.sqrt(2)))
    assert sp.simplify(minimum_gap-(sp.sqrt(2)*a-1)**2/a) == 0
    even_delta = sp.factor(4*n*T-O*n**2)
    odd_delta = sp.factor(4*n*T-O*(n**2-1))
    return {
        "rho": str(rho), "ray_coefficient_C_a": str(C),
        "minimum_C": "3+2*sqrt(2) at a=1/sqrt(2)",
        "diagonal_rho": str(diagonal_rho),
        "diagonal_benchmark_margin": str(diagonal_margin),
        "diagonal_beats_exactly_from": "k>=5",
        "even_benchmark_delta": str(even_delta),
        "odd_benchmark_delta": str(odd_delta),
    }


def pxc146_boundary():
    out = []
    for m in range(1, 9):
        T = F(9*m+4)
        rho = F(14*(5*m-1), 5*(9*m+4))
        overlap = F(10*m+27, 5)
        assert rho == F(2)-2*overlap/T
        out.append({"m": m, "n": m+6, "total": str(T),
                    "rho": str(rho), "overlap": str(overlap)})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [check_case(m, r) for m in range(2, 13) for r in range(3, 13)]
    assert all(case["benchmark_margin"].startswith("-") for case in cases
               if case["m"] == case["r"] and case["m"] <= 4)
    assert all(not case["benchmark_margin"].startswith("-")
               for case in cases if case["m"] == case["r"] and case["m"] >= 5)

    # Load-bearing fail-open control: move one unit in B from g to d. This
    # preserves efficiency but undercuts H by one; the independent verifier
    # recomputes a different Lmin.
    m, r = 5, 5
    good, _, _ = family(m, r)
    bad, _, _ = family(m, r, bad=True)
    Hrow = (0, 0, 1, 0, r-1, 1)
    assert dot(good[0], Hrow)-dot(bad[1], Hrow) == 1
    payload = {
        "claim": "PXC151 infinite exact two-block family beats the balanced G benchmark",
        "domain": "integers m>=2, r>=3; define the r=2 boundary as the existing PXC146 H_m family",
        "symbolic": symbolic_audit(),
        "construction": {
            "roles": list(ROLES),
            "T": "2*m*r+m+r+1",
            "Lmin": "(1^m;m-1,m(2r-1);1,1^r,1)",
            "Lmax": "lambda*X+(1-lambda)*B, lambda=(2m+1)/(m(2r+1))",
            "overlap": "2m+r+2",
        },
        "PXC146_r_equals_2_boundary_calibration": pxc146_boundary(),
        "cases": cases,
        "negative_control": {"m": m, "r": r,
                             "B_moves_one_unit_g_to_d": True,
                             "H_undercut_by": "1"},
        "scope": "conventional-proof transcription; external correctness and prior-art review pending",
    }
    text = json.dumps(payload, indent=2)+"\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
