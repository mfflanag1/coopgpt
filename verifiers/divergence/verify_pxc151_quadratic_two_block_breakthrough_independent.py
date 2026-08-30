#!/usr/bin/env python3
"""Independent Z3 role-orbit selector replay for PXC151.

The core and objectives are invariant under permutations within U and E.
Permutation averaging preserves every previously fixed lexicographic face,
so each stage has an optimal block-symmetric allocation.  The role-orbit
model therefore computes the unrestricted selector values, not a heuristic
restriction to symmetric candidates.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3


def zq(x):
    return z3.Q(x.numerator, x.denominator)


def fq(x):
    x = z3.simplify(x)
    if z3.is_int_value(x):
        return F(x.as_long())
    return F(x.numerator_as_long(), x.denominator_as_long())


def family(m, r, bad=False):
    y = m*(2*r-1)
    T = 2*m*r+m+r+1
    X = (F(1), F(m-1), F(y), F(1), F(1), F(1))
    B = (F(0), F(0), F(0), F(1 if bad else 0),
         F(2*m+1), F(m if bad else m+1))
    C = (F(0), F(m+1), F(r*(2*m+1)), F(0), F(0), F(0))
    return X, B, C


def orbit_rows(points, m, r):
    rows = []
    for uc in range(m+1):
        for ec in range(r+1):
            for bits in range(16):
                b, c, d, g = ((bits >> j) & 1 for j in range(4))
                counts = (uc, b, c, d, ec, g)
                if counts == (m, 1, 1, 1, r, 1):
                    continue
                value = min(sum((P[i]*counts[i] for i in range(6)), F(0))
                            for P in points)
                rows.append((counts, value))
    return rows


def optimum(constraints, expression, maximize):
    solver = z3.Optimize()
    solver.add(*constraints)
    handle = solver.maximize(expression) if maximize else solver.minimize(expression)
    assert solver.check() == z3.sat
    return fq(handle.value())


def selector(points, m, r, mode):
    mult = (m, 1, 1, 1, r, 1)
    total = sum((mult[i]*points[0][i] for i in range(6)), F(0))
    y = z3.Reals(f"U_{mode} b_{mode} c_{mode} d_{mode} E_{mode} g_{mode}")
    rows = orbit_rows(points, m, r)
    base = [sum(mult[i]*y[i] for i in range(6)) == zq(total)]
    base.extend(sum(counts[i]*y[i] for i in range(6)) >= zq(value)
                for counts, value in rows)
    fixed, free, stages = {}, list(range(6)), []
    while free:
        prefix = base+[y[i] == zq(value) for i, value in fixed.items()]
        level_var = z3.Real(f"level_{mode}_{len(stages)}")
        if mode == "min":
            level = optimum(prefix+[y[i] >= level_var for i in free],
                            level_var, True)
            face = prefix+[y[i] >= zq(level) for i in free]
            pinned = [i for i in free if optimum(face, y[i], True) == level]
        else:
            level = optimum(prefix+[y[i] <= level_var for i in free],
                            level_var, False)
            face = prefix+[y[i] <= zq(level) for i in free]
            pinned = [i for i in free if optimum(face, y[i], False) == level]
        assert pinned
        stages.append({"level": str(level), "pinned_roles": pinned})
        for role in pinned:
            fixed[role] = level
            free.remove(role)
    return tuple(fixed[i] for i in range(6)), stages, len(rows)


def check(m, r):
    points = family(m, r)
    X = points[0]
    lam = F(2*m+1, m*(2*r+1))
    expected_z = tuple(lam*points[0][i]+(1-lam)*points[1][i]
                       for i in range(6))
    got_x, min_stages, count = selector(points, m, r, "min")
    got_z, max_stages, _ = selector(points, m, r, "max")
    assert got_x == X, (m, r, got_x, X)
    assert got_z == expected_z, (m, r, got_z, expected_z)
    mult = (m, 1, 1, 1, r, 1)
    T = F(2*m*r+m+r+1)
    O = sum((F(mult[i])*min(got_x[i], got_z[i]) for i in range(6)), F(0))
    rho = F(2)-2*O/T
    assert O == 2*m+r+2
    n = m+r+4
    benchmark = F(2)-F(8*n, n*n-(n % 2))
    return {
        "m": m, "r": r, "n": n, "coalition_orbits": count,
        "Lmin_roles": [str(q) for q in got_x],
        "Lmax_roles": [str(q) for q in got_z],
        "overlap": str(O), "rho": str(rho),
        "benchmark_margin": str(rho-benchmark),
        "Lmin_stages": min_stages, "Lmax_stages": max_stages,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [check(m, r) for m, r in (
        (2, 3), (3, 3), (3, 4), (4, 4), (5, 5), (6, 6),
        (6, 8), (8, 6), (8, 8), (10, 10), (12, 7), (12, 12),
    )]
    assert all(case["benchmark_margin"].startswith("-")
               for case in cases if case["m"] == case["r"] <= 4)
    assert all(not case["benchmark_margin"].startswith("-")
               for case in cases if case["m"] == case["r"] >= 5)

    m, r = 5, 5
    bad_points = family(m, r, bad=True)
    bad_x, bad_stages, _ = selector(bad_points, m, r, "min")
    assert bad_x != bad_points[0]
    payload = {
        "claim": "independent exact staged-selector calibration of PXC151",
        "implementation": "standalone Z3 QF_LRA on directly generated U/E coalition-count orbits; permutation averaging makes the role reduction exact at every staged face; imports no project or primary-verifier code",
        "cases": cases,
        "negative_control": {
            "m": m, "r": r,
            "one_unit_H_undercut_changes_Lmin": True,
            "observed_Lmin_roles": [str(q) for q in bad_x],
            "stages": bad_stages,
        },
        "scope": "finite independent calibration; the manuscript incidence and minimax-dual proofs supply all m,r",
    }
    text = json.dumps(payload, indent=2)+"\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
