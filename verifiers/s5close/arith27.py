"""Task #27, step 2: how much of the 2961-way split dies to HAND LEMMAS alone?

Two nets are measured, both with NO game variable v -- only the stratum level
variables -- so anything they kill is killed by a statement a human can check.

 NET H (A3-FREE).  Levels, orderings, totals, plus
   L1''  the Lmax top stratum has >= 2 players (combinatorial exclusion);
   L7    some player of the Lmax top stratum D1 has Lmin payoff >= M
         (L7 applied to the core point x);
   L7'   some player of the Lmin bottom stratum P has Lmax payoff <= mu
         (L7' applied to the core point z);
   and the failure hypothesis ratio >= R.
 NET HA = NET H + the two A3 anchor conditions of arith22 (L1, L2), i.e. the
   net used by the accepted proof, plus the new L7/L7' rows.

Reported against the accepted baseline (arith22: 1953 excluded by L1', 800
killed arithmetically, 208 left to the solver).
"""
from __future__ import annotations
import itertools
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
sys.path.insert(0, HERE)
import arith22
from arith22 import q, compositions, tables

N = 5


def net(r, c, tbl, R, with_a3):
    """Return 'L1-excluded', 'killed' or 'survives'."""
    A, B = len(r), len(c)
    if c[-1] == 1:
        return "L1-excluded"                                    # L1''
    m = [z3.Real(f"m{k}") for k in range(A)]
    Mv = [z3.Real(f"M{l}") for l in range(B)]
    s = z3.Solver()
    s.add(m[0] >= 0, Mv[0] >= 0)
    s.add(z3.Sum([q(r[k]) * m[k] for k in range(A)]) == 1)
    s.add(z3.Sum([q(c[l]) * Mv[l] for l in range(B)]) == 1)
    s += [m[k] < m[k + 1] for k in range(A - 1)]
    s += [Mv[l] < Mv[l + 1] for l in range(B - 1)]
    mu, Mx = m[0], Mv[B - 1]
    # L7  : some player of D1 (column B-1) has Lmin level >= M
    rows_in_D1 = [k for k in range(A) if tbl[k][B - 1]]
    s.add(z3.Or([m[k] >= Mx for k in rows_in_D1]))
    # L7' : some player of P (row 0) has Lmax level <= mu
    cols_in_P = [l for l in range(B) if tbl[0][l]]
    s.add(z3.Or([Mv[l] <= mu for l in cols_in_P]))
    if with_a3:
        d0 = []
        for sset in itertools.product(*[range(tbl[k][B - 1] + 1)
                                        for k in range(A)]):
            k0 = sum(sset)
            if k0 < 2:
                continue
            d0.append(z3.And(
                z3.Sum([q(sset[k]) * m[k] for k in range(A)]) >= q(k0) * Mx,
                q(k0) * Mx <= 1 - q(5 - k0) * mu))
        if not d0:
            return "L1-excluded"
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
    s.add(ratio >= q(R))
    res = s.check()
    assert res in (z3.sat, z3.unsat), f"z3 returned {res}"
    return "survives" if res == z3.sat else "killed"


def main():
    R = F(sys.argv[1]) if len(sys.argv) > 1 else F(1, 2)
    todo = [(r, c, t) for r in compositions(N) for c in compositions(N)
            for t in tables(r, c)]
    out = {}
    for name, a3 in (("H_a3free", False), ("HA_with_a3", True)):
        tally = {"L1-excluded": 0, "killed": 0, "survives": 0}
        surv = []
        for r, c, tbl in todo:
            k = net(r, c, tbl, R, a3)
            tally[k] += 1
            if k == "survives":
                surv.append([list(r), list(c), tbl])
        out[name] = {"tally": tally, "survivors": surv}
        print(f"NET {name}, target {R}: "
              f"{tally['L1-excluded']} excluded by L1'', "
              f"{tally['killed']} killed by the hand net, "
              f"{tally['survives']} survive", flush=True)
    base = json.load(open(f"{HERE}/arith22_1_2.json"))["results"]
    print(f"baseline arith22 (A3 anchors, no L7/L7'): "
          f"{sum(1 for x in base if x['verdict']=='no-anchor')} excluded, "
          f"{sum(1 for x in base if x['verdict']=='closed')} killed, "
          f"{sum(1 for x in base if x['verdict']=='open')} survive")
    json.dump(out, open(f"{HERE}/arith27_{str(R).replace('/','_')}.json", "w"),
              indent=1)


if __name__ == "__main__":
    main()
