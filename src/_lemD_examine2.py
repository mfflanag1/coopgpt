from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (tight_coalitions, residual_cover, star_holds, core_max_xS, xS,
                  core_min_xT, exact_lp_min)
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
# reconstruct the seed-5 game that produced S=[0,1,2],R=[2]. Re-run generator to find it.
import random
from hunt_exact_points import rand_point_sum, game_from_points
rng=random.Random(5*7919); N=31; n=5
found=None
import time
t0=time.time()
while time.time()-t0<100 and not found:
    kk=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        if S==0b111:  # {0,1,2}
            found=(g,phi,S); break
if found:
    g,phi,S=found
    print("v",[str(u) for u in g.v]);print("phi",[str(p) for p in phi],"S",members(S,n),"v(S)",str(g.v[S]),"phi(S)",str(xS(phi,S,n)))
    rc=residual_cover(g,phi,S)
    print("cover",[members(U,n) for U in rc['lambda']],"lam",[str(v) for v in rc['lambda'].values()],"r",{k:str(v) for k,v in rc['r'].items()},"mu",str(rc['mu']))
    W=0
    for U in rc['lambda']: W|=U
    Tstar=W&S; R=S&~W
    print("W",members(W,n),"Tstar",members(Tstar,n),"R",members(R,n))
    print("N\\S subset W?",((N^S)&~W)==0,"S|W==N?",(S|W)==N)
    delta=g.v[S]+g.v[W]-g.v[N]-g.v[Tstar]
    print("delta",str(delta))
    print("M^(Tstar)=max{x(S):x(Tstar)=v(Tstar)}=",str(maxxS_Ttight(g,S,Tstar)),"  (want <= phi(S)=",str(xS(phi,S,n)),", =v(S)=",str(g.v[S]),"?)")
    # also brute: is there ANY proper T!=S with M^(T)<=phi(S)?
    pS=xS(phi,S,n); good=[(members(T,n),str(maxxS_Ttight(g,S,T))) for T in range(1,N) if T!=S and (maxxS_Ttight(g,S,T) or 0)<=pS]
    print("all T with M^(T)<=phi(S):",good)
else:
    print("not found in time")
