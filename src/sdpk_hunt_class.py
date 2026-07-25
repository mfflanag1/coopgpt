"""Bonus-tier SD-prekernel multi-valuedness hunt, restricted to exact / totally
balanced games (generators from hunt_sd.gen). Same search as sdpk_hunt."""
import random, sys, json
from fractions import Fraction as F
import numpy as np
from scipy.optimize import minimize
from sd import sd_prenucleolus_float, certified_sd_prenucleolus
from sdpk import is_equalized, is_efficient
from sdpk_float import s_pairs_float
from hunt_sd import gen

def to_x(n,t,vN):
    xf=np.empty(n); xf[:n-1]=t; xf[n-1]=vN-t.sum(); return xf

def polish(n,g,xf):
    vN=g.v[g.N]; cands=[]
    for md in (6,12,24,48):
        x=[F(xf[i]).limit_denominator(md) for i in range(n-1)]; x.append(vN-sum(x)); cands.append(x)
    for k in (1,2,3,4,6,8,12,24):
        x=[F(round(xf[i]*k),k) for i in range(n-1)]; x.append(vN-sum(x)); cands.append(x)
    seen=set()
    for x in cands:
        key=tuple(x)
        if key in seen or sum(x)!=vN: continue
        seen.add(key)
        if is_equalized(g,x): return x
    return None

def hunt(cls,n,trials,seed,log,nstart=14):
    rng=random.Random(seed); tried=0; best=None
    for t in range(trials):
        g=gen(cls,n,rng)
        if g is None: continue
        x0f=sd_prenucleolus_float(g)
        if x0f is None: continue
        tried+=1
        vf=np.array([float(x) for x in g.v]); vN=float(g.v[g.N])
        def obj(tt):
            xf=to_x(n,tt,vN); res,_=s_pairs_float(n,g.N,vf,xf); return sum(r*r for r in res)
        for s in range(nstart):
            if s<nstart//2:
                t0=x0f[:n-1]+np.array([rng.uniform(-4,4) for _ in range(n-1)])
            else:
                t0=np.array([vN/n+rng.uniform(-vN,vN) for _ in range(n-1)])
            r=minimize(obj,t0,method="Nelder-Mead",
                       options={"xatol":1e-10,"fatol":1e-18,"maxiter":2000,"maxfev":2000})
            xf=to_x(n,r.x,vN); dist=float(np.max(np.abs(xf-x0f)))
            if r.fun<1e-9 and dist>1e-2:
                x=polish(n,g,xf)
                if x is not None:
                    xstar=certified_sd_prenucleolus(g)
                    if xstar is not None and list(x)!=list(xstar) and is_equalized(g,xstar):
                        msg=(f"*** {cls} CANDIDATE trial {t}\n    v={vl(g)}\n"
                             f"    x={x}\n    x*={list(xstar)}\n"
                             f"    x in core={g.in_core(x)}\n")
                        log.write(msg); log.flush(); print(msg,end="",flush=True)
                        return ("WITNESS",g,x,xstar)
            if r.fun<1e-7 and dist>1e-2 and (best is None or r.fun<best[0]):
                best=(r.fun,vl(g),dist)
        if tried%10==0:
            m=f"[{cls} n={n}] tried {tried} (trial {t}); best far-resid {best[0] if best else 'none'}\n"
            log.write(m); log.flush(); print(m,end="",flush=True)
    return ("NONE",best,tried)

def vl(g): return [int(x) if x.denominator==1 else str(x) for x in g.v]

if __name__=="__main__":
    cls=sys.argv[1] if len(sys.argv)>1 else "exact"
    n=int(sys.argv[2]) if len(sys.argv)>2 else 4
    trials=int(sys.argv[3]) if len(sys.argv)>3 else 300
    seed=int(sys.argv[4]) if len(sys.argv)>4 else 7
    with open(f"../results/agent_sdpk_hunt_{cls}_n{n}.txt","a") as log:
        h=f"\n=== SD-PK {cls} hunt n={n} trials={trials} seed={seed} ===\n"
        log.write(h); log.flush(); print(h,end="")
        res=hunt(cls,n,trials,seed,log)
        if res[0]=="WITNESS":
            _,g,x,xstar=res
            out={"cls":cls,"n":n,"v":[str(v) for v in g.v],
                 "x_second":[str(v) for v in x],"x_sd_prenucleolus":[str(v) for v in xstar],
                 "x_in_core":g.in_core(x)}
            json.dump(out,open(f"../results/agent_sdpk_witness_{cls}.json","w"),indent=2)
            m=f"SAVED to results/agent_sdpk_witness_{cls}.json\n"; log.write(m); print(m,end="")
        else:
            _,best,tried=res
            m=f"NO {cls} WITNESS in {tried} games. best far-resid {best[0] if best else 'none'} (at {best[1] if best else ''}, dist {best[2] if best else ''})\n"
            log.write(m); log.flush(); print(m,end="")
