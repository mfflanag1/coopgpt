"""Floating discovery: 0/low/high nested whole-owner bundles, symmetric LP."""
from fractions import Fraction as Q
from pathlib import Path
from math import isqrt
import json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def run(n,k,eps):
    A=n*n
    def val(b,c):
        if b+c==0:return Q(0)
        low=(b+c)*eps;high=1+(b+c-1)*eps;total=c*high+(n-c)*low
        vs=[total/n]
        for s in range(1,n):
            a=Q(n-s,n*n) if s<k else Q(0)
            sh=max(0,s-(n-c));part=sh*high+(s-sh)*low
            vs.append(Q(A,s*s)*part+a*(total-part))
        return min(vs)/eps
    states=[(b,c) for b in range(n+1) for c in range(n+1-b)];idx={z:i for i,z in enumerate(states)}
    values={z:val(*z) for z in states};B=2*len(states);rows=[];cols=[];data=[];rhs=[];desc=[]
    def add(terms,r,d):
        j=len(rhs)
        for col,v in terms:
            if v:rows.append(j);cols.append(col);data.append(float(v))
        rhs.append(float(r));desc.append(d)
    for b,c in states:
        i=idx[b,c];T=values[b,c]
        add([(2*i,b),(2*i+1,c),(B,-T)],0,['budget',b,c])
        for bb in range(b+1):
            for cc in range(c+1):
                v=values[bb,cc]
                if v:add([(2*i,-bb),(2*i+1,-cc)],-v,['coalition',b,c,bb,cc])
        if b:
            j=idx[b-1,c+1];add([(2*i,1),(2*j+1,-1)],0,['low_to_high',b,c])
    M=coo_matrix((data,(rows,cols)),shape=(len(rhs),B+1)).tocsr();obj=np.zeros(B+1);obj[-1]=1
    z=linprog(obj,A_ub=M,b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':30})
    out={'n':n,'k':k,'epsilon':str(eps),'success':z.success,'status':z.message,'factor':z.fun,'rows':len(rhs)}
    if z.success:
        out['rational_guess']=str(Q(float(z.fun)).limit_denominator(10**7))
        out['dual']=[{'constraint':d,'multiplier':str(Q(-float(w)).limit_denominator(10**9))} for d,w in zip(desc,z.ineqlin.marginals) if w < -1e-9]
    return out
results=[]
for n in [4,6,8,12,16,24,32]:
    for k in sorted(set([1,2,isqrt(n)])):
        r=run(n,k,Q(1,100*n**4));results.append(r)
        print({k:v for k,v in r.items() if k!='dual'},flush=True)
Path(__file__).with_name('BUNDLE_THRESHOLD_LP_DISCOVERY.json').write_text(json.dumps(results,indent=2)+'\n')
