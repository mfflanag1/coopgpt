"""Deterministic construction, from the structure inside cor:cfg's own proof.
T=16, j=a, Lmin=(2,2,2,5,5) so P={a,b,c}, R={d,e}; a 3-set S0={c,d,e} attains
nu with v(S0)=12, so EVERY generator row must satisfy g_c+g_d+g_e >= 12, i.e.
g_a+g_b <= 4; and f({a})=2 forces g_a <= 2.  Search that slice deterministically.
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L, lmax as LM
n, FULL, T = 5, 31, 16

def test(rows, verbose=False):
    if any(min(r[i] for r in rows) != 0 for i in range(n)):
        return None
    gens = [tuple(F(q) for q in r) for r in rows]
    if len({sum(g) for g in gens}) != 1:
        return None
    w, sh = L.normalize(n, L.envelope(n, gens))
    if w[FULL] != T:
        return None
    x = L.lmin(n, w); z = LM.lmax(n, w)
    sx, sz = L.strata(x), L.strata(z)
    if [len(b) for b in sx] != [3, 2] or [len(b) for b in sz] != [1, 4]:
        return None
    if z[sz[0][0]] != 0:
        return None
    return (w, x, z, sx, sz)

pool = [(2,2,2,5,5), (0,4,4,4,4), (2,0,4,5,5), (2,2,0,7,5), (2,2,12,0,0),
        (0,4,12,0,0), (2,0,0,7,7), (0,0,16,0,0), (2,2,4,4,4), (0,2,2,7,5)]
best = None
for r in range(3, 7):
    for combo in itertools.combinations(pool, r):
        if (2,2,2,5,5) not in combo:
            continue
        res = test(list(combo))
        if res:
            best = (list(combo), res); break
    if best: break

if not best:
    print("no CFG game found in the designed pool")
    sys.exit(0)
rows, (w, x, z, sx, sz) = best
P, R = set(sx[0]), set(sx[1]); j = sz[0][0]; mu = x[sx[0][0]]
print("GENUINE CFG GAME (deterministic construction, T=16)")
print("  generator rows:", rows)
print(f"  Lmin = {[str(q) for q in x]}   Lmax = {[str(q) for q in z]}")
print(f"  mu = {mu} = T*{F(mu,T)}   rho = {x[sx[1][0]]} = T*{F(x[sx[1][0]],T)}")
print(f"  j = {L.LETTERS[j]}   j is Lmin-poor: {j in P}   (L2')")
ex, bad = L.is_exact_lp(n, w)
print(f"  exact at definition level (LP over the core): {ex}")
print(f"  ratio ||x-z||_1 / T = {sum(abs(x[i]-z[i]) for i in range(n))}/{T}"
      f" = {F(sum(abs(x[i]-z[i]) for i in range(n)), T)}")
pp = sorted(P - {j})
viol = []
for S in range(1, FULL):
    U = FULL ^ S
    if sum(x[i] for i in range(n) if S >> i & 1) != T - w[U]:
        continue
    lhs = len([i for i in pp if S >> i & 1]); rhs = len([i for i in R if S >> i & 1])
    if lhs > rhs:
        a_ = len([i for i in P if U >> i & 1]); b_ = len([i for i in R if U >> i & 1])
        viol.append((L.nm(n,S), f"{lhs}>{rhs}", (a_, b_, 1 if (U>>j)&1 else 0)))
print("  KEY-LEMMA violations at mu = T/8 (MUST be nonempty, else the hand")
print("  proof would prove mu > T/8, which this very game refutes):")
for vv in viol:
    print("     S =", vv[0], " |Sn{p1,p2}| > |SnR| :", vv[1],
          "  complement shape (a,b,eps) =", vv[2])
