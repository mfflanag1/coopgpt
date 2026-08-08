"""Task #27, increment 3: EMPIRICAL SCREEN for middle-stratum lemmas.

The net stalls at 132 because L7/L7' speak only about the extreme strata.
Rather than guess, this screens a batch of candidate statements about the
middle strata against all 2668 harvested genuine exact games.  A candidate that
survives gets proved; one that dies gets recorded as dead so nobody tries it
again.  Nothing here is used until it is proved.

Candidates (x = Lmin, z = Lmax; Lmin strata poorest-first B^0..B^{A-1} at
levels m_0<...; Lmax strata poorest-first D^0..D^{B-1} at levels M_0<...):

 C1  for EVERY Lmax stratum l, some i in D^l has x_i >= M_l
     (the generalization of L7, which is the case l = B-1)
 C2  for EVERY Lmin stratum k, some i in B^k has z_i <= m_k
     (the generalization of L7')
 C3  z(D1) <= x(D1)              -- top-stratum sum domination
 C4  x(P)  >= z(P)               -- bottom-stratum sum domination
 C5  for every Lmax rich suffix U (union of the top strata): z(U) <= x(U)
 C6  for every Lmin poor prefix L (union of the bottom strata): x(L) >= z(L)
 C7  LORENZ: for every k, the sum of the k smallest entries of x is >= the sum
     of the k smallest entries of z.  (True when the core has a Lorenz-greatest
     element -- e.g. convex games -- but exact games need not be convex, so
     this is exactly the sort of thing to test rather than assume.)
 C8  for every Lmax stratum l >= 1 and the corresponding stage-1 face
     statement instantiated at x: if max_i x_i <= M then some i in D^l has
     x_i >= M_l   (vacuous unless x happens to lie in the face; counted
     separately so a vacuous pass is visible)
"""
from __future__ import annotations
import itertools
import json
import sys
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE + "/lib")
import audit

N, FULL = 5, 31


def main():
    st = {"games": 0}
    for c in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"):
        st[c + "_cases"] = 0
        st[c + "_fail"] = 0
    ex = {}
    for src in ("harvest_seed22.json", "harvest_seed777.json"):
        for r in json.load(open(f"{HERE}/{src}"))["records"]:
            T = F(r["T"])
            x = [F(t) / T for t in r["lmin"]]
            z = [F(t) / T for t in r["lmax"]]
            st["games"] += 1
            sx = audit.strata(x)                    # poorest first
            sz = audit.strata(z)
            S = lambda p, idx: sum(p[i] for i in idx)
            mu, M = min(x), max(z)
            P, D1 = sx[0], sz[-1]
            for l, D in enumerate(sz):
                Ml = z[D[0]]
                st["C1_cases"] += 1
                if max(x[i] for i in D) < Ml:
                    st["C1_fail"] += 1
                    ex.setdefault("C1", r)
            for k, B in enumerate(sx):
                mk = x[B[0]]
                st["C2_cases"] += 1
                if min(z[i] for i in B) > mk:
                    st["C2_fail"] += 1
                    ex.setdefault("C2", r)
            st["C3_cases"] += 1
            if S(z, D1) > S(x, D1):
                st["C3_fail"] += 1
                ex.setdefault("C3", r)
            st["C4_cases"] += 1
            if S(x, P) < S(z, P):
                st["C4_fail"] += 1
                ex.setdefault("C4", r)
            for l in range(len(sz)):
                U = [i for b in sz[l:] for i in b]
                st["C5_cases"] += 1
                if S(z, U) > S(x, U):
                    st["C5_fail"] += 1
                    ex.setdefault("C5", r)
            for k in range(len(sx)):
                L = [i for b in sx[:k + 1] for i in b]
                st["C6_cases"] += 1
                if S(x, L) < S(z, L):
                    st["C6_fail"] += 1
                    ex.setdefault("C6", r)
            xs, zs = sorted(x), sorted(z)
            for k in range(1, N + 1):
                st["C7_cases"] += 1
                if sum(xs[:k]) < sum(zs[:k]):
                    st["C7_fail"] += 1
                    ex.setdefault("C7", r)
            if max(x) <= M:
                for l, D in enumerate(sz):
                    st["C8_cases"] += 1
                    if max(x[i] for i in D) < z[D[0]]:
                        st["C8_fail"] += 1
    print(json.dumps(st, indent=1))
    print()
    for c in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"):
        v = "SURVIVES" if st[c + "_fail"] == 0 else f"DEAD ({st[c+'_fail']})"
        print(f"  {c}: {v}   ({st[c+'_cases']} cases)")
    json.dump({"stats": st,
               "counterexamples": {k: {"v": r["v"], "T": r["T"],
                                       "lmin": r["lmin"], "lmax": r["lmax"]}
                                   for k, r in ex.items()}},
              open(f"{HERE}/cands.json", "w"), indent=1)


if __name__ == "__main__":
    main()
