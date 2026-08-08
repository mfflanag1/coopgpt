"""INDEPENDENT cross-check of decisive.py, by enumeration of tight families.

Discharges: the same verdicts as decisive.py, by a logically different route.
decisive.py hands z3 one monolithic formula in which tightness is implicit and
leximin is a Farkas certificate.  Here tightness is made EXPLICIT and the two
halves are separated:

  * COMBINATORIAL half.  Once the tight family Tt and the strata B_1<...<B_k
    are fixed, "phi = Lmin" depends on NOTHING else: the tangent cone of the
    core at phi is  D = {d : d(N)=0, d(T)>=0 for T in Tt},  and phi is leximin
    iff for every stage t there is no d in D with d|B_<t = 0, d|B_t >= 0,
    d|B_t != 0.  That is an exact rational LP with no game in it.
    The condition is MONOTONE INCREASING in Tt (more tight sets, smaller cone).

  * NUMERIC half.  Given Tt, ask for an exact singleton-normalized game whose
    Lmin-tight family CONTAINS Tt and which carries the configuration.  That is
    an exact LP (exactness encoded by one attaining core point per coalition).
    It is MONOTONE DECREASING in Tt (more equalities, fewer games).

The two monotonicities give a terminating CEGAR: start from {S1,S2}; if the
numeric LP is infeasible, prune (every superset is too); if leximin holds,
report a candidate; otherwise take an improving direction d and branch on the
coalitions T with d(T) < 0, since the true tight family must contain one of
them in order to block d.

Usage: python3 families.py N P Q [--limit NODES]
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L
import decisive as D
import z3


# ------------------------------------------------------- combinatorial half

def improving_direction(n, family, blocks):
    """Return (t, i, d) for a leximin-improving direction, or None."""
    FULL = (1 << n) - 1
    pre = []
    for t, blk in enumerate(blocks):
        d = [z3.Real(f"d{i}") for i in range(n)]
        base = [z3.Sum(d) == 0]
        for T in family:
            base.append(z3.Sum([d[i] for i in range(n) if T >> i & 1]) >= 0)
        for l in pre:
            base.append(d[l] == 0)
        for c in blk:
            base.append(d[c] >= 0)
        for i in blk:
            s = z3.Solver()
            s.add(base)
            s.add(d[i] == 1)               # cone: scale any positive to 1
            r = s.check()
            assert r != z3.unknown
            if r == z3.sat:
                mdl = s.model()
                dv = [L.rat(mdl.eval(d[j], model_completion=True))
                      for j in range(n)]
                return (t, i, dv)
        pre = pre + blk
    return None


# -------------------------------------------------------------- numeric half

def numeric_feasible(n, p, q, family, blocks, timeout_s=300):
    """Is there an exact singleton-normalized game, with the PART(p,q)
    configuration and the declared strata, whose Lmin-tight family CONTAINS
    `family`?  (Relaxation: other coalitions may also be tight.)"""
    FULL = (1 << n) - 1
    m = p + q
    f, g = n - 2, n - 1
    S1 = sum(1 << i for i in range(p)) | (1 << f)
    S2 = sum(1 << i for i in range(p, m)) | (1 << g)
    H = (1 << f) | (1 << g)
    v = {S: z3.Real(f"v{S}") for S in range(1, FULL + 1)}
    phi = [z3.Real(f"phi{i}") for i in range(n)]
    s = z3.Solver()
    s.set("timeout", int(timeout_s * 1000))

    def tot(vec, S):
        return z3.Sum([vec[i] for i in range(n) if S >> i & 1])

    for i in range(n):
        s.add(v[1 << i] == 0)
    s.add(z3.Sum(phi) == v[FULL])
    for S in range(1, FULL):
        s.add(tot(phi, S) >= v[S])
    for S in range(1, FULL):                      # exactness
        z = [z3.Real(f"z{S}_{i}") for i in range(n)]
        s.add(z3.Sum(z) == v[FULL])
        for A in range(1, FULL):
            s.add(tot(z, A) >= v[A])
        s.add(tot(z, S) == v[S])
    s.add(tot(phi, S1) == v[S1])
    s.add(tot(phi, S2) == v[S2])
    s.add(tot(phi, H) == v[H] + 1)
    for blk in blocks:
        for i in blk[1:]:
            s.add(phi[i] == phi[blk[0]])
    for t in range(len(blocks) - 1):
        s.add(phi[blocks[t][0]] < phi[blocks[t + 1][0]])
    s.add(phi[blocks[0][0]] >= 0)
    for T in family:
        s.add(tot(phi, T) == v[T])
    r = s.check()
    assert r != z3.unknown, "numeric LP returned unknown"
    return r == z3.sat


# ---------------------------------------------------------------------- CEGAR

def search(n, p, q, blocks, limit=200000, verbose=False):
    FULL = (1 << n) - 1
    m = p + q
    f, g = n - 2, n - 1
    S1 = sum(1 << i for i in range(p)) | (1 << f)
    S2 = sum(1 << i for i in range(p, m)) | (1 << g)
    root = frozenset({S1, S2})
    seen = set()
    stack = [root]
    nodes = 0
    pruned = 0
    candidates = []
    while stack:
        fam = stack.pop()
        if fam in seen:
            continue
        seen.add(fam)
        nodes += 1
        if nodes > limit:
            raise RuntimeError("node limit exceeded")
        if not numeric_feasible(n, p, q, sorted(fam), blocks):
            pruned += 1
            continue
        imp = improving_direction(n, sorted(fam), blocks)
        if imp is None:
            candidates.append(sorted(fam))
            continue
        t, i, d = imp
        for T in range(1, FULL):
            if T in fam:
                continue
            if sum(d[j] for j in range(n) if T >> j & 1) < 0:
                stack.append(fam | {T})
    return {"nodes": nodes, "pruned": pruned, "candidates": candidates}


def main():
    n, p, q = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    limit = 200000
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    strats = D.stratifications(n, p, q)
    print(f"PART({p},{q}) n={n}: tight-family CEGAR over {len(strats)} "
          f"stratifications", flush=True)
    out = []
    tot_nodes = tot_cand = 0
    for idx, (blocks, tag) in enumerate(strats):
        t0 = time.time()
        res = search(n, p, q, blocks, limit=limit)
        el = round(time.time() - t0, 2)
        tot_nodes += res["nodes"]
        tot_cand += len(res["candidates"])
        print(f"  [{idx:3d}] {tag:38s} nodes={res['nodes']:6d} "
              f"pruned={res['pruned']:6d} candidates={len(res['candidates']):4d}"
              f"  {el:7.2f}s", flush=True)
        if res["candidates"]:
            for c in res["candidates"][:5]:
                print("        CANDIDATE tight family:",
                      [L.nm(n, T) for T in c], flush=True)
        out.append({"idx": idx, "tag": tag, "nodes": res["nodes"],
                    "pruned": res["pruned"],
                    "candidates": [[L.nm(n, T) for T in c]
                                   for c in res["candidates"]]})
    print(f"TOTAL nodes={tot_nodes} candidates={tot_cand}")
    print("VERDICT:", "IMPOSSIBLE (no candidate tight family survives)"
          if tot_cand == 0 else "candidates exist -- must be audited")
    json.dump(out, open(f"/private/tmp/claude-501/-Users-maxf/"
                        f"f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23/"
                        f"families_{n}_{p}_{q}.json", "w"), indent=1)


if __name__ == "__main__":
    main()


# ------------------------------------------------- drop-the-hypothesis variant

def numeric_feasible_req(n, p, q, family, blocks, required, timeout_s=300):
    """As numeric_feasible, but the configuration imposes tightness only for
    the coalitions in `required` (a subset of {S1, S2}).  Used by the
    drop-the-hypothesis control: with S2 dropped, a slack h=2 boundary at n=5
    carrying a tight trace-{f} coalition DOES exist, so the CEGAR must find
    candidates -- at the same n and through the same code as the UNSAT runs."""
    FULL = (1 << n) - 1
    m = p + q
    f, g = n - 2, n - 1
    H = (1 << f) | (1 << g)
    v = {S: z3.Real(f"v{S}") for S in range(1, FULL + 1)}
    phi = [z3.Real(f"phi{i}") for i in range(n)]
    s = z3.Solver()
    s.set("timeout", int(timeout_s * 1000))

    def tot(vec, S):
        return z3.Sum([vec[i] for i in range(n) if S >> i & 1])

    for i in range(n):
        s.add(v[1 << i] == 0)
    s.add(z3.Sum(phi) == v[FULL])
    for S in range(1, FULL):
        s.add(tot(phi, S) >= v[S])
    for S in range(1, FULL):
        z = [z3.Real(f"z{S}_{i}") for i in range(n)]
        s.add(z3.Sum(z) == v[FULL])
        for A in range(1, FULL):
            s.add(tot(z, A) >= v[A])
        s.add(tot(z, S) == v[S])
    for T in required:
        s.add(tot(phi, T) == v[T])
    s.add(tot(phi, H) == v[H] + 1)
    for blk in blocks:
        for i in blk[1:]:
            s.add(phi[i] == phi[blk[0]])
    for t in range(len(blocks) - 1):
        s.add(phi[blocks[t][0]] < phi[blocks[t + 1][0]])
    s.add(phi[blocks[0][0]] >= 0)
    for T in family:
        s.add(tot(phi, T) == v[T])
    r = s.check()
    assert r != z3.unknown
    return r == z3.sat


def search_req(n, p, q, blocks, required, limit=200000):
    FULL = (1 << n) - 1
    root = frozenset(required)
    seen, stack, nodes, pruned, candidates = set(), [root], 0, 0, []
    while stack:
        fam = stack.pop()
        if fam in seen:
            continue
        seen.add(fam)
        nodes += 1
        if nodes > limit:
            raise RuntimeError("node limit exceeded")
        if not numeric_feasible_req(n, p, q, sorted(fam), blocks, required):
            pruned += 1
            continue
        imp = improving_direction(n, sorted(fam), blocks)
        if imp is None:
            candidates.append(sorted(fam))
            continue
        t, i, d = imp
        for T in range(1, FULL):
            if T in fam:
                continue
            if sum(d[j] for j in range(n) if T >> j & 1) < 0:
                stack.append(fam | {T})
    return {"nodes": nodes, "pruned": pruned, "candidates": candidates}
