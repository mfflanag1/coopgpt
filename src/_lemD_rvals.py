import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, exact_lp_min
def members(S,n): return [i for i in range(n) if S>>i&1]
def two_valued_cover_exists(g,phi,S):
    """Try to find a cover with r_k in {1, sigma} only, i.e. r 2-valued.
    Actually test: does residual_cover give r with <=2 distinct values, OR can we
    find a cover where T*={r<sigma} all have r=1? Simpler: min r on S; check if a cover
    with r_k in {1,sigma} feasible. We just report distinct r-values of residual_cover."""
    rc=residual_cover(g,phi,S)
    if rc is None: return None,None
    vals=set(rc['r'].values()); return sorted(vals), rc['mu']
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*104729); N=(1<<n)-1; t0=time.time()
sf=0; twoval=0; onemin=0; rconstOnTstar=0; multi=[]
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        if rc is None: continue
        vals=sorted(set(rc['r'].values())); sig=rc['mu']
        if len(vals)<=2: twoval+=1
        # T* = {k in S : r_k < sigma}; is r constant on T*?
        Tset=[k for k,rv in rc['r'].items() if rv<sig]
        Trvals=set(rc['r'][k] for k in Tset)
        if len(Trvals)<=1: rconstOnTstar+=1
        if min(vals)==1: onemin+=1
        if len(vals)>2:
            multi.append((members(S,n),[str(x) for x in vals],str(sig)))
    if sf and sf%25==0:
        print(f"[prog] sf={sf} 2valued={twoval} rconst_on_T*={rconstOnTstar} min==1:{onemin} multi_examples={len(multi)} t={time.time()-t0:.0f}s",flush=True)
print(f"n={n} seed={seed}: sf={sf} 2valued:{twoval} rconstOnT*:{rconstOnTstar} minEq1:{onemin} MULTIval:{len(multi)}",flush=True)
if multi: print("multi-valued r examples (S, rvals, sigma):",multi[:8],flush=True)
