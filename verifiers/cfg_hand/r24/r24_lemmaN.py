"""LEMMA N (new, proved) and its guard.  No LP at all -- pure Fraction algebra.

LEMMA N.  Let p be a player, M a coalition containing p, B = M\{p},
C = N\M.  Let wh be the reduced game on M at the face {y(M) = f(M)}:
    wh(A) = max over D subset C of [ v(A u D) + v(C\D) - v(C) ].
Then     wh(B)  <=  f(M) - f({p}).

PROOF.  Fix D subset C.  The two coalitions {p} u (C\D) and {p} u B u D are
disjoint apart from p and their union is N, so their loads are 2 at p and 1
everywhere else: a cover with excess exactly 1 at p.  The cover bound
sum_S f(S) >= sum_k c_k y_k, evaluated at the core point attaining f({p})
(exactness at N\{p}), gives
    f(p u (C\D)) + f(p u B u D)  >=  T + f({p}).
Substituting f(X) = T - v(N\X) -- so f(p u (C\D)) = T - v(B u D) and
f(p u B u D) = T - v(C\D) -- turns this into
    v(B u D) + v(C\D)  <=  T - f({p}),
and since v(C) = T - f(M) this is exactly
    v(B u D) + v(C\D) - v(C)  <=  f(M) - f({p}).
Taking the maximum over D gives the lemma.                                  []

CONSEQUENCE.  Chain saturation of {p} inside M can NEVER fail for numerical
reasons: the lower bound that the face forces on B always leaves p room to
reach f({p}).  It can fail only through NON-EXACTNESS of the face reduced game
wh at B, i.e. min over the face of y(B) strictly exceeding wh(B).
"""
import random
from fractions import Fraction as F
import lib24 as L

def subsets(S):
    out, A = [], S
    while A:
        out.append(A); A = (A - 1) & S
    return out + [0]

rng = random.Random(20240809)
checked = tight = 0
for _ in range(60):
    while True:
        total = rng.randint(4, 16)
        gens = [tuple(F(b-a) for a, b in zip([0]+c, c+[total]))
                for c in (sorted(rng.randrange(total+1) for _ in range(4))
                          for _ in range(rng.randint(2, 5)))]
        if all(min(g[i] for g in gens) == 0 for i in range(5)):
            break
    v = L.envelope(gens); f, T = L.fvec(v)
    for p in range(5):
        for M in range(1, 32):
            if not (M >> p & 1):
                continue
            B, C = M ^ (1 << p), L.FULL ^ M
            if B == 0:
                continue
            wh = max(v[B | D] + v[C ^ D] - v[C] for D in subsets(C))
            assert wh <= f[M] - f[1 << p], f"LEMMA N FAIL {L.nm(M)}"
            checked += 1
            if wh == f[M] - f[1 << p]:
                tight += 1
print(f"LEMMA N verified on {checked} (game, p, M) triples; TIGHT in {tight} "
      f"of them ({100*tight//checked}%) -- so it is not a slack bound.")

# claim 7: the n=4 balanced witness has mu < lambda yet its lambda-argmin caps
# ARE attained, so 'argmin cap attained' is strictly weaker than (EXlam).
import genn as G
v4 = [F(0)]*16
v4[2|4] = v4[2|8] = v4[4|8] = F(2,3); v4[15] = F(1)
f4, T4 = G.fvec(4, v4)
lam4 = G.lam_of(4, f4)
arg = [A for A in range(1, 16) if F(f4[A],1)/G.card(A) == lam4]
print(f"\nn=4 balanced witness: lambda = {lam4}, mu = {G.mu_of(4, f4, T4)}, "
      f"argmins {[G.nm(4,A) for A in arg]}")
for A in arg:
    m, _ = G.core_max(4, f4, T4, [1 if A >> k & 1 else 0 for k in range(4)])
    print(f"   max core y({G.nm(4,A)}) = {m}  vs f = {f4[A]}   "
          f"{'ATTAINED' if m == f4[A] else 'NOT attained'}")
print("So 'the lambda-argmin cap is attained' does NOT imply (EXlam): it holds")
print("here while mu = 0 < 1/6 = lambda.  The two are genuinely different.")
