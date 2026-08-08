"""closecfg.py + the FULL multi-stage pinning machinery of stages.py.

Same hypothesis set as closecfg.py, with (H5)/(H6) -- the single bottom-Lmin
and single top-Lmax pinnings -- replaced by the complete ladders

  (H5*) every Lmin stratum k is pinned at its level m_k, given the strata
        below it  (stages.floor_stage; k = 0 is exactly closecfg's (H5)),
  (H6*) every Lmax stratum l is pinned at its level M_l, given the strata
        above it (stages.ceiling_stage; l = B-1 is exactly closecfg's (H6),
        l = B-2 is the ceiling SECOND STAGE that s5full/REPORT.txt section 7
        identified as the missing machinery).

Vacuous stages (fewer than two free players left, or the stratum exhausting
the remaining ground set) are skipped -- they certify nothing, see stages.py.

CONTROLS, as required by campaign discipline:
  --controls runs, for the same configuration,
   (C-drop) all pinning ladders deleted  -> must be SAT
   (C-pos)  failure hypothesis negated   -> must be SAT
  and reports both alongside the verdict.
"""
from __future__ import annotations
import itertools
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + "/lib")
from cone import inequalities
import stages
from closecfg import q, layout, reps

N, FULL = 5, 31
SZ = [bin(S).count("1") for S in range(32)]


class Prog2:
    def __init__(self, r, c, tbl, target, use_pin=True, fail=True,
                 floor_stages=None, ceil_stages=None):
        A, B = len(r), len(c)
        cell, P, D1 = layout(r, c, tbl)
        self.P, self.D1 = P, D1
        rowmask = [sum(1 << i for i in range(N) if cell[i][0] == k)
                   for k in range(A)]
        colmask = [sum(1 << i for i in range(N) if cell[i][1] == l)
                   for l in range(B)]
        m = [z3.Real(f"m{k}") for k in range(A)]
        Mv = [z3.Real(f"M{l}") for l in range(B)]
        v = [z3.Real(f"v{S}") for S in range(32)]
        self.m, self.Mv, self.v = m, Mv, v
        mu, Mx = m[0], Mv[B - 1]
        self.mu, self.Mx = mu, Mx
        x = [m[cell[i][0]] for i in range(N)]
        z = [Mv[cell[i][1]] for i in range(N)]
        s = z3.Solver()
        s.add(m[0] >= 0, Mv[0] >= 0)
        s.add(z3.Sum([q(r[k]) * m[k] for k in range(A)]) == 1)
        s.add(z3.Sum([q(c[l]) * Mv[l] for l in range(B)]) == 1)
        for k in range(A - 1):
            s.add(m[k] < m[k + 1])
        for l in range(B - 1):
            s.add(Mv[l] < Mv[l + 1])
        s.add(v[0] == 0, v[FULL] == 1)
        for i in range(N):
            s.add(v[1 << i] == 0)
        xS = lambda S: z3.Sum([x[i] for i in range(N) if S >> i & 1])
        zS = lambda S: z3.Sum([z[i] for i in range(N) if S >> i & 1])
        for S in range(1, FULL):
            s.add(v[S] >= 0)
            s.add(v[S] <= xS(S))
            s.add(v[S] <= zS(S))
            s.add(v[S] <= q(SZ[S]) * Mx)
            s.add(1 - v[FULL ^ S] >= q(SZ[S]) * mu)
        d0 = [v[S0] == q(SZ[S0]) * Mx
              for S0 in reps(D1, cell, lambda cl: cl[0], lo=2)]
        assert d0, "no admissible ceiling anchor"
        s.add(z3.Or(d0))
        ds = [1 - v[FULL ^ Ss] == q(SZ[Ss]) * mu
              for Ss in reps(P, cell, lambda cl: cl[1], lo=1)]
        assert ds
        s.add(z3.Or(ds))
        self.nS0, self.nSs = len(d0), len(ds)
        self.stageinfo = {}
        if use_pin:
            for k in (range(A) if floor_stages is None else floor_stages):
                cons, nv = stages.floor_stage(v, x, rowmask, k, m[k], f"F{k}_")
                if cons:
                    s.add(cons)
                    self.stageinfo[f"floor{k}"] = nv
            for l in (reversed(range(B)) if ceil_stages is None
                      else ceil_stages):
                cons, nv = stages.ceiling_stage(v, z, colmask, l, Mv[l],
                                                f"C{l}_")
                if cons:
                    s.add(cons)
                    self.stageinfo[f"ceil{l}"] = nv
        ratio = z3.Sum([z3.Abs(x[i] - z[i]) for i in range(N)])
        self.ratio = ratio
        s.add(ratio > q(target) if fail else ratio <= q(target))
        self.s = s

    def run(self, ineqs, budget=400):
        v = self.v
        for _ in range(budget):
            res = self.s.check()
            assert res in (z3.sat, z3.unsat), f"z3 returned {res}"
            if res == z3.unsat:
                return False, None
            mo = self.s.model()

            def val(e):
                e = z3.simplify(mo.eval(e, model_completion=True))
                if z3.is_int_value(e):
                    return F(e.as_long())
                if z3.is_rational_value(e):
                    return F(e.numerator_as_long(), e.denominator_as_long())
                raise RuntimeError(f"non-rational model value {e!r}")
            vv = [val(v[S]) for S in range(32)]
            bad = None
            for ineq in ineqs:
                if sum(F(ineq[S]) * vv[S] for S in range(1, 32) if ineq[S]) > 0:
                    bad = ineq
                    break
            if bad is None:
                return True, {"v": [str(t) for t in vv],
                              "m": [str(val(t)) for t in self.m],
                              "M": [str(val(t)) for t in self.Mv],
                              "ratio": str(val(self.ratio))}
            self.s.add(z3.Sum([z3.RealVal(bad[S]) * v[S]
                               for S in range(1, 32) if bad[S]]) <= 0)
        raise RuntimeError("cone-cut budget exhausted")


def check2(r, c, tbl, target, ineqs, controls=False):
    p = Prog2(r, c, tbl, target)
    out = {"lmin": list(r), "lmax": list(c), "tbl": tbl, "target": str(target),
           "n_S0": p.nS0, "n_Sstar": p.nSs, "stages": p.stageinfo,
           "P": p.P, "D1": p.D1}
    feas, wit = p.run(ineqs)
    out["feasible"] = feas
    if feas:
        out["witness"] = wit
    if controls:
        out["control_drop_pinning_feasible"] = Prog2(
            r, c, tbl, target, use_pin=False).run(ineqs)[0]
        out["control_positive_feasible"] = Prog2(
            r, c, tbl, target, fail=False).run(ineqs)[0]
    return out


if __name__ == "__main__":
    import argparse
    import time
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="1/2")
    ap.add_argument("--lmin", default="3,2")
    ap.add_argument("--lmax", default="1,4")
    ap.add_argument("--tbl", default="1,2;0,2")
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()
    r = tuple(int(t) for t in a.lmin.split(","))
    c = tuple(int(t) for t in a.lmax.split(","))
    tbl = [[int(t) for t in row.split(",")] for row in a.tbl.split(";")]
    t0 = time.time()
    res = check2(r, c, tbl, F(a.target), inequalities(N), controls=a.controls)
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(res, indent=1))
