#!/usr/bin/env python3
"""Standalone SMT replay of PXC145 (eight- and nine-player formula failures); imports no project module.

For each embedded game: exactness and normalization of the lower envelope, both staged
selectors recomputed by fresh Z3 Optimize calls (no certificates), an active-tangent
QF_LRA audit of every stage, and rho compared with the formula 2-8n/(n^2-(n mod 2)).
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3

GAMES = [
 {
  "name": "H8",
  "generators": [
   [
    2,
    12,
    20,
    2,
    2,
    2,
    2,
    2
   ],
   [
    0,
    0,
    0,
    18,
    10,
    10,
    6,
    0
   ],
   [
    0,
    16,
    28,
    0,
    0,
    0,
    0,
    0
   ],
   [
    0,
    0,
    15,
    3,
    10,
    10,
    6,
    0
   ]
  ],
  "Lmin": [
   "2",
   "12",
   "20",
   "2",
   "2",
   "2",
   "2",
   "2"
  ],
  "Lmax": [
   "1/5",
   "6/5",
   "46/5",
   "46/5",
   "46/5",
   "46/5",
   "28/5",
   "1/5"
  ]
 },
 {
  "name": "H9",
  "generators": [
   [
    1,
    9,
    15,
    1,
    1,
    1,
    1,
    1,
    1
   ],
   [
    0,
    0,
    0,
    13,
    7,
    7,
    4,
    0,
    0
   ],
   [
    0,
    11,
    20,
    0,
    0,
    0,
    0,
    0,
    0
   ],
   [
    0,
    0,
    11,
    2,
    7,
    7,
    4,
    0,
    0
   ]
  ],
  "Lmin": [
   "1",
   "9",
   "15",
   "1",
   "1",
   "1",
   "1",
   "1",
   "1"
  ],
  "Lmax": [
   "1/15",
   "3/5",
   "33/5",
   "33/5",
   "33/5",
   "33/5",
   "19/5",
   "1/15",
   "1/15"
  ]
 }
]


def formula(n):
    return F(2) - F(8 * n, n * n - (n % 2))


def q(a):
    a = F(a)
    return z3.Q(a.numerator, a.denominator)


def z3_fraction(value):
    if z3.is_int_value(value):
        return F(value.as_long())
    return F(value.as_fraction())


class Game:
    def __init__(self, gens):
        self.G = [tuple(F(a) for a in g) for g in gens]
        self.N = len(gens[0]); self.T = sum(self.G[0])
        self.V = tuple(min(self.csum(g, s) for g in self.G) for s in range(1 << self.N))

    def csum(self, p, s):
        return sum((p[i] for i in range(self.N) if s >> i & 1), F(0))

    def core(self, solver, y):
        solver.add(z3.Sum(y) == q(self.T), *[yi >= 0 for yi in y])
        for s in range(1, (1 << self.N) - 1):
            solver.add(z3.Sum([y[i] for i in range(self.N) if s >> i & 1]) >= q(self.V[s]))

    def selector(self, mode):
        N = self.N
        pinned, free, stages = {}, set(range(N)), []
        while free:
            y = [z3.Real(f"{mode}_level_{len(stages)}_{i}") for i in range(N)]
            phi = z3.Real(f"{mode}_phi_{len(stages)}")
            opt = z3.Optimize(); self.core(opt, y)
            for i, value in pinned.items():
                opt.add(y[i] == q(value))
            if mode == "min":
                opt.add(*[y[i] >= phi for i in free]); handle = opt.maximize(phi)
            else:
                opt.add(*[y[i] <= phi for i in free]); handle = opt.minimize(phi)
            if opt.check() != z3.sat:
                raise AssertionError((mode, "level"))
            level = z3_fraction(opt.lower(handle) if mode == "min" else opt.upper(handle))
            newly = []
            for i in sorted(free):
                yy = [z3.Real(f"{mode}_pin_{len(stages)}_{i}_{j}") for j in range(N)]
                oo = z3.Optimize(); self.core(oo, yy)
                for j, value in pinned.items():
                    oo.add(yy[j] == q(value))
                if mode == "min":
                    oo.add(*[yy[j] >= q(level) for j in free]); h = oo.maximize(yy[i])
                else:
                    oo.add(*[yy[j] <= q(level) for j in free]); h = oo.minimize(yy[i])
                if oo.check() != z3.sat:
                    raise AssertionError((mode, "pin"))
                trial = z3_fraction(oo.lower(h) if mode == "min" else oo.upper(h))
                if trial == level:
                    newly.append(i)
            if not newly:
                raise AssertionError((mode, "empty stage"))
            for i in newly:
                pinned[i] = level; free.remove(i)
            stages.append((str(level), newly))
        return tuple(pinned[i] for i in range(N)), stages

    def tangent_audit(self, point, mode):
        N = self.N
        blocks = [tuple(i for i, a in enumerate(point) if a == level)
                  for level in sorted(set(point), reverse=(mode == "max"))]
        active = [s for s in range(1, (1 << N) - 1) if self.csum(point, s) == self.V[s]]
        earlier, checks = [], []
        for stage, block in enumerate(blocks):
            for designated in block:
                d = [z3.Real(f"d_{mode}_{stage}_{designated}_{i}") for i in range(N)]
                solver = z3.SolverFor("QF_LRA"); solver.add(z3.Sum(d) == 0)
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
                if solver.check() != z3.unsat:
                    raise AssertionError((mode, stage, designated))
                checks.append({"stage": stage, "player": designated, "status": "unsat"})
            earlier.extend(block)
        return active, checks


def verify(game):
    g = Game(game["generators"]); N, T, V = g.N, g.T, g.V
    if any(sum(x) != T or min(x) < 0 for x in g.G):
        raise AssertionError("generators")
    if any(V[1 << i] for i in range(N)) or V[-1] != T:
        raise AssertionError("normalization")
    for s, value in enumerate(V):
        if not any(g.csum(x, s) == value for x in g.G):
            raise AssertionError(("attainment", s))
    X = tuple(F(a) for a in game["Lmin"]); Z = tuple(F(a) for a in game["Lmax"])
    xmin, xs = g.selector("min"); zmax, zs = g.selector("max")
    if xmin != X or zmax != Z:
        raise AssertionError((game["name"], xmin, zmax))
    xa, xc = g.tangent_audit(X, "min"); za, zc = g.tangent_audit(Z, "max")
    distance = sum(abs(a - b) for a, b in zip(X, Z)); rho = distance / T
    if rho <= formula(N):
        raise AssertionError(("no violation", rho))
    return {"name": game["name"], "n": N, "total": str(T), "Lmin": [str(a) for a in xmin], "Lmax": [str(a) for a in zmax],
            "Lmin_stages": xs, "Lmax_stages": zs, "tangent_checks": len(xc) + len(zc),
            "Lmin_active_rows": xa, "Lmax_active_rows": za,
            "rho": str(rho), "formula_value": str(formula(N)), "excess": str(rho - formula(N))}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); args = parser.parse_args()
    payload = {"claim": "independent standalone SMT replay of PXC145",
               "implementation": "fresh Z3 Optimize staged selectors plus QF_LRA active-tangent audit; no project imports, no certificates",
               "games": [verify(game) for game in GAMES]}
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
