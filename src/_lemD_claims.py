import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, core_min_xT
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*7919); N=(1<<n)-1; t0=time.time()
sf=0; A=0; Wt=0; B=0; Rmaxr=0
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,5*n)
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
        if not rc['lambda']: continue
        W=0
        for U in rc['lambda']: W|=U
        Tstar=W&S; R=S&~W
        r=rc['r']; sig=rc['mu']
        # R = max-r members?
        Rcheck=set(k for k in members(S,n) if r[k]==sig)
        if Rcheck==set(members(R,n)): Rmaxr+=1
        # Claim A: phi(R)=max_core x(R)
        if R!=0:
            mcR=core_max_xS(g,R); phiR=xS(phi,R,n)
            if phiR==mcR: A+=1
        # W tight at phi?
        if xS(phi,W,n)==g.v[W]: Wt+=1
        # Claim B: v(S)-v(S\R)=max_core x(R)
        if R!=0:
            lhs=g.v[S]-g.v[S&~R]; rhs=core_max_xS(g,R)
            if lhs==rhs: B+=1
            else:
                print("B FAIL v(S)-v(S\\R)=",str(lhs)," maxcore x(R)=",str(rhs),"S",members(S,n),"R",members(R,n),flush=True)
print(f"n={n} seed={seed}: sf={sf} R=maxr:{Rmaxr} ClaimA(phiR=maxcoreR):{A} Wtight:{Wt} ClaimB(margRS=maxcoreR):{B} t={time.time()-t0:.0f}s",flush=True)
