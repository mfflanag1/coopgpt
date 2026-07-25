import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, exact_lp_min, residual_cover, tight_coalitions
def members(S,n): return [i for i in range(n) if S>>i&1]
def maxxS_fix_k_floor(g,S,k):
    # max x(S) s.t. core and x_k = m_k
    n,N,v=g.n,g.N,g.v; mk=v[1<<k]
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if i==k else 0 for i in range(n)]]; b_eq=[v[N],mk]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*99991); N=(1<<n)-1
t0=time.time(); sf=0; conjC=0; conjC_le=0; fails=[]
while time.time()-t0<cap:
    k=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        Sm=members(S,n)
        best_floor=min(maxxS_fix_k_floor(g,S,k) for k in Sm)
        if best_floor==g.v[S]: conjC+=1
        if best_floor<=pS: conjC_le+=1
        else:
            fails.append(([str(u) for u in g.v],Sm,str(best_floor),str(pS),str(g.v[S])))
            print("*** ConjC FAIL: min_k maxxS|x_k=floor > phi(S) ***",[str(u) for u in g.v],Sm,"best",str(best_floor),"phi(S)",str(pS),flush=True)
print(f"n={n} seed={seed}: starfails={sf} conjC(=v(S)):{conjC} conjC(<=phi(S)):{conjC_le} FAILS:{len(fails)} t={time.time()-t0:.0f}s",flush=True)
