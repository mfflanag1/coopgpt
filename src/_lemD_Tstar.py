import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, exact_lp_min, residual_cover
def members(S,n): return [i for i in range(n) if S>>i&1]
def maxxS_Ttight(g,S,T):
    n,N,v=g.n,g.N,g.v
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if T>>i&1 else 0 for i in range(n)]]; b_eq=[v[N],v[T]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*3571); N=(1<<n)-1; t0=time.time()
sf=0; eqvS=0; levPhi=0; bad=0
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
        if rc is None: 
            print("no cover?!",flush=True); continue
        Tstar=0
        for U in rc['lambda']: Tstar |= (U & S)
        if Tstar==0 or Tstar==S:
            # degenerate; fall back note
            print("Tstar degenerate:",members(Tstar,n),"S",members(S,n),"cover",[members(U,n) for U in rc['lambda']],flush=True)
        mx=maxxS_Ttight(g,S,Tstar) if (Tstar and Tstar!=S) else None
        if mx is not None and mx==g.v[S]: eqvS+=1
        if mx is not None and mx<=pS: levPhi+=1
        if not (mx is not None and mx<=pS):
            bad+=1
            print("*** Tstar FAILS to cap x(S)<=phi(S) ***",[str(u) for u in g.v],"S",members(S,n),"Tstar",members(Tstar,n),"M=",str(mx),"phi(S)",str(pS),"cover",[members(U,n) for U in rc['lambda']],flush=True)
print(f"n={n} seed={seed}: sf={sf} Tstar_M==v(S):{eqvS} Tstar_M<=phi(S):{levPhi} BAD:{bad} t={time.time()-t0:.0f}s",flush=True)
