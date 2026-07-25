"""Enumerate ALL arrangement-vertex undominated escapes for a witness, and
relate each to gamma-hat. Looking for the cleanest universal construction."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, '/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from largeness_exact import exact_solve
from core_stability import in_core, is_imputation, is_dominated_by_core, certify_undominated

WIT_VN4 = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
BASE_VN6 = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]

def all_escapes(tag, v, n):
    g = Game(n, [F(x) for x in v]); N = g.N
    fixed, A, esN = egalitarian_procedure(n, [F(x) for x in v])
    gh = [fixed[i] for i in range(n)]
    delta = sum(gh) - g.v[N]
    print(f"\n=== {tag} n={n} v(N)={v[N]} claims={[str(x) for x in gh]} delta={delta} ===")
    planes = []
    for S in range(1, N):
        planes.append(([1 if S>>i&1 else 0 for i in range(n)], g.v[S]))
    for i in range(n):
        row=[0]*n; row[i]=1; planes.append((row, g.v[1<<i]))
    eff=([1]*n, g.v[N])
    seen=set(); escapes=[]
    for combo in itertools.combinations(range(len(planes)), n-1):
        M=[planes[j][0] for j in combo]+[eff[0]]
        b=[planes[j][1] for j in combo]+[eff[1]]
        y=exact_solve([r[:] for r in M], b[:], n)
        if y is None: continue
        key=tuple(y)
        if key in seen: continue
        seen.add(key)
        if not is_imputation(g,y) or in_core(g,y): continue
        dom,_=is_dominated_by_core(g,y)
        if not dom:
            escapes.append(y)
    print(f"  #undominated escapes = {len(escapes)}")
    for y in escapes:
        diff=[y[i]-gh[i] for i in range(n)]
        stripped=[i for i in range(n) if y[i]<gh[i]]
        boosted=[i for i in range(n) if y[i]>gh[i]]
        floored=[i for i in range(n) if y[i]==g.v[1<<i]]  # at individual value
        print(f"    y={[str(x) for x in y]}  y-gh={[str(d) for d in diff]}  strip={stripped} boost={boosted} atfloor={floored}")
    return escapes

if __name__=="__main__":
    all_escapes("vN4 canonical", WIT_VN4, 5)
    all_escapes("vN6 hub", BASE_VN6, 5)
