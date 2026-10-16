"""Bounded floating diagnostic for a stronger continuous certificate.

Only proposes directions; results are not exact certificates or theorems.
"""
import json
import math
import numpy as np
from scipy.optimize import linprog

C=1+1/(2*math.e)
K=math.e-1


def solve(s,delta,pb,u,mlo=0,mhi=1,zlo=0,zhi=C,use_jensen=False,roles=False,subset=False):
    q=.5*math.exp(1-1/u)
    aa=1-q*(1+1/u)
    eta=q/s
    lam=aa+eta
    mu=K*K*eta*eta/(4*aa)
    p=K*eta
    factor=.8*math.exp(-delta)
    if use_jensen:
        zm=min(mhi,zhi)
        factor=max(factor,math.exp(-K*zm*(1+math.log(mhi/zm))) if zm else 1)
    b=.5*math.exp(1-s)*factor
    rows=[[1,-1,0,0,0],[-C,1,0,0,0],[0,-1,0,0,0],[-1,1,1,0,0],
          [0,1,1,0,0],[0,0,1,1,0],[4/3,0,1,-1,0],[0,-1,0,1,0],
          [0,-p,0,p,1],[0,-mu-aa,0,mu,1],[1,0,0,0,0]]
    rhs=[0,0,pb-s,1,1.5,1,4/3,0,0,aa*(pb-s),1]
    if roles:
        for t in [.25,.5,.75,.9,.98]:
            rows.append([0,1,1-t,0,0])
            rhs.append(1+.5*math.exp(-t))
            rows.append([-(1+.5*t*math.exp(-1/t)),1,1-t,0,0])
            rhs.append(1-t)
    if subset:
        c=C-1
        rows.append([2,0,1-c,-c,0])
        rhs.append(2+K*math.sqrt(c*mhi*delta))
    obj=np.array([0,0,lam-b,0,1])
    out=linprog(-obj,A_ub=rows,b_ub=rhs,A_eq=[[C,-1,0,0,0]],b_eq=[delta],
                bounds=[(mlo,mhi),(0,C),(0,1),(zlo,zhi),(0,None)],method="highs")
    if not out.success:
        return None
    return 1+lam*(s-1)-out.fun, out.x.tolist(),u,factor


def best(s,delta,pb,**kwargs):
    arr=[v for u in np.linspace(.43,.87,23) if (v:=solve(s,delta,pb,float(u),**kwargs))]
    return min(arr,key=lambda v:v[0]) if arr else None


if __name__=="__main__":
    baseline=[]
    for pb in [51/40,11/8]:
        for s in [1.4,1.5,1.6,1.7,1.8,2]:
            v=best(s,0,pb)
            baseline.append({"pb":pb,"s":s,"delta":0,"best":v})
    # Fine enough only to diagnose whether Jensen changes the load-bearing face.
    jensen=[]
    for pb in [51/40,11/8]:
        for s in [1.4,1.5,1.6,1.7,1.8,2]:
            cells=[]
            for mi in range(12):
                for zi in range(12):
                    v=best(s,0,pb,mlo=mi/12,mhi=(mi+1)/12,zlo=C*zi/12,zhi=C*(zi+1)/12,use_jensen=True)
                    if v:
                        cells.append((v,mi,zi))
            jensen.append({"pb":pb,"s":s,"delta":0,"worst":max(cells,key=lambda v:v[0][0]) if cells else None})
    print(json.dumps({"scope":"floating diagnostic only","baseline":baseline,"jensen":jensen},indent=2))
