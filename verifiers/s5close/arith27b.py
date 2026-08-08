"""Task #27, step 3: the hand net EXTENDED by the protector lemmas L11/L12.

PROTECTOR (proved in lemmas27.py's docstring, A3-free, two lines).  Let phi be
the leximin point (resp. the leximax point) and phi_i < phi_j.  Shifting a
little payoff from j to i strictly improves leximin (resp. leximax), so the
shifted point must leave the core; the constraint it breaks is a coalition A
with phi(A) = v(A) and j in A, i not in A.  Hence:

  L11 (floor).   x_i < x_j  =>  some proper A with j in A, i not in A has
                 x(A) = v(A), and since z is a core point, x(A) <= z(A).
  L12 (ceiling). z_i < z_j  =>  some proper A with j in A, i not in A has
                 z(A) = v(A), and since x is a core point, z(A) <= x(A).

Both are statements about the LEVELS only -- no game variable -- so they belong
in the hand net.  Each is a disjunction over the 8 subsets A with j in A and
i not in A.

Nets measured (all with no v, target R):
  H    levels + L1'' + L7 + L7'                       (A3-free, the step-2 net)
  HP   H + L11 + L12                                  (A3-free, with protectors)
  HA   H + the A3 anchors                             (= the accepted baseline)
  HAP  HA + L11 + L12                                 (everything)
"""
from __future__ import annotations
import itertools
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
sys.path.insert(0, HERE)
from arith22 import q, compositions, tables

N, FULL = 5, 31


def build(r, c, tbl, R, a3, prot):
    A, B = len(r), len(c)
    if c[-1] == 1:
        return None                                            # L1''
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
    s.add(z3.Or([m[k] >= Mx for k in range(A) if tbl[k][B - 1]]))      # L7
    s.add(z3.Or([Mv[l] <= mu for l in range(B) if tbl[0][l]]))         # L7'
    xS = lambda S: z3.Sum([x[i] for i in range(N) if S >> i & 1])
    zS = lambda S: z3.Sum([z[i] for i in range(N) if S >> i & 1])
    if prot:
        for i in range(N):
            for j in range(N):
                subs = [S for S in range(1, FULL)
                        if (S >> j & 1) and not (S >> i & 1)]
                if cell[i][0] < cell[j][0]:                            # L11
                    s.add(z3.Or([xS(S) <= zS(S) for S in subs]))
                if cell[i][1] < cell[j][1]:                            # L12
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
    s.add(z3.Sum([q(tbl[k][l]) * z3.Abs(m[k] - Mv[l])
                  for k in range(A) for l in range(B) if tbl[k][l]]) >= q(R))
    return s


def verdict(r, c, tbl, R, a3, prot):
    s = build(r, c, tbl, R, a3, prot)
    if s is None:
        return "L1-excluded"
    res = s.check()
    assert res in (z3.sat, z3.unsat), f"z3 returned {res}"
    return "survives" if res == z3.sat else "killed"


def main():
    R = F(sys.argv[1]) if len(sys.argv) > 1 else F(1, 2)
    todo = [(r, c, t) for r in compositions(N) for c in compositions(N)
            for t in tables(r, c)]
    out = {}
    for name, a3, prot in (("H", False, False), ("HP", False, True),
                           ("HA", True, False), ("HAP", True, True)):
        tally = {"L1-excluded": 0, "killed": 0, "survives": 0}
        surv = []
        for r, c, tbl in todo:
            k = verdict(r, c, tbl, R, a3, prot)
            tally[k] += 1
            if k == "survives":
                surv.append([list(r), list(c), tbl])
        out[name] = {"tally": tally, "survivors": surv}
        print(f"  net {name:4s} (a3={a3}, protectors={prot}): "
              f"{tally['L1-excluded']} excluded, {tally['killed']} killed, "
              f"{tally['survives']} SURVIVE", flush=True)
        json.dump(out, open(f"{HERE}/arith27b_{str(R).replace('/','_')}.json",
                            "w"), indent=1)


if __name__ == "__main__":
    main()
