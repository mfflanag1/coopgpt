import random, sys, time, json
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, exact_lp_min, residual_cover, tight_coalitions
def members(S,n): return [i for i in range(n) if S>>i&1]
def strata(g,phi):
    m=[g.v[1<<i] for i in range(g.n)]; gains=[phi[i]-m[i] for i in range(g.n)]
    levels=sorted(set(gains)); return [ [i for i in range(g.n) if gains[i]==lv] for lv in levels], gains
def M_k(g,S,k):
    n,N,v=g.n,g.N,g.v; mk=v[1<<k]
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if i==k else 0 for i in range(n)]]; b_eq=[v[N],mk]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt
n=int(sys.argv[1]); seed=int(sys.argv[2]); log=sys.argv[3]
def out(s):
    with open(log,'a') as f: f.write(s+'\n')
rng=random.Random(seed*57689); N=(1<<n)-1; t0=time.time(); sf=0; cok=0; cfail=0
out(f"=== anat n={n} seed={seed} @ {time.strftime('%H:%M:%S')} ===")
while True:
    k=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    strat,gains=strata(g,phi)
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        Sm=members(S,n)
        Mk={k2:M_k(g,S,k2) for k2 in Sm}
        certk=[k2 for k2 in Sm if Mk[k2]==g.v[S]]
        # relation of S to strata: which strata do S members fall in
        strloc={k2:[li for li,st in enumerate(strat) if k2 in st][0] for k2 in Sm}
        if certk: cok+=1
        else: cfail+=1
        rec=dict(v=[str(u) for u in g.v],S=Sm,vS=str(g.v[S]),phiS=str(pS),
                 gains=[str(x) for x in gains],strata=[list(st) for st in strat],
                 r={k2:str(v2) for k2,v2 in rc['r'].items()} if rc else None,
                 Mk={k2:str(v2) for k2,v2 in Mk.items()},certk=certk,
                 strloc=strloc, S_is_bottomstratum=(set(Sm)==set(strat[0])))
        out(("CONJC_OK " if certk else "CONJC_FAIL ")+json.dumps(rec))
        if not certk:
            out("!!!! CONJ C FAILED !!!!")
    if sf and (sf%5==0):
        out(f"[prog] starfails={sf} conjC_ok={cok} conjC_fail={cfail} t={time.time()-t0:.0f}s")
