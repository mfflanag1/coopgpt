"""FAST float falsification of (KEY) at n=6,7 (avoids exact-simplex blowup).
All LPs via scipy HiGHS. Per star-fail (float): build cover via float residual LP,
W/T*/P, check KEY margin = v(W) - phi(P) - v(T*) in float. Any margin < -1e-4 =>
exact recheck and shout. Also tally non-constant covers. Games are exact (integer
points) so float values are near-integers/simple rationals; a real KEY violation
would show a clearly negative margin.
"""
import random, sys, time, json
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import Game
from leximin import leximin_core_float, leximin_core_exact
from lemD import star_holds, core_max_xS, xS, residual_cover
from hunt_exact_points import rand_point_sum, game_from_points

def members(S,n): return [i for i in range(n) if S>>i&1]

def core_ub(n,N,v):
    A=[[-1.0 if T>>i&1 else 0.0 for i in range(n)] for T in range(1,N)]
    b=[-float(v[T]) for T in range(1,N)]
    return A,b

def core_max_xS_f(n,N,v,S):
    A,b=core_ub(n,N,v); Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

def star_max_f(n,N,v,x,S):
    A,b=core_ub(n,N,v)
    for i in range(n):
        if S>>i&1:
            row=[0.0]*n; row[i]=-1.0; A.append(row); b.append(-float(x[i]))
    Aeq=[[1.0]*n]; beq=[float(v[N])]
    c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method="highs")
    return None if not r.success else -r.fun

def tights_f(n,N,v,x,tol=1e-6):
    return [T for T in range(1,N) if abs(sum(x[i] for i in range(n) if T>>i&1)-float(v[T]))<tol]

def residual_cover_f(n,N,v,x,S,tol=1e-6):
    """float cover: min sum r_k (push residuals down / feasibility) with
    sigma - sum_{U∋i}lambda_U = r_i (i in S, r_i>=1), =0 (off S). vars lambda(>=0),sigma,r(S).
    Returns (lam_list, sigma, r_dict) or None."""
    T=tights_f(n,N,v,x,tol); m=len(T)
    Sm=members(S,n)
    nl=m; ai=m; nv=m+1+len(Sm); ridx={k:m+1+t for t,k in enumerate(Sm)}
    Aeq=[]; beq=[]
    for i in range(n):
        row=[0.0]*nv
        for t,U in enumerate(T):
            if U>>i&1: row[t]=-1.0
        row[ai]=1.0
        if S>>i&1: row[ridx[i]]=-1.0
        Aeq.append(row); beq.append(0.0)
    bounds=[(0,None)]*m+[(None,None)]+[(1,None)]*len(Sm)
    c=[0.0]*nv
    for k in Sm: c[ridx[k]]=1.0    # minimize sum r -> canonical small cover
    r=linprog(c,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
    if not r.success: return None
    sol=r.x
    lam=[(T[t],sol[t]) for t in range(m) if sol[t]>tol]
    sigma=sol[ai]; rd={k:sol[ridx[k]] for k in Sm}
    return lam,sigma,rd

def run(n,seed0,trials,log):
    def out(s):
        print(s,flush=True)
        with open(log,'a') as f: f.write(s+'\n')
    rng=random.Random(seed0*104729+7); N=(1<<n)-1; t0=time.time()
    games=scr=sf=nc=0; key_ok=key_bad=0; nc_key_ok=0; suspicious=0
    def biased(c):
        k=rng.randint(2,3); base=rand_point_sum(n,c,rng); pts=[base]
        for _ in range(k-1):
            p=list(base); idx=rng.sample(range(n),rng.randint(1,n))
            s=sum(p[i] for i in idx); nvv=rand_point_sum(len(idx),s,rng)
            for j,i in enumerate(idx): p[i]=nvv[j]
            pts.append(p)
        return pts
    out(f"=== KEY-FLOAT n={n} seed0={seed0} trials={trials} @ {time.strftime('%H:%M:%S')} ===")
    for t in range(trials):
        c=rng.randint(n,6*n); v=game_from_points(n,biased(c)).v
        games+=1
        phif=leximin_core_float(n,v,tol=1e-9)
        if phif is None: continue
        did=False
        for S in range(1,N):
            if bin(S).count("1")<2: continue
            pS=sum(phif[i] for i in range(n) if S>>i&1)
            mx=core_max_xS_f(n,N,v,S)
            if mx is None or mx<=pS+1e-6: continue
            sm=star_max_f(n,N,v,phif,S)
            if sm is None or sm>pS+1e-6: continue   # star holds
            cov=residual_cover_f(n,N,v,phif,S)
            if cov is None: continue
            lam,sigma,rd=cov
            if not lam: continue
            did=True; sf+=1
            W=0
            for (U,l) in lam: W|=U
            Tstar=W&S; P=N&~S
            rT=[rd[k] for k in members(Tstar,n)]
            isnc = (max(rT)-min(rT))>1e-5 if rT else False
            if isnc: nc+=1
            vW=float(v[W]); rhs=sum(phif[i] for i in members(P,n))+float(v[Tstar])
            margin=vW-rhs
            if margin>=-1e-4:
                key_ok+=1
                if isnc: nc_key_ok+=1
            else:
                suspicious+=1
                out(f"[suspicious margin={margin:.5f}] exact-rechecking S={members(S,n)}...")
                g=Game(n,v); phi=leximin_core_exact(g)
                h,_,_=star_holds(g,phi,S)
                if not h:
                    rc=residual_cover(g,phi,S)
                    if rc and rc['lambda']:
                        We=0
                        for U in rc['lambda']: We|=U
                        Te=We&S; Pe=N&~S
                        exm=g.v[We]-(xS(phi,Pe,n)+g.v[Te])
                        if exm<0:
                            key_bad+=1
                            out("*** (KEY) VIOLATION (exact) *** "+json.dumps(dict(n=n,
                                v=[str(u) for u in g.v],S=members(S,n),W=members(We,n),
                                Tstar=members(Te,n),margin=str(exm))))
                            json.dump(dict(n=n,v=[str(u) for u in g.v],S=members(S,n)),
                                open(f"../results/WITNESS_KEY_CX_n{n}_s{seed0}_{sf}.json","w"))
                        else:
                            key_ok+=1
                            out(f"  exact margin={exm} >=0 (float artifact)")
        if sf and sf%50==0:
            out(f"[prog] games={games} sf={sf} nc={nc} | KEY ok={key_ok} bad={key_bad} "
                f"susp={suspicious} | ncKEYok={nc_key_ok} t={time.time()-t0:.0f}s")
    out(f"DONE n={n} s={seed0}: games={games} sf={sf} nc={nc} KEY ok={key_ok} bad={key_bad} "
        f"suspicious={suspicious} ncKEYok={nc_key_ok}")

if __name__=="__main__":
    n=int(sys.argv[1]); seed0=int(sys.argv[2]); trials=int(sys.argv[3]); log=sys.argv[4]
    run(n,seed0,trials,log)
