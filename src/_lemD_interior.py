# Test: is the cover polytope's r-projection all-2-valued (=> C_S ray-like),
# or only its VERTICES 2-valued (interior 3-valued)? Find 2 distinct covers, average.
import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, tight_coalitions, exact_lp_min
def members(S,n): return [i for i in range(n) if S>>i&1]
def cover_full(g,phi,S,obj):
    # returns (lambda dict over tights, sigma, r dict) optimizing obj·r
    n,N=g.n,g.N; tights=tight_coalitions(g,phi)
    Sm=[k for k in range(n) if S>>k&1]
    m=len(tights); nv=m+1+len(Sm); ri={k:m+1+t for t,k in enumerate(Sm)}
    A_eq,b_eq=[],[]
    for i in range(n):
        row=[0]*nv
        for t,T in enumerate(tights):
            if T>>i&1: row[t]=-1
        row[m]=1
        if S>>i&1: row[ri[i]]=-1
        A_eq.append(row); b_eq.append(0)
    A_ub,b_ub=[],[]
    for t in range(m):
        row=[0]*nv; row[t]=-1; A_ub.append(row); b_ub.append(0)
    for k in Sm:
        row=[0]*nv; row[ri[k]]=-1; A_ub.append(row); b_ub.append(-1)
    c=[0]*nv
    for k in Sm: c[ri[k]]=-obj.get(k,0)
    opt,sol=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    if opt is None or opt=='unbounded': return None
    lam={tights[t]:sol[t] for t in range(m) if sol[t]!=0}
    return lam, sol[m], {k:sol[ri[k]] for k in Sm}
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*7); N=(1<<n)-1; t0=time.time()
sf=0; interior3=0; distinct_covers=0
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<3: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        Sm=members(S,n)
        covers=[]
        for _ in range(15):
            obj={k:rng.randint(-4,4) for k in Sm}
            res=cover_full(g,phi,S,obj)
            if res: covers.append(res[2])  # r dict
        # find two covers with different r
        uniq=[]
        for r in covers:
            if all(r!=u for u in uniq): uniq.append(r)
        if len(uniq)>=2:
            distinct_covers+=1
            # average two distinct
            r1,r2=uniq[0],uniq[1]
            ravg={k:(r1[k]+r2[k])/2 for k in Sm}
            if len(set(ravg.values()))>=3:
                interior3+=1
                if interior3<=3:
                    print("INTERIOR 3-VALUED (avg of 2 vertex covers):",Sm,"r1",{k:str(v) for k,v in r1.items()},"r2",{k:str(v) for k,v in r2.items()},"avg",{k:str(v) for k,v in ravg.items()},flush=True)
print(f"n={n} seed={seed}: sf={sf} distinct_cover_pairs={distinct_covers} interior_3valued={interior3} t={time.time()-t0:.0f}s",flush=True)
