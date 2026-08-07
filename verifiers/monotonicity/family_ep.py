"""Targeted search for a monotonicity failure at an EXACT-PARTITION base,
inside the parameter region of the tight-top-stratum family.

Rationale: the mechanism that broke C-B was internal redistribution inside a
TIGHT suffix (the top stratum held its total exactly while one member paid
and another was paid).  That mechanism needs no slack suffix at all, so the
natural place to look for an exact-partition failure is the same family with
its one slack suffix closed to zero.  Same rows as ca/family.py; here we keep
members whose phi has NO slack richer suffix.
"""
from __future__ import annotations
import json, random, sys, time
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3")
import audit
from hunt2 import boundaries, nm, core_expr, dmax
from probeA_sweep import exact_lp

N = 6; FULL = 63
BASE = dict(a=11, b=7, c=10, e=4, f=3, g=1, h=2, i=1, j=15, T=18)


def rows(p):
    return ((0, p['a'], 0, p['b'], 0, 0),
            (0, p['c'], 0, p['e'], p['f'], p['g']),
            (p['h'], 0, p['i'], 0, p['j'], 0))


def main(seed, budget, out):
    rng = random.Random(seed); t0 = time.time()
    st = {"seed": seed, "tried": 0, "valid": 0, "EP": 0, "EP2": 0,
          "prefilter": 0, "windows": 0, "bumps": 0, "viol_exact": 0,
          "hits": [], "elapsed": 0}
    while time.time() - t0 < budget:
        p = dict(BASE)
        p["T"] = BASE["T"] + rng.randint(-6, 18)
        p["a"] = BASE["a"] + rng.randint(-6, 10); p["b"] = p["T"] - p["a"]
        p["c"] = BASE["c"] + rng.randint(-6, 10)
        p["e"] = BASE["e"] + rng.randint(-4, 8)
        p["f"] = BASE["f"] + rng.randint(-3, 8)
        p["g"] = p["T"] - p["c"] - p["e"] - p["f"]
        p["h"] = BASE["h"] + rng.randint(-2, 8)
        p["i"] = BASE["i"] + rng.randint(-1, 8)
        p["j"] = p["T"] - p["h"] - p["i"]
        st["tried"] += 1
        R = rows(p)
        if any(q < 0 for r in R for q in r):
            continue
        if any(sum(r) != p["T"] for r in R):
            continue
        if any(min(r[k] for r in R) != 0 for k in range(N)):
            continue
        st["valid"] += 1
        gens = [tuple(F(q) for q in r) for r in R]
        w = audit.envelope(N, gens)
        if w[FULL] == 0:
            continue
        phi = audit.lmin(N, w)
        if phi is None:
            continue
        bnd = boundaries(N, w, phi)
        if any(s > 0 for _, s in bnd):
            continue                       # want exact partition only
        st["EP"] += 1
        st["EP2"] += bool(bnd)
        x, base = core_expr(N, w)
        for S in range(1, FULL):
            if bin(S).count("1") < 2 or time.time() - t0 > budget:
                continue
            sS = sum(phi[q] for q in range(N) if S >> q & 1) - w[S]
            g = min(w[S | (1 << q)] - w[S] for q in range(N) if not S >> q & 1)
            if g <= sS:
                continue
            st["prefilter"] += 1
            dm = dmax(N, w, S, x, base)
            if dm is None:
                continue
            if dm > sS:
                st["windows"] += 1
            for d in sorted({dm, sS + (dm - sS) / 2, sS + (dm - sS) / 4,
                             sS + 3 * (dm - sS) / 4}):
                if d <= sS:
                    continue
                w2 = list(w); w2[S] = w[S] + d
                st["bumps"] += 1
                if not exact_lp(N, w2):
                    continue
                phi2 = audit.lmin(N, w2)
                if phi2 is None:
                    continue
                W = [q for q in range(N) if S >> q & 1 and phi2[q] < phi[q]]
                if not W:
                    continue
                Wm = sum(1 << q for q in W)
                st["viol_exact"] += 1
                rec = {"params": p, "rows": [list(r) for r in R],
                       "phi": [str(q) for q in phi],
                       "phi2": [str(q) for q in phi2], "S": nm(N, S),
                       "d": str(d), "s_phi_S": str(sS), "d_max": str(dm),
                       "W": nm(N, Wm),
                       "boundaries": [[nm(N, H), str(s)] for H, s in bnd],
                       "s_phi_W": str(sum(phi[q] for q in range(N)
                                          if Wm >> q & 1) - w[Wm])}
                st["hits"].append(rec)
                print("*** EXACT-PARTITION FAILURE ***", json.dumps(rec),
                      flush=True)
    st["elapsed"] = round(time.time() - t0, 1)
    json.dump(st, open(out, "w"), indent=1)
    print(json.dumps({k: y for k, y in st.items() if k != "hits"}))


if __name__ == "__main__":
    main(int(sys.argv[1]), float(sys.argv[2]),
         f"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/"
         f"scratchpad/ca/h7fam_{sys.argv[1]}.json")
