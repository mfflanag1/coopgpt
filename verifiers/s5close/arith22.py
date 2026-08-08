"""CONFIGURATION TRIAGE: the exact game-free ceiling, per configuration.

Discharges: the step "which configurations can still carry ratio > 1/2, and how
strong a lower bound on mu does each need".  Section 3 of s5full/REPORT.txt
computed this ceiling with NO configuration data and got 3/2; here the same
game-free reasoning is run separately inside every (Lmin-shape, Lmax-shape,
overlap-table) configuration, which is what makes the ceiling usable.

A CONFIGURATION is (r, c, tbl):  r = Lmin stratum sizes poorest->richest,
c = Lmax stratum sizes poorest->richest, tbl[k][l] = number of players in
Lmin stratum k and Lmax stratum l (a contingency table with margins r, c).
Unknowns are only the level values m_0<...<m_{A-1} and M_0<...<M_{B-1}.

CONSTRAINTS USED (all proved; T normalized to 1):
 (L)  sum_k r_k m_k = 1, sum_l c_l M_l = 1, m,M >= 0, strict within-order.
 (S0) A3 ceiling anchor.  M = nu is attained at some S0 with v(S0)=M|S0|.
      Then |S0|>=2 (singletons are 0), z(S0) >= v(S0) = M|S0| with z <= M
      forces z = M on S0, i.e. S0 lies in the TOP Lmax stratum; and
      x(S0) >= v(S0) = M|S0|.  Also f(N\\S0) >= mu|N\\S0| (A3 floor) reads
      M|S0| = v(S0) <= 1 - mu(5-|S0|).
 (S*) A3 floor anchor.  mu = lambda is attained at some S* with f(S*)=mu|S*|.
      Then x(S*) <= f(S*) = mu|S*| with x >= mu forces x = mu on S*, i.e. S*
      lies in the BOTTOM Lmin stratum; and z(S*) <= f(S*) = mu|S*|.  Also
      v(N\\S*) = 1 - mu|S*| obeys 0 <= v(N\\S*) <= M(5-|S*|) (A3 ceiling).
 Both anchors are existentially quantified: the encoding is a DISJUNCTION over
 the admissible (stratum-composition of S0, stratum-composition of S*).
 Enlarging the disjunction only enlarges the feasible set, so every verdict
 "no configuration of this shape reaches ratio R" is conservative.

OUTPUT arith22.json: for every configuration, whether ratio >= R is feasible,
and if so  mu_hi := max{ mu : ratio >= R feasible }, so that the finite check
needed to close it is exactly "mu > mu_hi" (verified by a second, strict call).
"""
from __future__ import annotations
import itertools
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
N = 5


def compositions(n):
    """All ordered compositions of n as tuples."""
    out = []
    for k in range(1, n + 1):
        for cut in itertools.combinations(range(1, n), k - 1):
            pts = (0,) + cut + (n,)
            out.append(tuple(pts[i + 1] - pts[i] for i in range(k)))
    return out


def tables(r, c):
    """All nonneg integer matrices with row sums r and column sums c."""
    A, B = len(r), len(c)

    def rec(k, colrem):
        if k == A:
            if all(x == 0 for x in colrem):
                yield []
            return
        for row in rowfills(r[k], colrem, 0, []):
            yield from ([row] + rest
                        for rest in rec(k + 1,
                                        [colrem[j] - row[j] for j in range(B)]))

    def rowfills(tot, colrem, j, acc):
        if j == B:
            if tot == 0:
                yield list(acc)
            return
        for x in range(min(tot, colrem[j]) + 1):
            yield from rowfills(tot - x, colrem, j + 1, acc + [x])

    return list(rec(0, list(c)))


def q(x):
    x = F(x)
    return z3.RealVal(f"{x.numerator}/{x.denominator}")


