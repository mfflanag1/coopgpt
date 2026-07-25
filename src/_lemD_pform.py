import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, exact_lp_min
def members(S,n): return [i for i in range(n) if S>>i&1]
def opt_yP_given_Wfloor(g, Wm, coef, sense):
    # optimize sum coef_i y_i over {y in core, y(W)=v(W)}; sense='max' or 'min'
    n,N,v=g.n,g.N,g.v
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if Wm>>i&1 else 0 for i in range(n)]]; b_eq=[v[N],v[Wm]]
    c=[(-coef[i] if sense=='max' else coef[i]) for i in range(n)]
    opt,sol=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    if opt is None or opt=='unbounded': return None
    return (-opt if sense=='max' else opt)
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*971); N=(1<<n)-1; t0=time.time()
sf=0; pform_ok=0; simult=0; nc=0; nc_pform=0; bad=0
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
        Wm=0
        for U in rc['lambda']: Wm|=U
        Tmask=Wm&S; P=N&~S
        isnc=len(set(r[k] for k in Tstar))>=2
        if isnc: nc+=1
        coefP=[1 if P>>i&1 else 0 for i in range(n)]
        maxyP=opt_yP_given_Wfloor(g,Wm,coefP,'max')
        if maxyP is None: continue
        phiP=xS(phi,P,n)
        ok = maxyP>=phiP
        if ok: pform_ok+=1
        if isnc and ok: nc_pform+=1
        if not ok:
            bad+=1
            print("*** P-FORM FAILS max{y(P):Wfloor}<phi(P) ***","S",members(S,n),"maxyP",str(maxyP),"phiP",str(phiP),"nc",isnc,"v",[str(u) for u in g.v],flush=True)
        # simultaneous flooring: min{y(T*): core, y(W)=v(W)} == v(T*)?
        coefT=[1 if Tmask>>i&1 else 0 for i in range(n)]
        minyT=opt_yP_given_Wfloor(g,Wm,coefT,'min')
        if minyT==g.v[Tmask]: simult+=1
    if sf and sf%30==0:
        print(f"[prog] sf={sf} pform_ok={pform_ok} simult={simult} nc={nc}(pform {nc_pform}) bad={bad} t={time.time()-t0:.0f}s",flush=True)
print(f"n={n} seed={seed}: sf={sf} PFORMok:{pform_ok} simult_floor:{simult} nonconst:{nc}(pform_ok:{nc_pform}) BAD:{bad} t={time.time()-t0:.0f}s",flush=True)
