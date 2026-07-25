import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*333667); N=(1<<n)-1; t0=time.time()
sf=0; g3ok=0; nonconst=0; nonconst_ok=0; bad=0
while time.time()-t0<cap:
    kk=rng.randint(2,4); c=rng.randint(n,7*n)
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
        slackT=xS(phi,Tmask,n)-g.v[Tmask]
        # r-level sets D_l within T*: values rho_1>...>rho_q, D_l={k in T*: r_k>=rho_l}
        vals=sorted(set(r[k] for k in Tstar),reverse=True)  # rho_1>...>rho_q
        rhos=vals+[F(0)]
        rhs=sig*slackT
        lhs=F(0)
        for l in range(len(vals)):
            Dl=0
            for k in Tstar:
                if r[k]>=vals[l]: Dl|=1<<k
            slackD=xS(phi,Dl,n)-g.v[Dl]
            lhs+=(rhos[l]-rhos[l+1])*slackD
        nc = len(vals)>=2
        if nc: nonconst+=1
        if lhs<=rhs:
            g3ok+=1
            if nc: nonconst_ok+=1
        else:
            bad+=1
            print("*** GOAL3 FAILS ***",[str(u) for u in g.v],"S",members(S,n),"T*",Tstar,"r",{k:str(v) for k,v in r.items()},"lhs",str(lhs),"rhs",str(rhs),flush=True)
    if sf and sf%40==0:
        print(f"[prog] sf={sf} GOAL3ok={g3ok} nonconst={nonconst}(ok {nonconst_ok}) bad={bad} t={time.time()-t0:.0f}s",flush=True)
print(f"n={n} seed={seed}: sf={sf} GOAL3ok:{g3ok} nonconst:{nonconst}(ok:{nonconst_ok}) BAD:{bad} t={time.time()-t0:.0f}s",flush=True)
