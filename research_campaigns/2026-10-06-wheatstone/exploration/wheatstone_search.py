"""Exploratory coupled Sobol search only: no numerical finding is a proof."""
import json
from itertools import product
import numpy as np
from scipy.stats import qmc

def cuts(n,edges,s,t):
    cs=[]
    for bits in range(1<<n):
        if not bits>>s&1 or bits>>t&1: continue
        cs.append(sum(1<<i for i,(a,b) in enumerate(edges) if bits>>a&1 and not bits>>b&1))
    return sorted(set(cs))

def matrix(cs,m):
    return np.array([[bool(c>>i&1) for i in range(m)] for c in cs],dtype=float)

class Network:
    def __init__(self,n,edges):
        self.n,self.edges=n,edges
        self.m=len(edges)
        self.cs=cuts(n,edges,0,n-1)
        self.mini=[c for c in self.cs if not any(a!=c and a&c==a for a in self.cs)]
        self.cm=matrix(self.mini,self.m)
        self.bounds=[]
        for a,b in edges:
            self.bounds.append([matrix(cuts(n,edges,*pair),self.m) for pair in [(0,a),(b,n-1)] if pair[0]!=pair[1]])
    def caps(self,c):
        return np.array([min([c[i]]+[np.min(a@c) for a in bs]) for i,bs in enumerate(self.bounds)])
    def pay(self,c,e,u):
        d=self.caps(c)
        v=u*d
        v[:,e]=0
        containing=self.cm[self.cm[:,e]>0]
        excluding=self.cm[self.cm[:,e]==0]
        a=np.min(v@containing.T,axis=1)
        b=np.min(v@excluding.T,axis=1) if len(excluding) else np.full(len(u),np.inf)
        return np.minimum(d[e],np.maximum(0,b-a))

def main():
    rng=np.random.default_rng(913551)
    graphs=[('bridge',4,[(0,1),(0,2),(1,3),(2,3),(1,2)])]
    for n in (5,6):
        graphs.append(('overlap'+str(n),n,[(i,j) for i in range(n) for j in (i+1,i+2) if j<n]))
    graphs.append(('complete5',5,[(i,j) for i in range(5) for j in range(i+1,5)]))
    best=None
    for name,n,es in graphs:
        g=Network(n,es)
        u=qmc.Sobol(g.m,scramble=True,seed=619).random_base2(11)
        worst=0
        for trial in range(3000):
            c=rng.integers(1,33,g.m).astype(float)
            # Wide scales expose saturation regimes; all reports rational.
            if trial%2: c=2.0**rng.integers(-4,5,g.m)
            e=int(rng.integers(g.m))
            h=c.copy();h[e]+=max(0.125,c[e]/4)
            diff=g.pay(h,e,u)-g.pay(c,e,u)
            change=float(np.mean(diff))
            scale=min(g.cm@c)
            if change/scale < worst:
                worst=change/scale
                item=dict(graph=name,n=n,edges=es,low=c.tolist(),high=h.tolist(),owner=e,
                          change=change,relative=worst,standard_error=float(np.std(diff)/np.sqrt(len(diff))),
                          low_caps=g.caps(c).tolist(),high_caps=g.caps(h).tolist())
                if best is None or worst<best['relative']:
                    best=item
                    print(json.dumps(item),flush=True)
                    with open('/tmp/wheatstone_candidate.json','w') as f:json.dump(item,f,indent=2)
            if worst < -0.0001 and trial>300:break
        print(json.dumps(dict(completed_graph=name,trials=trial+1,minimal_cuts=len(g.mini),worst=worst)),flush=True)
    print(json.dumps(dict(status='exploratory_only',best=best)),flush=True)

if __name__=='__main__':main()
