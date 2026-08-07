"""Decide PART(p,q) with the leximin condition included.

The plain relaxation (exact cone + phi in core + tightness + slack + strict
stratification) is too weak: it returns models whose phi is NOT the leximin
point.  Two additions:

  LEXIMIN STAGE 1, as a quantified linear condition
      forall x. x in core(v)  ->  min_i x_i <= min_i phi_i
  Eliminating x from linear constraints whose right-hand sides are the
  variables v keeps the result linear in v, so z3's LRA quantifier handling
  applies.

  REALITY CHECK on any SAT model: rebuild the game from the model's v,
  recompute Lmin from scratch with audit.lmin, and test whether the partition
  configuration really occurs at that Lmin.  A model that survives this is a
  genuine witness; one that does not shows the encoding is still a relaxation.

Usage: python3 decide.py N p q [--lex]
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/census7/zp")

import audit
import exactcone
import z3

BASE = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/census7/zp"


def nm(n, m):
    return exactcone.nm(n, m)


def build(n, p, q, lex, timeout_s=900):
    FULL = (1 << n) - 1
    f, g = n - 2, n - 1
    A = sum(1 << i for i in range(p)) | (1 << f)
    B = sum(1 << i for i in range(p, p + q)) | (1 << g)
    H = (1 << f) | (1 << g)
    assert A | B == FULL and A & B == 0
    v = {S: z3.Real(f"v{S}") for S in range(1, FULL + 1)}
    phi = [z3.Real(f"p{i}") for i in range(n)]
    tmin = z3.Real("tmin")
    s = z3.Solver()
    s.set("timeout", int(timeout_s * 1000))
    for i in range(n):
        s.add(v[1 << i] == 0, phi[i] >= 0)
    s.add(z3.Sum(phi) == v[FULL])
    for S in range(1, FULL):
        s.add(z3.Sum([phi[i] for i in range(n) if S >> i & 1]) >= v[S])
    for lam, r in exactcone.systems(n):
        s.add(z3.Sum([c * v[S] for S, c in lam.items()]) <= r * v[FULL])
    s.add(z3.Sum([phi[i] for i in range(n) if A >> i & 1]) == v[A])
    s.add(z3.Sum([phi[i] for i in range(n) if B >> i & 1]) == v[B])
    s.add(z3.Sum([phi[i] for i in range(n) if H >> i & 1]) == v[H] + 1)
    for i in range(n - 2):
        s.add(phi[i] < phi[f], phi[i] < phi[g])
    # ONE-PACKET NECESSARY CONDITION (paper4 Thm 3): at a slack strict
    # boundary some delta>0 packet exists, so either a proper tight T ⊇ H
    # (full trace) or a tight split pair with delta>0.
    Lp = [i for i in range(n - 2)]
    terms = []
    for T in range(1, FULL):
        if T & H == H:
            terms.append(z3.Sum([phi[i] for i in range(n) if T >> i & 1])
                         == v[T])
    for a1 in range(1 << (n - 2)):
        T1 = (1 << f) | sum(1 << i for i in Lp if a1 >> i & 1)
        for a2 in range(1 << (n - 2)):
            T2 = (1 << g) | sum(1 << i for i in Lp if a2 >> i & 1)
            r = {i: ((T1 >> i & 1) + (T2 >> i & 1)) for i in Lp}
            b = max(r.values()) if r else 0
            delta = 1 + sum(b - r[i] for i in Lp) - b
            if delta <= 0:
                continue
            terms.append(z3.And(
                z3.Sum([phi[i] for i in range(n) if T1 >> i & 1]) == v[T1],
                z3.Sum([phi[i] for i in range(n) if T2 >> i & 1]) == v[T2]))
    s.add(z3.Or(terms))

    if lex:
        for i in range(n):
            s.add(tmin <= phi[i])
        s.add(z3.Or([tmin == phi[i] for i in range(n)]))
        x = [z3.Real(f"x{i}") for i in range(n)]
        body = z3.And([z3.Sum(x) == v[FULL]] +
                      [z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= v[S]
                       for S in range(1, FULL)])
        s.add(z3.ForAll(x, z3.Implies(
            body, z3.Or([x[i] <= tmin for i in range(n)]))))
    return s, v, phi, A, B, H


def reality_check(n, mdl, v, p, q):
    """Rebuild the model's game, recompute Lmin, test the configuration."""
    FULL = (1 << n) - 1
    w = [F(0)] * (1 << n)
    for S in range(1, FULL + 1):
        w[S] = audit.rat(mdl.eval(v[S], model_completion=True))
    if w[FULL] <= 0:
        return {"verdict": "degenerate (v(N) <= 0)"}
    exact = audit.is_exact(n, w) if n <= 5 else None
    phi2 = audit.lmin(n, w)
    if phi2 is None:
        return {"verdict": "no Lmin", "exact": exact}
    f, g = n - 2, n - 1
    A = sum(1 << i for i in range(p)) | (1 << f)
    B = sum(1 << i for i in range(p, p + q)) | (1 << g)
    H = (1 << f) | (1 << g)
    blocks = audit.strata(phi2)
    sufs = [sum(1 << i for b in blocks[j + 1:] for i in b)
            for j in range(len(blocks) - 1)]
    ok_bd = H in sufs
    slack = sum(phi2[i] for i in range(n) if H >> i & 1) - w[H]
    tA = sum(phi2[i] for i in range(n) if A >> i & 1) == w[A]
    tB = sum(phi2[i] for i in range(n) if B >> i & 1) == w[B]
    return {"verdict": "GENUINE WITNESS" if (ok_bd and slack > 0 and tA and tB)
            else "model is not realized at its own Lmin",
            "exact": exact, "lmin": [str(x) for x in phi2],
            "H_is_strict_boundary": ok_bd, "slack": str(slack),
            "A_tight": tA, "B_tight": tB,
            "v": {nm(n, S): str(w[S]) for S in range(1, FULL + 1) if w[S] != 0}}


def main():
    n, p, q = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    lex = "--lex" in sys.argv
    s, v, phi, A, B, H = build(n, p, q, lex)
    t0 = time.time()
    res = s.check()
    el = round(time.time() - t0, 1)
    tag = "with leximin stage 1" if lex else "relaxation only"
    print(f"PART({p},{q}) n={n} [{tag}]: {res}  ({el}s)")
    out = {"n": n, "p": p, "q": q, "lex": lex, "status": str(res),
           "elapsed": el}
    if res == z3.sat:
        mdl = s.model()
        out["phi"] = [str(audit.rat(mdl.eval(phi[i], model_completion=True)))
                      for i in range(n)]
        print("  phi =", out["phi"])
        rc = reality_check(n, mdl, v, p, q)
        out["reality_check"] = rc
        print("  reality check:", rc["verdict"])
        for k in ("exact", "lmin", "H_is_strict_boundary", "slack",
                  "A_tight", "B_tight"):
            if k in rc:
                print(f"     {k}: {rc[k]}")
    json.dump(out, open(f"{BASE}/decide_{n}_{p}_{q}{'_lex' if lex else ''}.json",
                        "w"), indent=1)


if __name__ == "__main__":
    main()
