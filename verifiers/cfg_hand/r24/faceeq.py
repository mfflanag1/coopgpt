"""Core(w) == F_p EXACTLY (not merely F_p subset Core(w)).

This is the point on which the round-24 reduction differs from the REFUTED
contraction/merge route: the merge map enlarges the core, while the face game
w reproduces the face on the nose, so a point produced for w IS a core point
of v.  Checked by comparing max over F_p of y(A) with max over Core(w) of x(A)
for every A and every p, demanding EQUALITY.
"""
import random
from fractions import Fraction as F
import lib24 as L, genn as G

def subs(U):
    out, A = [], U
    while A:
        out.append(A); A = (A - 1) & U
    return out

def relabel(A, U):
    return sum(1 << i for i, k in enumerate(L.bits(U)) if A >> k & 1)

rng = random.Random(555)
n_eq = 0
for _ in range(12):
    while True:
        total = rng.randint(4, 16)
        gens = [tuple(F(b-a) for a, b in zip([0]+c, c+[total]))
                for c in (sorted(rng.randrange(total+1) for _ in range(4))
                          for _ in range(rng.randint(2, 5)))]
        if all(min(g[i] for g in gens) == 0 for i in range(5)):
            break
    v = L.envelope(gens); f, T = L.fvec(v)
    for p in range(5):
        c = f[1 << p]; U = L.FULL ^ (1 << p)
        f4 = [F(0)] * 16
        for A in subs(U):
            f4[relabel(A, U)] = min(f[A | (1 << p)] - c, f[A])
        f4[15] = T - c
        for A in subs(U):
            h, *_ = L.core_max(f, T, [1 if A >> k & 1 else 0 for k in range(5)],
                               eqs=[(1 << p, c)])
            a4 = relabel(A, U)
            h4, _ = G.core_max(4, f4, T - c,
                               [1 if a4 >> i & 1 else 0 for i in range(4)])
            assert h == h4, f"NOT EQUAL: {h} vs {h4}"
            n_eq += 1
print(f"Core(w) == F_p verified on {n_eq} (game, p, A) triples: EQUALITY holds.")
print("So the face game neither loses nor gains core points -- the objection")
print("that killed the contraction/merge route does not apply.")