def build(r, c, tbl):
    """Return (solver-constraint list, m, M, mu, Mx, ratio_expr)."""
    A, B = len(r), len(c)
    m = [z3.Real(f"m{k}") for k in range(A)]
    Mv = [z3.Real(f"M{l}") for l in range(B)]
    cons = [m[0] >= 0, Mv[0] >= 0,
            z3.Sum([q(r[k]) * m[k] for k in range(A)]) == 1,
            z3.Sum([q(c[l]) * Mv[l] for l in range(B)]) == 1]
    cons += [m[k] < m[k + 1] for k in range(A - 1)]
    cons += [Mv[l] < Mv[l + 1] for l in range(B - 1)]
    mu, Mx = m[0], Mv[B - 1]

    # (S0): choose how many S0-players come from each Lmin stratum, all inside
    # the top Lmax stratum (column B-1).
    d0 = []
    for s in itertools.product(*[range(tbl[k][B - 1] + 1) for k in range(A)]):
        k0 = sum(s)
        if k0 < 2:
            continue
        cl = [z3.Sum([q(s[k]) * m[k] for k in range(A)]) >= q(k0) * Mx,
              q(k0) * Mx <= 1 - q(5 - k0) * mu]
        if k0 == 5:
            cl.append(q(5) * Mx == 1)
        d0.append(z3.And(cl))
    if not d0:
        return None
    cons.append(z3.Or(d0))

    # (S*): choose how many S*-players come from each Lmax stratum, all inside
    # the bottom Lmin stratum (row 0).
    ds = []
    for t in itertools.product(*[range(tbl[0][l] + 1) for l in range(B)]):
        ks = sum(t)
        if ks < 1:
            continue
        cl = [z3.Sum([q(t[l]) * Mv[l] for l in range(B)]) <= q(ks) * mu,
              1 - q(ks) * mu >= 0]
        if ks == 5:
            cl.append(1 - q(5) * mu == 0)
        else:
            cl.append(1 - q(ks) * mu <= q(5 - ks) * Mx)
        ds.append(z3.And(cl))
    if not ds:
        return None
    cons.append(z3.Or(ds))

    ratio = z3.Sum([q(tbl[k][l]) * z3.Abs(m[k] - Mv[l])
                    for k in range(A) for l in range(B) if tbl[k][l]])
    return cons, m, Mv, mu, Mx, ratio


def rat(e):
    e = z3.simplify(e)
    if z3.is_int_value(e):
        return F(e.as_long())
    if z3.is_rational_value(e):
        return F(e.numerator_as_long(), e.denominator_as_long())
    return None


def analyse(r, c, tbl, R):
    b = build(r, c, tbl)
    if b is None:
        return {"verdict": "no-anchor"}
    cons, m, Mv, mu, Mx, ratio = b
    s = z3.Solver()
    s.add(cons)
    s.add(ratio >= q(R))
    res = s.check()
    assert res in (z3.sat, z3.unsat), f"z3 returned {res}"
    if res == z3.unsat:
        return {"verdict": "closed"}
    # sup of mu over the ratio >= R region
    o = z3.Optimize()
    o.add(cons)
    o.add(ratio >= q(R))
    h = o.maximize(mu)
    assert o.check() == z3.sat
    hi = rat(o.upper(h))
    out = {"verdict": "open", "mu_hi": str(hi) if hi is not None else "?"}
    if hi is not None:
        s2 = z3.Solver()
        s2.add(cons)
        s2.add(ratio > q(R))
        s2.add(mu >= q(hi))
        r2 = s2.check()
        assert r2 in (z3.sat, z3.unsat)
        out["strict_closed_at_mu_hi"] = (r2 == z3.unsat)
    # a witness of the extreme
    mo = o.model()
    out["witness"] = {
        "m": [str(rat(mo.eval(x, model_completion=True))) for x in m],
        "M": [str(rat(mo.eval(x, model_completion=True))) for x in Mv],
        "ratio": str(rat(mo.eval(ratio, model_completion=True))),
    }
    return out


def main():
    R = F(sys.argv[1]) if len(sys.argv) > 1 else F(1, 2)
    comps = compositions(N)
    todo = []
    for r in comps:
        for c in comps:
            for tbl in tables(r, c):
                todo.append((r, c, tbl))
    print(f"{len(comps)} compositions, {len(todo)} configurations, target R={R}",
          flush=True)
    assert len(todo) < 200000, "enumeration cap"
    res = []
    for i, (r, c, tbl) in enumerate(todo):
        a = analyse(r, c, tbl, R)
        a.update({"lmin": list(r), "lmax": list(c), "tbl": tbl})
        res.append(a)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(todo)}  open so far: "
                  f"{sum(1 for x in res if x['verdict']=='open')}", flush=True)
    openc = [x for x in res if x["verdict"] == "open"]
    print(f"RESULT target {R}: {len(res)} configurations, {len(openc)} OPEN, "
          f"{sum(1 for x in res if x['verdict']=='closed')} closed, "
          f"{sum(1 for x in res if x['verdict']=='no-anchor')} anchorless")
    tag = str(R).replace("/", "_")
    json.dump({"target": str(R), "results": res},
              open(f"{HERE}/arith22_{tag}.json", "w"), indent=1)
    for x in openc:
        print(f"  OPEN lmin={x['lmin']} lmax={x['lmax']} tbl={x['tbl']} "
              f"mu_hi={x['mu_hi']} strictclosed={x.get('strict_closed_at_mu_hi')}")


if __name__ == "__main__":
    main()
