"""UNIFIED per-configuration finite check (task #22 main driver).

Discharges, for one configuration at a time, the statement
        "no singleton-normalized exact 5-player game in this configuration has
         ratio > R",
by exhibiting one exact-rational z3 program that is UNSAT.  Generalizes
verifiers/o2/o2main.py (which did the single configuration CFG with the target
folded into the hypothesis mu < 1/8) to an arbitrary configuration, and adds
the CEILING-side stage-1 pinning that s5full/REPORT.txt section 7 asked for.

A CONFIGURATION is (r, c, tbl) as in arith22.py.  Players are labelled
canonically cell by cell, so P := Lmin bottom stratum = row 0, and D1 := Lmax
top stratum = column B-1.

HYPOTHESES (each a proved consequence of the configuration; T = 1):
 (H1) v(empty)=v({i})=0, v(N)=1, v >= 0            [singleton-normalized,
                                                    superadditive]
 (H2) x = Lmin in Core:  v(S) <= x(S)
 (H3) z = Lmax in Core:  v(S) <= z(S)
 (H4) A3: mu = lambda and M = nu, so v(S) <= M|S| and 1 - v(N\\S) >= mu|S|
      for every S, with equality somewhere:
        (H4a) some S0 with v(S0) = M|S0|;  S0 lies in D1 and |S0| >= 2
        (H4b) some S* with 1 - v(N\\S*) = mu|S*|;  S* lies in P
      encoded as disjunctions over one representative per cell-composition
      (players inside a cell are interchangeable: v is a free variable and the
      whole program is invariant under permuting them).
 (H5) FLOOR PINNING: max{x(P) : x in Core, x >= mu*1} = |P| mu.  By LP duality
      (pinvert.py) this holds iff some vertex (alpha,beta) of the game-free
      polyhedron D_P satisfies
          alpha*(1-5mu) + sum_S beta_S * ((1 - v(N\\S)) - mu|S|)  <=  0.
 (H6) CEILING PINNING (stage 1, new): min{x(D1) : x in Core, x <= M*1} = |D1| M.
      Same polyhedron with (c_M, h) = (5M - 1, M|S| - v(S)):
          alpha*(5M-1) + sum_S beta_S * (M|S| - v(S))  <=  0.
 (H7) the 280 exact-cone inequalities, added lazily as separating cuts.
 (F)  FAILURE: sum_i |x_i - z_i| > R.

UNSAT of the conjunction proves the configuration obeys ratio <= R.

CONTROLS (run with --controls):
 (C-drop) delete (H5)+(H6): the program must become SAT, i.e. the encoding can
          express a failure and it is the pinning that forbids it.
 (C-pos)  replace (F) by its negation: the program must be SAT, i.e. the
          hypothesis set is not self-contradictory.
 A third, external positive control -- genuine harvested games satisfying the
 whole hypothesis set of their own configuration -- is in poscontrol.py.
"""
from __future__ import annotations
import itertools
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
sys.path.insert(0, HERE + "/lib")
from cone import inequalities
import pinvert

N, FULL = 5, 31
SZ = [bin(S).count("1") for S in range(32)]


def q(x):
    x = F(x)
    return z3.RealVal(f"{x.numerator}/{x.denominator}")


def layout(r, c, tbl):
    """Canonical player labelling; returns (cell_of_player, P, D1)."""
    A, B = len(r), len(c)
    cell, p = [], 0
    for k in range(A):
        for l in range(B):
            for _ in range(tbl[k][l]):
                cell.append((k, l))
                p += 1
    assert p == N
    P = [i for i in range(N) if cell[i][0] == 0]
    D1 = [i for i in range(N) if cell[i][1] == B - 1]
    return cell, P, D1


def reps(pool, cell, key, lo=1):
    """One representative subset per multiset of cell-labels, from `pool`."""
    seen, out = set(), []
    for k in range(lo, len(pool) + 1):
        for c in itertools.combinations(pool, k):
            sig = tuple(sorted(key(cell[i]) for i in c))
            if sig in seen:
                continue
            seen.add(sig)
            out.append(sum(1 << i for i in c))
    return out


