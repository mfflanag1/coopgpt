"""Existence-direction test: is a natural canonical core selection coalitionally
monotonic on EXACT games? Candidate = ANALYTIC CENTER of the core
(argmax sum_S log(x(S)-v(S)) s.t. x(N)=v(N)) -- a unique, continuous core selection.
For exact base + each exact single-coalition bump (member of a bump family), check
whether every i in the bumped coalition has AC_i(bumped) >= AC_i(base) (coalitional
monotonicity). Report violations. A clean pass is constructive evidence that a
coalitionally monotonic core selection EXISTS on exact games.
NOTE: float; a violation here only rejects THIS selection, it does not settle
existence; a pass supports existence.
"""
import random, sys
import numpy as np
from scipy.optimize import minimize
from hunt_monotonic import rand_game
from floatscreen import is_balanced_float, is_exact_float, _core_min_xS_float

def analytic_center(n, v):
    """Maximize sum_{proper S} log(x(S)-v(S)) with x(N)=v(N). Substitute
    x_{n-1}=v(N)-sum_{i<n-1} x_i and minimize the negative. Returns x or None."""
    N=(1<<n)-1
    props=[S for S in range(1,N)]
    def full(y):
        x=np.empty(n); x[:n-1]=y; x[n-1]=v[N]-y.sum()
        return x
    def negbar(y):
        x=full(y)
        s=0.0
        for S in props:
            g=sum(x[i] for i in range(n) if S>>i&1)-v[S]
            if g<=1e-12: return 1e18
            s+=np.log(g)
        return -s
    # start from an interior point: average of core_min per singleton + slack
    x0=np.array([_core_min_xS_float(n,v,1<<i) or 0.0 for i in range(n)])
    # nudge interior
    y0=x0[:n-1]+0.01
    best=None
    for trial in range(4):
        r=minimize(negbar, y0, method="Nelder-Mead",
                   options={"xatol":1e-9,"fatol":1e-9,"maxiter":20000})
        if r.fun<1e17:
            best=full(r.x); break
        y0=y0+np.array([0.1*(trial+1)]*(n-1))
    return best

def run(trials, seed, dmax=3):
    rng=random.Random(seed); n=4
    bases=0; checks=0; viol=0; maxdrop=0.0; examples=[]
    for t in range(trials):
        g=rand_game(4,rng,"general"); v=[float(x) for x in g.v]
        if not is_balanced_float(4,v): continue
        ve=[0.0]*16; ve[15]=v[15]; ok=True
        for S in range(1,15):
            m=_core_min_xS_float(4,v,S)
            if m is None: ok=False; break
            ve[S]=m
        if not ok: continue
        base=ve
        acb=analytic_center(4,base)
        if acb is None: continue
        bases+=1
        for S in range(1,15):
            for d in range(1,dmax+1):
                vv=list(base); vv[S]+=d
                if not is_exact_float(4,vv): continue
                ac2=analytic_center(4,vv)
                if ac2 is None: continue
                checks+=1
                for i in range(4):
                    if S>>i&1 and ac2[i] < acb[i]-1e-6:
                        viol+=1; drop=acb[i]-ac2[i]; maxdrop=max(maxdrop,drop)
                        if len(examples)<5:
                            examples.append((S,d,i,round(drop,4)))
                            print(f"AC VIOLATION base={base} S={S:b} d={d} player{i} drop={drop:.4f}",flush=True)
                break
        if bases%200==0:
            print(f"[t={t}] bases={bases} checks={checks} viol={viol} maxdrop={maxdrop:.4f}",flush=True)
        if bases>=1500: break
    print(f"FINAL bases={bases} monotonicity-checks={checks} violations={viol} maxdrop={maxdrop:.4f}",flush=True)

if __name__=="__main__":
    run(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv)>2 else 1)
