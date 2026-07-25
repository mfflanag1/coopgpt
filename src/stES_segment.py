"""Targeted escape search exploiting the 1-D (segment) core. An undominated escape
must block A and B on their tight coalitions, so its coordinates tend to sit at
endpoint values. Enumerate y with y_i in {floor_i, A_i, B_i, max(A_i,B_i)} (and a
few blends), sum = v(N), and exact-check undomination. Fast; finds the escape if
it is endpoint-coordinate-valued."""
import sys, itertools, json
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from core_stability import certify_undominated, in_core, is_imputation, is_dominated_by_core

CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}

def undom(g,y):
    return is_imputation(g,y) and (not in_core(g,y)) and (not is_dominated_by_core(g,y)[0])

def search(idx):
    V=CANDS[idx]; g=Game(6,[F(x) for x in V]); N=g.N; n=6
    A,B=[[F(x) for x in ep] for ep in json.load(open(f"/tmp/cvx_{idx}.json"))]
    fl=[g.v[1<<i] for i in range(n)]
    vN=g.v[N]
    # candidate values per coordinate
    cand=[]
    for i in range(n):
        vals={fl[i], A[i], B[i], max(A[i],B[i]), min(A[i],B[i]), (A[i]+B[i])/2}
        cand.append(sorted(vals))
    print(f"cand{idx}: value choices per coord sizes {[len(c) for c in cand]}",flush=True)
    found=[]; tried=0
    for combo in itertools.product(*cand):
        if sum(combo)!=vN: continue
        tried+=1
        y=list(combo)
        if undom(g,y):
            found.append([str(x) for x in y])
            print(f"  ESCAPE y={[str(x) for x in y]}",flush=True)
            if len(found)>=3: break
    print(f"cand{idx}: tried {tried} sum-feasible combos; escapes={len(found)}",flush=True)
    return found

if __name__=="__main__":
    for idx in (1,2):
        print(f"=== segment search cand{idx} ===",flush=True)
        search(idx)
