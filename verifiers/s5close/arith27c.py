"""Task #27, increment 2: hand net with TIGHT-FAMILY reasoning (net HAPT).

The protectors supply tight coalitions one at a time; L14/L15/L16 say how tight
coalitions combine.  Encoding both together needs a Boolean marker per
coalition -- still no game variable v, so every constraint remains a statement
about the two allocations that a reader can check.

  tx[A] : "A is x-tight", i.e. x(A) = v(A)      (A proper nonempty)
  tz[A] : "A is z-tight"

  tx[A]                      =>  x(A) <= z(A)                        (L11)
  tz[A]                      =>  z(A) <= x(A)                        (L12)
  x_i < x_j                  =>  Or_{A: j in A, i not in A} tx[A]    (protector)
  z_i < z_j                  =>  Or_{A: j in A, i not in A} tz[A]    (protector)
  tx[A] & tx[B], A,B disjoint =>  tx[A u B]                          (L14)
  tz[A] & tz[B], A,B disjoint =>  tz[A u B]                          (L14)
  tx[A] & tz[B], A subset B   =>  x(A) <= z(B)                       (L15)
  tz[A] & tx[B], A subset B   =>  z(A) <= x(B)                       (L15)
  tx[A] & tz[B], A,B disjoint =>  x(A)+z(B) <= min(x(AuB), z(AuB))   (L16)
(L17 is automatic: tx[A] and tz[A] together already force x(A) = z(A).)

All verified on 2668 genuine games in tightfam.py.  Complement closure is NOT
used -- it is false, as that script confirms.

usage: python3 arith27c.py <target> [--all]
  default: run only on the 132 survivors of net HAP, plus the soundness check
  that no configuration the harvests actually produced is killed.
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
from arith22 import q, compositions, tables

N, FULL = 5, 31
PROPER = list(range(1, FULL))


def build(r, c, tbl, R, a3=True, tight=True, fail=True):
    A, B = len(r), len(c)
    if c[-1] == 1:
        return None
    cell = []
    for k in range(A):
        for l in range(B):
            cell += [(k, l)] * tbl[k][l]
    m = [z3.Real(f"m{k}") for k in range(A)]
    Mv = [z3.Real(f"M{l}") for l in range(B)]
    x = [m[cell[i][0]] for i in range(N)]
    z = [Mv[cell[i][1]] for i in range(N)]
    s = z3.Solver()
    s.add(m[0] >= 0, Mv[0] >= 0)
    s.add(z3.Sum([q(r[k]) * m[k] for k in range(A)]) == 1)
    s.add(z3.Sum([q(c[l]) * Mv[l] for l in range(B)]) == 1)
    s += [m[k] < m[k + 1] for k in range(A - 1)]
    s += [Mv[l] < Mv[l + 1] for l in range(B - 1)]
    mu, Mx = m[0], Mv[B - 1]
    s.add(z3.Or([m[k] >= Mx for k in range(A) if tbl[k][B - 1]]))       # L7
    s.add(z3.Or([Mv[l] <= mu for l in range(B) if tbl[0][l]]))          # L7'
    xS = lambda S: z3.Sum([x[i] for i in range(N) if S >> i & 1])
    zS = lambda S: z3.Sum([z[i] for i in range(N) if S >> i & 1])
    if tight:
        tx = {S: z3.Bool(f"tx{S}") for S in PROPER}
        tz = {S: z3.Bool(f"tz{S}") for S in PROPER}
        for S in PROPER:
            s.add(z3.Implies(tx[S], xS(S) <= zS(S)))
            s.add(z3.Implies(tz[S], zS(S) <= xS(S)))
        for i in range(N):
            for j in range(N):
                subs = [S for S in PROPER if (S >> j & 1) and not (S >> i & 1)]
                if cell[i][0] < cell[j][0]:
                    s.add(z3.Or([tx[S] for S in subs]))
                if cell[i][1] < cell[j][1]:
                    s.add(z3.Or([tz[S] for S in subs]))
        for Aa in PROPER:
            for Bb in PROPER:
                if Aa & Bb == 0 and (Aa | Bb) in tx:                    # L14/L16
                    s.add(z3.Implies(z3.And(tx[Aa], tx[Bb]), tx[Aa | Bb]))
                    s.add(z3.Implies(z3.And(tz[Aa], tz[Bb]), tz[Aa | Bb]))
                    s.add(z3.Implies(z3.And(tx[Aa], tz[Bb]),
                                     z3.And(xS(Aa) + zS(Bb) <= xS(Aa | Bb),
                                            xS(Aa) + zS(Bb) <= zS(Aa | Bb))))
                if Aa != Bb and Aa & Bb == Aa:                          # L15
                    s.add(z3.Implies(z3.And(tx[Aa], tz[Bb]), xS(Aa) <= zS(Bb)))
                    s.add(z3.Implies(z3.And(tz[Aa], tx[Bb]), zS(Aa) <= xS(Bb)))
    else:
        for i in range(N):
            for j in range(N):
                subs = [S for S in PROPER if (S >> j & 1) and not (S >> i & 1)]
                if cell[i][0] < cell[j][0]:
                    s.add(z3.Or([xS(S) <= zS(S) for S in subs]))
                if cell[i][1] < cell[j][1]:
                    s.add(z3.Or([zS(S) <= xS(S) for S in subs]))
    if a3:
        d0 = []
        for ss in itertools.product(*[range(tbl[k][B - 1] + 1)
                                      for k in range(A)]):
            k0 = sum(ss)
            if k0 >= 2:
                d0.append(z3.And(
                    z3.Sum([q(ss[k]) * m[k] for k in range(A)]) >= q(k0) * Mx,
                    q(k0) * Mx <= 1 - q(5 - k0) * mu))
        if not d0:
            return None
        s.add(z3.Or(d0))
        ds = []
        for t in itertools.product(*[range(tbl[0][l] + 1) for l in range(B)]):
            ks = sum(t)
            if ks < 1:
                continue
            cl = [z3.Sum([q(t[l]) * Mv[l] for l in range(B)]) <= q(ks) * mu,
                  1 - q(ks) * mu >= 0]
            cl.append(1 - q(5) * mu == 0 if ks == 5
                      else 1 - q(ks) * mu <= q(5 - ks) * Mx)
            ds.append(z3.And(cl))
        s.add(z3.Or(ds))
    ratio = z3.Sum([q(tbl[k][l]) * z3.Abs(m[k] - Mv[l])
                    for k in range(A) for l in range(B) if tbl[k][l]])
    s.add(ratio >= q(R) if fail else ratio < q(R))
    return s


def verdict(r, c, tbl, R, **kw):
    s = build(r, c, tbl, R, **kw)
    if s is None:
        return "L1-excluded"
    res = s.check()
    assert res in (z3.sat, z3.unsat), f"z3 returned {res}"
    return "survives" if res == z3.sat else "killed"


def main():
    R = F(sys.argv[1]) if len(sys.argv) > 1 else F(1, 2)
    tag = str(R).replace("/", "_")
    prev = json.load(open(f"{HERE}/arith27b_{tag}.json"))
    todo = [(tuple(a), tuple(b), c) for a, b, c in prev["HAP"]["survivors"]]
    print(f"net HAPT on the {len(todo)} survivors of net HAP, target {R}",
          flush=True)
    killed, surv = 0, []
    for r, c, tbl in todo:
        k = verdict(r, c, tbl, R)
        if k == "killed":
            killed += 1
        else:
            surv.append([list(r), list(c), tbl])
    print(f"  killed a further {killed}; {len(surv)} SURVIVE net HAPT",
          flush=True)

    # SOUNDNESS: no configuration the harvests actually produced may be killed
    import audit
    obs = set()
    for src in ("harvest_seed22.json", "harvest_seed777.json"):
        for g in json.load(open(f"{HERE}/{src}"))["records"]:
            xx = [F(t) for t in g["lmin"]]
            zz = [F(t) for t in g["lmax"]]
            sx, sz = audit.strata(xx), audit.strata(zz)
            ri = {i: k for k, b in enumerate(sx) for i in b}
            ci = {i: l for l, b in enumerate(sz) for i in b}
            t = [[0] * len(sz) for _ in sx]
            for i in range(N):
                t[ri[i]][ci[i]] += 1
            obs.add((tuple(len(b) for b in sx), tuple(len(b) for b in sz),
                     json.dumps(t)))
    bad = []
    for r, c, tj in sorted(obs):
        tbl = json.loads(tj)
        # a configuration that OCCURS must remain feasible without the failure
        # hypothesis, i.e. the net must not be contradictory on it
        if verdict(r, c, tbl, R, fail=False) == "killed":
            bad.append([list(r), list(c), tbl])
    print(f"  soundness: {len(obs)} observed configurations, "
          f"{len(bad)} wrongly killed (must be 0)")
    for b in bad:
        print("     WRONGLY KILLED", b)
    json.dump({"target": str(R), "input": len(todo), "killed": killed,
               "survivors": surv, "observed": len(obs),
               "wrongly_killed": bad},
              open(f"{HERE}/arith27c_{tag}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
