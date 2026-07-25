"""CEILING-PROTECTION RULE (candidate LP-free proof of stable => ES).

For non-ES v: gamma-hat aspiration, delta = sum gh - v(N) > 0, M_i = v(N)-v(N\i).
Single strip y = gamma-hat - delta*e_p (p with gh_p - v({p}) >= delta).

CLAIM (sufficient, proven by hand):
  y is UNDOMINATED by the core if for every coalition Q with p in Q and
  g(Q):=gamma-hat(Q)-v(Q) < delta  (exactly the blockers of y), there is some
  j in Q\{p} with gamma-hat_j = M_j (a "ceiling-tight" player).
  Reason: domination via Q needs core x tight on Q with x_j > y_j = gamma-hat_j = M_j,
  but every core x has x_j <= M_j. Contradiction. => no dominating Q.

This test:
 (1) verifies the ceiling condition really implies undomination (cross-check vs LP);
 (2) tests whether a valid p (absorbing + ceiling-protected) ALWAYS exists for non-ES games.
No core LP is used to SELECT p; the LP is only a cross-check.
"""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0, '/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, is_balanced_game
from es_check_main import egalitarian_procedure
from core_stability import in_core, is_imputation, is_dominated_by_core
from stES_test_construction import rand_point_sum, game_from_points, rand_balanced_superadd

def ceiling_protected_players(g):
    """Return list of players p for which single-strip y=gh-delta*e_p is
    ceiling-protected (LP-FREE sufficient undomination) and absorbing-feasible."""
    n, N = g.n, g.N
    fixed, A, esN = egalitarian_procedure(n, list(g.v))
    if esN: return None, None, None
    gh = [fixed[i] for i in range(n)]
    delta = sum(gh) - g.v[N]
    M = [g.v[N] - g.v[N ^ (1<<i)] for i in range(n)]
    tight_ceiling = set(i for i in range(n) if gh[i] == M[i])
    good = []
    for p in range(n):
        if gh[p] - g.v[1<<p] < delta:   # cannot absorb delta -> not a single strip
            continue
        ok = True
        for Q in range(1, N):           # proper coalitions containing p
            if not (Q >> p & 1): continue
            gQ = g.xS(gh, Q) - g.v[Q]   # aspiration gap
            if gQ < delta:              # Q blocks y
                others = [j for j in members(Q, n) if j != p]
                if not any(j in tight_ceiling for j in others):
                    ok = False; break
        if ok:
            good.append(p)
    return good, gh, delta

def lp_undominated(g, gh, delta, p):
    y = list(gh); y[p] = gh[p] - delta
    if not is_imputation(g, y): return None
    if in_core(g, y): return None
    dom, _ = is_dominated_by_core(g, y)
    return (not dom)

def run(seed=1, n=5, ntrials=400):
    rng = random.Random(seed)
    st = {"nonES":0, "has_ceiling_p":0, "ceiling_verified_undom":0,
          "ceiling_false_positive":0, "no_ceiling_p":0}
    nocase = []
    for t in range(ntrials):
        if rng.random()<0.6:
            k=rng.randint(2,4); c=rng.randint(n,20)
            g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        else:
            g=rand_balanced_superadd(n,rng)
        good, gh, delta = ceiling_protected_players(g)
        if good is None: continue
        st["nonES"]+=1
        if good:
            st["has_ceiling_p"]+=1
            # cross-check EVERY ceiling-protected p is really LP-undominated
            for p in good:
                v = lp_undominated(g, gh, delta, p)
                if v is True: st["ceiling_verified_undom"]+=1
                elif v is False:
                    st["ceiling_false_positive"]+=1
                    print("!!! CEILING RULE FALSE POSITIVE", [str(x) for x in g.v], "p=",p, flush=True)
        else:
            st["no_ceiling_p"]+=1
            nocase.append({"v":[str(x) for x in g.v], "gh":[str(x) for x in gh], "delta":str(delta)})
        if st["nonES"]%25==0:
            print(f"  ...nonES={st['nonES']} has_ceiling_p={st['has_ceiling_p']} "
                  f"no_ceiling_p={st['no_ceiling_p']} falsepos={st['ceiling_false_positive']}", flush=True)
    return st, nocase

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    ntr=int(sys.argv[2]) if len(sys.argv)>2 else 400
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    st, nocase = run(seed, n, ntr)
    print(json.dumps(st, indent=1))
    if nocase:
        print(f"=== {len(nocase)} non-ES games with NO ceiling-protected single-strip player ===")
        for c in nocase[:12]: print(json.dumps(c))
