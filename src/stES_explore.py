"""Route-1 exploration: reverse-engineer the escaping imputations of our two
certified non-ES witnesses from their egalitarian-claims structure.

Goal: understand the map (gamma-hat, A-hat) -> undominated escape y, so we can
state a general construction and prove stable-core => ES by contrapositive.
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, '/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, popcount
from es_check_main import egalitarian_procedure
from core_stability import (in_core, is_imputation, is_dominated_by_core,
                            dominated_via, certify_undominated)

# canonical vN4 witness (min-generator x1=(0,0,1,1,2), x2=(1,1,0,2,0))
WIT_VN4 = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
# hub witness claims (1,1,3,1,1)
BASE_VN6 = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]

def analyze(tag, v, n, known_escape):
    g = Game(n, [F(x) for x in v])
    N = g.N
    fixed, A, esN = egalitarian_procedure(n, [F(x) for x in v])
    gh = [fixed[i] for i in range(n)]
    print(f"\n=== {tag}  n={n}  v(N)={v[N]} ===")
    print(f"  claims gamma-hat = {[str(x) for x in gh]}  sum={sum(gh)}  delta={sum(gh)-g.v[N]}")
    print(f"  ES? {esN}")
    Ahat = [S for S in range(1, N+1) if g.xS(gh, S) == g.v[S]]
    print(f"  A-hat (tight, incl N if ES): {[members(S,n) for S in Ahat]}")
    # which player(s) are in every proper tight coalition = hub(s)
    proper_tight = [S for S in Ahat if S != N]
    hubs = [i for i in range(n) if all(S >> i & 1 for S in proper_tight)]
    print(f"  hub(s) [in every proper tight coalition] = {hubs}")
    # aspiration ceilings M_i = v(N)-v(N\{i})
    M = [g.v[N] - g.v[N ^ (1<<i)] for i in range(n)]
    print(f"  marginals M_i = v(N)-v(N\\i) = {[str(x) for x in M]}")
    # known escape
    y = [F(x) for x in known_escape]
    print(f"  known escape y = {[str(x) for x in y]}  sum={sum(y)}")
    cert = certify_undominated(g, y)
    print(f"  escape undominated & outside core? {'YES' if cert else 'NO'}")
    if cert:
        print(f"    blocking coalitions: {[members(S,n) for S in cert['blocking_coalitions']]}")
    # relation of escape to claims
    diff = [y[i]-gh[i] for i in range(n)]
    print(f"  y - gamma-hat = {[str(d) for d in diff]}")
    stripped = [i for i in range(n) if y[i] < gh[i]]
    boosted  = [i for i in range(n) if y[i] > gh[i]]
    kept     = [i for i in range(n) if y[i] == gh[i]]
    print(f"  stripped(below claim)={stripped}  boosted(above)={boosted}  kept(=claim)={kept}")
    print(f"  y_i vs M_i: {[(str(y[i]),str(M[i])) for i in range(n)]}")
    return g, gh, Ahat, M, y

if __name__ == "__main__":
    analyze("vN4 canonical", WIT_VN4, 5, [0,1,1,2,0])
    analyze("vN6 hub", BASE_VN6, 5, [1,1,3,1,0])
