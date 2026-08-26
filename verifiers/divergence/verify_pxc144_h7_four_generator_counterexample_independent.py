#!/usr/bin/env python3
"""Standalone SMT replay of PXC144 (H_7); imports no project module.

Recomputes both staged selectors from the 128 coalition values with fresh Z3
Optimize calls (no certificates, no hand chain), audits every stage by an
active-tangent QF_LRA query, and recomputes rho and the overlap.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3

N = 7
T = 13
G = ((1, 4, 7, 0, 0, 0, 1), (0, 0, 0, 5, 3, 3, 2), (0, 5, 8, 0, 0, 0, 0), (0, 0, 4, 1, 3, 3, 2))
X = tuple(F(a) for a in (1, 3, 5, 1, 1, 1, 1))
Z = tuple(F(a, 5) for a in (1, 3, 13, 13, 13, 13, 9))


def csum(p, s):
    return sum((F(p[i]) for i in range(N) if s >> i & 1), F(0))


V = tuple(min(csum(g, s) for g in G) for s in range(1 << N))


def q(a):
    a = F(a)
    return z3.Q(a.numerator, a.denominator)


def core(solver, y):
    solver.add(z3.Sum(y) == T, *[yi >= 0 for yi in y])
    for s in range(1, (1 << N) - 1):
        solver.add(z3.Sum([y[i] for i in range(N) if s >> i & 1]) >= q(V[s]))


def z3_fraction(value):
    if z3.is_int_value(value):
        return F(value.as_long())
    return F(value.as_fraction())


def selector(mode):
    pinned, free, stages = {}, set(range(N)), []
    while free:
        y = [z3.Real(f"{mode}_level_{len(stages)}_{i}") for i in range(N)]
        phi = z3.Real(f"{mode}_phi_{len(stages)}")
        opt = z3.Optimize()
        core(opt, y)
        for i, value in pinned.items():
            opt.add(y[i] == q(value))
        if mode == "min":
            opt.add(*[y[i] >= phi for i in free])
            handle = opt.maximize(phi)
        else:
            opt.add(*[y[i] <= phi for i in free])
            handle = opt.minimize(phi)
        if opt.check() != z3.sat:
            raise AssertionError((mode, "level"))
        level = z3_fraction(opt.lower(handle) if mode == "min" else opt.upper(handle))
        newly = []
        for i in sorted(free):
            yy = [z3.Real(f"{mode}_pin_{len(stages)}_{i}_{j}") for j in range(N)]
            oo = z3.Optimize()
            core(oo, yy)
            for j, value in pinned.items():
                oo.add(yy[j] == q(value))
            if mode == "min":
                oo.add(*[yy[j] >= q(level) for j in free])
                h = oo.maximize(yy[i])
            else:
                oo.add(*[yy[j] <= q(level) for j in free])
                h = oo.minimize(yy[i])
            if oo.check() != z3.sat:
                raise AssertionError((mode, "pin"))
            trial = z3_fraction(oo.lower(h) if mode == "min" else oo.upper(h))
            if trial == level:
                newly.append(i)
        if not newly:
            raise AssertionError((mode, "empty stage"))
        for i in newly:
            pinned[i] = level
            free.remove(i)
        stages.append((str(level), newly))
    return tuple(pinned[i] for i in range(N)), stages


def tangent_audit(point, mode):
    blocks = [tuple(i for i, a in enumerate(point) if a == level)
              for level in sorted(set(point), reverse=(mode == "max"))]
    active = [s for s in range(1, (1 << N) - 1) if csum(point, s) == V[s]]
    earlier, checks = [], []
    for stage, block in enumerate(blocks):
        for designated in block:
            d = [z3.Real(f"d_{mode}_{stage}_{designated}_{i}") for i in range(N)]
            solver = z3.SolverFor("QF_LRA")
            solver.add(z3.Sum(d) == 0)
            for s in active:
                solver.add(z3.Sum([d[i] for i in range(N) if s >> i & 1]) >= 0)
            for i in range(N):
                if point[i] == 0:
                    solver.add(d[i] >= 0)
            for i in earlier:
                solver.add(d[i] == 0)
            if mode == "min":
                solver.add(*[d[i] >= 0 for i in block], d[designated] >= 1)
            else:
                solver.add(*[d[i] <= 0 for i in block], d[designated] <= -1)
            verdict = solver.check()
            if verdict != z3.unsat:
                raise AssertionError((mode, stage, designated, verdict))
            checks.append({"stage": stage, "player": designated, "status": "unsat"})
        earlier.extend(block)
    return active, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if any(sum(g) != T or min(g) < 0 for g in G):
        raise AssertionError("generators")
    if any(V[1 << i] for i in range(N)) or V[-1] != T:
        raise AssertionError("normalization")
    for s, value in enumerate(V):
        if not any(csum(g, s) == value for g in G):
            raise AssertionError(("attainment", s))
    for g in G:
        if any(csum(g, s) < V[s] for s in range(1 << N)):
            raise AssertionError("core")
    xmin, xmin_stages = selector("min")
    zmax, zmax_stages = selector("max")
    if xmin != X or zmax != Z:
        raise AssertionError((xmin, zmax))
    xa, xc = tangent_audit(X, "min")
    za, zc = tangent_audit(Z, "max")
    distance = sum(abs(a - b) for a, b in zip(X, Z))
    overlap = sum(min(a, b) for a, b in zip(X, Z))
    rho = distance / T
    if rho != F(56, 65) or overlap != F(37, 5) or overlap >= F(7, 12) * T:
        raise AssertionError((rho, overlap))
    payload = {
        "claim": "independent standalone SMT replay of PXC144 (H_7)",
        "implementation": "fresh Z3 Optimize staged selectors plus QF_LRA active-tangent audit; no project imports, no certificates",
        "exactness": {"coalitions": 1 << N, "singleton_values": [str(V[1 << i]) for i in range(N)]},
        "selectors": {"Lmin": [str(a) for a in xmin], "Lmax": [str(a) for a in zmax],
                      "Lmin_stages": xmin_stages, "Lmax_stages": zmax_stages},
        "tangent_audit": {"Lmin_active_rows": xa, "Lmax_active_rows": za,
                          "Lmin_checks": xc, "Lmax_checks": zc},
        "violation": {"distance": str(distance), "rho": str(rho), "overlap": str(overlap),
                      "overlap_over_T": str(overlap / T), "formula_value_5_over_6": "5/6",
                      "rho_minus_formula": str(rho - F(5, 6))},
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
