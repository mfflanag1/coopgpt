#!/usr/bin/env python3
"""Exact transcription audit for the PXC150 pair-menu family."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import sympy as sp


def dot(point, counts):
    return sum((point[i] * counts[i] for i in range(len(point))), F(0))


def enc(xs):
    return [str(x) for x in xs]


def family(m, k):
    assert m >= 1 and k >= 2
    x = F(m * (2*k - 1), 2*(k - 1))
    y = F(m * k, k - 1)
    q = 1 + F(m, 2*(k - 1))
    T = F(m) + x + y + 2*k + 2
    X = (F(1), x, y, F(1), F(1), F(1), F(1))
    B = (F(0), F(0), F(0), x + 1, q, q, F(m + 1))
    G = (F(0), x + 2, F(m) + y + 2*k,
         F(0), F(0), F(0), F(0))
    mult = (m, 1, 1, 1, k, k, 1)
    assert all(dot(P, mult) == T for P in (X, B, G))
    assert all(min(P[i] for P in (X, B, G)) == 0 for i in range(7))
    return (X, B, G), (x, y, q, T)


def check_case(m, k):
    points, (x, y, q, T) = family(m, k)
    X, B, G = points
    rows = {
        "Pij": (0, 1, 1, 1, 1, 1, 1),
        "Hij": (0, 0, 1, 0, 1, 1, 1),
        "R3": (0, 1, 1, 1, k, k, 0),
        "R5A": (0, 1, 0, 0, 1, 0, 1),
        "R5B": (0, 1, 0, 0, 0, 1, 1),
    }
    expected = {
        "Pij": x + y + 4,
        "Hij": y + 3,
        "R3": x + y + 2*k + 1,
        "R5A": x + 2,
        "R5B": x + 2,
    }
    row_values = {}
    for name, row in rows.items():
        sums = tuple(dot(P, row) for P in points)
        assert min(sums) == expected[name] == sums[0], (name, sums)
        row_values[name] = {"value": str(expected[name]),
                            "generator_sums": enc(sums)}

    lam = F(x + 1, x + y)
    Z = tuple(lam*X[i] + (1-lam)*B[i] for i in range(7))
    M = lam*y
    assert Z[2] == Z[3] == M == max(Z)

    # Symmetry-averaged minimax dual.  There are 2k loser players e.
    eta = F(1, 4*k - 1)
    per_cde = F(2*k - 1, 2*k*(4*k - 1))
    per_Ucdeg = F(1, 2*k*(4*k - 1))
    alpha_c = F(2*k - 1, 4*k - 1)
    alpha_d = F(2*k, 4*k - 1)
    assert alpha_c + alpha_d == 1
    # Loads on each individual role U,b,c,d,e,g.
    loads = (2*k*per_Ucdeg, eta,
             2*k*(per_cde + per_Ucdeg),
             eta + 2*k*(per_cde + per_Ucdeg),
             per_cde + per_Ucdeg, 2*k*per_Ucdeg)
    assert loads == (eta, eta, eta + alpha_c, eta + alpha_d,
                     eta, eta)
    v_bd, v_cde, v_Ucdeg = x + 1, y + 2, F(m) + y + 3
    dual = (eta*v_bd + 2*k*per_cde*v_cde
            + 2*k*per_Ucdeg*v_Ucdeg - eta*T)
    assert dual == M

    # Equality in the positive dual rows fixes b and every loser once c=d=M.
    fixed_b = v_bd - M
    fixed_e = v_cde - 2*M
    assert fixed_b == Z[1] and fixed_e == Z[4] == Z[5]
    # The tight beg row supplies the remaining lower bound on g; efficiency
    # then fixes U.  Its value is shared by all three generators.
    beg = (0, 1, 0, 0, 1, 0, 1)
    beg_sums = tuple(dot(P, beg) for P in points)
    assert beg_sums == (x + 2, x + 2, x + 2)
    fixed_g = x + 2 - fixed_b - fixed_e
    assert fixed_g == Z[6] and fixed_g > Z[0]
    assert dot(Z, (m, 1, 1, 1, k, k, 1)) == T

    overlap = (m*Z[0] + Z[1] + Z[2] + 2*k + 2)
    direct_overlap = sum((F(n)*min(X[i], Z[i])
                          for i, n in enumerate((m, 1, 1, 1, k, k, 1))), F(0))
    assert overlap == direct_overlap == lam*(m + x + y) + 2*k + 2
    rho = F(2) - 2*overlap/T
    return {
        "m": m, "k": k, "n": m + 2*k + 4, "total": str(T),
        "generators": [enc(P) for P in points],
        "Lmin_roles": enc(X), "Lmax_roles": enc(Z),
        "lambda": str(lam), "ceiling": str(M),
        "overlap": str(overlap), "rho": str(rho),
        "tight_rows": row_values,
        "minimax_dual": {
            "eta_bd": str(eta), "per_cde": str(per_cde),
            "per_Ucdeg": str(per_Ucdeg),
            "alpha_c": str(alpha_c), "alpha_d": str(alpha_d),
            "objective": str(dual),
        },
    }


def symbolic_audit():
    m, k = sp.symbols("m k", positive=True)
    x = m*(2*k - 1)/(2*(k - 1))
    y = m*k/(k - 1)
    T = m + x + y + 2*k + 2
    lam = (x + 1)/(x + y)
    M = lam*y
    O = lam*(m + x + y) + 2*k + 2
    rho = sp.factor(2 - 2*O/T)
    a = sp.symbols("a", positive=True)
    ray = sp.simplify(sp.limit(rho.subs(m, a*k), k, sp.oo))
    assert ray == 3*a/(3*a + 2)
    assert sp.simplify(M - (lam + (1-lam)*(x+1))) == 0
    return {
        "x": str(sp.factor(x)), "y": str(sp.factor(y)),
        "lambda": str(sp.factor(lam)), "ceiling": str(sp.factor(M)),
        "overlap": str(sp.factor(O)), "rho": str(rho),
        "ray_limit_m_over_k_to_a": str(ray),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [check_case(m, k) for k in range(2, 11) for m in range(1, 13)]
    # Load-bearing negative control: decreasing the G-coordinate at b by one
    # and preserving efficiency undercuts every beg row by exactly one.
    m, k = 4, 3
    points, (x, y, q, T) = family(m, k)
    Gbad = (F(0), x + 1, F(m) + y + 2*k + 1,
            F(0), F(0), F(0), F(0))
    beg = (0, 1, 0, 0, 1, 0, 1)
    gap = dot(points[0], beg) - dot(Gbad, beg)
    assert gap == 1 and dot(Gbad, (m, 1, 1, 1, k, k, 1)) == T
    payload = {
        "claim": "PXC150 exact three-generator realization of the complete pair-menu skeleton",
        "domain": "integers m>=1, k>=2; define the r=2 boundary separately as H_m",
        "symbolic": symbolic_audit(),
        "cases": cases,
        "negative_control": {"m": m, "k": k,
                             "G_b_decreased_by_one": True,
                             "beg_undercut_by": str(gap)},
        "scope": "conventional-proof transcription; not an upper bound for arbitrary exact games",
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
