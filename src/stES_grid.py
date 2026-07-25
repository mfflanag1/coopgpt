"""Fast grid search over low-denominator imputations for cand1,cand2: enumerate
y with y_i = floor_i + k_i/d (sum k_i = (v(N)-sum floor)*d), float-screen for
undominated-outside-core, exact-certify hits. Catches false-alarm escapes quickly."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from core_stability import certify_undominated
from stability_float import in_core_float,is_dominated_float,_core_rows

CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}
def compositions(total, parts):
    if parts==1:
        yield (total,); return
    for first in range(total+1):
        for rest in compositions(total-first, parts-1):
            yield (first,)+rest

def gridsearch(idx, dens=(2,3,4,5,6,7)):
    V=CANDS[idx]; n=6; g=Game(n,[F(x) for x in V]); N=g.N
    vf=[float(x) for x in g.v]; base=_core_rows(vf,n,N)
    fl=[g.v[1<<i] for i in range(n)]
    spare=g.v[N]-sum(fl)
    hits=[]
    for d in dens:
        units=int(spare*d)
        cnt=0
        for comp in compositions(units, n):
            y=[fl[i]+F(comp[i],d) for i in range(n)]
            yf=[float(x) for x in y]
            if in_core_float(vf,n,N,yf): continue
            # must be outside core (some violation) and undominated
            blk=[S for S in range(1,N) if sum(yf[i] for i in range(n) if S>>i&1)<vf[S]-1e-7]
            if not blk: continue
            if is_dominated_float(vf,n,N,yf,base): continue
            if certify_undominated(g,y):
                hits.append([str(x) for x in y])
                print(f"  cand{idx} d={d} ESCAPE {[str(x) for x in y]}",flush=True)
                if len(hits)>=2: return hits
        print(f"  cand{idx} d={d}: no escape (compositions scanned for {units} units)",flush=True)
    return hits

if __name__=="__main__":
    for idx in (1,2):
        print(f"=== grid cand{idx} ===",flush=True)
        h=gridsearch(idx)
        if not h: print(f"  cand{idx}: NO grid escape (d<=6)",flush=True)
