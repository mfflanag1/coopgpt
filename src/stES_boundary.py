"""Core-vertex-boundary escape search for cand1,cand2 (closes the completeness gap
that coalition+floor arrangement enumeration leaves open).

An undominated escape y* touches a core face: for its critical blocking coalition S,
y*|S lies ON the Pareto frontier of pi_S(core face tight on S) -> y* shares coordinates
with a CORE VERTEX. So we (1) collect many core vertices via random-direction exact LP,
(2) for each core vertex x and coalition S, build y that equals x on S and pushes N\\S
players toward floors (an imputation, blocking via other coalitions), (3) also perturb
core vertices by lowering coords + redistributing. Exact-certify undominated hits.
Finding ANY escape => false alarm (core NOT stable)."""
import sys, itertools, random
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, exact_lp_min
from core_stability import certify_undominated, in_core, is_imputation, is_dominated_by_core

CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}

def core_max(g, cvec):
    """argmax c.x over core (exact). Returns x or None."""
    n,N=g.n,g.N
    A_ub,b_ub=[],[]
    for T in range(1,N):
        A_ub.append([-1 if T>>i&1 else 0 for i in range(n)]); b_ub.append(-g.v[T])
    A_eq=[[1]*n]; b_eq=[g.v[N]]
    opt,x=exact_lp_min([-c for c in cvec],A_ub,b_ub,A_eq,b_eq)
    if opt is None or opt=='unbounded': return None
    return x

def core_vertices(g, tries=400, seed=0):
    rng=random.Random(seed); verts=set()
    n=g.n
    # axis + random directions
    dirs=[]
    for i in range(n):
        e=[0]*n; e[i]=1; dirs.append(e)
        e=[0]*n; e[i]=-1; dirs.append(e)
    for _ in range(tries):
        dirs.append([rng.randint(-5,5) for _ in range(n)])
    for c in dirs:
        x=core_max(g,c)
        if x is not None: verts.add(tuple(x))
    return [list(v) for v in verts]

def undom(g,y):
    return is_imputation(g,y) and (not in_core(g,y)) and (not is_dominated_by_core(g,y)[0])

def search(idx):
    V=CANDS[idx]; g=Game(6,[F(x) for x in V]); N=g.N; n=6
    fl=[g.v[1<<i] for i in range(n)]
    verts=core_vertices(g)
    print(f"cand{idx}: {len(verts)} core vertices sampled",flush=True)
    tried=0
    # (1) match a core vertex on S, floor others + slack
    for x in verts:
        for S in range(1,N):
            if g.xS(x,S)!=g.v[S]: continue  # x tight on S (a face)
            out=[i for i in range(n) if not (S>>i&1)]
            need=g.v[N]-g.v[S]
            base=sum(fl[i] for i in out)
            if need<base: continue
            # distribute need among out: floors + slack to one player, try each
            for extra_to in out:
                y=[None]*n
                for i in range(n):
                    if S>>i&1: y[i]=F(x[i])
                    else: y[i]=fl[i]
                y[extra_to]=fl[extra_to]+(need-base)
                tried+=1
                if undom(g,y):
                    print(f"  ESCAPE (vertex-match S={members(S,n)}) y={[str(a) for a in y]}",flush=True)
                    return y
    # (2) perturb core vertices: lower one coord to floor, redistribute to another
    for x in verts:
        for i in range(n):
            drop=F(x[i])-fl[i]
            if drop<=0: continue
            for j in range(n):
                if j==i: continue
                y=[F(a) for a in x]; y[i]=fl[i]; y[j]=y[j]+drop
                tried+=1
                if undom(g,y):
                    print(f"  ESCAPE (perturb {i}->floor, +{j}) y={[str(a) for a in y]}",flush=True)
                    return y
    print(f"  cand{idx}: NO boundary escape found (tried={tried} candidates over {len(verts)} core vertices)",flush=True)
    return None

if __name__=="__main__":
    for idx in (1,2):
        print(f"=== boundary search cand{idx} ===",flush=True)
        search(idx)
