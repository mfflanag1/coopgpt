#!/usr/bin/env python3
"""Independent role-orbit staged-selector replay for PXC150."""
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


def family(m, k, bad=False):
    x = F(m * (2*k - 1), 2*(k - 1))
    y = F(m*k, k - 1)
    q = 1 + F(m, 2*(k - 1))
    X = (F(1), x, y, F(1), F(1), F(1), F(1))
    B = (F(0), F(0), F(0), x + 1, q, q, F(m + 1))
    G = (F(0), x + (1 if bad else 2),
         F(m) + y + 2*k + (1 if bad else 0),
         F(0), F(0), F(0), F(0))
    return X, B, G


def orbits(points, m, k):
    rows = []
    for uc in range(m + 1):
        for ac in range(k + 1):
            for bc in range(k + 1):
                for bits in range(16):
                    b, c, d, g = ((bits >> j) & 1 for j in range(4))
                    counts = (uc, b, c, d, ac, bc, g)
                    if counts == (m, 1, 1, 1, k, k, 1):
                        continue
                    value = min(sum((P[i]*counts[i] for i in range(7)), F(0))
                                for P in points)
                    rows.append((counts, value))
    return rows


def optimum(constraints, expression, maximize):
    solver = z3.Optimize()
    solver.add(*constraints)
    handle = solver.maximize(expression) if maximize else solver.minimize(expression)
    assert solver.check() == z3.sat
    return fq(handle.value())


def selector(points, m, k, mode):
    mult = (m, 1, 1, 1, k, k, 1)
    total = sum((mult[i]*points[0][i] for i in range(7)), F(0))
    y = z3.Reals(f"U_{mode} b_{mode} c_{mode} d_{mode} A_{mode} B_{mode} g_{mode}")
    rows = orbits(points, m, k)
    base = [sum(mult[i]*y[i] for i in range(7)) == zq(total)]
    base.extend(sum(counts[i]*y[i] for i in range(7)) >= zq(value)
                for counts, value in rows)
    fixed, free, stages = {}, list(range(7)), []
    while free:
        prefix = base + [y[i] == zq(value) for i, value in fixed.items()]
        level_var = z3.Real(f"level_{mode}_{len(stages)}")
        if mode == "min":
            level = optimum(prefix + [y[i] >= level_var for i in free], level_var, True)
            face = prefix + [y[i] >= zq(level) for i in free]
            pinned = [i for i in free if optimum(face, y[i], True) == level]
        else:
            level = optimum(prefix + [y[i] <= level_var for i in free], level_var, False)
            face = prefix + [y[i] <= zq(level) for i in free]
            pinned = [i for i in free if optimum(face, y[i], False) == level]
        assert pinned
        stages.append({"level": str(level), "pinned_roles": pinned})
        for role in pinned:
            fixed[role] = level
            free.remove(role)
    return tuple(fixed[i] for i in range(7)), stages, len(rows)


def check(m, k):
    points = family(m, k)
    X, B, _ = points
    x, y = X[1], X[2]
    lam = F(x + 1, x + y)
    expected_z = tuple(lam*X[i] + (1-lam)*B[i] for i in range(7))
    got_x, min_stages, count = selector(points, m, k, "min")
    got_z, max_stages, _ = selector(points, m, k, "max")
    assert got_x == X, (m, k, got_x, X)
    assert got_z == expected_z, (m, k, got_z, expected_z)
    mult = (m, 1, 1, 1, k, k, 1)
    T = sum((mult[i]*X[i] for i in range(7)), F(0))
    O = sum((mult[i]*min(X[i], got_z[i]) for i in range(7)), F(0))
    return {"m": m, "k": k, "coalition_orbits": count,
            "Lmin_roles": [str(q) for q in got_x],
            "Lmax_roles": [str(q) for q in got_z],
            "rho": str(F(2) - 2*O/T),
            "Lmin_stages": min_stages, "Lmax_stages": max_stages}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [check(m, k) for m, k in
             ((1, 2), (2, 2), (4, 2), (2, 3), (3, 3),
              (4, 3), (9, 3), (4, 4), (12, 4), (5, 5))]
    m, k = 4, 3
    bad_points = family(m, k, bad=True)
    got_bad, stages, _ = selector(bad_points, m, k, "min")
    assert got_bad != bad_points[0]
    payload = {
        "claim": "independent exact staged-selector calibration of PXC150",
        "implementation": "standalone Z3 QF_LRA on directly generated U/A/B coalition-count orbits; no project selector or primary-verifier imports",
        "cases": cases,
        "negative_control": {"m": m, "k": k,
                             "one_unit_beg_undercut_changes_Lmin": True,
                             "observed_Lmin_roles": [str(q) for q in got_bad],
                             "stages": stages},
        "scope": "finite independent calibration; the manuscript weighted-cover and equality proof supply all m,k",
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
