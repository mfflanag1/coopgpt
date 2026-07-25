"""Complete core-vertex enumeration for a lower-dimensional core: identify fully-tight
coalitions (min=max=v(S) over core), reduce to the core's affine hull, run scipy
HalfspaceIntersection in the full-dim reduced space, map vertices back, exactify.
Reports vertex count and #distinct per-coordinate values (sizes the extended arrangement)."""
import sys, itertools, json
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
from scipy.spatial import HalfspaceIntersection
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, exact_lp_min
from largeness_exact import exact_solve

CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}

def core_minmax_float(vf,n,N,S):
    A=[[-1.0 if T>>i&1 else 0.0 for i in range(n)] for T in range(1,N)]
    b=[-vf[T] for T in range(1,N)]
    c=[1.0 if S>>i&1 else 0.0 for i in range(n)]
    r1=linprog(c,A_ub=A,b_ub=b,A_eq=[[1.0]*n],b_eq=[vf[N]],bounds=[(None,None)]*n,method="highs")
    r2=linprog([-x for x in c],A_ub=A,b_ub=b,A_eq=[[1.0]*n],b_eq=[vf[N]],bounds=[(None,None)]*n,method="highs")
    if not(r1.success and r2.success): return None
    return r1.fun, -r2.fun

def run(idx):
    V=CANDS[idx]; n=6; g=Game(n,[F(x) for x in V]); N=g.N; vf=[float(x) for x in g.v]
    fully=[]
    for S in range(1,N):
        mm=core_minmax_float(vf,n,N,S)
        if mm is None: continue
        mn,mx=mm
        if abs(mn-vf[S])<1e-7 and abs(mx-vf[S])<1e-7: fully.append(S)
    print(f"cand{idx}: fully-tight coalitions {[members(S,n) for S in fully]}",flush=True)
    # affine hull: x(T)=v(T) for T in fully, x(N)=v(N). Basis of solution space.
    Aeq=np.array([[1.0 if T>>i&1 else 0.0 for i in range(n)] for T in fully]+[[1.0]*n])
    beq=np.array([vf[T] for T in fully]+[vf[N]])
    # particular solution + nullspace
    x0,_,_,_=np.linalg.lstsq(Aeq,beq,rcond=None)
    u,s,vt=np.linalg.svd(Aeq)
    rank=int((s>1e-9).sum())
    Nul=vt[rank:].T  # columns span nullspace, dim = n-rank
    d=Nul.shape[1]
    print(f"cand{idx}: core affine dim = {d}",flush=True)
    if d==0:
        print(f"cand{idx}: core is a single point {x0}",flush=True); return
    # reduce inequalities x(S)>=v(S) (S not fully-tight) to z-space: x=x0+Nul z
    halfspaces=[]  # [a | b] meaning a.z + b <= 0
    for S in range(1,N):
        if S in fully: continue
        cS=np.array([1.0 if S>>i&1 else 0.0 for i in range(n)])
        a=cS@Nul                # coeff on z
        off=cS@x0 - vf[S]       # x(S)-v(S) = a.z + off >= 0  ->  -a.z - off <= 0
        if np.linalg.norm(a)<1e-12: continue
        halfspaces.append(list(-a)+[-off])
    halfspaces=np.array(halfspaces)
    # interior point via Chebyshev in z-space
    A=halfspaces[:,:d]; bb=-halfspaces[:,d]
    norms=np.linalg.norm(A,axis=1)
    res=linprog([0.0]*d+[-1.0],A_ub=np.hstack([A,norms.reshape(-1,1)]),b_ub=bb,
                bounds=[(None,None)]*d+[(0,None)],method="highs")
    if not res.success or res.x[d]<1e-9:
        print(f"cand{idx}: reduced polytope still degenerate (r={res.x[d] if res.success else 'NA'})",flush=True); return
    interior=res.x[:d]
    hs=HalfspaceIntersection(halfspaces, interior)
    verts=set()
    for z in hs.intersections:
        xf=x0+Nul@z
        # exactify: tight coalitions at xf
        tight=[S for S in range(1,N) if abs(sum(xf[i] for i in range(n) if S>>i&1)-vf[S])<1e-6]
        for combo in itertools.combinations(tight,n-1):
            M=[[F(1) if S>>i&1 else F(0) for i in range(n)] for S in combo]+[[F(1)]*n]
            be=[F(g.v[S]) for S in combo]+[g.v[N]]
            xe=exact_solve([r[:] for r in M],be,n)
            if xe is None: continue
            if all(sum(xe[i] for i in range(n) if S>>i&1)>=g.v[S] for S in range(1,N)) and sum(xe)==g.v[N]:
                verts.add(tuple(xe)); break
    print(f"cand{idx}: {len(verts)} core vertices",flush=True)
    distinct=[sorted(set(str(v[i]) for v in verts)) for i in range(n)]
    tot_extra=sum(len(distinct[i]) for i in range(n))
    for i in range(n):
        print(f"   coord {i}: {len(distinct[i])} vals {distinct[i]}",flush=True)
    print(f"cand{idx}: extended arrangement extra planes ~ {tot_extra}; total planes ~ {62+6+tot_extra}",flush=True)
    json.dump([[str(x) for x in v] for v in verts], open(f"/tmp/cvx_{idx}.json","w"))

if __name__=="__main__":
    for idx in (1,2):
        try: run(idx)
        except Exception as e: print(f"cand{idx} FAILED: {e}",flush=True)
