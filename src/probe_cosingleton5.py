"""Direct EXACT probe of the prime-suspect shape at n=5: co-singleton star on a
simplex-type exact base (the n=5 analog of the reviewer's n=4 core-intersection
refutation).  base b: v(N)=c, v(S)=w_S (small) on proper S; arms t_k = bump
N\\{k} by d_k.  We test, exactly:
  - is each game exact?
  - is the family feasible? (core + monotonicity LP)
  - what is the exact min-monotonicity slack?
and whether the arm cores have EMPTY intersection (the n=4 phenomenon).
"""
from fractions import Fraction as F
from itertools import combinations
from tugame import Game, is_balanced_game, exact_lp_min
from hunt_sd import exactify, is_exact_game
from family_infeasible import is_family_feasible, certify_infeasible

n = 5
N = (1 << n) - 1

def core_min_xS(g, S):
    A_ub, b_ub = [], []
    for T in range(1, N):
        A_ub.append([-1 if T >> i & 1 else 0 for i in range(n)]); b_ub.append(-g.v[T])
    A_eq = [[1] * n]; b_eq = [g.v[N]]
    c = [1 if S >> i & 1 else 0 for i in range(n)]
    opt, _ = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    return opt

def cores_intersect(games):
    """Is there a single x in every game's core? (exact LP)"""
    A_ub, b_ub = [], []
    for g in games:
        for T in range(1, N):
            A_ub.append([-1 if T >> i & 1 else 0 for i in range(n)]); b_ub.append(-g.v[T])
    A_eq = [[1] * n]; b_eq = [games[0].v[N]]  # all same v(N) here
    opt, x = exact_lp_min([0] * n, A_ub, b_ub, A_eq, b_eq)
    return opt is not None

def build(c, w, dks):
    """simplex-ish base with proper values w (dict S->val); arms bump N\\{k} by dks[k]."""
    v = [F(0)] * (1 << n); v[N] = F(c)
    for S, val in w.items():
        v[S] = F(val)
    b = exactify(Game(n, v))
    if b is None:
        return None
    arms = []
    for k in range(n):
        S = N ^ (1 << k)
        v2 = list(b.v); v2[S] += dks[k]
        arms.append((S, Game(n, v2)))
    return b, arms

def report(tag, c, w, dks):
    r = build(c, w, dks)
    if r is None:
        print(f"{tag}: base not balanced"); return
    b, arms = r
    games = [b] + [g for _, g in arms]
    exacts = [is_exact_game(g) for g in games]
    if not all(exacts):
        print(f"{tag}: exact={exacts} (some arm left exact class) c={c} d={dks}"); return
    edges = [(0, j + 1, S) for j, (S, _) in enumerate(arms)]
    feas, _ = is_family_feasible(games, edges)
    inter = cores_intersect([g for _, g in arms])
    print(f"{tag}: c={c} d={dks} all_exact={all(exacts)} arms_core_intersect={inter} FAMILY_FEASIBLE={feas}")
    if not feas:
        cert = certify_infeasible(games, edges)
        print(f"   *** INFEASIBLE, cert={cert.get('infeasible')}, farkas_rhs={cert.get('farkas',{}) and cert['farkas']['rhs'] if cert.get('farkas') else None}")
        return games, edges

# pure simplex base (all proper 0), co-singleton bumps of various depths
print("=== pure simplex base, all proper = 0 ===")
for c in [5, 6, 8, 10]:
    for d in [1, 2, 3]:
        report(f"simplex c={c} d={d}", c, {}, [d] * n)
    # asymmetric depths
    report(f"simplex c={c} asym", c, {}, [1, 2, 3, 4, 5])
    report(f"simplex c={c} big", c, {}, [c - 1] * n)

print("\n=== simplex base with a few positive proper values ===")
report("w1", 10, {0b00011: 2, 0b01100: 2}, [2, 2, 2, 2, 2])
report("w2", 12, {0b00111: 3, 0b11000: 2, 0b10010: 1}, [3, 3, 3, 3, 3])
report("w3", 8, {0b01010: 1, 0b00101: 1, 0b10001: 1}, [2, 2, 2, 2, 2])
