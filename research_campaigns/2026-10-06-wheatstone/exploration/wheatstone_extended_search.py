import json
import numpy as np
from scipy.stats import qmc
from wheatstone_search import Network
rng=np.random.default_rng(89353)
graphs=[('bridge_parallel_series',5,[(0,1),(0,2),(1,3),(2,3),(1,2),(0,3),(3,4)]),
        ('bridge_series',5,[(0,1),(0,2),(1,3),(2,3),(1,2),(3,4)])]
for k in (2,4,8):
    graphs.append(('bridge_fan'+str(k),5,[(0,1),(0,2)]+[(1,3)]*k+[(2,3),(1,2),(0,3),(3,4)]))
for name,n,es in graphs:
 g=Network(n,es);u=qmc.Sobol(g.m,scramble=True,seed=787).random_base2(13)
 best=0
 for trial in range(3000):
    if 'fan' in name:
        k=g.m-6
        eps=2.0**(-int(rng.integers(1,7)))
        c=np.array([1-2*eps,eps]+[10.0]*k+[10.,10.,2.,1.])
        e=0;h=c.copy();h[e]=1-eps
    else:
        c=rng.integers(1,65,g.m).astype(float)
        if trial%2:c=2.0**rng.integers(-5,6,g.m)
        e=int(rng.integers(g.m));h=c.copy();h[e]+=max(.015625,c[e]/16)
    diff=g.pay(h,e,u)-g.pay(c,e,u);change=float(np.mean(diff))
    if change<best:
        best=change;r=dict(name=name,edges=es,low=c.tolist(),high=h.tolist(),owner=e,change=change,
                           standard_error=float(np.std(diff)/np.sqrt(len(diff))),
                           caps_low=g.caps(c).tolist(),caps_high=g.caps(h).tolist())
        print(json.dumps(r),flush=True)
        with open('/tmp/wheatstone_mean_candidate.json','w') as f:json.dump(r,f,indent=2)
    if best<-.000001:break
    if 'fan' in name and trial>20:break
 print(json.dumps(dict(graph=name,trials=trial+1,minimum=best)),flush=True)
