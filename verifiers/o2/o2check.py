"""(*)  f({j}) >= T/8  for the Lmax-starved player, in configuration CFG at n=5.

CFG (route1 S5PROOF Part B2): v singleton-normalized exact on 5 players,
T = v(N); x = Lmin has strata (3,2); z = Lmax has strata (1,4) with z_j = 0 for
exactly one player j.  Then 4M = T, i.e. M = T/4 (C1).

DERIVATION OF THE FINITE PROGRAM (not the lead's sketch -- rederived).

Normalise T = 1; everything below is homogeneous of degree 1 in v, and T = 0
forces v == 0.  Write z0 for the vector with z0_j = 0 and z0_i = 1/4 otherwise.

 (A) z0 = Lmax in Core        =>   v(S) <= (|S| - [j in S])/4  for every S.
 (B) M = 1/4 and A3 (now PROVED, task #14) give nu = M = 1/4, so some S* has
     v(S*) = |S*|/4.  ((A) already gives nu <= 1/4.)
 (C) THE SIZE LEMMA (route1 C2, uses only (A)): f(S)/|S| >= 1/8 for S != {j}.
     Hence, under the failure hypothesis f({j}) < 1/8, the minimum defining
     lambda is attained AT {j}:   lambda = f({j}).
 (D) A3's mu-side gives mu := min_i Lmin_i = lambda = f({j}).
 (E) j MUST BE POOR under the failure hypothesis -- this needs no computation
     and closes, for the purposes of (*), the sub-case route1 left open in
     Part E.  If j were rich then f({j}) >= x_j = rho = (1-3mu)/2, and
     f({j}) < 1/8 would give rho < 1/8, whence mu < rho < 1/8 and
     rho = (1-3mu)/2 > (1 - 3/8)/2 = 5/16 > 1/8, a contradiction.
 (F) So Lmin = x0 = (mu, mu, mu, rho, rho) on (j, a, b, c, d) with
     rho = (1-3mu)/2, and x0 in Core:  v(S) <= mu|S n L| + rho|S n R|.

Relabelling: j = 0, L = {0,1,2}, R = {3,4} is free (the stabiliser of j acts
transitively on the choices of the rich pair).  Every displayed condition is
LINEAR in the unknowns (v, mu) -- rho = (1-3mu)/2 is linear -- so the failure of
(*) inside CFG is decided by 31 exact linear programs, one per choice of S*,
each carrying the 280 exact-cone inequalities.

Note the hypotheses used are WEAKER than full CFG: the pinning conditions that
make the Lmin strata exactly (3,2) are never needed, only x0 in Core.  So an
infeasibility verdict proves more than (*).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F

import z3

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
sys.path.insert(0, SCR + "/sel/a3check")
from cone import inequalities

N = 5
FULL = (1 << N) - 1
J = 0
L = [0, 1, 2]
R = [3, 4]


def nm(S):
    return "".join("abcde"[i] for i in range(N) if S >> i & 1) or "0"


def sz(S):
    return bin(S).count("1")


def program(Sstar, ineqs, use_cone=True, use_x0=True, use_z0=True,
            use_nu=True, budget=300):
    v = [z3.Real(f"v{S}") for S in range(1 << N)]
    mu = z3.Real("mu")
    rho = (1 - 3 * mu) / 2
    s = z3.Solver()
    s.add(v[0] == 0)
    for i in range(N):
        s.add(v[1 << i] == 0)
    s.add(v[FULL] == 1)

    if use_z0:                                   # (A)  z0 in Core
        for S in range(1, FULL + 1):
            s.add(v[S] <= F(sz(S) - (1 if S >> J & 1 else 0), 4))
    if use_nu:                                   # (B)  nu = 1/4 attained at S*
        s.add(v[Sstar] == F(sz(Sstar), 4))
        for S in range(1, FULL + 1):
            s.add(4 * v[S] <= sz(S))
    # (C)+(D)  failure: mu = lambda = f({j}) < 1/8
    s.add(mu == 1 - v[FULL ^ (1 << J)])
    s.add(mu >= 0)
    s.add(mu < F(1, 8))
    if use_x0:                                   # (F)  x0 = Lmin in Core
        for S in range(1, FULL + 1):
            s.add(v[S] <= mu * len([i for i in L if S >> i & 1])
                  + rho * len([i for i in R if S >> i & 1]))

    if not use_cone:
        return (s.check() == z3.sat), None
    for _ in range(budget):
        r = s.check()
        assert r in (z3.sat, z3.unsat), f"z3 returned {r}"
        if r == z3.unsat:
            return False, None
        m = s.model()

        def val(e):
            q = z3.simplify(m.eval(e, model_completion=True))
            return (F(q.as_long()) if z3.is_int_value(q)
                    else F(q.numerator_as_long(), q.denominator_as_long()))
        vv = [val(v[S]) for S in range(1 << N)]
        bad = None
        for c in ineqs:
            if sum(F(c[S]) * vv[S] for S in range(1, 1 << N) if c[S]) > 0:
                bad = c
                break
        if bad is None:
            return True, {"v": [str(q) for q in vv], "mu": str(val(mu))}
        s.add(z3.Sum([z3.RealVal(bad[S]) * v[S]
                      for S in range(1, 1 << N) if bad[S]]) <= 0)
    raise RuntimeError("cut budget exhausted")


def main():
    ineqs = inequalities(N)
    print(f"{len(ineqs)} exact-cone inequalities", flush=True)
    res = {"full": {}, "controls": {}}
    hits = []
    for Sstar in range(1, FULL + 1):
        feas, wit = program(Sstar, ineqs)
        res["full"][nm(Sstar)] = feas
        if feas:
            hits.append({"Sstar": nm(Sstar), **wit})
            print(f"  S*={nm(Sstar):6s} FEASIBLE {wit}", flush=True)
    print(f"MAIN: {sum(res['full'].values())} of {FULL} choices of S* feasible")

    # controls: which hypothesis is load-bearing?
    for label, kw in (("no cone", dict(use_cone=False)),
                      ("no x0 (drop Lmin)", dict(use_x0=False)),
                      ("no z0 (drop Lmax)", dict(use_z0=False)),
                      ("no nu = 1/4", dict(use_nu=False))):
        cnt = 0
        for Sstar in range(1, FULL + 1):
            feas, _ = program(Sstar, ineqs, **kw)
            cnt += bool(feas)
        res["controls"][label] = cnt
        print(f"  control [{label}]: {cnt} of {FULL} choices of S* feasible",
              flush=True)

    json.dump({"main_feasible": hits, "per_Sstar": res["full"],
               "controls": res["controls"]},
              open(f"{SCR}/sel/o2/o2check.json", "w"), indent=1)


if __name__ == "__main__":
    main()
