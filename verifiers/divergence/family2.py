"""The (n-3 | 3) two-block family suggested by the complete 2-generator
enumerations at n=5 (max 1/2) and n=6 (max 2/3):

   A = {0,...,a-1} with a = n-3,   B = the remaining 3 players
   g = (T-(a-1)c, c, ..., c, 0,0,0)      supported on A
   h = (0,...,0, T/2, T/4, T/4)          supported on B
   T = 4k

Conjectured ratio: (n-4)/(n-3)  -- which is 0 at n=4, 1/2 at n=5, 2/3 at n=6.
"""
import sys, time
from fractions import Fraction as F
import lib

def run(nmax=9, Ts=(4, 8, 12)):
    for n in range(4, nmax + 1):
        a = n - 3
        best = (F(-1), None)
        for T in Ts:
            for c in range(1, T + 1):
                head = T - (a - 1) * c
                if head < c or head < 1:
                    continue
                g = tuple([head] + [c] * (a - 1) + [0, 0, 0])
                h = tuple([0] * a + [F(T, 2), F(T, 4), F(T, 4)])
                if sum(h) != T or len(g) != n or len(h) != n:
                    continue
                t0 = time.time()
                r = lib.gap_ratio(n, [g, h])
                if r is None:
                    continue
                w, mn, mx, l1, ratio = r
                if ratio > best[0]:
                    best = (ratio, (T, c, g, h, mn, mx, l1, w[(1 << n) - 1],
                                    time.time() - t0))
        ratio, info = best
        T, c, g, h, mn, mx, l1, tot, dt = info
        tgt = F(n - 4, n - 3)
        print(f"n={n} a={a}: best ratio {ratio} ({float(ratio):.5f})  "
              f"(n-4)/(n-3)={tgt} match={ratio==tgt}  "
              f"[old conj (n-4)/(n-2)={F(n-4,n-2)}]")
        print(f"    T={T} c={c} g={tuple(str(q) for q in g)} "
              f"h={tuple(str(q) for q in h)}  total={tot} l1={l1} [{dt:.1f}s]")
        print(f"    Lmin={lib.s(mn)}")
        print(f"    Lmax={lib.s(mx)}")

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
