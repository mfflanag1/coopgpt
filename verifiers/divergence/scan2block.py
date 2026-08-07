"""Scan the generalized TWO-BLOCK 2-generator family.

  A = {head} u {p 'small' players},  g = (G, c, c, ..., c)      |A| = p+1
  B = k players,                     h = (u, u, ..., u)  or  (2u, u, ..., u)
  common total  T = G + c*p = u*k  (or (k+1)*u for the 2u variant)
  n = p + 1 + k

The extremal witnesses found by complete enumeration at n=5,6,7,8 all have this
shape.  Scan (k, c, u) at fixed n and report the maximum ratio.

usage: python3 scan2block.py <n> [umax]
"""
import sys, time
from fractions import Fraction as F
import lib


def run(n, umax=10, verbose=True):
    best = F(0); wit = []
    t0 = time.time(); cnt = 0
    for k in range(1, n - 1):
        p = n - 1 - k
        if p < 0:
            continue
        for hshape in ("flat", "double"):
            for c in (1, 2, 3):
                for u in range(1, umax + 1):
                    if hshape == "flat":
                        h_tail = [u] * k
                    else:
                        if k < 2:
                            continue
                        h_tail = [2 * u] + [u] * (k - 1)
                    T = sum(h_tail)
                    G = T - c * p
                    if G < 1 or G < c:
                        continue
                    g = tuple([G] + [c] * p + [0] * k)
                    h = tuple([0] * (p + 1) + h_tail)
                    r = lib.gap_ratio(n, [g, h])
                    cnt += 1
                    if r is None:
                        continue
                    w, mn, mx, l1, ratio = r
                    if ratio > best:
                        best = ratio; wit = [(k, c, u, hshape, g, h, mn, mx, l1, T)]
                        if verbose:
                            print(f"  k={k} p={p} c={c} u={u} {hshape} T={T} "
                                  f"g={g} h={h} -> {ratio} ({float(ratio):.5f})")
                            print(f"      Lmin={lib.s(mn)}")
                            print(f"      Lmax={lib.s(mx)}")
    m = n - 5
    fam = F(3 * m - 1, 2 * (m + 1)) if m >= 1 else F(0)
    print(f"n={n}: scanned {cnt} games in {time.time()-t0:.1f}s   MAX={best} "
          f"({float(best):.5f})   known family (3m-1)/(2(m+1))={fam}   "
          f"beats family: {best > fam}")
    return best, wit


if __name__ == "__main__":
    n = int(sys.argv[1])
    umax = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    run(n, umax)
