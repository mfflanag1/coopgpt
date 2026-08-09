"""Construct a genuine CFG game directly, rather than sampling for it.
Target (paper5 cor:cfg): Lmin = (T/8,T/8,T/8,5T/16,5T/16), Lmax = (0,T/4 x4).
Take T = 16 so everything is integral: Lmin = (2,2,2,5,5), Lmax = (0,4,4,4,4).
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L, lmax as LM

n, FULL = 5, 31
cands = [
    [(2,2,2,5,5), (0,4,4,4,4)],
    [(2,2,2,5,5), (0,4,4,4,4), (8,0,0,4,4)],
    [(2,2,2,5,5), (0,4,4,4,4), (0,8,0,4,4), (0,0,8,4,4)],
    [(2,2,2,5,5), (0,4,4,4,4), (8,4,4,0,0)],
    [(2,2,2,5,5), (0,4,4,4,4), (2,2,2,10,0), (2,2,2,0,10)],
]
for idx, rows in enumerate(cands):
    gens = [tuple(F(q) for q in r) for r in rows]
    if len({sum(g) for g in gens}) != 1:
        print(idx, "skip: totals differ"); continue
    if any(min(g[i] for g in gens) != 0 for i in range(n)):
        print(idx, "skip: not singleton-normalized"); continue
    w, sh = L.normalize(n, L.envelope(n, gens))
    x = L.lmin(n, w); z = LM.lmax(n, w)
    T = w[FULL]
    sx, sz = L.strata(x), L.strata(z)
    cfg = ([len(b) for b in sx] == [3,2] and [len(b) for b in sz] == [1,4]
           and z[sz[0][0]] == 0)
    print(f"[{idx}] rows={rows}")
    print(f"     Lmin={[str(q) for q in x]}  Lmax={[str(q) for q in z]}  T={T}  CFG={cfg}")
    if not cfg:
        continue
    P, R = set(sx[0]), set(sx[1]); j = sz[0][0]
    print(f"     mu/T={x[sx[0][0]]/T}  rho/T={x[sx[1][0]]/T}  j={L.LETTERS[j]}  j in P: {j in P}")
    pp = sorted(P - {j})
    viol = []
    for S in range(1, FULL):
        U = FULL ^ S
        if sum(x[i] for i in range(n) if S >> i & 1) != T - w[U]:
            continue
        lhs = len([i for i in pp if S >> i & 1]); rhs = len([i for i in R if S >> i & 1])
        if lhs > rhs:
            a = len([i for i in P if U >> i & 1]); b = len([i for i in R if U >> i & 1])
            viol.append((L.nm(n,S), f"{lhs}>{rhs}", (a,b,1 if (U>>j)&1 else 0)))
    print(f"     KEY LEMMA violations (expected, since mu = T/8): {viol}")
    break
