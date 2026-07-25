"""Deterministic exact floor-vertex escape search over the surviving n=6 candidates.
For each: enumerate arrangement vertices with k players at floor (k=5,4,3,2), remaining
tight planes = coalitions. Reliable (exact). Any undominated => false alarm (non-stable).
If none for k in 2..5, report as STRONG candidate (needs k<=1 / full enumeration)."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import in_core,is_imputation,is_dominated_by_core

CANDS=[
 [0,0,0,0,0,2,2,2,1,1,1,1,3,3,3,3,1,2,2,2,1,3,4,4,3,3,3,3,4,5,5,5,0,2,3,4,0,2,3,5,3,5,5,5,3,5,6,7,1,3,4,6,1,3,4,6,4,6,7,7,4,6,7,9],
 [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
]

def undom(g,y):
    return is_imputation(g,y) and (not in_core(g,y)) and (not is_dominated_by_core(g,y)[0])

def floor_search(g, ks=(5,4,3,2), cap_per_k=3000000):
    n,N=g.n,g.N
    fl=[g.v[1<<i] for i in range(n)]
    planes=[([1 if S>>i&1 else 0 for i in range(n)], g.v[S]) for S in range(1,N)]
    floorplane={i:([1 if j==i else 0 for j in range(n)], fl[i]) for i in range(n)}
    eff=([1]*n,g.v[N])
    from largeness_exact import exact_solve
    seen=set()
    for k in ks:
        need=n-1-k
        if need<0: continue
        cnt=0
        for Z in itertools.combinations(range(n),k):
            base=[floorplane[i] for i in Z]
            for combo in itertools.combinations(range(len(planes)),need):
                cnt+=1
                if cnt>cap_per_k:
                    print(f"    k={k}: hit cap {cap_per_k}",flush=True); break
                M=[b[0] for b in base]+[planes[c][0] for c in combo]+[eff[0]]
                b=[b[1] for b in base]+[planes[c][1] for c in combo]+[eff[1]]
                y=exact_solve([r[:] for r in M],b[:],n)
                if y is None: continue
                key=tuple(y)
                if key in seen: continue
                seen.add(key)
                if undom(g,y):
                    return ("floor",k,Z,[str(x) for x in y])
            else:
                continue
            break
        print(f"    k={k} done, verts seen={len(seen)}",flush=True)
    return None

if __name__=="__main__":
    for idx,V in enumerate(CANDS):
        g=Game(6,[F(x) for x in V])
        fixed,A,esN=egalitarian_procedure(6,list(g.v))
        gh=[fixed[i] for i in range(6)]; delta=sum(gh)-g.v[g.N]
        Ahat=[members(S,6) for S in range(1,g.N) if g.xS(gh,S)==g.v[S]]
        M=[g.v[g.N]-g.v[g.N^(1<<i)] for i in range(6)]
        print(f"\n### CANDIDATE {idx}: gh={[str(x) for x in gh]} delta={delta}")
        print(f"    floors={[str(g.v[1<<i]) for i in range(6)]} M={[str(x) for x in M]}")
        print(f"    A-hat={Ahat}")
        r=floor_search(g)
        if r: print(f"    >>> FALSE ALARM: escape {r}")
        else: print(f"    >>> NO floor-vertex escape (k=2..5). STRONG candidate.")
