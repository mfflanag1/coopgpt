"""Exact core-vertex enumeration for cand1,cand2 via scipy HalfspaceIntersection
in the (n-1)-dim efficiency hyperplane, then exact reconstruction (identify tight
constraints at each float vertex, solve exactly). Reports vertex count + distinct
per-coordinate values (sizing the extended arrangement)."""
import sys, itertools
import numpy as np
from fractions import Fraction as F
from scipy.spatial import HalfspaceIntersection
from scipy.optimize import linprog
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from largeness_exact import exact_solve

CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}

def core_vertices_exact(g):
    n,N=g.n,g.N
    vf=[float(x) for x in g.v]
    # substitute x_{n-1} = v(N) - sum_{i<n-1} x_i ; variables u=x_0..x_{n-2} (n-1 dims)
    # constraint x(S) >= v(S): sum_{i in S} x_i >= v(S).
    # In u-space: for i<n-1 coefficient a_i = [i in S]; x_{n-1}=vN - sum u.
    # x(S) = sum_{i in S,i<n-1} u_i + [n-1 in S]*(vN - sum_j u_j)
    #       = sum_i ( [i in S] - [n-1 in S] ) u_i + [n-1 in S]*vN
    # >= v(S)  ->  -sum_i(...) u_i <= [n-1 in S]*vN - v(S)
    A=[]; b=[]
    for S in range(1,N):  # proper coalitions (efficiency handled by substitution)
        row=[ ( (1 if S>>i&1 else 0) - (1 if S>>(n-1)&1 else 0) ) for i in range(n-1) ]
        rhs = (vf[N] if S>>(n-1)&1 else 0) - vf[S]
        A.append([-c for c in row]); b.append(rhs)
    A=np.array(A); b=np.array(b)
    # Chebyshev center for interior point
    # max r s.t. A u + ||A_i|| r <= b
    norms=np.linalg.norm(A,axis=1)
    Ac=np.hstack([A, norms.reshape(-1,1)])
    res=linprog(np.array([0.0]*(n-1)+[-1.0]), A_ub=Ac, b_ub=b, bounds=[(None,None)]*(n-1)+[(0,None)], method="highs")
    if not res.success:
        return None
    interior=res.x[:n-1]
    halfspaces=np.hstack([A, -b.reshape(-1,1)])  # A u - b <= 0 form: [A | -b], A u + (-b) <=0
    try:
        hs=HalfspaceIntersection(halfspaces, interior)
    except Exception as e:
        print("HSI failed:",e); return None
    verts=set()
    for vpt in hs.intersections:
        # reconstruct exact: find tight coalition constraints (within tol), take n-1 independent + solve exact 6D
        xfull=list(vpt)+[vf[N]-sum(vpt)]
        tight=[S for S in range(1,N) if abs(sum(xfull[i] for i in range(n) if S>>i&1)-vf[S])<1e-6]
        # need n-1 independent coalition planes + efficiency
        for combo in itertools.combinations(tight, n-1):
            M=[[F(1) if S>>i&1 else F(0) for i in range(n)] for S in combo]+[[F(1)]*n]
            bb=[F(g.v[S]) for S in combo]+[g.v[N]]
            xe=exact_solve([r[:] for r in M], bb, n)
            if xe is None: continue
            # verify in core
            if all(sum(xe[i] for i in range(n) if S>>i&1)>=g.v[S] for S in range(1,N)) and sum(xe)==g.v[N]:
                verts.add(tuple(xe)); break
    return [list(v) for v in verts]

if __name__=="__main__":
    for idx,V in CANDS.items():
        g=Game(6,[F(x) for x in V])
        verts=core_vertices_exact(g)
        if verts is None:
            print(f"cand{idx}: core-vertex enumeration failed"); continue
        print(f"cand{idx}: {len(verts)} core vertices")
        distinct=[sorted(set(str(v[i]) for v in verts)) for i in range(6)]
        for i in range(6):
            print(f"   coord {i}: {len(distinct[i])} distinct values: {distinct[i]}")
        import json
        with open(f"/tmp/corevx_{idx}.json","w") as f:
            json.dump([[str(x) for x in v] for v in verts], f)
        print(f"   saved /tmp/corevx_{idx}.json")
