#!/usr/bin/env python3
"""Bounded numerical gate only: self-consistent component-scale Huber on path4."""
import json
import itertools
import numpy as np
from scipy.optimize import minimize

weights = np.array([1.0, 2.8, 4.0])

def prices(cap, mask):
    n = len(cap)
    components = []
    start = 0
    for e in range(n-1):
        if not mask & (1 << e):
            components.append((start, e+1))
            start = e+1
    components.append((start, n))
    p = np.zeros(n)
    for a, b in components:
        if b-a == 1:
            continue
        ws = weights[a:b-1]
        cs = np.array(cap[a:b])
        W = max(ws)
        def fun(x):
            return np.dot(cs, np.where(x <= W/2, x*x/W, x-W/4))
        def jac(x):
            return cs*np.minimum(2*x/W, 1)
        res = minimize(fun, np.full(b-a, W/2), jac=jac,
                       bounds=[(0, W)]*(b-a),
                       constraints={'type':'ineq', 'fun':lambda x: x[:-1]+x[1:]-ws},
                       method='SLSQP', options={'ftol':1e-12,'maxiter':500})
        if not res.success:
            raise RuntimeError(res.message)
        p[a:b] = res.x
    slacks = p[:-1]+p[1:]-weights
    if np.min(slacks)<-1e-7:
        return None
    actual_mask = sum(1<<e for e,x in enumerate(slacks) if abs(x)<1e-7)
    if actual_mask != mask:
        return None
    return p.tolist()

out=[]
for A in [0.5,1,1.25,1.5,2,2.5,3,4,5,6,8,10,20,100]:
    cap=[A,1,1,1]
    candidates=[{'mask':mask,'p':p} for mask in range(8) if (p:=prices(cap,mask)) is not None]
    out.append({'capacity':cap,'candidates':candidates})
print(json.dumps({'status':'NUMERICAL SCOUT','weights':weights.tolist(),'profiles':out},indent=2))
