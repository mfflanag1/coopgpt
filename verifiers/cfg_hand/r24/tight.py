"""The EQUALITY STRUCTURE of (R): which games/pairs make it tight, and what
lambda's attaining coalition S* looks like there.

For every in-regime exact game and ordered pair with
        max_Core (2 y_p + y_q) = 3*lambda   (margin zero),
report: T, lambda, the coalitions attaining lambda, where p and q sit relative
to them, f(p), f(q), f(pq), and an optimal core point.

MOTIVE.  f(S*) = lambda|S*| means S* is capped at exactly lambda per capita in
EVERY core point (f is the attained max).  That is the only place a proof can
get the extra lambda that the free cover bound (which stops at T + 2lambda) is
missing.
"""
import random
import sys
from collections import Counter
from fractions import Fraction as F

import lib24 as L

NG = int(sys.argv[1]) if len(sys.argv) > 1 else 40
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 909


def rand_gens(rng):
    while True:
        total = rng.randint(4, 16)
        gens = []
        for _ in range(rng.randint(2, 5)):
            cuts = sorted(rng.randrange(total + 1) for _ in range(4))
            gens.append(tuple(F(b - a)
                              for a, b in zip([0] + cuts, cuts + [total])))
        if all(min(g[i] for g in gens) == 0 for i in range(5)):
            return gens


def main():
    rng = random.Random(SEED)
    pat = Counter()
    shown = 0
    inreg = 0
    ntight = 0
    npairs = 0
    while inreg < NG:
        gens = rand_gens(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        if L.lam_proper(f, T) > F(T, 5):
            continue
        inreg += 1
        lam = L.lam_of(f, T)
        att = [S for S in L.ALLNE if F(f[S], 1) / L.card(S) == lam]
        for p in range(5):
            for q in range(5):
                if p == q:
                    continue
                npairs += 1
                w = [0] * 5
                w[p], w[q] = 2, 1
                val, y, eta, gam, _ = L.core_max(f, T, w)
                if val != 3 * lam:
                    continue
                ntight += 1
                # where do p and q sit relative to the attaining coalitions?
                sig = []
                for S in att:
                    sig.append((L.card(S), bool(S >> p & 1), bool(S >> q & 1)))
                key = tuple(sorted(set(sig)))
                pat[key] += 1
                keyf = (f[1 << p] == lam, f[1 << q] == lam,
                        f[(1 << p) | (1 << q)] == 2 * lam,
                        y[p] == lam, y[q] == lam, eta < 0)
                pat[("F", keyf)] += 1
                if shown < 6:
                    shown += 1
                    print(f"TIGHT  T={T} lambda={lam}  p={L.LETTERS[p]} "
                          f"q={L.LETTERS[q]}")
                    print(f"   lambda attained at: "
                          f"{[L.nm(S) for S in att]}")
                    print(f"   f(p)={f[1<<p]} f(q)={f[1<<q]} "
                          f"f(pq)={f[(1<<p)|(1<<q)]}  "
                          f"opt y = {[str(t) for t in y]}   eta = {eta}")
                    print(f"   dual gamma: "
                          f"{ {L.nm(S): str(g) for S, g in gam.items()} }")
    print(f"\nin-regime games {inreg}, ordered pairs {npairs}, "
          f"TIGHT pairs {ntight}")
    print("\npatterns (size of S*, p in S*, q in S*) -> count:")
    for k, c in pat.most_common(14):
        if k and k[0] == "F":
            print(f"   [f(p)=lam, f(q)=lam, f(pq)=2lam, y_p=lam, y_q=lam, "
                  f"eta<0] = {k[1]} : {c}")
        else:
            print(f"   {k} : {c}")


if __name__ == "__main__":
    main()
