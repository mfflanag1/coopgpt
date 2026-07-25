import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, exact_lp_min
def members(S,n): return [i for i in range(n) if S>>i&1]
def subgame_max(g, Tmask, c):
    # max sum_k c[k] z_k over core of T*-subgame (players = members(Tmask))
    n=g.n; mem=members(Tmask,n); k=len(mem)
    idx={mem[i]:i for i in range(k)}
    # subgame values: for coalition C subset mem
    def vC(bits):  # bits over subgame indices
        S=0
        for i in range(k):
            if bits>>i&1: S|=1<<mem[i]
        return g.v[S]
    A_ub,b_ub=[],[]
    for bits in range(1,(1<<k)-1):
        A_ub.append([-1 if bits>>i&1 else 0 for i in range(k)]); b_ub.append(-vC(bits))
    A_eq=[[1]*k]; b_eq=[vC((1<<k)-1)]
    cc=[-(c.get(mem[i],0)) for i in range(k)]  # maximize
    opt,sol=exact_lp_min(cc,A_ub,b_ub,A_eq,b_eq)
    if opt is None or opt=='unbounded': return None
    return -opt
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*13); N=(1<<n)-1; t0=time.time()
sf=0; need2ok=0; nc=0; nc_ok=0; bad=0
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        if not rc['lambda']: continue
        sig=rc['mu']; r=rc['r']
        Tstar=[k for k in members(S,n) if r[k]<sig]
        if not Tstar: continue
        Tmask=0
        for k in Tstar: Tmask|=1<<k
        cvec={k:sig-r[k] for k in Tstar}  # sigma - r_k >=0
        lhs=sum(cvec[k]*phi[k] for k in Tstar)   # (sig-r).phi
        rhs=subgame_max(g,Tmask,cvec)            # max over core(T*)
        if rhs is None: continue
        isnc=len(set(r[k] for k in Tstar))>=2
        if isnc: nc+=1
        if lhs>=rhs:
            need2ok+=1
            if isnc: nc_ok+=1
        else:
            bad+=1
            print("*** NEED'' FAILS ***","S",members(S,n),"r",{k:str(v) for k,v in r.items()},"lhs",str(lhs),"rhs",str(rhs),"v",[str(u) for u in g.v],flush=True)
    if sf and sf%30==0:
        print(f"[prog] sf={sf} NEED2ok={need2ok} nonconst={nc}(ok {nc_ok}) bad={bad} t={time.time()-t0:.0f}s",flush=True)
print(f"n={n} seed={seed}: sf={sf} NEED2ok:{need2ok} nonconst:{nc}(ok:{nc_ok}) BAD:{bad} t={time.time()-t0:.0f}s",flush=True)
