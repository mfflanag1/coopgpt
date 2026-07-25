import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, exact_lp_min, round1_dual
def members(S,n): return [i for i in range(n) if S>>i&1]
def M_k(g,S,k):
    n,N,v=g.n,g.N,g.v; mk=v[1<<k]
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if i==k else 0 for i in range(n)]]; b_eq=[v[N],mk]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*1237); N=(1<<n)-1; t0=time.time(); sf=0
hypA=0  # {k in S: pi_k>0} subset certk ?
hypB=0  # exists k in S with pi_k>0 and M_k=v(S)
while time.time()-t0<cap:
    k=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    pi,lam,sig=round1_dual(g)
    if pi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        Sm=members(S,n)
        certk=set(k2 for k2 in Sm if M_k(g,S,k2)==g.v[S])
        piS=set(k2 for k2 in Sm if pi[k2]>0)
        if piS<=certk: hypA+=1
        else: 
            print("HYPA FAIL: {k in S: pi_k>0} not subset certk",[str(u) for u in g.v],"S",Sm,"piS",sorted(piS),"certk",sorted(certk),"pi",[str(x) for x in pi],flush=True)
        if piS & certk: hypB+=1
        elif piS: print("HYPB note: piS nonempty but disjoint from certk",Sm,sorted(piS),sorted(certk),flush=True)
print(f"n={n} seed={seed}: sf={sf} hypA(piS<=certk):{hypA} hypB(piS&certk):{hypB} t={time.time()-t0:.0f}s",flush=True)
