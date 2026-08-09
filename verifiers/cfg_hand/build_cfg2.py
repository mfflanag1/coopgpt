"""Targeted construction of a genuine CFG game.
Design constraints read off cor:cfg with T=16: Lmin=(2,2,2,5,5),
Lmax=(0,4,4,4,4), j=a.  f({a}) = 2 forces max_g g_a = 2, so every generator row
has g_a <= 2 and some row has g_a = 0.  Search inside that slice.
"""
import sys, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L, lmax as LM
n, FULL, T = 5, 31, 16
rng = random.Random(5)
base = [(2,2,2,5,5), (0,4,4,4,4)]
found = None
for trial in range(4000):
    rows = list(base)
    for _ in range(rng.randint(2, 4)):
        ga = rng.choice([0, 1, 2])
        rest = T - ga
        cuts = sorted(rng.randrange(rest + 1) for _ in range(3))
        parts = [b - a for a, b in zip([0] + cuts, cuts + [rest])]
        rows.append(tuple([ga] + parts))
    if any(min(r[i] for r in rows) != 0 for i in range(n)):
        continue
    gens = [tuple(F(q) for q in r) for r in rows]
    w, sh = L.normalize(n, L.envelope(n, gens))
    if w[FULL] != T:
        continue
    try:
        x = L.lmin(n, w); z = LM.lmax(n, w)
    except Exception:
        continue
    sx, sz = L.strata(x), L.strata(z)
    if [len(b) for b in sx] != [3, 2] or [len(b) for b in sz] != [1, 4]:
        continue
    if z[sz[0][0]] != 0:
        continue
    found = (rows, w, x, z, sx, sz)
    break

if not found:
    print("no CFG game constructed in 4000 tries")
    sys.exit(0)
rows, w, x, z, sx, sz = found
P, R = set(sx[0]), set(sx[1]); j = sz[0][0]
mu = x[sx[0][0]]
print("GENUINE CFG GAME (constructed, T=16)")
print("  rows :", rows)
print(f"  Lmin = {[str(q) for q in x]}   Lmax = {[str(q) for q in z]}")
print(f"  mu = {mu} = T*{F(mu,T)},  j = {L.LETTERS[j]},  j Lmin-poor: {j in P}")
ex, bad = L.is_exact_lp(n, w)
print(f"  exact at definition level: {ex}")
pp = sorted(P - {j})
viol = []
for S in range(1, FULL):
    U = FULL ^ S
    if sum(x[i] for i in range(n) if S >> i & 1) != T - w[U]:
        continue
    lhs = len([i for i in pp if S >> i & 1]); rhs = len([i for i in R if S >> i & 1])
    if lhs > rhs:
        a = len([i for i in P if U >> i & 1]); b = len([i for i in R if U >> i & 1])
        viol.append((L.nm(n, S), f"|Sn(p1p2)|={lhs} > |SnR|={rhs}",
                     f"U shape (a,b,eps)=({a},{b},{1 if (U>>j)&1 else 0})"))
print(f"  KEY-LEMMA violations at mu = T/8 (must be nonempty):")
for vv in viol:
    print("    ", vv)
