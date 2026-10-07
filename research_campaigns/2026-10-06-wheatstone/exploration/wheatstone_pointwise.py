import json
import numpy as np
from scipy.stats import qmc
from wheatstone_search import Network

rng=np.random.default_rng(905113)
for n in (4,5,6,7):
    es=[(i,j) for i in range(n) for j in (i+1,i+2) if j<n]
    g=Network(n,es)
    # Rational coordinates, so any single integrand violation is exactly checkable.
    u=rng.integers(0,65,(1024,g.m))/64
    best=0
    for trial in range(5000):
        c=rng.integers(1,33,g.m).astype(float)
        e=int(rng.integers(g.m));h=c.copy();h[e]+=1
        diff=g.pay(h,e,u)-g.pay(c,e,u)
        k=int(np.argmin(diff))
        if diff[k]<best:
            best=float(diff[k])
            r=dict(graph='overlap'+str(n),edges=es,low=c.tolist(),high=h.tolist(),owner=e,
                   uniform=u[k].tolist(),integrand_change=best,
                   low_caps=g.caps(c).tolist(),high_caps=g.caps(h).tolist())
            print(json.dumps(r),flush=True)
            with open('/tmp/wheatstone_pointwise_candidate.json','w') as f:json.dump(r,f,indent=2)
        if best<0:break
    print(json.dumps(dict(n=n,trials=trial+1,minimal_cuts=len(g.mini),worst=best)),flush=True)
    if best<0:break
