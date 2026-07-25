"""Non-constant-cover hunter with TEETH. Float-screen star-fails; exact-verify.
For every star-fail: exact (KEY) v(W)>=phi(P)+v(T*), and decisive d*(S)<=slack (Lemma D).
Flags non-constant-on-T* covers specially. Biased toward thin cores (k=2,3), n=6,7.
Any (KEY) violation OR d*>slack is saved and shouted.
"""
import random, sys, time, json
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import Game
from leximin import leximin_core_float, leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump)
from hunt_exact_points import rand_point_sum, game_from_points

def members(S,n): return [i for i in range(n) if S>>i&1]

def core_max_xS_f(n,N,v,S):
    A=[]; b=[]
    for T in range(1,N):
        A.append([-1.0 if T>>i&1 else 0.0 for i in range(n)]); b.append(-float(v[T]))
    Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

def star_max_f(n,N,v,x,S):
    A=[]; b=[]
    for T in range(1,N):
        A.append([-1.0 if T>>i&1 else 0.0 for i in range(n)]); b.append(-float(v[T]))
    for i in range(n):
        if S>>i&1:
            row=[0.0]*n; row[i]=-1.0; A.append(row); b.append(-float(x[i]))
    Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

def rand_points_biased(n,c,rng):
    """thin core: 2-3 points; bias toward shared coords to make nested tight chains."""
    k=rng.randint(2,3)
    base=rand_point_sum(n,c,rng)
    pts=[base]
    for _ in range(k-1):
        p=list(base)
        # perturb by moving mass between a few coords -> keeps many coalitions tied to base
        nmov=rng.randint(1,n)
        idx=rng.sample(range(n),min(nmov,n))
        # random redistribution among idx keeping their partial sum
        s=sum(p[i] for i in idx)
        newvals=rand_point_sum(len(idx),s,rng)
        for j,i in enumerate(idx): p[i]=newvals[j]
        pts.append(p)
    return pts

n=int(sys.argv[1]); seed0=int(sys.argv[2]); trials=int(sys.argv[3])
log=sys.argv[4] if len(sys.argv)>4 else None
TOL=1e-6
def out(s):
    print(s,flush=True)
    if log:
        with open(log,'a') as f: f.write(s+'\n')

rng=random.Random(seed0*104729+7); N=(1<<n)-1; t0=time.time()
games=0; screened=0; sf=0; nc=0
key_ok=0; key_bad=0; lemD_ok=0; lemD_bad=0
nc_key_ok=0; nc_key_bad=0
maxdepth=0  # max #distinct r-values on T*
out(f"=== KEY-NC n={n} seed0={seed0} trials={trials} @ {time.strftime('%H:%M:%S')} ===")

for t in range(trials):
    c=rng.randint(n,6*n)
    v=game_from_points(n,rand_points_biased(n,c,rng)).v
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
    screened+=1
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
        sig=rc['mu']; r=rc['r']
        W=0
        for Uc in rc['lambda']: W|=Uc
        Tstar=W&S; P=N&~S
        rT=[r[k] for k in members(Tstar,n)]
        ndist=len(set(rT))
        isnc = ndist>1
        if isnc: nc+=1; maxdepth=max(maxdepth,ndist)
        # (KEY)
        vW=g.v[W]; rhs=xS(phi,P,n)+g.v[Tstar]
        keyok = vW>=rhs
        if keyok: key_ok+=1
        else: key_bad+=1
        if isnc:
            if keyok: nc_key_ok+=1
            else: nc_key_bad+=1
        if not keyok:
            pay=dict(n=n,v=[str(u) for u in g.v],S=members(S,n),W=members(W,n),
                     Tstar=members(Tstar,n),vW=str(vW),rhs=str(rhs),
                     r={kk:str(r[kk]) for kk in r},phi=[str(p) for p in phi])
            out("*** (KEY) VIOLATION *** "+json.dumps(pay))
            json.dump(pay,open(f"../results/WITNESS_KEY_CX_n{n}_s{seed0}_{sf}.json","w"),indent=1)
        # decisive Lemma D: d*(S)<=slack
        d=max_exact_bump(g,S); slack=pS-g.v[S]
        if d<=slack: lemD_ok+=1
        else:
            lemD_bad+=1
            pay=dict(n=n,v=[str(u) for u in g.v],S=members(S,n),dstar=str(d),
                     slack=str(slack),phi=[str(p) for p in phi],
                     keyok=keyok,r={kk:str(r[kk]) for kk in r})
            out("*** LEMMA D COUNTEREXAMPLE d*>slack *** "+json.dumps(pay))
            json.dump(pay,open(f"../results/WITNESS_lemD_CX_n{n}_s{seed0}_{sf}.json","w"),indent=1)
        if isnc:
            out(f"[nc {nc}] S={members(S,n)} rT={sorted(str(x) for x in rT)} "
                f"ndist={ndist} sig={sig} KEY={keyok} lemD={d<=slack} "
                f"sW={xS(phi,W,n)-vW} sT={xS(phi,Tstar,n)-g.v[Tstar]}")
    if games%300==0:
        out(f"[prog] games={games} scr={screened} sf={sf} nc={nc}(maxdist={maxdepth}) "
            f"KEY ok={key_ok} bad={key_bad} | lemD ok={lemD_ok} bad={lemD_bad} | "
            f"NCkey ok={nc_key_ok} bad={nc_key_bad} t={time.time()-t0:.0f}s")

out(f"DONE n={n} s={seed0}: games={games} scr={screened} sf={sf} nc={nc} maxdist={maxdepth}")
out(f"  KEY ok={key_ok} bad={key_bad} | lemD ok={lemD_ok} bad={lemD_bad}")
out(f"  non-const covers: KEY ok={nc_key_ok} bad={nc_key_bad}")
