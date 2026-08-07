"""Extremal-class invariants at n=5 (priority #3).

A 'flat split' of an exact game is a coalition S with v(S) + v(N\\S) = v(N).
Every core point then has x(S) = v(S) exactly, so x(S) is CONSTANT on the core
-- this is the affine 'seesaw' seen in the counterexample, where the core reads
x0 = x3 = s, x1 = 1-s, x2+x4 = 3-s.

Tests, over every distinct n=5 game found by any search:
  * does the extremal class always carry a flat split, and of what sizes?
  * does Lmax always have a zero coordinate at extremality?
  * is the Lmin stratification always (3,2)?
  * is |supp(Lmax)| always 4?
"""
import json, glob, os
from collections import Counter
from fractions import Fraction as F
import lib

N = 5
FULL = 31


def flat_splits(w):
    """Coalitions S (1 <= |S| <= n-1) with w(S) + w(N\\S) = w(N)."""
    out = []
    for S in range(1, FULL):
        if w[S] + w[FULL ^ S] == w[FULL]:
            out.append(S)
    return out


def load_games():
    recs = {}
    for path in glob.glob("top_*.json") + glob.glob("climb_*.json") + \
                glob.glob("exhaust2_*.json") + glob.glob("exhaust_k*.json") + \
                glob.glob("cspace_*.json") + glob.glob("structure_top.json"):
        try:
            data = json.load(open(path))
        except Exception:
            continue
        pools = data if isinstance(data, list) else []
        if isinstance(data, dict):
            for k in ("top", "witnesses"):
                if isinstance(data.get(k), list):
                    pools += data[k]
            if data.get("best"):
                pools.append(data["best"])
        for r in pools:
            if not isinstance(r, dict):
                continue
            gens = r.get("gens") or r.get("final")
            if gens is None and "g" in r and "h" in r:
                gens = [r["g"], r["h"]]
            if gens is None or any(len(g) != N for g in gens):
                continue
            key = tuple(sorted(tuple(str(q) for q in g) for g in gens))
            recs[key] = [tuple(F(str(q)) for q in g) for g in gens]
    return list(recs.values())


def main():
    games = load_games()
    print(f"{len(games)} distinct n=5 games")
    rows = []
    for gens in games:
        r = lib.gap_ratio(N, gens)
        if r is None:
            continue
        w, mn, mx, l1, ratio = r
        fs = flat_splits(w)
        rows.append(dict(ratio=ratio, w=w, mn=mn, mx=mx, gens=gens,
                         flats=fs,
                         flat_sizes=sorted(set(bin(S).count("1") for S in fs)),
                         zeros_mx=sum(1 for q in mx if q == 0),
                         supp_mx=sum(1 for q in mx if q != 0),
                         strata_mn=tuple(len(b) for b in lib.strata(mn)),
                         strata_mx=tuple(len(b) for b in lib.strata(mx))))
    rows.sort(key=lambda d: -d["ratio"])
    ex = [d for d in rows if d["ratio"] == F(1, 2)]
    hi = [d for d in rows if d["ratio"] > F(1, 3)]
    zero = [d for d in rows if d["ratio"] == 0]
    print(f"  extremal (ratio=1/2): {len(ex)}   above 1/3: {len(hi)}   "
          f"gap-zero: {len(zero)}   total profiled: {len(rows)}")

    def summarize(tag, group):
        if not group:
            return
        print(f"\n--- {tag}  (n={len(group)}) ---")
        print("  has a flat split      :",
              Counter("yes" if d["flats"] else "no" for d in group).most_common())
        print("  flat-split sizes      :",
              Counter(str(d["flat_sizes"]) for d in group).most_common(5))
        print("  #flat splits          :",
              Counter(len(d["flats"]) for d in group).most_common(5))
        print("  zeros in Lmax         :",
              Counter(d["zeros_mx"] for d in group).most_common())
        print("  |supp Lmax|           :",
              Counter(d["supp_mx"] for d in group).most_common())
        print("  Lmin strata           :",
              Counter(str(d["strata_mn"]) for d in group).most_common(4))
        print("  Lmax strata           :",
              Counter(str(d["strata_mx"]) for d in group).most_common(4))

    summarize("EXTREMAL ratio = 1/2", ex)
    summarize("ABOVE 1/3 (incl. extremal)", hi)
    summarize("GAP = 0 (control)", zero)

    # does a flat split of size 2 specifically characterise extremality?
    print("\n--- flat split of size 2 present? ---")
    for tag, group in (("ratio=1/2", ex), ("1/3<ratio<1/2",
                                           [d for d in hi if d["ratio"] < F(1, 2)]),
                       ("ratio=0", zero)):
        c = Counter("yes" if 2 in d["flat_sizes"] else "no" for d in group)
        print(f"   {tag:>16}: {c.most_common()}")

    # in the extremal class, is the starved Lmax player always inside the size-2 flat?
    print("\n--- extremal: is the Lmax-zero player in the size-2 flat split? ---")
    c = Counter()
    for d in ex:
        z = [i for i in range(N) if d["mx"][i] == 0]
        two = [S for S in d["flats"] if bin(S).count("1") == 2]
        if not two or len(z) != 1:
            c["n/a"] += 1
            continue
        c["yes" if any(S >> z[0] & 1 for S in two) else "no"] += 1
    print("  ", c.most_common())
    json.dump(dict(n_games=len(rows), n_extremal=len(ex)),
              open("seesaw_summary.json", "w"), indent=1)


if __name__ == "__main__":
    main()
