"""COMPLETE enumeration of k-generator singleton-normalized exact games at n=5
for a given common total T, up to player permutation and generator permutation.

usage: python3 exhaust3.py <k> <T> [--count]
"""
import sys, json, time, itertools
from fractions import Fraction as F
import lib


def comps(T, k):
    """Compositions of T into exactly k nonnegative parts."""
    if k == 1:
        yield (T,)
        return
    for first in range(T + 1):
        for rest in comps(T - first, k - 1):
            yield (first,) + rest


def canon(rows):
    """Canonical form under row perms + column perms."""
    best = None
    for perm in itertools.permutations(range(len(rows))):
        R = [rows[p] for p in perm]
        cols = sorted(zip(*R), reverse=True)
        key = tuple(cols)
        if best is None or key < best:
            best = key
    return best


def enumerate_games(k, T, n=5):
    """Yield canonical k-generator singleton-normalized games with total T."""
    allc = list(comps(T, n))
    seen = set()
    if k == 2:
        for r1 in allc:
            zero1 = [i for i in range(n) if r1[i] == 0]
            for r2 in allc:
                if any(r1[i] > 0 and r2[i] > 0 for i in range(n)):
                    continue
                c = canon([r1, r2])
                if c not in seen:
                    seen.add(c)
                    yield (r1, r2)
        return
    if k == 3:
        for r1 in allc:
            for r2 in allc:
                U = [i for i in range(n) if r1[i] > 0 and r2[i] > 0]
                freei = [i for i in range(n) if i not in U]
                if not freei:
                    continue
                for tail in comps(T, len(freei)):
                    r3 = [0] * n
                    for j, i in enumerate(freei):
                        r3[i] = tail[j]
                    r3 = tuple(r3)
                    if any(min(r1[i], r2[i], r3[i]) > 0 for i in range(n)):
                        continue
                    c = canon([r1, r2, r3])
                    if c not in seen:
                        seen.add(c)
                        yield (r1, r2, r3)
        return
    raise ValueError("k must be 2 or 3")


def main():
    k = int(sys.argv[1]); T = int(sys.argv[2])
    count_only = "--count" in sys.argv
    n = 5
    games = list(enumerate_games(k, T, n))
    print(f"k={k} T={T}: {len(games)} canonical games")
    if count_only:
        return
    best = F(0); wit = []
    t0 = time.time(); nz = 0
    hist = {}
    for gs in games:
        r = lib.gap_ratio(n, gs)
        if r is None:
            continue
        w, mn, mx, l1, ratio = r
        nz += 1
        hist[str(ratio)] = hist.get(str(ratio), 0) + 1
        if ratio > best:
            best = ratio; wit = [(gs, mn, mx, l1, w[31])]
            print(f"  new max {ratio} ({float(ratio):.5f}) gens={gs}")
            print(f"     Lmin={lib.s(mn)} Lmax={lib.s(mx)}")
        elif ratio == best and len(wit) < 20:
            wit.append((gs, mn, mx, l1, w[31]))
    print(f"k={k} T={T}: evaluated {nz}, MAX = {best} ({float(best):.6f}), "
          f"{time.time()-t0:.1f}s")
    top = sorted(hist.items(), key=lambda kv: -F(kv[0]))[:8]
    print("  top ratios:", [(a, b) for a, b in top])
    with open(f"exhaust_k{k}_T{T}.json", "w") as f:
        json.dump(dict(k=k, T=T, ngames=nz, max_ratio=str(best),
                       spectrum=[[a, b] for a, b in top],
                       witnesses=[dict(gens=[list(g) for g in gs], lmin=lib.s(mn),
                                       lmax=lib.s(mx), l1=str(l1), total=str(tt))
                                  for gs, mn, mx, l1, tt in wit]), f, indent=1)


if __name__ == "__main__":
    main()
