"""INDEPENDENT RE-DERIVATION of the per-configuration verdicts, sharing no
machinery with closecfg2.py.

closecfg2 encodes:                     closecfg3 encodes instead:
  exactness  = 280 facet inequalities    Theorem A: one attaining core vector
               (Studeny-Kratochvil),     per coalition -- purely existential and
               added as lazy cuts        linear, no catalogue, no completeness
                                         assumption
  Lmin/Lmax  = pinning ladders, LP-      Theorem B (floor) and its mirror
               dualized over game-free   (ceiling, re-derived in farkas.py):
               polyhedra whose VERTICES  a quantifier-free Farkas identity per
               are enumerated, with      (stage, player) with the tight-support
               reduced-game caps as      DISJUNCTION -- no reduced game, no
               minima over preimages     preimage minima, no vertex enumeration

Both are exact characterizations of the same configuration, so they must agree
on every verdict.  Agreement is a cross-check on two things at once: the
soundness of each encoding, and the correctness of the leximax mirror.

Shared with closecfg2 (deliberately, so the two test the same theorem): the
configuration layout, the core memberships, and the two A3 anchor disjunctions
of lemmas L1 and L2.  Run with --no-anchors to drop even those.

HYPOTHESES
 (H1) v(empty) = v({i}) = 0, v(N) = 1, v >= 0
 (H2) x = Lmin in Core, (H3) z = Lmax in Core
 (HA) Theorem A: for each proper nonempty S a vector w^S with w^S(N) = 1,
      w^S(A) >= v(A) for all proper A, and w^S(S) = v(S)
 (HB) Theorem B: for each Lmin stage t and each i in B_t, multipliers
      y >= 0 (supported on x-tight proper coalitions), eta, rho, sigma >= 0
      satisfying the floor IDENTITY
 (HC) the mirror of (HB) for z and the Lmax stages
 (H4) the A3 anchor disjunctions (unless --no-anchors)
 (F)  sum_i |x_i - z_i| > target
"""
from __future__ import annotations
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + "/lib")
from closecfg import q, layout, reps

N, FULL = 5, 31
PROPER = list(range(1, FULL))
SZ = [bin(S).count("1") for S in range(32)]


class Prog3:
    def __init__(self, r, c, tbl, target, use_certs=True, fail=True,
                 anchors=True):
        A, B = len(r), len(c)
        cell, P, D1 = layout(r, c, tbl)
        rowmask = [[i for i in range(N) if cell[i][0] == k] for k in range(A)]
        colmask = [[i for i in range(N) if cell[i][1] == l] for l in range(B)]
        m = [z3.Real(f"m{k}") for k in range(A)]
        Mv = [z3.Real(f"M{l}") for l in range(B)]
        v = [z3.Real(f"v{S}") for S in range(32)]
        self.v, self.m, self.Mv = v, m, Mv
        mu, Mx = m[0], Mv[B - 1]
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
        for S in PROPER:
            s.add(v[S] >= 0)
            s.add(v[S] <= xS(S))                                      # (H2)
            s.add(v[S] <= zS(S))                                      # (H3)
        if anchors:
            d0 = [v[S0] == q(SZ[S0]) * Mx
                  for S0 in reps(D1, cell, lambda cl: cl[0], lo=2)]
            assert d0, "no admissible ceiling anchor (L1: Lmax top stratum is a singleton)"
            s.add(z3.Or(d0))                                          # (H4a)
            ds = [1 - v[FULL ^ Ss] == q(SZ[Ss]) * mu
                  for Ss in reps(P, cell, lambda cl: cl[1], lo=1)]
            s.add(z3.Or(ds))                                          # (H4b)
        # (HA) Theorem A: exactness is existential and linear
        for S in PROPER:
            w = [z3.Real(f"w{S}_{i}") for i in range(N)]
            s.add(z3.Sum(w) == 1)
            for Aa in PROPER:
                s.add(z3.Sum([w[i] for i in range(N) if Aa >> i & 1]) >= v[Aa])
            s.add(z3.Sum([w[i] for i in range(N) if S >> i & 1]) == v[S])
        self.ncerts = 0
        if use_certs:
            self._farkas(s, v, x, rowmask, ceiling=False, tag="F")   # (HB)
            self._farkas(s, v, z, colmask[::-1], ceiling=True, tag="C")  # (HC)
        ratio = z3.Sum([z3.Abs(x[i] - z[i]) for i in range(N)])
        self.ratio = ratio
        s.add(ratio > q(target) if fail else ratio <= q(target))
        self.s = s

    def _farkas(self, s, v, phi, blocks, ceiling, tag):
        """(HB)/(HC): one Farkas identity per (stage, player).  `blocks` is
        given in stage order -- increasing payoff for the floor, decreasing for
        the ceiling."""
        sgn = +1 if ceiling else -1
        rhs = -1 if ceiling else +1
        phiS = lambda S: z3.Sum([phi[i] for i in range(N) if S >> i & 1])
        pinned = []
        for t, Bt in enumerate(blocks):
            for i in Bt:
                y = {Aa: z3.Real(f"{tag}y{t}_{i}_{Aa}") for Aa in PROPER}
                eta = z3.Real(f"{tag}eta{t}_{i}")
                rho = {l: z3.Real(f"{tag}rho{t}_{i}_{l}") for l in pinned}
                sig = {cc: z3.Real(f"{tag}sig{t}_{i}_{cc}") for cc in Bt}
                for Aa in PROPER:
                    s.add(y[Aa] >= 0)
                    # (SUPPORT): y_A = 0 unless A is phi-tight
                    s.add(z3.Or(y[Aa] == 0, phiS(Aa) == v[Aa]))
                for cc in Bt:
                    s.add(sig[cc] >= 0)
                for j in range(N):
                    e = -z3.Sum([y[Aa] for Aa in PROPER if Aa >> j & 1]) + eta
                    if j in pinned:
                        e = e + rho[j]
                    if j in Bt:
                        e = e + sgn * sig[j]
                    s.add(e == z3.RealVal(rhs if j == i else 0))
                self.ncerts += 1
            pinned = pinned + list(Bt)

    def run(self):
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
        return True, {"v": [str(val(self.v[S])) for S in range(32)],
                      "m": [str(val(t)) for t in self.m],
                      "M": [str(val(t)) for t in self.Mv],
                      "ratio": str(val(self.ratio))}


def check3(r, c, tbl, target, controls=False, anchors=True):
    p = Prog3(r, c, tbl, target, anchors=anchors)
    out = {"lmin": list(r), "lmax": list(c), "tbl": tbl, "target": str(target),
           "n_farkas_certificates": p.ncerts, "anchors": anchors}
    feas, wit = p.run()
    out["feasible"] = feas
    if feas:
        out["witness"] = wit
    if controls:
        out["control_drop_certs_feasible"] = Prog3(
            r, c, tbl, target, use_certs=False, anchors=anchors).run()[0]
        out["control_positive_feasible"] = Prog3(
            r, c, tbl, target, fail=False, anchors=anchors).run()[0]
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
    ap.add_argument("--no-anchors", action="store_true")
    a = ap.parse_args()
    r = tuple(int(t) for t in a.lmin.split(","))
    c = tuple(int(t) for t in a.lmax.split(","))
    tbl = [[int(t) for t in row.split(",")] for row in a.tbl.split(";")]
    t0 = time.time()
    res = check3(r, c, tbl, F(a.target), controls=a.controls,
                 anchors=not a.no_anchors)
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps({k: val for k, val in res.items() if k != "witness"},
                     indent=1))
