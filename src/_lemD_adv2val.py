import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, tight_coalitions, exact_lp_min
def members(S,n): return [i for i in range(n) if S>>i&1]
def find_cover(g,phi,S,obj_r):
    """find cover (lambda>=0 tight, mu, r_k>=1 k in S, r_j=0 j not S) optimizing sum obj_r[k]*r_k.
    Returns r dict or None."""
    n,N=g.n,g.N
    tights=tight_coalitions(g,phi)
    Sm=[k for k in range(n) if S>>k&1]
    m=len(tights); nvars=m+1+len(Sm)   # lambda, mu, r(Sm)
    ridx={k:m+1+t for t,k in enumerate(Sm)}
    A_eq,b_eq=[],[]
    for i in range(n):
        row=[0]*nvars
        for t,T in enumerate(tights):
            if T>>i&1: row[t]=-1
        row[m]=1
        if S>>i&1: row[ridx[i]]=-1
        A_eq.append(row); b_eq.append(0)
    A_ub,b_ub=[],[]
    for t in range(m):
        row=[0]*nvars; row[t]=-1; A_ub.append(row); b_ub.append(0)
    for k in Sm:
        row=[0]*nvars; row[ridx[k]]=-1; A_ub.append(row); b_ub.append(-1)
    c=[0]*nvars
    for k in Sm: c[ridx[k]]=-obj_r[k]   # maximize sum obj*r
    opt,sol=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    if opt is None or opt=='unbounded': return None
    return {k:sol[ridx[k]] for k in Sm}
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*69691); N=(1<<n)-1; t0=time.time()
sf=0; found3=0; ex=None
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<3: continue  # need >=3 members for 3 values
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        Sm=members(S,n)
        for trial in range(8):
            obj={k:rng.randint(-3,3) for k in Sm}
            r=find_cover(g,phi,S,obj)
            if r is None: continue
            vals=set(r.values())
            if len(vals)>=3:
                found3+=1; ex=([str(u) for u in g.v],Sm,{k:str(v) for k,v in r.items()})
                print("*** 3-VALUED COVER FOUND ***",ex,flush=True)
                break
        if ex: break
    if ex: break
print(f"n={n} seed={seed}: sf(>=3members)={sf} found3valued={found3} t={time.time()-t0:.0f}s",flush=True)
