"""Exactly certify the clean n=5 structural result:
base b: v(N)=6, all proper coalitions 0 (a simplex/exact game); arms t_k bump
v(N\\{k}) by 5. Each t_k is exact; the FIVE arm cores have EMPTY intersection
(each forces x_k <= 1, so sum <= 5 < 6), yet the coalitional-monotonicity
family LP is FEASIBLE -- a monotonic core selection exists on this family.
This is the n=5 analog of the reviewer's n=4 Helly-refutation, showing empty
core intersection does NOT imply family infeasibility at n=5 either.
"""
from fractions import Fraction as F
from tugame import Game, is_balanced_game, exact_lp_min
from hunt_sd import is_exact_game
from family_infeasible import is_family_feasible, verify_witness

n = 5; N = 31
v = [F(0)] * (1 << n); v[N] = F(6)
b = Game(n, v)

def bump(g, S, d):
    v2 = list(g.v); v2[S] += d; return Game(n, v2)

arms = [(N ^ (1 << k), 5) for k in range(n)]
games = [b] + [bump(b, S, d) for S, d in arms]
edges = [(0, j + 1, S) for j, (S, d) in enumerate(arms)]

print("base exact:", is_exact_game(b), "balanced:", is_balanced_game(b))
print("arms exact:", [is_exact_game(g) for g in games[1:]])
print("arms balanced:", [is_balanced_game(g) for g in games[1:]])

# arm cores intersect?
A_ub, b_ub = [], []
for g in games[1:]:
    for T in range(1, N):
        A_ub.append([-1 if T >> i & 1 else 0 for i in range(n)]); b_ub.append(-g.v[T])
opt, x = exact_lp_min([0] * n, A_ub, b_ub, [[1] * n], [F(6)])
print("arm cores intersect (exact):", opt is not None)

feas, wit = is_family_feasible(games, edges)
print("FAMILY FEASIBLE (exact):", feas)
if feas:
    ok, why = verify_witness(games, edges, wit)
    print("witness verified:", ok, why)
    print("x^b =", [str(u) for u in wit[0]])
    for k in range(n):
        print(f"y^(arm {k}, bump N\\{{{k}}}) =", [str(u) for u in wit[k + 1]])
