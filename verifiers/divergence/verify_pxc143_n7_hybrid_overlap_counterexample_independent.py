#!/usr/bin/env python3
"""Standalone SMT replay of PXC143; imports no project module."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3

N = 7
T = 119376
X = (8507, 24825, 41719, 17026, 8555, 8519, 10225)
Z = (36, 132, 25137, 25137, 25125, 25113, 18696)
G = (X, Z,
     (0,132,25233,25209,25077,24993,18732),
     (180,0,25029,25413,25077,25137,18540),
     (48,0,0,50310,25281,25065,18672),
     (8483,25293,58733,0,8231,8399,10237),
     (60,41575,66880,8507,0,312,2042),
     (8207,33596,58685,8543,96,0,10249),
     (60,43785,68754,6501,132,144,0))


def csum(p, s): return sum(p[i] for i in range(N) if s >> i & 1)


V = tuple(min(csum(g, s) for g in G) for s in range(1 << N))


def q(a):
    a = F(a)
    return z3.Q(a.numerator, a.denominator)


def core(solver, y):
    solver.add(z3.Sum(y) == T, *[yi >= 0 for yi in y])
    for s in range(1, (1 << N) - 1):
        solver.add(z3.Sum([y[i] for i in range(N) if s >> i & 1]) >= V[s])


def z3_fraction(value):
    if z3.is_int_value(value): return F(value.as_long())
    return F(value.as_fraction())


def selector(mode):
    pinned, free, stages = {}, set(range(N)), []
    while free:
        y = [z3.Real(f"{mode}_level_{len(stages)}_{i}") for i in range(N)]
        phi = z3.Real(f"{mode}_phi_{len(stages)}")
        opt = z3.Optimize(); core(opt, y)
        for i, value in pinned.items(): opt.add(y[i] == q(value))
        if mode == "min":
            opt.add(*[y[i] >= phi for i in free]); handle = opt.maximize(phi)
        else:
            opt.add(*[y[i] <= phi for i in free]); handle = opt.minimize(phi)
        if opt.check() != z3.sat: raise AssertionError((mode, "level"))
        level = z3_fraction(opt.lower(handle) if mode == "min" else opt.upper(handle))
        newly = []
        for i in sorted(free):
            yy = [z3.Real(f"{mode}_pin_{len(stages)}_{i}_{j}") for j in range(N)]
            oo = z3.Optimize(); core(oo, yy)
            for j, value in pinned.items(): oo.add(yy[j] == q(value))
            if mode == "min":
                oo.add(*[yy[j] >= q(level) for j in free]); h = oo.maximize(yy[i])
            else:
                oo.add(*[yy[j] <= q(level) for j in free]); h = oo.minimize(yy[i])
            if oo.check() != z3.sat: raise AssertionError((mode, "pin"))
            trial = z3_fraction(oo.lower(h) if mode == "min" else oo.upper(h))
            if trial == level: newly.append(i)
        if not newly: raise AssertionError((mode, "empty stage"))
        for i in newly: pinned[i] = level; free.remove(i)
        stages.append((str(level), newly))
    return tuple(pinned[i] for i in range(N)), stages


def tangent_audit(point, mode):
    reverse = mode == "max"
    blocks = [tuple(i for i, a in enumerate(point) if a == level)
              for level in sorted(set(point), reverse=reverse)]
    active = [s for s in range(1, (1 << N) - 1) if csum(point, s) == V[s]]
    earlier, checks = [], []
    for stage, block in enumerate(blocks):
        for designated in block:
            d = [z3.Real(f"d_{mode}_{stage}_{designated}_{i}") for i in range(N)]
            solver = z3.SolverFor("QF_LRA"); solver.add(z3.Sum(d) == 0)
            for s in active: solver.add(z3.Sum([d[i] for i in range(N) if s >> i & 1]) >= 0)
            for i in earlier: solver.add(d[i] == 0)
            if mode == "min":
                solver.add(*[d[i] >= 0 for i in block], d[designated] >= 1)
            else:
                solver.add(*[d[i] <= 0 for i in block], d[designated] <= -1)
            verdict = solver.check()
            if verdict != z3.unsat: raise AssertionError((mode, stage, designated, verdict))
            checks.append({"stage": stage, "player": designated, "status": "unsat"})
        earlier.extend(block)
    return active, checks


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); args = parser.parse_args()
    if any(sum(g) != T or min(g) < 0 for g in G): raise AssertionError("generators")
    if any(V[1 << i] for i in range(N)): raise AssertionError("singletons")
    # Direct lower-envelope exactness check, independent of the selector LP.
    for s, value in enumerate(V):
        if not any(csum(g, s) == value for g in G): raise AssertionError(("attainment", s))
    for g in G:
        if any(csum(g, s) < V[s] for s in range(1 << N)): raise AssertionError("core")
    xmin, xmin_stages = selector("min"); zmax, zmax_stages = selector("max")
    if xmin != tuple(map(F, X)) or zmax != tuple(map(F, Z)): raise AssertionError((xmin, zmax))
    xa, xc = tangent_audit(X, "min"); za, zc = tangent_audit(Z, "max")
    distance = sum(abs(a-b) for a,b in zip(X,Z)); overlap = F(T)-F(distance,2); target=F(7,12)*T
    if overlap-target != -6: raise AssertionError((overlap,target))
    payload = {
        "claim": "independent standalone SMT replay of PXC143",
        "implementation": "fresh Z3 Optimize staged selectors plus QF_LRA active-tangent audit; no project imports",
        "exactness": {"coalitions": 128, "singleton_values": [V[1 << i] for i in range(N)]},
        "selectors": {"Lmin": list(map(str,xmin)), "Lmax": list(map(str,zmax)),
                      "Lmin_stages": xmin_stages, "Lmax_stages": zmax_stages},
        "tangent_audit": {"Lmin_active_rows": xa, "Lmax_active_rows": za,
                           "Lmin_checks": xc, "Lmax_checks": zc},
        "violation": {"distance": str(distance), "overlap": str(overlap),
                      "target": str(target), "margin": str(overlap-target)},
    }
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output: args.output.write_text(rendered)
    print(rendered,end="")


if __name__ == "__main__": main()
