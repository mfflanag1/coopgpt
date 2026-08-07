"""The A3 finite check at n = 5.

REDUCTION (route1 P9, restated).  For a singleton-normalized exact game v with
T = v(N), nu = max_S v(S)/|S|, lambda = min_S f(S)/|S|, f(S) = T - v(N\\S):

  M = nu       iff  every fractional cover w has sum_S w_S h(S)  >= h(N),
                    h(S) = nu|S| - v(S) >= 0;
  mu = lambda  iff  every fractional cover w has sum_S w_S f'(S) >= f'(N),
                    f'(S) = f(S) - lambda|S| >= 0.

Both objectives are nonnegative, so each minimum is attained at a VERTEX of the
cover polyhedron; there are 2287 of them at n = 5 (coververt.py), of which 1292
are balanced.  Balanced covers never beat the trivial one (route1 P10), so only
the 995 strictly over-covering vertices can witness a failure.

FINITENESS.  Fix the anchor S0 attaining nu (resp. S1 attaining lambda) and fix
an over-covering vertex w.  Then nu (resp. lambda) is a linear function of v,
every hypothesis is linear in v, and the failure condition is a single strict
linear inequality.  So A3 fails at n = 5 iff one of the finitely many programs

    v(empty) = 0,  v({i}) = 0,  v(N) = 1            (scale is free: homogeneous)
    exact cone: sum_S c_S v(S) <= 0 for every inequality assigned to an
                indecomposable min-semi-balanced system (16 types under S_5)
    anchor:     |S0| v(S) <= |S| v(S0) for every S   [nu = v(S0)/|S0|]
    failure:    sum_S w_S h(S) < h(N)

is feasible.  Feasibility is decided EXACTLY with z3, using lazy generation of
the cone inequalities: a relaxation that is infeasible proves the full program
infeasible, and a model that violates no cone inequality IS an exact game.
"""
from __future__ import annotations

import itertools
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


def nm(mask):
    return "".join("abcde"[i] for i in range(N) if mask >> i & 1) or "0"


def load_vertices():
    raw = json.load(open(f"{SCR}/sel/a3check/coververts.json"))
    out = []
    for v in raw:
        w = {int(S): F(x) for S, x in v}
        load = [sum(x for S, x in w.items() if S >> i & 1) for i in range(N)]
        out.append((w, all(y == 1 for y in load)))
    return out


def canon_pairs(verts, anchors):
    """(w, anchor) up to permutations of N."""
    keys = []
    for p in itertools.permutations(range(N)):
        mp = {S: sum(1 << p[i] for i in range(N) if S >> i & 1)
              for S in range(1, FULL + 1)}
        keys.append((p, mp))
    seen = {}
    for w, _ in verts:
        for A in anchors:
            best = None
            for p, mp in keys:
                k = (tuple(sorted((mp[S], x) for S, x in w.items())), mp[A])
                if best is None or k < best:
                    best = k
            if best not in seen:
                seen[best] = (w, A)
    return list(seen.values())


def rat(e):
    e = z3.simplify(e)
    if z3.is_int_value(e):
        return F(e.as_long())
    return F(e.numerator_as_long(), e.denominator_as_long())


def run(side, w, anchor, ineqs, budget=200):
    """Exact feasibility of the failure program.  Returns None (infeasible) or
    the witnessing game."""
    v = [z3.Real(f"v{S}") for S in range(1 << N)]
    s = z3.Solver()
    s.add(v[0] == 0)
    for i in range(N):
        s.add(v[1 << i] == 0)
    s.add(v[FULL] == 1)
    a = len([1 for i in range(N) if anchor >> i & 1])
    if side == "M":
        # nu = v(anchor)/|anchor| is the maximum of v(S)/|S|
        nu = v[anchor] / a
        for S in range(1, FULL + 1):
            s.add(a * v[S] <= len([1 for i in range(N) if S >> i & 1]) * v[anchor])
        h = lambda S: (len([1 for i in range(N) if S >> i & 1])) * nu - v[S]
        hN = N * nu - v[FULL]
    else:
        # lambda = f(anchor)/|anchor| is the minimum of f(S)/|S|
        f = lambda S: v[FULL] - v[FULL ^ S]
        lam = f(anchor) / a
        for S in range(1, FULL + 1):
            s.add(a * f(S) >= len([1 for i in range(N) if S >> i & 1]) * f(anchor))
        h = lambda S: f(S) - len([1 for i in range(N) if S >> i & 1]) * lam
        hN = v[FULL] - N * lam
    s.add(hN > 0)
    s.add(z3.Sum([z3.RealVal(f"{x.numerator}/{x.denominator}") * h(S)
                  for S, x in w.items()]) < hN)

    for _ in range(budget):
        r = s.check()
        # soundness: z3 is complete for linear real arithmetic, so "unknown"
        # must never be silently read as "infeasible".
        assert r in (z3.sat, z3.unsat), f"z3 returned {r}"
        if r == z3.unsat:
            return None
        m = s.model()
        val = [rat(m.eval(v[S], model_completion=True)) for S in range(1 << N)]
        bad = None
        for c in ineqs:
            t = sum(F(c[S]) * val[S] for S in range(1, 1 << N) if c[S])
            if t > 0:
                bad = c
                break
        if bad is None:
            return val
        s.add(z3.Sum([z3.RealVal(bad[S]) * v[S]
                      for S in range(1, 1 << N) if bad[S]]) <= 0)
    raise RuntimeError("cut budget exhausted")


def main():
    ineqs = inequalities(N)
    verts = load_vertices()
    over = [(w, b) for w, b in verts if not b]
    print(f"{len(ineqs)} exact-cone inequalities; {len(verts)} cover vertices, "
          f"{len(over)} strictly over-covering", flush=True)
    anchors = list(range(1, FULL + 1))
    pairs = canon_pairs(over, anchors)
    print(f"{len(over)*len(anchors)} (vertex, anchor) pairs -> "
          f"{len(pairs)} up to permutation", flush=True)

    results = {}
    for side in ("M", "mu"):
        hits = []
        for k, (w, A) in enumerate(pairs):
            out = run(side, w, A, ineqs)
            if out is not None:
                hits.append({"anchor": nm(A),
                             "cover": {nm(S): str(x) for S, x in w.items()},
                             "v": [str(q) for q in out]})
                print(f"  {side}-side FEASIBLE: anchor {nm(A)} cover "
                      f"{ {nm(S): str(x) for S, x in w.items()} }", flush=True)
            if (k + 1) % 200 == 0:
                print(f"  {side}: {k+1}/{len(pairs)} classes, {len(hits)} feasible",
                      flush=True)
        results[side] = hits
        print(f"{side}-side: {len(hits)} feasible classes out of {len(pairs)}",
              flush=True)
    json.dump({"n_inequalities": len(ineqs), "n_vertices": len(verts),
               "n_overcovering": len(over), "n_classes": len(pairs),
               "M_hits": results["M"], "mu_hits": results["mu"]},
              open(f"{SCR}/sel/a3check/a3lp.json", "w"), indent=1)


if __name__ == "__main__":
    main()
