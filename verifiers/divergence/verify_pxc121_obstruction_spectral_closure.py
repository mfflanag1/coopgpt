#!/usr/bin/env python3
"""Primary exact audit of the PXC121 zero-demand obstruction families."""
from __future__ import annotations

import json
import argparse
from pathlib import Path
from fractions import Fraction as F
import sympy as sp


def target_coefficient(n: int) -> F:
    return F(n, (n * n) // 4)


def opposite_residual(x, z, top):
    xs = sorted(x[i] for i in range(len(x)) if i not in top)
    zs = sorted((z[i] for i in range(len(z)) if i not in top), reverse=True)
    return sum((min(a, b) for a, b in zip(xs, zs)), F(0))


def actual_top_bound(x, z):
    maximum = max(z)
    top = {i for i, q in enumerate(z) if q == maximum}
    return sum((min(x[i], maximum) for i in top), F(0)) + opposite_residual(x, z, top)


def symbolic_checks():
    k = sp.symbols("k", integer=True, positive=True)
    M, q, J, K, mu = sp.symbols("M q J K mu")
    u = (q + J + (k - 1) * K) / (k + 1)
    T = 2 * M + 2 * q + J + (k - 1) * K
    p = (T - (k + 2) * u) / 2
    B = 2 * M + 2 * u + mu + (k - 1) * K
    assert sp.simplify(2 * (k + 1) * (p - M) - ((q - J) + (k - 1) * (q - K))) == 0
    c0 = (k + 2) / (2 * (k + 1))
    small = 2 * k * (M - q) - (k - 2) * J + (k - 1) * (k + 4) * K + 2 * (k + 1) * mu
    assert sp.simplify(2 * (k + 1) * (B - c0 * T) - small) == 0
    small_u = 2 * k * (M - q) + 2 * q + (4 - k) * J + (k - 1) * (k + 6) * K
    assert sp.simplify(small.subs(mu, u) - small_u) == 0
    large = 10 * M - 8 * q - 4 * J + 18 * u + 5 * (k - 1) * K + 9 * mu
    assert sp.simplify(9 * B - 4 * T - large) == 0
    return {
        "top_gap_identity": "2(k+1)(p-M)=(q-J)+(k-1)(q-K)",
        "small_k_identity": "2(k+1)(B_H-c0*T)=2k(M-q)-(k-2)J+(k-1)(k+4)K+2(k+1)min(u,J)",
        "large_k_identity": "9B_H-4T=10M-8q-4J+18u+5(k-1)K+9min(u,J)",
    }


def pxc101_samples():
    rows = []
    for k in range(2, 65):
        for K in (F(1, 4), F(1, 2), F(1)):
            for J in (F(3, 2), F(2), F(5, 2)):
                for q in (F(3), F(7, 2), F(4)):
                    if not q > J > K:
                        continue
                    for theta in (F(1, 4), F(1, 2), F(3, 4)):
                        M = q + theta * (k - 1) * K
                        if not q + (k - 1) * K >= M:
                            continue
                        if not (k + 2) * q + (k - 1) * K > (2 * k + 1) * J:
                            continue
                        u = (q + J + (k - 1) * K) / (k + 1)
                        T = 2 * M + 2 * q + J + (k - 1) * K
                        p = (T - (k + 2) * u) / 2
                        x = (p, p) + (u,) * (k + 2)
                        z = (M, M, q, q, J) + (K,) * (k - 1)
                        B = actual_top_bound(x, z)
                        formula = 2 * M + 2 * u + min(u, J) + (k - 1) * K
                        assert B == formula
                        assert B >= target_coefficient(k + 4) * T
                        rows.append((k, M, q, J, K, B, T))
    assert {r[0] for r in rows} == set(range(2, 65))
    return rows


def pxc106_samples():
    rows = []
    for psize in range(1, 13):
        for qsize in range(1, 13):
            m = psize + qsize
            for A in (F(41, 10), F(17, 4), F(9, 2), F(19, 4), F(5), F(11, 2)):
                if not F(4) < A < F(6):
                    continue
                if not psize * (A - 1) > (m + 1) * (A - 4):
                    continue
                if not qsize * (A - 1) > (m + 1) * (A - 4):
                    continue
                u = (A + m) / (m + 1)
                t = (16 - u) / 2
                T = 16 + A + m
                x = (t, t) + (u,) * (m + 2)
                z = (F(6), F(6), A, F(4)) + (F(1),) * m
                B = actual_top_bound(x, z)
                assert B == 12 + 2 * u + m
                assert B > F(2, 3) * T
                assert B >= target_coefficient(m + 4) * T
                rows.append((psize, qsize, A, B, T))
    assert rows
    return rows


def positive_demand_controls():
    cases = {
        "actual_top_fixed_failure": (
            (F(9), F(8), F(19, 2), F(8), F(1, 2), F(1, 2), F(1, 2)),
            (F(9), F(17, 2), F(9), F(17, 2), F(1), F(0), F(0)),
        ),
        "top_and_bottom_fixed_failure": (
            (F(19, 2), F(1, 2), F(1, 2), F(1, 2), F(45, 4), F(45, 4), F(17, 2)),
            (F(10), F(1), F(0), F(1), F(21, 2), F(21, 2), F(9)),
        ),
    }
    out = {}
    for name, (x, z) in cases.items():
        T = sum(x, F(0))
        demand = target_coefficient(len(x)) * T - actual_top_bound(x, z)
        assert demand > 0
        out[name] = str(demand / T)
    assert out == {"actual_top_fixed_failure": "1/24", "top_and_bottom_fixed_failure": "1/42"}
    return out


def common_sharp_boundary():
    k = 2
    M = q = F(1, 4)
    J = K = F(0)
    T = 2 * M + 2 * q + J + (k - 1) * K
    u = (q + J + (k - 1) * K) / (k + 1)
    p = (T - (k + 2) * u) / 2
    x = (p, p) + (u,) * (k + 2)
    z = (M, M, q, q, J, K)
    B = actual_top_bound(x, z)
    assert T == 1 and B == F(2, 3)
    return {
        "k": k,
        "B_H_over_T": str(B / T),
        "lost_strict_conditions": ["M>q", "J>K"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    common = pxc101_samples()
    reciprocal = pxc106_samples()
    payload = {
        "claim": "dimension-free spectral closure of the complete PXC101 common and PXC106 reciprocal obstruction chambers",
        "symbolic_identities": symbolic_checks(),
        "PXC101_exact_samples": len(common),
        "PXC101_k_range": [min(r[0] for r in common), max(r[0] for r in common)],
        "PXC106_exact_samples": len(reciprocal),
        "PXC101_target_equality_boundary": common_sharp_boundary(),
        "positive_demand_fail_open_controls": positive_demand_controls(),
        "scope": "conventional all-k proofs for two complete parametric obstruction chambers; not all of either PXC114 branch and not PXC120",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
