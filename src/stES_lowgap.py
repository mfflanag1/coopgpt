"""Fast focused exact escape search: restrict arrangement planes to FLOORS + the
coalitions with SMALLEST aspiration gap g(S)=gamma-hat(S)-v(S) (escapes' tight
constraints live among low-gap coalitions). Enumerate all (n-1)-subsets of this
small plane set + efficiency, exact-solve, exact-certify undominated escape.
Validates on cand0 (must refind its escape); resolves cand1,cand2 if false alarms."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import in_core,is_imputation,is_dominated_by_core,certify_undominated
from largeness_exact import exact_solve
from stability_float import in_core_float,is_dominated_float,_core_rows

CANDS=[
 [0,0,0,0,0,2,2,2,1,1,1,1,3,3,3,3,1,2,2,2,1,3,4,4,3,3,3,3,4,5,5,5,0,2,3,4,0,2,3,5,3,5,5,5,3,5,6,7,1,3,4,6,1,3,4,6,4,6,7,7,4,6,7,9],
 [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
]

def search(g, topk=22):
    n,N=g.n,g.N
    vf=[float(x) for x in g.v]; base=_core_rows(vf,n,N)
    lo=[vf[1<<i] for i in range(n)]
    def undom_f(y):
        yf=[float(x) for x in y]
        if abs(sum(yf)-vf[N])>1e-7: return False
        if any(yf[i]<lo[i]-1e-9 for i in range(n)): return False
        if in_core_float(vf,n,N,yf): return False
        return not is_dominated_float(vf,n,N,yf,base)
    fixed,A,esN=egalitarian_procedure(n,list(g.v))
    gh=[fixed[i] for i in range(n)]
    fl=[g.v[1<<i] for i in range(n)]
    # coalition planes sorted by gap
    coals=sorted(range(1,N), key=lambda S: g.xS(gh,S)-g.v[S])
    chosen=coals[:topk]
    planes=[([1 if S>>i&1 else 0 for i in range(n)], g.v[S]) for S in chosen]
    for i in range(n):
        row=[0]*n; row[i]=1; planes.append((row, fl[i]))
    eff=([1]*n,g.v[N]); seen=set(); found=[]
    for combo in itertools.combinations(range(len(planes)), n-1):
        M=[planes[j][0] for j in combo]+[eff[0]]
        b=[planes[j][1] for j in combo]+[eff[1]]
        y=exact_solve([r[:] for r in M],b[:],n)
        if y is None: continue
        key=tuple(y)
        if key in seen: continue
        seen.add(key)
        if undom_f(y) and certify_undominated(g,y):
            found.append([str(x) for x in y])
            if len(found)>=2: break
    return found, len(seen)

if __name__=="__main__":
    for i,V in enumerate(CANDS):
        g=Game(6,[F(x) for x in V])
        for topk in (18,26,34):
            found,nv=search(g,topk=topk)
            print(f"cand{i} topk={topk}: verts={nv} escapes={found}",flush=True)
            if found: break
        if not found:
            print(f"cand{i}: NO low-gap escape up to topk=34 -> escalate full enum",flush=True)
