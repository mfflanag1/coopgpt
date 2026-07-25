"""Fast float screen for star-fail configs, exact-verify + lattice/KEY analysis only
on games that screen positive. scipy for screening; exact rationals for all reported
facts. Jobs:
 (L2) is W = union of cover coalitions TIGHT at phi?
 (L3) does (KEY)<=>slack(W)<=slack(T*) hold (exact), and with equality?
 also record r-value multiset on T* (constant vs non-constant cover).
"""
import random, sys, time
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import Game
from leximin import leximin_core_float, leximin_core_exact
from lemD import star_holds, core_max_xS, xS, residual_cover, tight_coalitions
from hunt_exact_points import rand_point_sum, game_from_points

def members(S,n): return [i for i in range(n) if S>>i&1]

def core_constraints_float(n,N,v):
    A=[]; b=[]
    for S in range(1,N):
        A.append([-1.0 if S>>i&1 else 0.0 for i in range(n)]); b.append(-float(v[S]))
    return A,b

def core_max_xS_f(n,N,v,S):
    A,b=core_constraints_float(n,N,v)
    Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

def star_max_f(n,N,v,x,S):
    # max y(S) s.t. core, y_i>=x_i on S
    A,b=core_constraints_float(n,N,v)
    for i in range(n):
        if S>>i&1:
            row=[0.0]*n; row[i]=-1.0; A.append(row); b.append(-float(x[i]))
    Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

n=int(sys.argv[1]); seed0=int(sys.argv[2]); trials=int(sys.argv[3])
log=sys.argv[4] if len(sys.argv)>4 else None
TOL=1e-6
def out(s):
    print(s, flush=True)
    if log:
        with open(log,'a') as f: f.write(s+'\n')

rng=random.Random(seed0*7919+13); N=(1<<n)-1; t0=time.time()
games=0; screened=0; sf=0
W_tight=0; W_nottight=0
key_ok=0; key_bad=0; key_eq=0; key_strict=0
nonconst=0; const=0
out(f"=== KEY screen n={n} seed0={seed0} trials={trials} @ {time.strftime('%H:%M:%S')} ===")

for t in range(trials):
    kk=rng.randint(2,4); c=rng.randint(n,7*n)
    v=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)]).v
    games+=1
    phif=leximin_core_float(n,v,tol=1e-9)
    if phif is None: continue
    # float screen: any S with room and star-fail?
    cand=[]
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=sum(phif[i] for i in range(n) if S>>i&1)
        mx=core_max_xS_f(n,N,v,S)
        if mx is None or mx<=pS+TOL: continue          # no room
        sm=star_max_f(n,N,v,phif,S)
        if sm is None: continue
        if sm<=pS+TOL:                                  # star fails (can't raise S-total)
            cand.append(S)
    if not cand: continue
    screened+=1
    # exact verify this game
    g=Game(n,v)
    phi=leximin_core_exact(g)
    if phi is None: continue
    tights=set(tight_coalitions(g,phi))
    for S in cand:
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        rc=residual_cover(g,phi,S)
        if rc is None or not rc['lambda']: continue
        sf+=1
        sig=rc['mu']; r=rc['r']
        W=0
        for Uc in rc['lambda']: W|=Uc
        Tstar=W&S
        # r on T*
        rT=[r[k] for k in members(Tstar,n)]
        if len(set(rT))>1: nonconst+=1
        else: const+=1
        sW=xS(phi,W,n)-g.v[W]
        if sW==0: W_tight+=1
        else: W_nottight+=1
        sT=xS(phi,Tstar,n)-g.v[Tstar]
        if sW<=sT: key_ok+=1
        else:
            key_bad+=1
            out("*** KEY VIOLATION slack(W)>slack(T*) *** "
                +f"v={[str(u) for u in g.v]} S={members(S,n)} W={members(W,n)} "
                +f"Tstar={members(Tstar,n)} sW={sW} sT={sT} r={ {kk2:str(r[kk2]) for kk2 in r} }")
        if sW==sT: key_eq+=1
        else: key_strict+=1
        if len(set(rT))>1:
            out(f"[nonconst cover] v={[str(u) for u in g.v]} S={members(S,n)} "
                f"W={members(W,n)} Tstar={members(Tstar,n)} rT={[str(x) for x in rT]} "
                f"sig={sig} sW={sW} sT={sT}")
    if games%200==0:
        out(f"[prog] games={games} screened={screened} sf={sf} | Wtight={W_tight} "
            f"Wnottight={W_nottight} | KEYok={key_ok} bad={key_bad} (eq={key_eq} "
            f"strict={key_strict}) | cover const={const} nonconst={nonconst} t={time.time()-t0:.0f}s")

out(f"DONE n={n} seed0={seed0}: games={games} screened={screened} sf={sf}")
out(f"  W tight={W_tight}  W NOT tight={W_nottight}")
out(f"  KEY ok={key_ok} bad={key_bad}  (equality={key_eq} strict={key_strict})")
out(f"  cover const-on-T*={const} nonconst-on-T*={nonconst}")
