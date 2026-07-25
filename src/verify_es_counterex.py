"""Definitive independent certification of the exact non-ES counterexample (n=5).

Checks, all in exact rational arithmetic:
 (1) EXACTNESS: for every proper S, exhibit a core point x^S with x^S(S)=v(S)
     (via exact LP), and confirm min_core x(S) == v(S).
 (2) EGALITARIAN CLAIMS via a FRESH independent re-implementation of the
     Dietzenbacher procedure; cross-check against eshunt.egalitarian_procedure.
 (3) claims are an ASPIRATION (gamma(S) >= v(S) for all S) with a tight
     coalition for each player; and gamma(N) > v(N)  =>  gamma not in core  =>  NOT ES.
 (4) basic structure: balanced, superadditive.
"""
from fractions import Fraction as F
from itertools import combinations
from tugame import Game, is_balanced_game
from hunt_sd import is_exact_game, core_min_xS
from eshunt import egalitarian_procedure

V = ["0","0","3","3","0","1","5","5","2","4","7","8","2","4","7","9",
     "0","0","3","3","0","2","5","5","3","4","8","8","3","5","8","10"]
n = 5
v = [F(x) for x in V]
g = Game(n, v)
N = g.N

def xS(x, S):
    return sum(x[i] for i in range(n) if S >> i & 1)

def core_point_attaining(S):
    """Exact core point x with x(S)=v(S): min x(S) over core; return witness x."""
    from tugame import exact_lp_min
    A_ub, b_ub = [], []
    for T in range(1, N):
        A_ub.append([-1 if T >> i & 1 else 0 for i in range(n)]); b_ub.append(-v[T])
    A_eq = [[1]*n]; b_eq = [v[N]]
    c = [1 if S >> i & 1 else 0 for i in range(n)]
    opt, x = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    return opt, x

print("=== (1) EXACTNESS: core-min witnesses ===")
bad = []
for S in range(1, N):
    opt, x = core_point_attaining(S)
    assert opt is not None and opt != 'unbounded', f"core empty for S={S:05b}"
    # x is a genuine core point?
    assert xS(x, N) == v[N], "witness not efficient"
    assert all(xS(x, T) >= v[T] for T in range(1, N)), "witness violates a core ineq"
    assert xS(x, S) == v[S], f"witness x(S)!=v(S) at {S:05b}"
    if opt != v[S]:
        bad.append((S, opt, v[S]))
print("  every proper S has a core point attaining v(S), and min_core x(S)==v(S):",
      "YES" if not bad else f"NO {bad}")
print("  toolkit is_exact_game:", is_exact_game(g))

print("=== (2) EGALITARIAN CLAIMS (fresh independent implementation) ===")
def fresh_procedure(v):
    coals = list(range(1, (1<<n)))
    P = 0; gamma = {}
    rounds = []
    while P != N:
        chi = {}
        for S in coals:
            fixed = [i for i in range(n) if (S>>i&1) and (P>>i&1)]
            free = [i for i in range(n) if (S>>i&1) and not (P>>i&1)]
            if free:
                share = (v[S] - sum(gamma[i] for i in fixed)) / len(free)
                chi[S] = {**{i: gamma[i] for i in fixed}, **{i: share for i in free}}
            else:
                chi[S] = {i: gamma[i] for i in fixed}
        best = {i: max(chi[S][i] for S in coals if i in chi[S]) for i in range(n)}
        A = [S for S in coals
             if sum(chi[S].values()) == v[S]
             and all(chi[S][i] == best[i] for i in chi[S])]
        newP = 0
        for S in A:
            newP |= S
            for i in chi[S]:
                gamma[i] = chi[S][i]
        assert newP | P != P, "stuck"
        P |= newP
        rounds.append((A, dict(gamma)))
    Nadm = N in A
    return [gamma[i] for i in range(n)], Nadm, rounds

claims_fresh, Nadm_fresh, rounds = fresh_procedure(v)
gamma_tool, A_tool, k, Nadm_tool = egalitarian_procedure(g)
print("  fresh claims :", [str(c) for c in claims_fresh])
print("  toolkit claims:", [str(c) for c in gamma_tool])
assert claims_fresh == gamma_tool, "two implementations DISAGREE"
assert Nadm_fresh == Nadm_tool
gamma = claims_fresh
print("  N egalitarian-admissible? ", Nadm_fresh, " (False => NOT ES)")
for i,(A,gm) in enumerate(rounds,1):
    print(f"    round {i}: admissible={[format(S,'05b') for S in A]} fixed={ {j:str(gm[j]) for j in gm} }")

print("=== (3) ASPIRATION + not-in-core ===")
asp = all(xS(gamma, S) >= v[S] for S in range(1, N+1))
print("  gamma(S) >= v(S) for all S (aspiration):", asp)
tight = {i: [S for S in range(1,N+1) if (S>>i&1) and xS(gamma,S)==v[S]] for i in range(n)}
print("  per-player tight coalitions nonempty:", all(tight[i] for i in range(n)))
print(f"  gamma(N) = {xS(gamma,N)}  vs  v(N) = {v[N]}   inflation = {xS(gamma,N)-v[N]}")
in_core = g.in_core(gamma)
print("  gamma in core:", in_core, " => ES:", in_core)

print("=== (4) structure ===")
print("  balanced:", is_balanced_game(g), " superadditive:", g.is_superadditive(),
      " convex:", g.is_convex())

print()
print("VERDICT: exact =", (not bad) and is_exact_game(g),
      "| NOT ES =", (not Nadm_fresh) and (not in_core),
      "=> COUNTEREXAMPLE CONFIRMED" if ((not bad) and is_exact_game(g) and not in_core) else "=> FAILED")
