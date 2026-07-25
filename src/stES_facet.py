"""Facet-outward local escape test for cand1,cand2. Since U (undominated imputations)
is CONVEX and contains the core C, any escape (point of U\\C) is reachable across a core
FACET. For each essential coalition S0 (a facet y(S0)=v(S0)), take a facet-interior point
y0 and step OUTWARD (move mass from an S0-player to an outside player, so y(S0)<v(S0)),
exact-checking undomination. Any undominated outside point => core NOT stable (false alarm)."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, exact_lp_min
from core_stability import certify_undominated, in_core, is_imputation, is_dominated_by_core

CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}

def facet_interior(g, S0):
    """max s s.t. y(N)=v(N), y(S0)=v(S0), y(S)>=v(S)+s (proper S!=S0), y_i>=v(i)+s. Returns y or None."""
    n,N=g.n,g.N
    # vars y_0..y_{n-1}, s  (index n = s)
    A_ub,b_ub=[],[]
    for S in range(1,N):
        if S==S0: continue
        row=[-1 if S>>i&1 else 0 for i in range(n)]+[1]  # -y(S)+s <= -v(S)
        A_ub.append(row); b_ub.append(-g.v[S])
    for i in range(n):
        row=[0]*n+[1]; row[i]=-1  # -y_i + s <= -v(i)
        A_ub.append(row); b_ub.append(-g.v[1<<i])
    A_eq=[[1 if S0>>i&1 else 0 for i in range(n)]+[0],[1]*n+[0]]
    b_eq=[g.v[S0],g.v[N]]
    opt,sol=exact_lp_min([0]*n+[-1],A_ub,b_ub,A_eq,b_eq)  # max s
    if opt is None or opt=='unbounded': return None
    return sol[:n]

def undom(g,y):
    return is_imputation(g,y) and (not in_core(g,y)) and (not is_dominated_by_core(g,y)[0])

def search(idx):
    V=CANDS[idx]; g=Game(6,[F(x) for x in V]); N=g.N; n=6
    ess=[]
    for S0 in range(1,N):
        y0=facet_interior(g,S0)
        if y0 is None: continue
        # is it a genuine facet interior (y0(S0)=v(S0), others strictly bigger)? keep all with y0
        ess.append((S0,y0))
    print(f"cand{idx}: {len(ess)} coalitions with feasible facet-interior point",flush=True)
    steps=[F(1,2),F(1),F(1,4),F(3,2),F(2),F(1,3),F(2,3)]
    tried=0
    for S0,y0 in ess:
        Sin=[i for i in range(n) if S0>>i&1]
        Sout=[i for i in range(n) if not (S0>>i&1)]
        for a in Sin:
            for b in Sout:
                for d in steps:
                    if y0[a]-d < g.v[1<<a]: continue
                    y=[F(x) for x in y0]; y[a]-=d; y[b]+=d
                    tried+=1
                    if undom(g,y):
                        print(f"  ESCAPE across S0={members(S0,n)} move {a}->{b} d={d}: y={[str(x) for x in y]}",flush=True)
                        return y
    print(f"  cand{idx}: NO facet-outward escape (tried={tried})",flush=True)
    return None

if __name__=="__main__":
    for idx in (1,2):
        print(f"=== facet-outward cand{idx} ===",flush=True)
        search(idx)
