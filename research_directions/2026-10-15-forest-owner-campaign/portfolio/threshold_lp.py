from fractions import Fraction as Q
from math import isqrt
from pathlib import Path
import json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def run(n,k,H,A):
    # Fully symmetric fixed n axis-owner min-linear technology. Finite report grid
    # {0,1,H}; scale parameter A is rational, not a fitted outcome.
    states=[(b,c) for b in range(n+1) for c in range(n+1-b)]
    idx={s:i for i,s in enumerate(states)};B=2*len(states)
    rows=[];cols=[];data=[];rhs=[];desc=[]
    def val(b,c):
        need=max(0,k-(n-b-c));small=min(b,need)+max(0,need-b)*H
        return min(Q(b+c*H),A*small)
    def add(coef,r,d):
        j=len(rhs)
        for i,v in coef:
            if v:rows.append(j);cols.append(i);data.append(float(v))
        rhs.append(float(r));desc.append(d)
    for b,c in states:
        i=idx[b,c];T=val(b,c)
        add([(2*i,b),(2*i+1,c),(B,-T)],0,['budget',b,c])
        for bb in range(b+1):
            for cc in range(c+1):
                v=val(bb,cc)
                if v:add([(2*i,-bb),(2*i+1,-cc)],-v,['coalition',b,c,bb,cc])
        if b:
            j=idx[b-1,c+1]
            add([(2*i,1),(2*j+1,-1)],0,['monotone',b,c])
    mat=coo_matrix((data,(rows,cols)),shape=(len(rhs),B+1)).tocsr()
    obj=np.zeros(B+1);obj[-1]=1
    res=linprog(obj,A_ub=mat,b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':30})
    out={'n':n,'k':k,'H':H,'A':str(A),'success':res.success,'status':res.message,'factor':res.fun,'rows':len(rhs)}
    if res.success:
        out['rational_guess']=str(Q(float(res.fun)).limit_denominator(10**6))
        out['dual']=[{'constraint':d,'multiplier':str(Q(-float(w)).limit_denominator(10**6))} for d,w in zip(desc,res.ineqlin.marginals) if w < -1e-8]
    return out

results=[]
for n,k in [(4,2),(6,2),(8,3),(12,3),(16,4),(20,4),(24,5),(32,6)]:
    for A in [Q(n,k),Q(n),Q(1)]:
        r=run(n,k,n*n,A);results.append(r)
        print({key:v for key,v in r.items() if key!='dual'},flush=True)
Path(__file__).with_name('THRESHOLD_LP_DISCOVERY.json').write_text(json.dumps(results,indent=2)+'\n')
