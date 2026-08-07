"""Structural analysis of near-extremal n=5 games collected across all searches."""
import json, glob, os
from fractions import Fraction as F
import lib

N = 5
FULL = 31

def load():
    recs = []
    for path in glob.glob("top_*.json") + glob.glob("climb_*.json") + \
                glob.glob("exhaust*.json") + glob.glob("cspace_*.json"):
        try:
            data = json.load(open(path))
        except Exception:
            continue
        pools = []
        if isinstance(data, list):
            pools = data
        else:
            for key in ("top", "witnesses"):
                if key in data and isinstance(data[key], list):
                    pools += data[key]
            if data.get("best"):
                pools.append(data["best"])
        for r in pools:
            if not isinstance(r, dict):
                continue
            if r.get("n", 5) != 5:
                continue
            gens = r.get("gens") or r.get("final")
            if gens is None and "g" in r and "h" in r:
                gens = [r["g"], r["h"]]
            if gens is None or any(len(g) != N for g in gens):
                continue
            recs.append((path, [tuple(F(str(q)) for q in g) for g in gens]))
    return recs


def profile(gens):
    r = lib.gap_ratio(N, gens)
    if r is None:
        return None
    w, mn, mx, l1, ratio = r
    T = w[FULL]
    smn = [len(b) for b in lib.strata(mn)]
    smx = [len(b) for b in lib.strata(mx)]
    zeros_mx = sum(1 for q in mx if q == 0)
    zeros_mn = sum(1 for q in mn if q == 0)
    uniform_mx = len(set(mx)) == 1
    # is Lmax the uniform point?
    # tight coalitions at Lmin / Lmax
    tight_mn = [S for S in range(1, FULL)
                if sum(mn[i] for i in range(N) if S >> i & 1) == w[S]]
    tight_mx = [S for S in range(1, FULL)
                if sum(mx[i] for i in range(N) if S >> i & 1) == w[S]]
    return dict(ratio=ratio, T=T, l1=l1, lmin=mn, lmax=mx,
                strata_min=tuple(smn), strata_max=tuple(smx),
                zeros_lmax=zeros_mx, zeros_lmin=zeros_mn, uniform_lmax=uniform_mx,
                ntight_min=len(tight_mn), ntight_max=len(tight_mx),
                minlevel=min(mn), maxlevel=max(mx))


def main():
    recs = load()
    print(f"loaded {len(recs)} candidate games from search outputs")
    seen = set(); prof = []
    for path, gens in recs:
        key = tuple(sorted(gens))
        if key in seen:
            continue
        seen.add(key)
        p = profile(gens)
        if p is None:
            continue
        p["gens"] = gens
        p["src"] = os.path.basename(path)
        prof.append(p)
    prof.sort(key=lambda p: -p["ratio"])
    print(f"{len(prof)} distinct games profiled\n")
    print("=== TOP 20 BY RATIO ===")
    print(f"{'ratio':>8} {'T':>5} {'strataMin':>12} {'strataMax':>12} "
          f"{'0s in Lmax':>10} {'Lmin':>34} {'Lmax':>30}")
    for p in prof[:20]:
        print(f"{str(p['ratio']):>8} {str(p['T']):>5} {str(p['strata_min']):>12} "
              f"{str(p['strata_max']):>12} {p['zeros_lmax']:>10} "
              f"{str(lib.s(p['lmin'])):>34} {str(lib.s(p['lmax'])):>30}")
    # aggregate over games above the old bound
    hi = [p for p in prof if p["ratio"] > F(1, 3)]
    print(f"\n=== AGGREGATE over the {len(hi)} distinct games with ratio > 1/3 ===")
    for field in ("strata_min", "strata_max", "zeros_lmax", "zeros_lmin",
                  "uniform_lmax"):
        d = {}
        for p in hi:
            d[str(p[field])] = d.get(str(p[field]), 0) + 1
        print(f"  {field:>14}: {sorted(d.items(), key=lambda kv: -kv[1])}")
    ex = [p for p in prof if p["ratio"] == F(1, 2)]
    print(f"\n=== the {len(ex)} distinct games attaining 1/2 ===")
    for field in ("strata_min", "strata_max", "zeros_lmax", "uniform_lmax"):
        d = {}
        for p in ex:
            d[str(p[field])] = d.get(str(p[field]), 0) + 1
        print(f"  {field:>14}: {sorted(d.items(), key=lambda kv: -kv[1])}")
    print("\n  normalized (T=4) Lmin/Lmax of the 1/2-games:")
    seen2 = set()
    for p in ex:
        sc = F(4, 1) / p["T"]
        a = tuple(sorted(q * sc for q in p["lmin"]))
        b = tuple(sorted(q * sc for q in p["lmax"]))
        if (a, b) in seen2:
            continue
        seen2.add((a, b))
        print(f"    Lmin~{[str(q) for q in a]}  Lmax~{[str(q) for q in b]}")
    json.dump([dict(ratio=str(p["ratio"]), T=str(p["T"]),
                    gens=[[str(q) for q in g] for g in p["gens"]],
                    lmin=lib.s(p["lmin"]), lmax=lib.s(p["lmax"]),
                    strata_min=list(p["strata_min"]), strata_max=list(p["strata_max"]),
                    zeros_lmax=p["zeros_lmax"], src=p["src"])
               for p in prof[:60]], open("structure_top.json", "w"), indent=1)


if __name__ == "__main__":
    main()
