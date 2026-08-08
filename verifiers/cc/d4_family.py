"""d4: regenerate the BT constructive family and record, for every member, the
data the closed forms have to reproduce: phi, the stratum shape, the tight
coalitions at phi, every richer-suffix slack, H*, and the exact bump window
(s_phi(S), alpha_ex(S)] together with the violation it produces.

BT parametrization (paper4 / verifiers/monotonicity/family.py):
    A = (0, a, 0, b, 0, 0)        a + b         = T
    B = (0, c, 0, e, f, g)        c + e + f + g = T
    C = (h, 0, i, 0, j, 0)        h + i + j     = T
Every coordinate vanishes in some row, so v = min(A,B,C) is exact and
singleton-normalized for free (paper4's lower-envelope lemma).

usage: d4_family.py <mode: axis|box> <budget_s> [seed]
"""
import sys, json, time, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

N = 6
FULL = 63
W1 = dict(a=11, b=7, c=10, e=4, f=3, g=1, h=2, i=1, j=15, T=18)   # ex:notsuffix
W2 = dict(a=15, b=14, c=9, e=9, f=6, g=5, h=4, i=4, j=21, T=29)   # ex:notstratum


def rows(p):
    return ((0, p["a"], 0, p["b"], 0, 0),
            (0, p["c"], 0, p["e"], p["f"], p["g"]),
            (p["h"], 0, p["i"], 0, p["j"], 0))


def ok(p):
    R = rows(p)
    if any(q < 0 for r in R for q in r):
        return None
    if any(sum(r) != p["T"] for r in R):
        return None
    if any(min(r[k] for r in R) != 0 for k in range(N)):
        return None
    if p["T"] <= 0:
        return None
    return R


def analyse(p):
    R = ok(p)
    if R is None:
        return None
    v = L.envelope(N, [tuple(F(q) for q in r) for r in R])
    phi = L.lmin_staged(N, v)
    if phi is None:
        return None
    suf = L.suffixes(N, v, phi)
    if not suf or suf[-1][2] != 0:          # BT: top stratum phi-tight
        return None
    if not any(s > 0 for _, _, s in suf):
        return None
    H, js = L.hstar(N, v, phi)
    out = dict(params=dict(p), rows=[list(r) for r in R],
               phi=[str(q) for q in phi],
               strata=[[k + 1 for k in b] for b in L.strata(N, phi)],
               suffixes=[[L.nm(N, Hj), str(s)] for _, Hj, s in suf],
               Hstar=L.nm(N, H), HstarMask=H, jstar=js,
               tight=[T for T in L.masks(N) if L.xsum(phi, N, T) == v[T]],
               viol=[])
    for S in range(1, FULL):
        if bin(S).count("1") < 2:
            continue
        sS = L.slack(N, v, phi, S)
        g = L.g_of(N, v, S)
        if g is None or g <= sS:
            continue
        amax = L.alpha_exact_max(N, v, S)
        if amax is None or amax <= sS:
            continue
        for al in [amax, sS + (amax - sS) / 2, sS + (amax - sS) / 4]:
            if al <= sS:
                continue
            w = L.bumped(v, S, al)
            phi2 = L.lmin_staged(N, w)
            if phi2 is None:
                continue
            Wl = [k for k in L.members(N, S) if phi2[k] < phi[k]]
            if not Wl:
                continue
            Wm = sum(1 << k for k in Wl)
            out["viol"].append(dict(S=L.nm(N, S), Smask=S, s_phi_S=str(sS),
                                    alpha=str(al), alpha_ex=str(amax),
                                    g=str(g), W=L.nm(N, Wm), Wmask=Wm,
                                    phi2=[str(q) for q in phi2],
                                    left=(Wm & ~H) == 0, right=(H & ~S) == 0))
    return out if out["viol"] else None


def main():
    mode = sys.argv[1]
    budget = float(sys.argv[2])
    t0 = time.time()
    hits, tried = [], 0
    if mode == "axis":
        for base in (W1, W2):
            for k in ("a", "c", "e", "f", "g", "h", "i", "T"):
                for d in range(-8, 15):
                    if time.time() - t0 > budget:
                        break
                    p = dict(base)
                    p[k] = base[k] + d
                    if k == "T":
                        p["b"] = p["T"] - p["a"]
                        p["g"] = p["T"] - p["c"] - p["e"] - p["f"]
                        p["j"] = p["T"] - p["h"] - p["i"]
                    if k == "a":
                        p["b"] = p["T"] - p["a"]
                    if k in ("c", "e", "f"):
                        p["g"] = p["T"] - p["c"] - p["e"] - p["f"]
                    if k == "g":
                        p["c"] = p["T"] - p["e"] - p["f"] - p["g"]
                    if k in ("h", "i"):
                        p["j"] = p["T"] - p["h"] - p["i"]
                    tried += 1
                    r = analyse(p)
                    if r:
                        r["axis"] = "%s%+d" % (k, d)
                        r["base"] = "W1" if base is W1 else "W2"
                        hits.append(r)
                        print("HIT %s%+d  phi=%s  H*=%s  nviol=%d"
                              % (k, d, r["phi"], r["Hstar"], len(r["viol"])), flush=True)
    else:
        rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 0)
        while time.time() - t0 < budget:
            base = rng.choice([W1, W2])
            p = dict(base)
            p["T"] = base["T"] + rng.randint(-6, 16)
            p["a"] = base["a"] + rng.randint(-6, 10)
            p["b"] = p["T"] - p["a"]
            p["c"] = base["c"] + rng.randint(-6, 10)
            p["e"] = base["e"] + rng.randint(-5, 7)
            p["f"] = base["f"] + rng.randint(-5, 7)
            p["g"] = p["T"] - p["c"] - p["e"] - p["f"]
            p["h"] = base["h"] + rng.randint(-3, 7)
            p["i"] = base["i"] + rng.randint(-3, 7)
            p["j"] = p["T"] - p["h"] - p["i"]
            tried += 1
            r = analyse(p)
            if r:
                r["base"] = "W1" if base is W1 else "W2"
                hits.append(r)
                if len(hits) % 10 == 1:
                    print("HIT#%d %s phi=%s H*=%s" % (len(hits), p, r["phi"],
                                                      r["Hstar"]), flush=True)
    shapes = {}
    for h in hits:
        key = (tuple(map(tuple, h["strata"])), h["Hstar"],
               tuple(sorted(h["tight"])))
        shapes.setdefault(str(key), []).append(h["params"])
    summ = dict(mode=mode, tried=tried, members=len(hits),
                distinct_rows=len({tuple(map(tuple, h["rows"])) for h in hits}),
                n_shapes=len(shapes),
                shape_sizes=sorted((len(v) for v in shapes.values()), reverse=True),
                all_left=all(x["left"] for h in hits for x in h["viol"]),
                all_right=all(x["right"] for h in hits for x in h["viol"]),
                n_violations=sum(len(h["viol"]) for h in hits),
                elapsed=round(time.time() - t0, 1))
    json.dump(dict(summary=summ, hits=hits),
              open("family_%s.json" % mode, "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
