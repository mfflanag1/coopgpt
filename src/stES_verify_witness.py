"""Full exact verification battery for cand1/cand2 as STABLE non-ES witnesses.
Verifies: balanced; EXACT (min_core x(S)=v(S) all S); non-ES (2 implementations);
1-D segment core (12 fully-tight coalitions, dim 1); endpoints A,B exact + core=conv(A,B);
plus an INDEPENDENT dense-sampling stability sanity check (all outside-core samples dominated).
"""
import sys, itertools, random, json
import numpy as np
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, exact_lp_min, is_balanced_game
import es_check_main, pes as pesmod
from core_stability import is_dominated_by_core, in_core, is_imputation

CANDS={
 1:[0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 2:[0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}
def cmin(g,S,s):
    n,N=g.n,g.N;A=[[-1 if T>>i&1 else 0 for i in range(n)] for T in range(1,N)];b=[-g.v[T] for T in range(1,N)]
    o,x=exact_lp_min([s*(1 if S>>i&1 else 0) for i in range(n)],A,b,[[1]*n],[g.v[N]]);return s*o,x

def verify(idx):
    V=CANDS[idx];n=6;g=Game(n,[F(x) for x in V]);N=g.N
    out={"id":f"cand{idx}","n":n,"v":[str(x) for x in g.v],"v_N":str(g.v[N])}
    out["balanced"]=is_balanced_game(g)
    # exactness: min_core x(S)=v(S) all proper S
    exact=True; badS=[]
    fully=[]
    for S in range(1,N):
        mn,_=cmin(g,S,1); mx,_=cmin(g,S,-1)
        if mn!=g.v[S]: exact=False; badS.append((S,str(mn)))
        if mn==mx==g.v[S]: fully.append(S)
    out["exact"]=exact; out["exact_bad"]=badS[:3]
    # non-ES both implementations
    fx,_,es1=es_check_main.egalitarian_procedure(n,list(g.v)); gh1=[fx[i] for i in range(n)]
    cl,_,es2=pesmod.egalitarian_procedure(g)
    out["ES_escheck"]=es1; out["ES_pes"]=es2
    out["claims"]=[str(x) for x in gh1]; out["sum_claims"]=str(sum(gh1)); out["delta"]=str(sum(gh1)-g.v[N])
    out["nonES_agree"]=(es1==es2==False)
    # segment geometry
    rows=[[1 if S>>i&1 else 0 for i in range(n)] for S in fully]+[[1]*n]
    dim=n-int(np.linalg.matrix_rank(np.array(rows,dtype=float)))
    out["fully_tight"]=[members(S,n) for S in fully]; out["num_fully_tight"]=len(fully); out["core_dim"]=dim
    A=cmin(g,sum(1<<i for i in range(n)),1)[1]  # placeholder
    # endpoints via generic functional
    c=[1,7,13,23,37,53]
    _,Aend=cmin(g,0,1)  # dummy
    Aa=exact_lp_min([-ci for ci in c],[[-1 if T>>i&1 else 0 for i in range(n)] for T in range(1,N)]+[],[-g.v[T] for T in range(1,N)],[[1]*n],[g.v[N]])[1]
    Bb=exact_lp_min([ci for ci in c],[[-1 if T>>i&1 else 0 for i in range(n)] for T in range(1,N)],[-g.v[T] for T in range(1,N)],[[1]*n],[g.v[N]])[1]
    def incore(x): return sum(x)==g.v[N] and all(sum(x[i] for i in range(n) if S>>i&1)>=g.v[S] for S in range(1,N))
    out["A"]=[str(x) for x in Aa]; out["B"]=[str(x) for x in Bb]
    out["A_in_core"]=incore(Aa); out["B_in_core"]=incore(Bb)
    # core = conv(A,B): every core point x = A + t(B-A). Check by sampling core vertices via random dirs,
    # each must be A or B (segment has only 2 vertices).
    verts=set()
    rng=random.Random(idx)
    for _ in range(300):
        cc=[rng.randint(-6,6) for _ in range(n)]
        x=exact_lp_min([-z for z in cc],[[-1 if T>>i&1 else 0 for i in range(n)] for T in range(1,N)],[-g.v[T] for T in range(1,N)],[[1]*n],[g.v[N]])[1]
        if x: verts.add(tuple(x))
    out["distinct_core_vertices_sampled"]=len(verts)
    out["core_is_segment"]=(len(verts)==2)
    # INDEPENDENT dense sampling stability sanity: many outside-core imputations, all dominated?
    fl=[g.v[1<<i] for i in range(n)]; und=0; samp=0
    for _ in range(120):
        # random half/third-integer imputation
        cuts=sorted(rng.random() for _ in range(n-1)); prev=0; parts=[]
        for cpt in list(cuts)+[1.0]: parts.append(cpt-prev); prev=cpt
        y=[fl[i]+F(int(round(parts[i]*(float(g.v[N])-sum(float(f) for f in fl))*6)),6) for i in range(n)]
        d=g.v[N]-sum(y); y[0]+=d
        if not is_imputation(g,y) or in_core(g,y): continue
        samp+=1
        if not is_dominated_by_core(g,y)[0]: und+=1
        if und>0: break
    out["indep_samples_outside_core"]=samp; out["indep_undominated_found"]=und
    return out

if __name__=="__main__":
    res=[]
    for idx in (1,2):
        r=verify(idx); res.append(r)
        print(f"=== cand{idx} ===", flush=True)
        print(json.dumps(r,indent=1), flush=True)
