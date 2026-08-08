"""Configuration census of random exact 5-player games (task #22).

Discharges: (i) the POSITIVE CONTROLS demanded by campaign discipline -- every
finite check below must be shown non-vacuous on a genuine game in the
configuration it constrains; (ii) the empirical map of which (Lmin-shape,
Lmax-shape, zero-position) configurations occur at all and with what ratios.

Games are lower envelopes of k common-total nonnegative allocations, which is
exactly the class of exact games (v exact <=> v is the lower envelope of its
own core).  Lmin and Lmax are recomputed by staged exact z3 optimization
(verifiers/lib/audit.py, verifiers/lib/lmax.py) -- no shortcuts.

Output: harvest.json = one record per game with positive ratio OR with a zero
in Lmax, keyed by configuration.
"""
from __future__ import annotations
import json
import random
import sys
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE + "/lib")
import audit
import lmax as lmaxmod

N, FULL = 5, 31


def shape(p):
    return tuple(len(b) for b in audit.strata(p))


def profile(w):
    x = audit.lmin(N, w)
    z = lmaxmod.lmax(N, w)
    if x is None or z is None:
        return None
    T = w[FULL]
    mu, M = min(x), max(z)
    ratio = sum(abs(x[i] - z[i]) for i in range(N)) / T
    sx = audit.strata(x)
    sz = audit.strata(z)
    # which Lmin stratum does each Lmax-zero player sit in? (0 = poorest)
    lminidx = {}
    for k, b in enumerate(sx):
        for i in b:
            lminidx[i] = k
    Z = [i for i in range(N) if z[i] == 0]
    return {
        "v": [str(q) for q in w],
        "T": str(T),
        "lmin": [str(q) for q in x], "lmax": [str(q) for q in z],
        "lmin_shape": shape(x), "lmax_shape": shape(z),
        "mu": str(mu / T), "M": str(M / T), "ratio": str(ratio),
        "nzero": len(Z),
        "zero_in_lmin_strata": sorted(lminidx[i] for i in Z),
    }


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 22
    rng = random.Random(seed)
    out = f"{HERE}/harvest_seed{seed}.json"
    recs, counts = [], {}
    for t in range(trials):
        tot = rng.choice([4, 5, 6, 8, 10, 12, 16, 20, 24])
        npts = rng.randint(2, 6)
        hi = rng.choice([tot, tot, tot // 2 + 1])
        gens = audit.rand_gens(N, rng, npts, tot, max(hi, 1))
        v = audit.envelope(N, gens)
        w, _ = audit.normalize(N, v)
        if w[FULL] == 0:
            continue
        p = profile(w)
        if p is None:
            continue
        key = (str(p["lmin_shape"]), str(p["lmax_shape"]), p["nzero"],
               str(p["zero_in_lmin_strata"]))
        c = counts.setdefault(str(key), {"n": 0, "maxratio": "0", "poszero": 0})
        c["n"] += 1
        if F(p["ratio"]) > F(c["maxratio"]):
            c["maxratio"] = p["ratio"]
        if F(p["ratio"]) > 0 or p["nzero"]:
            recs.append(p)
        if (t + 1) % 250 == 0:
            print(f"  {t+1}/{trials} draws, {len(recs)} kept, "
                  f"{len(counts)} configurations", flush=True)
            json.dump({"counts": counts, "records": recs},
                      open(out, "w"), indent=1)
    json.dump({"counts": counts, "records": recs},
              open(out, "w"), indent=1)
    print(f"DONE {trials} draws, {len(recs)} records, {len(counts)} configurations")
    for k in sorted(counts, key=lambda k: -F(counts[k]["maxratio"])):
        print(f"  {k}  n={counts[k]['n']:4d}  maxratio={counts[k]['maxratio']}")


if __name__ == "__main__":
    main()
