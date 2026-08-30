#!/usr/bin/env python3
"""Exact transcription audit for the PXC149 split-block bottleneck."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def enc(xs):
    return [str(x) for x in xs]


def dot(point, counts):
    return sum((point[i] * counts[i] for i in range(len(point))), F(0))


def split_bound(m, u, v):
    xb = F(m * (u * v - 1), (u - 1) * (v - 1))
    xc = xb + 2 * m
    # Sharp c-zero singleton witness, roles U,b,c,d,A,B,g.
    w = (F(0), F(0), F(0), xb + m + 1,
         1 + F(m, u - 1), 1 + F(m, v - 1), F(m + 1))
    T = F(m) + xb + xc + u + v + 2
    assert dot(w, (m, 1, 1, 1, u, v, 1)) == T
    U, b, c, d, A, B, g = w
    got = (b + c + d + u*A + v*B, c + d + g,
           c + u*A + v*B + g, b + A + v*B, b + u*A + B)
    want = (xb + xc + u + v + 1, xc + 2, xc + u + v + 1,
            xb + v + 1, xb + u + 1)
    assert got == want
    return {"m": m, "u": u, "v": v, "Xb_bound": str(xb),
            "Xc_bound": str(xc), "sharp_c_zero_witness": enc(w)}


def family(m, k):
    xb = F(m * (k + 1), k - 1)
    xc = F(m * (3*k - 1), k - 1)
    D = F(2*k*m, k - 1) + 1
    q, s = 1 + F(m, k - 1), F(m + 1)
    L = xc + 2*k + 1
    T = F(m) + xb + xc + 2*k + 2
    X = (F(1), xb, xc, F(1), F(1), F(1), F(1))
    B = (F(0), F(0), F(0), D, q, q, s)
    C = (F(0), D, L, F(0), F(0), F(0), F(0))
    mult = (m, 1, 1, 1, k, k, 1)
    assert all(dot(P, mult) == T for P in (X, B, C))
    return (X, B, C), (xb, xc, D, q, s, L, T)


def balanced_case(m, k):
    points, p = family(m, k)
    X, B, C = points
    xb, xc, D, q, s, L, T = p
    rows = {
        "R3": (0, 1, 1, 1, k, k, 0),
        "R4": (0, 0, 1, 1, 0, 0, 1),
        "R7": (0, 0, 1, 0, k, k, 1),
        "FA": (0, 1, 0, 0, 1, k, 0),
        "FB": (0, 1, 0, 0, k, 1, 0),
        "MA": (0, 0, 1, 1, k-1, 0, 0),
        "MB": (0, 0, 1, 1, 0, k-1, 0),
    }
    values = {}
    for name, row in rows.items():
        sums = tuple(dot(P, row) for P in points)
        assert sums[0] == min(sums), (m, k, name, sums)
        values[name] = str(sums[0])

    lam = F(D, m + xb + xc)
    Z = tuple(lam*X[i] + (1-lam)*B[i] for i in range(7))
    M = lam*xc
    assert Z[2] == Z[3] == M and max(Z) == M

    # Symmetry-averaged minimax dual: cdg; all cd(A\i), cd(B\j); Ubd.
    eta = F(k-1, 5*k-1)
    missing = F(1, 5*k-1)
    ac, ad = F(2*k, 5*k-1), F(3*k-1, 5*k-1)
    assert ac + ad == 1
    loads = (eta, eta, eta + 2*k*missing,
             2*eta + 2*k*missing, (k-1)*missing,
             (k-1)*missing, eta)
    assert loads == (eta, eta, eta+ac, eta+ad, eta, eta, eta)
    dual = eta*(xc+2) + 2*k*missing*(xc+k) + eta*D - eta*T
    assert dual == M

    mult = (m, 1, 1, 1, k, k, 1)
    O = sum((mult[i]*min(X[i], Z[i]) for i in range(7)), F(0))
    assert O == lam*(m+xb+xc) + 2*k + 2
    rho = F(2) - 2*O/T
    closed = F(2*(3*k*m-k-m+1), 2*k*k+5*k*m-m-2)
    assert rho == closed
    return {"m": m, "k": k, "n": m+2*k+4, "total": str(T),
            "Lmin_roles": enc(X), "Lmax_roles": enc(Z),
            "lambda": str(lam), "ceiling": str(M), "overlap": str(O),
            "rho": str(rho), "tight_rows": values,
            "dual": {"eta": str(eta), "per_missing_row": str(missing),
                     "alpha_c": str(ac), "alpha_d": str(ad)}}


def pxc146_boundary():
    out = []
    for m in range(1, 5):
        G = (
            (F(1), F(3*m), F(5*m), F(1), F(1), F(1), F(1)),
            (F(0), F(0), F(0), F(4*m+1), F(2*m+1), F(2*m+1), F(m+1)),
            (F(0), F(3*m+2), F(6*m+2), F(0), F(0), F(0), F(0)),
            (F(0), F(0), F(7*m+1, 2), F(m+1, 2),
             F(2*m+1), F(2*m+1), F(m+1)),
        )
        assert all(dot(P, (m, 1, 1, 1, 1, 1, 1)) == 9*m+4 for P in G)
        out.append({"m": m, "n": m+6, "total": 9*m+4,
                    "generators": [enc(P) for P in G]})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    bounds = [split_bound(m, u, v) for m in range(1, 13)
              for u in range(2, 7) for v in range(2, 7)]
    cases = [balanced_case(m, k) for k in range(2, 13)
             for m in range(k, 13)]
    # Fail-open control: m=k-1 makes C undercut F by exactly one.
    k, m = 5, 4
    points, p = family(m, k)
    Frow = (0, 1, 0, 0, 1, k, 0)
    gap = dot(points[0], Frow) - dot(points[2], Frow)
    assert gap == 1
    payload = {
        "claim": "PXC149 split-block singleton-witness bottleneck and balanced sharp-family no-go",
        "universal_bounds": {
            "Xb": "m*(u*v-1)/((u-1)*(v-1))",
            "Xc": "Xb+2*m",
            "scope": "singleton-normalized exact games with the displayed R3/R4/R7/FA/FB X-tight skeleton",
        },
        "balanced_family": {
            "domain": "integers k>=2, m>=k",
            "lambda": "(2*k*m+k-1)/(m*(5*k-1))",
            "rho": "2*(3*k*m-k-m+1)/(2*k^2+5*k*m-m-2)",
            "ray_limit_m_over_k_to_a": "6*a/(5*a+2) < 6/5",
        },
        "sharp_bound_grid": bounds,
        "balanced_exact_grid": cases,
        "PXC146_r_equals_2_calibration": pxc146_boundary(),
        "negative_control": {"m": m, "k": k, "C_undercuts_F_by": str(gap)},
        "scope": "conventional-proof transcription; not all multi-row or nonsymmetric mechanisms",
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