class Prog:
    def __init__(self, r, c, tbl, target, use_pin=True, use_ceilpin=True,
                 fail=True):
        A, B = len(r), len(c)
        cell, P, D1 = layout(r, c, tbl)
        self.P, self.D1, self.cell = P, D1, cell
        m = [z3.Real(f"m{k}") for k in range(A)]
        Mv = [z3.Real(f"M{l}") for l in range(B)]
        v = [z3.Real(f"v{S}") for S in range(32)]
        self.m, self.Mv, self.v = m, Mv, v
        mu, Mx = m[0], Mv[B - 1]
        self.mu, self.Mx = mu, Mx
        x = [m[cell[i][0]] for i in range(N)]
        z = [Mv[cell[i][1]] for i in range(N)]
        self.x, self.z = x, z
        s = z3.Solver()
        s.add(m[0] >= 0, Mv[0] >= 0)
        s.add(z3.Sum([q(r[k]) * m[k] for k in range(A)]) == 1)
        s.add(z3.Sum([q(c[l]) * Mv[l] for l in range(B)]) == 1)
        for k in range(A - 1):
            s.add(m[k] < m[k + 1])
        for l in range(B - 1):
            s.add(Mv[l] < Mv[l + 1])
        # (H1)
        s.add(v[0] == 0, v[FULL] == 1)
        for i in range(N):
            s.add(v[1 << i] == 0)
        xS = lambda S: z3.Sum([x[i] for i in range(N) if S >> i & 1])
        zS = lambda S: z3.Sum([z[i] for i in range(N) if S >> i & 1])
        for S in range(1, FULL):
            s.add(v[S] >= 0)
            s.add(v[S] <= xS(S))                                        # (H2)
            s.add(v[S] <= zS(S))                                        # (H3)
            s.add(v[S] <= q(SZ[S]) * Mx)                                # (H4)
            s.add(1 - v[FULL ^ S] >= q(SZ[S]) * mu)                     # (H4)
        # (H4a)
        d0 = [v[S0] == q(SZ[S0]) * Mx
              for S0 in reps(D1, cell, lambda cl: cl[0], lo=2)]
        assert d0, "no admissible ceiling anchor"
        s.add(z3.Or(d0))
        # (H4b)
        ds = [1 - v[FULL ^ Ss] == q(SZ[Ss]) * mu
              for Ss in reps(P, cell, lambda cl: cl[1], lo=1)]
        assert ds
        s.add(z3.Or(ds))
        self.nS0, self.nSs = len(d0), len(ds)
        # (H5) floor pinning
        self.npinf = self.npinc = 0
        if use_pin:
            fp = lambda S: (1 - v[FULL ^ S]) - q(SZ[S]) * mu
            cl = []
            for al, be in pinvert.pinverts(P):
                cl.append(q(al) * (1 - 5 * mu)
                          + z3.Sum([q(b) * fp(S) for S, b in be] or [q(0)]) <= 0)
            s.add(z3.Or(cl))
            self.npinf = len(cl)
        # (H6) ceiling pinning, stage 1
        if use_ceilpin:
            h = lambda S: q(SZ[S]) * Mx - v[S]
            cl = []
            for al, be in pinvert.pinverts(D1):
                cl.append(q(al) * (5 * Mx - 1)
                          + z3.Sum([q(b) * h(S) for S, b in be] or [q(0)]) <= 0)
            s.add(z3.Or(cl))
            self.npinc = len(cl)
        # (F)
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


def check(r, c, tbl, target, ineqs, controls=False):
    out = {"lmin": list(r), "lmax": list(c), "tbl": tbl, "target": str(target)}
    p = Prog(r, c, tbl, target)
    out.update({"n_S0": p.nS0, "n_Sstar": p.nSs,
                "n_pin_floor": p.npinf, "n_pin_ceil": p.npinc,
                "P": p.P, "D1": p.D1})
    feas, wit = p.run(ineqs)
    out["feasible"] = feas
    if feas:
        out["witness"] = wit
    if controls:
        pd = Prog(r, c, tbl, target, use_pin=False, use_ceilpin=False)
        out["control_drop_pinning_feasible"] = pd.run(ineqs)[0]
        pp = Prog(r, c, tbl, target, fail=False)
        out["control_positive_feasible"] = pp.run(ineqs)[0]
    return out


if __name__ == "__main__":
    import argparse
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
    ineqs = inequalities(N)
    import time
    t0 = time.time()
    res = check(r, c, tbl, F(a.target), ineqs, controls=a.controls)
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(res, indent=1))
