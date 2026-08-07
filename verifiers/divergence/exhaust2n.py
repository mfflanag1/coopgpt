"""Complete 2-generator enumeration for general n (up to iso + scaling).

Same reduction as exhaust2.py: supports A,B disjoint with A u B = N (otherwise
null players reduce n), g|A and h|B are partitions of T into |A| resp. |B|
positive parts, sorted.  a ranges 1..floor(n/2).

usage: python3 exhaust2n.py <n> <Tmax> [Tmin]
"""
import sys, json, time
from fractions import Fraction as F
import lib
from exhaust2 import partitions


def main():
    n = int(sys.argv[1]); Tmax = int(sys.argv[2])
    Tmin = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    full = (1 << n) - 1
    best = F(0); wit = []; tot = 0
    t0 = time.time()
    for T in range(Tmin, Tmax + 1):
        for a in range(1, n // 2 + 1):
            b = n - a
            for gp in partitions(T, a):
                for hp in partitions(T, b):
                    g = tuple(list(gp) + [0] * b)
                    h = tuple([0] * a + list(hp))
                    r = lib.gap_ratio(n, [g, h])
                    if r is None:
                        continue
                    w, mn, mx, l1, ratio = r
                    tot += 1
                    if ratio > best:
                        best = ratio; wit = [(T, g, h, mn, mx, l1)]
                        print(f"  T={T} g={g} h={h} -> {ratio} ({float(ratio):.5f})")
                        print(f"     Lmin={lib.s(mn)} Lmax={lib.s(mx)}")
                    elif ratio == best and len(wit) < 10:
                        wit.append((T, g, h, mn, mx, l1))
    print(f"n={n} 2-gen COMPLETE T={Tmin}..{Tmax}: {tot} games, MAX={best} "
          f"({float(best):.6f})  bound (n-4)/(n-2)={F(n-4,n-2)}  {time.time()-t0:.1f}s")
    with open(f"exhaust2n_{n}_{Tmax}.json", "w") as f:
        json.dump(dict(n=n, Tmin=Tmin, Tmax=Tmax, games=tot, max_ratio=str(best),
                       conj_bound=str(F(n - 4, n - 2)),
                       witnesses=[dict(T=T, g=list(g), h=list(h), lmin=lib.s(mn),
                                       lmax=lib.s(mx), l1=str(l1))
                                  for T, g, h, mn, mx, l1 in wit]), f, indent=1)


if __name__ == "__main__":
    main()
