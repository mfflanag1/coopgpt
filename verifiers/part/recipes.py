"""Are the orthant-killing RECIPES numerically realizable?

Discharges the sufficiency side of PROOF_GENERAL.txt: an orthant-killing
certificate is necessary (Lemma I*), but a recipe is only a construction
PRINCIPLE if a genuine exact game carries it.  Here each recipe's coalitions
are imposed as phi-tight on top of the full decisive encoding, and any model is
audited end to end (rebuild v, re-derive exactness by LP, recompute Lmin from
scratch, re-check the configuration).

Usage: python3 recipes.py
"""
import sys, time, json
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, decisive as D
import z3


def layout(p, q):
    m = p + q
    n = m + 2
    return n, m, list(range(p)), list(range(p, m)), n - 2, n - 1


def recipe_sets(p, q):
    n, m, P, Q, f, g = layout(p, q)
    H = (1 << f) | (1 << g)
    if p >= 2 and q >= 2:
        b0 = Q[0]
        ts = [((1 << n) - 1) & ~(1 << b0) & ~(1 << x) for x in P]
        ts.append((1 << g) | sum(1 << i for i in P))
        return "A", ts
    if p == 1 and q >= 3:
        T0 = H | sum(1 << i for i in Q[2:])
        U = (1 << g) | (1 << Q[0]) | (1 << Q[1])
        return "B", [T0, U]
    return None, None


for (p, q) in [(2, 2), (1, 3), (2, 3), (3, 2)]:
    n = p + q + 2
    tag, ts = recipe_sets(p, q)
    if tag is None:
        continue
    found = None
    strats = D.stratifications(n, p, q)
    # the two-stratum shape L < H, where leximin reduces exactly to Lemma I*
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
    line = (f"PART({p},{q}) n={n} recipe {tag} "
            f"[{', '.join(L.nm(n, T) for T in ts)}] strata {stag}: {r}  {el}s")
    if r == z3.sat:
        aud = D.audit_model(n, p, q, s.model(), v)
        line += f"  AUDIT: {aud['verdict']}"
        found = aud
    print(line, flush=True)
    if found and found["verdict"] == "GENUINE WITNESS":
        print(f"    Lmin = {found['lmin']}   strata = {found['strata']}")
