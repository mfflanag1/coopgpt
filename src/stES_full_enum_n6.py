"""Definitive reliable escape search for a single n=6 game: float-prescreened
FULL arrangement-vertex enumeration (all C(68,5) bases of coalition + floor planes
with efficiency), exact-certify any undominated hit. Slow but complete.

Usage: python3 stES_full_enum_n6.py <cand_index>
"""
import sys, itertools
import numpy as np
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from core_stability import certify_undominated
from largeness_exact import exact_solve

CANDS=[
 [0,0,0,0,0,2,2,2,1,1,1,1,3,3,3,3,1,2,2,2,1,3,4,4,3,3,3,3,4,5,5,5,0,2,3,4,0,2,3,5,3,5,5,5,3,5,6,7,1,3,4,6,1,3,4,6,4,6,7,7,4,6,7,9],
 [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
]

def run(idx, worker=0, nworkers=1):
    V=CANDS[idx]; n=6; g=Game(n,[F(x) for x in V]); N=g.N
    vf=[float(x) for x in g.v]
    lo=[vf[1<<i] for i in range(n)]
    # planes as float rows (coalition incidence or floor) with rhs
    rows=[]; rhs=[]; kind=[]
    for S in range(1,N):
        rows.append([1.0 if S>>i&1 else 0.0 for i in range(n)]); rhs.append(vf[S]); kind.append(('S',S))
    for i in range(n):
        r=[0.0]*n; r[i]=1.0; rows.append(r); rhs.append(lo[i]); kind.append(('x',i))
    m=len(rows)
    eff=[1.0]*n; effr=vf[N]
    # core rows for float domination screen
    core_A=[]; core_b=[]
    for T in range(1,N):
        core_A.append([-1.0 if T>>i&1 else 0.0 for i in range(n)]); core_b.append(-vf[T])
    from scipy.optimize import linprog
    def dom_float(y,S):
        A=[r+[0.0] for r in core_A]; b=list(core_b)
        A.append([1.0 if S>>i&1 else 0.0 for i in range(n)]+[0.0]); b.append(vf[S])
        for i in range(n):
            if S>>i&1:
                rr=[0.0]*(n+1); rr[i]=-1.0; rr[n]=1.0; A.append(rr); b.append(-y[i])
        r=linprog([0.0]*n+[-1.0],A_ub=A,b_ub=b,A_eq=[[1.0]*n+[0.0]],b_eq=[vf[N]],
                  bounds=[(None,None)]*(n+1),method="highs")
        return r.success and (-r.fun)>1e-7
    def undom_float(y):
        if abs(sum(y)-vf[N])>1e-6: return False
        if any(y[i]<lo[i]-1e-7 for i in range(n)): return False
        blocking=[S for S in range(1,N) if sum(y[i] for i in range(n) if S>>i&1)<vf[S]-1e-7]
        if not blocking: return False  # in core
        for S in blocking:
            if dom_float(y,S): return False
        return True
    tested=0; hits=0
    for combo in itertools.combinations(range(m),n-1):
        if combo[0] % nworkers != worker: continue
        Mx=np.array([rows[j] for j in combo]+[eff]); bb=np.array([rhs[j] for j in combo]+[effr])
        try:
            if abs(np.linalg.det(Mx))<1e-9: continue
            y=np.linalg.solve(Mx,bb)
        except np.linalg.LinAlgError:
            continue
        tested+=1
        if undom_float(list(y)):
            # exact certify
            Me=[rows[j][:] for j in combo]+[[1]*n]
            be=[F(g.v[kind[j][1]]) if kind[j][0]=='S' else F(g.v[1<<kind[j][1]]) for j in combo]+[g.v[N]]
            ye=exact_solve([[F(a) for a in r] for r in Me], be, n)
            if ye is not None and certify_undominated(g,ye):
                print(f"  EXACT ESCAPE: {[str(a) for a in ye]} basis={[kind[j] for j in combo]}",flush=True)
                hits+=1
                return ye
        if tested%100000==0:
            print(f"  [c{idx}w{worker}] tested={tested} hits={hits}",flush=True)
    print(f"  DONE cand {idx} worker {worker}/{nworkers}: tested={tested} vertices, no escape in this shard",flush=True)
    return None

if __name__=="__main__":
    idx=int(sys.argv[1]) if len(sys.argv)>1 else 0
    worker=int(sys.argv[2]) if len(sys.argv)>2 else 0
    nworkers=int(sys.argv[3]) if len(sys.argv)>3 else 1
    print(f"=== FULL ENUM candidate {idx} worker {worker}/{nworkers} ===",flush=True)
    run(idx,worker,nworkers)
