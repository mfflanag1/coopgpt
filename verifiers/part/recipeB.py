"""Recipe B was WRONG (UNSAT).  This tests the corrected recipe B', read off
from what the real PART(1,3) witness actually does: two type-(1,1) coalitions
(both containing H) rather than one type-(1,1) and one type-(0,1).

   B'  (p = 1, q >= 3):   T1 = H u P u {b1},   T2 = H u {b2}.
   normals: T1 -> (0 ; -1 on Q\{b1}),  T2 -> (-1 ; -1 on Q\{b2}).
   Together they kill the nonnegative orthant, and Lemma 3 permits T2 because
   |Q \ T2| = q - 1 >= 2 exactly when q >= 3.
"""
import sys, time
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, decisive as D
import z3


def layout(p, q):
    m = p + q
    n = m + 2
    return n, m, list(range(p)), list(range(p, m)), n - 2, n - 1


def killsorthant(p, q, ts):
    n, m, P, Q, f, g = layout(p, q)
    d = [z3.Real(f"d{i}") for i in range(m)]
    s = z3.Solver()
    for i in range(m):
        s.add(d[i] >= 0)
    for T in ts:
        nu = [((T >> i) & 1) - ((T >> f) & 1) for i in P] + \
             [((T >> i) & 1) - ((T >> g) & 1) for i in Q]
        s.add(z3.Sum([nu[i] * d[i] for i in range(m)]) >= 0)
    s.add(z3.Sum(d) > 0)
    return s.check() == z3.unsat


for (p, q) in [(1, 3), (1, 4)]:
    n, m, P, Q, f, g = layout(p, q)
    H = (1 << f) | (1 << g)
    T1 = H | sum(1 << i for i in P) | (1 << Q[0])
    T2 = H | (1 << Q[1])
    ts = [T1, T2]
    print(f"PART({p},{q}) recipe B' = [{', '.join(L.nm(n,T) for T in ts)}]"
          f"  kills orthant: {killsorthant(p, q, ts)}")
    strats = D.stratifications(n, p, q)
    idx = [i for i, (b, t) in enumerate(strats)
           if len(b) == 2 and len(b[0]) == p + q][0]
    blocks, stag = strats[idx]
    s, v, phi, cfg = D.build(n, p, q, blocks)
    s.set("timeout", 1800 * 1000)
    for T in ts:
        s.add(z3.Sum([phi[i] for i in range(n) if T >> i & 1]) == v[T])
    t0 = time.time()
    r = s.check()
    el = round(time.time() - t0, 1)
    out = f"   strata {stag}: {r}  {el}s"
    if r == z3.sat:
        a = D.audit_model(n, p, q, s.model(), v)
        out += f"  AUDIT: {a['verdict']}  Lmin={a['lmin']}"
    print(out, flush=True)
