"""DESIGNED WITNESS: mu < lambda for a BALANCED four-player game.

Kills the hope that the round-24 slice reduction can close by citing a
four-player floor theorem for balanced games.  Also re-audits the round-24
sampling control: the random balanced sampler of n4bal.py found no violation
even at n = 5, where one is known (REPORT_A3's designed witness), so that
sampler's reachable shapes miss the region entirely and its zeros are void.

THE WITNESS.  N = {p,q,x,y}, T = 1, singleton-normalized,
        v(qx) = v(qy) = v(xy) = 2/3,   every other proper v(S) = 0.
Core: y(qx), y(qy), y(xy) >= 2/3 sum to 2(y_q+y_x+y_y) >= 2, so y_p <= 0,
hence y_p = 0 and y_q = y_x = y_y = 1/3.  A single core point.
f(pq) = 1 - v(xy) = 1/3, so lambda <= 1/6, while mu = 0.
"""
from fractions import Fraction as F

import genn as G

n = 4
P, Q, X, Y = 1, 2, 4, 8
FULL = 15
v = [F(0)] * 16
v[Q | X] = F(2, 3)
v[Q | Y] = F(2, 3)
v[X | Y] = F(2, 3)
v[FULL] = F(1)

f, T = G.fvec(n, v)
lam = G.lam_of(n, f)
mu = G.mu_of(n, f, T)
print("v :", {G.nm(n, S): str(v[S]) for S in range(1, 16) if v[S]})
print("f :", {G.nm(n, S): str(f[S]) for S in range(1, 16)})
print(f"T = {T}   lambda = {lam}   mu = {mu}")
print(f"lambda_proper = "
      f"{min(F(f[S],1)/G.card(S) for S in range(1, FULL))}   T/4 = {F(T,4)}  "
      f"(in regime: {min(F(f[S],1)/G.card(S) for S in range(1, FULL)) <= F(T,4)})")

# the core is the single point (0, 1/3, 1/3, 1/3)
pt = [F(0), F(1, 3), F(1, 3), F(1, 3)]
assert sum(pt) == T
for S in range(1, FULL):
    assert sum(pt[k] for k in G.bits(n, S)) >= v[S], G.nm(n, S)
print("core point (0,1/3,1/3,1/3) verified: the game IS BALANCED")
for k in range(n):
    hi, _ = G.core_max(n, f, T, [1 if i == k else 0 for i in range(n)])
    lo, _ = G.core_min(n, f, T, 1 << k)
    print(f"   player {G.nm(n, 1<<k)}: core range [{lo}, {hi}]")
assert mu < lam
print()
print(f"VERDICT: mu = {mu} < {lam} = lambda.  mu >= lambda is FALSE for "
      f"balanced four-player games.")
print("Exactness fails badly here: min over core of y(qxy) = 1 but "
      f"v(qxy) = {v[Q|X|Y]}, so f(p) = 1 while max over core of y_p = 0.")
print("Lemma E1 itself fails: no core point gives p even lambda.")
