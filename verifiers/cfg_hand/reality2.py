"""STEP R, on paper5 Theorem thm:n5's extremal game -- the canonical CFG game.
w = lower envelope of (1,0,0,1,2) and (0,1,3,0,0); T=4, ratio 1/2.
Here mu = T/8 EXACTLY, so the failure hypothesis is false and the key lemma
MUST fail; if it held, the hand proof would prove mu > T/8 and this game
refutes that.  The violating f-tight set must have complement shape (1,2,0).
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L, lmax as LM
n, FULL = 5, 31
gens = [tuple(F(q) for q in r) for r in [(1,0,0,1,2), (0,1,3,0,0)]]
w, sh = L.normalize(n, L.envelope(n, gens))
T = w[FULL]
x = L.lmin(n, w); z = LM.lmax(n, w)
sx, sz = L.strata(x), L.strata(z)
print("paper5 thm:n5 extremal game, T =", T)
print("  Lmin =", [str(q) for q in x], " strata", [len(b) for b in sx])
print("  Lmax =", [str(q) for q in z], " strata", [len(b) for b in sz])
ex, bad = L.is_exact_lp(n, w)
print("  exact at definition level:", ex)
cfg = ([len(b) for b in sx] == [3,2] and [len(b) for b in sz] == [1,4]
       and z[sz[0][0]] == 0)
print("  is CFG:", cfg)
P, R = set(sx[0]), set(sx[1]); j = sz[0][0]
mu, rho = x[sx[0][0]], x[sx[1][0]]
print(f"  mu = {mu} = T*{F(mu,T)}   rho = {rho} = T*{F(rho,T)}   "
      f"j = {L.LETTERS[j]}   j Lmin-poor: {j in P}")
print(f"  ratio = {F(sum(abs(x[i]-z[i]) for i in range(n)), T)}")
pp = sorted(P - {j})
print(f"  P = {[L.LETTERS[i] for i in sorted(P)]}, "
      f"p1,p2 = {[L.LETTERS[i] for i in pp]}, R = {[L.LETTERS[i] for i in sorted(R)]}")
viol = []
for S in range(1, FULL):
    U = FULL ^ S
    if sum(x[i] for i in range(n) if S >> i & 1) != T - w[U]:
        continue
    lhs = len([i for i in pp if S >> i & 1]); rhs = len([i for i in R if S >> i & 1])
    if lhs > rhs:
        a = len([i for i in P if U >> i & 1]); b = len([i for i in R if U >> i & 1])
        viol.append((L.nm(n,S), lhs, rhs, (a, b, 1 if (U>>j)&1 else 0)))
print("  KEY-LEMMA violations (must be nonempty):")
for S_, l_, r_, shp in viol:
    print(f"     S = {S_:6s} |S n (p1,p2)| = {l_} > {r_} = |S n R|   "
          f"complement shape (a,b,eps) = {shp}")
shapes = sorted({v[3] for v in viol})
print(f"  observed violating shapes: {shapes}   predicted by STEP S: [(1, 2, 0)]")
print("  MATCH:", shapes == [(1,2,0)])
