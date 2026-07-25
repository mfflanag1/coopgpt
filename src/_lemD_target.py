import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*8677); N=(1<<n)-1; t0=time.time()
sf=0; ineqOK=0; notWtight=0; notWtight_ok=0; packOK=0; bad=0
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
        if not rc['lambda']: continue
        W=0
        for U in rc['lambda']: W|=U
        Tstar=W&S; P=N&~S
        vW=g.v[W]; rhs=xS(phi,P,n)+g.v[Tstar]
        wt=(xS(phi,W,n)==vW)
        if not wt: notWtight+=1
        if vW>=rhs:
            ineqOK+=1
            if not wt: notWtight_ok+=1
        else:
            bad+=1
            print("*** v(W)<phi(P)+v(T*) ***",[str(u) for u in g.v],"S",members(S,n),"W",members(W,n),"vW",str(vW),"rhs",str(rhs),flush=True)
        # packing inequality: v(W) >= sum (lambda_U/sigma) v(U)
        sig=rc['mu']
        pack=sum(F(lv,1)*g.v[U] for U,lv in rc['lambda'].items())/sig if sig!=0 else None
        if pack is not None and vW>=pack: packOK+=1
    if sf and sf%20==0:
        print(f"[prog] sf={sf} ineqOK={ineqOK} notWt={notWtight}(ok {notWtight_ok}) packOK={packOK} bad={bad} t={time.time()-t0:.0f}s",flush=True)
print(f"n={n} seed={seed}: sf={sf} ineqOK:{ineqOK} notWtight:{notWtight}(ok:{notWtight_ok}) packOK:{packOK} BAD:{bad} t={time.time()-t0:.0f}s",flush=True)
