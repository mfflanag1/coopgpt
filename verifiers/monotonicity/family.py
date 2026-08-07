"""Constructive BT family: parametrize the refuting base game's rows.

Normalized rows of the witness (common total 18; every coordinate is zero
in some row, so by paper4's lower-envelope lemma v is automatically exact
and singleton-normalized -- exactness is FREE in this parametrization):

   A = (0, a, 0, b, 0, 0)          a + b       = T
   B = (0, c, 0, e, f, g)          c + e + f + g = T
   C = (h, 0, i, 0, j, 0)          h + i + j   = T
   witness: a=11,b=7, c=10,e=4,f=3,g=1, h=2,i=1,j=15, T=18.

A candidate COUNTS as a family member when: phi=Lmin(v) is BT (top stratum
phi-tight, some outer suffix slack), some S admits an exactness-preserving
bump past s_phi(S), and the resulting violation refutes C-A while
satisfying C-B.
"""
from __future__ import annotations
import json, sys, time, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3")
import audit
from hunt2 import boundaries, nm, core_expr, dmax
from probeA_sweep import exact_lp

N = 6; FULL = 63
BASE = dict(a=11, b=7, c=10, e=4, f=3, g=1, h=2, i=1, j=15, T=18)


def rows(p):
    A = (0, p['a'], 0, p['b'], 0, 0)
    B = (0, p['c'], 0, p['e'], p['f'], p['g'])
    C = (p['h'], 0, p['i'], 0, p['j'], 0)
    return A, B, C


def ok_rows(p):
    R = rows(p)
    if any(q < 0 for r in R for q in r):
        return None
    if any(sum(r) != p['T'] for r in R):
        return None
    for k in range(N):                     # singleton-normalized
        if min(r[k] for r in R) != 0:
            return None
    return R


def analyse(p, want_all=False):
    """Returns None, or a dict describing the BT violation this member gives."""
    R = ok_rows(p)
    if R is None:
        return None
    gens = [tuple(F(q) for q in r) for r in R]
    w = audit.envelope(N, gens)            # exact + normalized by construction
    if w[FULL] == 0:
        return None
    phi = audit.lmin(N, w)
    if phi is None:
        return None
    bnd = boundaries(N, w, phi)
    if len(bnd) < 2 or bnd[-1][1] != 0:
        return None                        # need BT: top stratum tight
    if not any(s > 0 for _, s in bnd):
        return None
    blocks = audit.strata(phi)
    sl = [q for q, (H, s) in enumerate(bnd) if s > 0]
    pblk = max(sl) + 1
    pred = sum(1 << q for q in blocks[pblk])
    x, base = core_expr(N, w)
    out = []
    for S in range(1, FULL):
        if bin(S).count("1") < 2:
            continue
        sS = sum(phi[q] for q in range(N) if S >> q & 1) - w[S]
        g = min(w[S | (1 << q)] - w[S] for q in range(N) if not S >> q & 1)
        if g <= sS:
            continue
        dm = dmax(N, w, S, x, base)
        if dm is None or dm <= sS:
            continue
        for d in sorted({dm, sS + (dm - sS) / 2, sS + (dm - sS) / 4}):
            if d <= sS:
                continue
            w2 = list(w); w2[S] = w[S] + d
            if not exact_lp(N, w2):
                continue
            phi2 = audit.lmin(N, w2)
            if phi2 is None:
                continue
            W = [q for q in range(N) if S >> q & 1 and phi2[q] < phi[q]]
            if not W:
                continue
            Wm = sum(1 << q for q in W)
            CA = Wm in [H for H, s in bnd if s > 0]
            CB = (Wm == pred)
            out.append({"S": nm(N, S), "Smask": S, "d": str(d), "d_max": str(dm),
                        "s_phi_S": str(sS), "W": nm(N, Wm), "pred": nm(N, pred),
                        "CA": CA, "CB": CB,
                        "phi2": [str(q) for q in phi2]})
            if not want_all:
                break
        if out and not want_all:
            break
    if not out:
        return None
    return {"params": dict(p), "rows": [list(r) for r in R],
            "phi": [str(q) for q in phi],
            "strata": [[q + 1 for q in b] for b in blocks],
            "bnd": [[nm(N, H), str(s)] for H, s in bnd],
            "viol": out}


def main():
    mode = sys.argv[1]; budget = float(sys.argv[2])
    t0 = time.time(); hits = []; tried = 0
    if mode == "one":                       # one parameter at a time
        for k in ("a", "c", "e", "f", "g", "h", "i", "T"):
            for delta in range(-6, 13):
                if time.time() - t0 > budget:
                    break
                p = dict(BASE)
                p[k] = BASE[k] + delta
                if k == "a": p["b"] = p["T"] - p["a"]
                if k in ("c", "e", "f"): p["g"] = p["T"] - p["c"] - p["e"] - p["f"]
                if k == "g": p["c"] = p["T"] - p["e"] - p["f"] - p["g"]
                if k in ("h", "i"): p["j"] = p["T"] - p["h"] - p["i"]
                if k == "T":
                    p["b"] = p["T"] - p["a"]
                    p["g"] = p["T"] - p["c"] - p["e"] - p["f"]
                    p["j"] = p["T"] - p["h"] - p["i"]
                tried += 1
                r = analyse(p)
                if r:
                    r["axis"] = f"{k}{delta:+d}"
                    hits.append(r)
                    print(f"HIT {k}{delta:+d}  rows={r['rows']} phi={r['phi']} "
                          f"bnd={r['bnd']} W={r['viol'][0]['W']} CA={r['viol'][0]['CA']} "
                          f"CB={r['viol'][0]['CB']}", flush=True)
    else:                                   # bounded box around the witness
        import random
        rng = random.Random(int(sys.argv[3]))
        while time.time() - t0 < budget:
            p = dict(BASE)
            p["T"] = BASE["T"] + rng.randint(-4, 14)
            p["a"] = BASE["a"] + rng.randint(-4, 8); p["b"] = p["T"] - p["a"]
            p["c"] = BASE["c"] + rng.randint(-4, 8)
            p["e"] = BASE["e"] + rng.randint(-3, 5)
            p["f"] = BASE["f"] + rng.randint(-3, 5)
            p["g"] = p["T"] - p["c"] - p["e"] - p["f"]
            p["h"] = BASE["h"] + rng.randint(-2, 5)
            p["i"] = BASE["i"] + rng.randint(-1, 5)
            p["j"] = p["T"] - p["h"] - p["i"]
            tried += 1
            r = analyse(p)
            if r:
                hits.append(r)
                print(f"HIT {p} phi={r['phi']} bnd={r['bnd']} "
                      f"W={r['viol'][0]['W']} CA={r['viol'][0]['CA']} "
                      f"CB={r['viol'][0]['CB']}", flush=True)
    res = {"mode": mode, "tried": tried, "hits": hits, "n_hits": len(hits),
           "distinct_rows": len({tuple(map(tuple, h["rows"])) for h in hits}),
           "all_refute_CA": all(not v["CA"] for h in hits for v in h["viol"]),
           "all_satisfy_CB": all(v["CB"] for h in hits for v in h["viol"])}
    json.dump(res, open(f"family_{mode}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "hits"}))


if __name__ == "__main__":
    main()
