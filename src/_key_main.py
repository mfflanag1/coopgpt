"""Consolidated decisive driver. Float-screen star-fails; per star-fail exact-test:
  (Q1)  exists a CONSTANT-on-T* Farkas cover  [proof route: => KEY via Steps 4-5]
  (KEY) v(W)>=phi(P)+v(T*) for the found cover  [verified target]
  (D)   d*(S) <= slack  [Lemma D itself; d*>slack would REFUTE the conjecture]
Reports any (Q1)-miss (would mean the const-cover proof route fails on some case),
any (KEY) violation, any Lemma D counterexample.
"""
import random, sys, time, json
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import Game, exact_lp_min
from leximin import leximin_core_float, leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump)
from hunt_exact_points import rand_point_sum, game_from_points
from _key_constcover import const_cover_exists

def members(S,n): return [i for i in range(n) if S>>i&1]

def core_max_xS_f(n,N,v,S):
    A=[[-1.0 if T>>i&1 else 0.0 for i in range(n)] for T in range(1,N)]
    b=[-float(v[T]) for T in range(1,N)]
    Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

def star_max_f(n,N,v,x,S):
    A=[[-1.0 if T>>i&1 else 0.0 for i in range(n)] for T in range(1,N)]
    b=[-float(v[T]) for T in range(1,N)]
    for i in range(n):
        if S>>i&1:
            row=[0.0]*n; row[i]=-1.0; A.append(row); b.append(-float(x[i]))
    Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

def rand_points_biased(n,c,rng):
    k=rng.randint(2,3)
    base=rand_point_sum(n,c,rng); pts=[base]
    for _ in range(k-1):
        p=list(base); idx=rng.sample(range(n),rng.randint(1,n))
        s=sum(p[i] for i in idx); nv=rand_point_sum(len(idx),s,rng)
        for j,i in enumerate(idx): p[i]=nv[j]
        pts.append(p)
    return pts

def run(n,seed0,trials,log,biased=True,doQ1=True):
    def out(s):
        print(s,flush=True)
        with open(log,'a') as f: f.write(s+'\n')
    rng=random.Random(seed0*104729+7); N=(1<<n)-1; t0=time.time()
    games=scr=sf=nc=0
    q1_ok=q1_miss=0; key_ok=key_bad=0; lemD_ok=lemD_bad=0
    nc_q1_ok=nc_q1_miss=0; _lastsf=[0]
    TOL=1e-6
    out(f"=== KEY-MAIN n={n} seed0={seed0} trials={trials} biased={biased} @ {time.strftime('%H:%M:%S')} ===")
    for t in range(trials):
        c=rng.randint(n,6*n)
        pts=rand_points_biased(n,c,rng) if biased else [rand_point_sum(n,c,rng) for _ in range(rng.randint(2,4))]
        v=game_from_points(n,pts).v
        games+=1
        phif=leximin_core_float(n,v,tol=1e-9)
        if phif is None: continue
        cand=[]
        for S in range(1,N):
            if bin(S).count("1")<2: continue
            pS=sum(phif[i] for i in range(n) if S>>i&1)
            mx=core_max_xS_f(n,N,v,S)
            if mx is None or mx<=pS+TOL: continue
            sm=star_max_f(n,N,v,phif,S)
            if sm is None or sm<=pS+TOL: cand.append(S)
        if not cand: continue
        scr+=1
        g=Game(n,v); phi=leximin_core_exact(g)
        if phi is None: continue
        for S in cand:
            pS=xS(phi,S,n)
            if core_max_xS(g,S)<=pS: continue
            h,_,_=star_holds(g,phi,S)
            if h: continue
            rc=residual_cover(g,phi,S)
            if rc is None or not rc['lambda']: continue
            sf+=1
            sig=rc['mu']; r=rc['r']; W=0
            for U in rc['lambda']: W|=U
            Tstar=W&S; P=N&~S
            rT=[r[k] for k in members(Tstar,n)]; isnc=len(set(rT))>1
            if isnc: nc+=1
            # (Q1)
            if doQ1:
                q1,part=const_cover_exists(g,phi,S)
                if q1: q1_ok+=1
                else:
                    q1_miss+=1
                    out("*** (Q1) MISS: no constant-on-T* cover *** "
                        +json.dumps(dict(n=n,v=[str(u) for u in g.v],S=members(S,n))))
                if isnc:
                    if q1: nc_q1_ok+=1
                    else: nc_q1_miss+=1
            # (KEY)
            keyok = g.v[W] >= xS(phi,P,n)+g.v[Tstar]
            if keyok: key_ok+=1
            else:
                key_bad+=1
                out("*** (KEY) VIOLATION *** "+json.dumps(dict(n=n,v=[str(u) for u in g.v],
                    S=members(S,n),W=members(W,n),Tstar=members(Tstar,n))))
            # (D): KEY=>LemD is proven, so only when KEY fails can LemD fail. Also
            # spot-check d* on a small independent sample to re-validate the implication.
            if (not keyok) or (sf % 50 == 0):
                d=max_exact_bump(g,S); slack=pS-g.v[S]
                if d<=slack: lemD_ok+=1
                else:
                    lemD_bad+=1
                    out("*** LEMMA D COUNTEREX d*>slack *** "+json.dumps(dict(n=n,
                        v=[str(u) for u in g.v],S=members(S,n),dstar=str(d),slack=str(slack))))
        if sf and sf%25==0 and sf!=_lastsf[0]:
            _lastsf[0]=sf
            out(f"[prog] games={games} scr={scr} sf={sf} nc={nc} | Q1 ok={q1_ok} miss={q1_miss} "
                f"| KEY ok={key_ok} bad={key_bad} | D ok={lemD_ok} bad={lemD_bad} "
                f"| ncQ1 ok={nc_q1_ok} miss={nc_q1_miss} t={time.time()-t0:.0f}s")
    out(f"DONE n={n} s={seed0}: games={games} scr={scr} sf={sf} nc={nc}")
    out(f"  Q1 const-cover exists: ok={q1_ok} MISS={q1_miss}")
    out(f"  KEY: ok={key_ok} bad={key_bad}")
    out(f"  Lemma D (d*<=slack): ok={lemD_ok} bad={lemD_bad}")
    out(f"  among non-const covers: Q1 ok={nc_q1_ok} MISS={nc_q1_miss}")

if __name__=="__main__":
    n=int(sys.argv[1]); seed0=int(sys.argv[2]); trials=int(sys.argv[3])
    log=sys.argv[4]; biased=("unbiased" not in sys.argv[5:])
    doQ1=("noq1" not in sys.argv[5:])
    run(n,seed0,trials,log,biased,doQ1)
