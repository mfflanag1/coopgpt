"""Floating-point discovery only. Exact duals require verify_certificate.py."""
from itertools import product
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def values(c, left):
    n=len(c); a=[0]*(1<<n); b=[0]*(1<<n); v=[0]*(1<<n)
    for mask in range(1,1<<n):
        bit=mask&-mask; i=bit.bit_length()-1; prev=mask^bit
        a[mask]=a[prev]+(c[i] if i<left else 0)
        b[mask]=b[prev]+(c[i] if i>=left else 0)
        v[mask]=min(a[mask],b[mask])
    return v


def run(left, right, grid, timeout=120):
    start=time.monotonic(); n=left+right
    ps=list(product(grid,repeat=n)); index={p:j for j,p in enumerate(ps)}
    beta=n*len(ps); rows=[];cols=[];data=[];rhs=[];desc=[]
    def add(terms,b,d):
        j=len(rhs)
        for i,a in terms:
            rows.append(j);cols.append(i);data.append(-a)
        rhs.append(-b);desc.append(d)
    for j,c in enumerate(ps):
        v=values(c,left);t=v[-1]
        add([(beta,t)]+[(n*j+i,-1) for i in range(n)],-t,{'kind':'budget','profile':c})
        for mask in range(1,1<<n):
            if v[mask]:add([(n*j+i,1) for i in range(n) if mask>>i&1],v[mask],{'kind':'cover','profile':c,'coalition':mask})
        for i in range(n):
            k=grid.index(c[i])
            if k:
                low=list(c);low[i]=grid[k-1];q=index[tuple(low)]
                add([(n*j+i,1),(n*q+i,-1)],0,{'kind':'monotone','profile':c,'low_profile':low,'owner':i})
    mat=coo_matrix((data,(rows,cols)),shape=(len(rhs),beta+1)).tocsr()
    cost=np.zeros(beta+1);cost[-1]=1
    res=linprog(cost,A_ub=mat,b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':timeout})
    report=dict(left=left,right=right,grid=grid,profiles=len(ps),rows=len(rhs),variables=beta+1,
                status=res.message,success=res.success,objective=res.fun,
                fairness='omitted: lower-bound relaxation only',scipy=scipy.__version__,
                elapsed_seconds=time.monotonic()-start,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if res.success:
        support=[]
        for d,w in zip(desc,-res.ineqlin.marginals):
            if w>1e-9:
                support.append(dict(d,multiplier=str(Fraction(float(w)).limit_denominator(1000000))))
        report['dual_support']=support
        report['objective_rational_guess']=str(Fraction(float(res.fun)).limit_denominator(1000000))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--left',type=int,required=True)
    parser.add_argument('--right',type=int,required=True);parser.add_argument('--grid',default='0,1,2')
    parser.add_argument('--timeout',type=int,default=120);parser.add_argument('--output',required=True)
    args=parser.parse_args();grid=list(map(int,args.grid.split(',')))
    if grid!=sorted(set(grid)) or min(grid)<0 or min(args.left,args.right)<1:raise ValueError('invalid domain')
    r=run(args.left,args.right,grid,args.timeout)
    Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
    print({k:v for k,v in r.items() if k!='dual_support'})
    print('support',len(r.get('dual_support',[])))
