"""Finite floating-point lower-bound discovery; certify each exported dual separately."""
import argparse
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def run(sizes, grid, fairness, timeout):
    start=time.monotonic(); n=sum(sizes); k=len(sizes)
    pools=[j for j,s in enumerate(sizes) for _ in range(s)]
    profiles=list(product(grid,repeat=n)); index={c:j for j,c in enumerate(profiles)}
    levels={v:j for j,v in enumerate(grid)}; beta=len(profiles)*n
    rowidx=[]; colidx=[]; data=[]; rhs=[]; desc=[]
    def add(terms,b,d):
        row=len(rhs)
        for col,coef in terms:
            rowidx.append(row);colidx.append(col);data.append(-coef)
        rhs.append(-b);desc.append(d)
    for j,c in enumerate(profiles):
        sums=[[0]*k for _ in range(1<<n)]
        for mask in range(1,1<<n):
            bit=mask&-mask;i=bit.bit_length()-1
            sums[mask]=sums[mask^bit].copy();sums[mask][pools[i]]+=c[i]
        T=min(sums[-1])
        add([(beta,T)]+[(j*n+i,-1) for i in range(n)],-T,dict(kind='budget',profile=c))
        for mask in range(1,1<<n):
            value=min(sums[mask])
            if value:add([(j*n+i,1) for i in range(n) if mask>>i&1],value,dict(kind='cover',profile=c,coalition=mask))
        if fairness=='bottleneck':
            for i in range(n):
                if c[i] and sums[-1][pools[i]]==T:
                    # A bottleneck-pool cut allocation is an original core point,
                    # so H_i=c_i here. Other H/k floors are omitted, a relaxation.
                    add([(j*n+i,k)],c[i],dict(kind='bottleneck_floor',profile=c,owner=i))
        for i in range(n):
            level=levels[c[i]]
            if level:
                low=list(c);low[i]=grid[level-1];low=tuple(low)
                add([(j*n+i,1),(index[low]*n+i,-1)],0,dict(kind='monotone',profile=c,low_profile=low,owner=i))
    matrix=coo_matrix((data,(rowidx,colidx)),shape=(len(rhs),beta+1)).tocsr()
    objective=np.zeros(beta+1);objective[-1]=1
    result=linprog(objective,A_ub=matrix,b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':timeout})
    report=dict(sizes=sizes,grid=grid,fairness=fairness,interpretation='lower-bound relaxation: all non-bottleneck H/k floors omitted' if fairness=='bottleneck' else 'lower-bound relaxation: all fairness omitted',profiles=len(profiles),rows=len(rhs),variables=beta+1,success=bool(result.success),status=result.message,objective=result.fun,scipy=scipy.__version__,elapsed_seconds=time.monotonic()-start,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if result.success:
        report['objective_rational_guess']=str(Fraction(float(result.fun)).limit_denominator(1000000))
        report['dual_support']=[dict(d,multiplier=str(Fraction(float(w)).limit_denominator(1000000))) for d,w in zip(desc,-result.ineqlin.marginals) if w>1e-9]
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sizes',required=True);p.add_argument('--grid',default='0,1,2');p.add_argument('--fairness',choices=['none','bottleneck'],default='none');p.add_argument('--timeout',type=int,default=120);p.add_argument('--output',required=True)
    a=p.parse_args();sizes=list(map(int,a.sizes.split(',')));grid=list(map(int,a.grid.split(',')))
    if len(sizes)<2 or min(sizes)<1 or not grid or grid!=sorted(set(grid)) or min(grid)<0:raise ValueError('invalid instance')
    r=run(sizes,grid,a.fairness,a.timeout);Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
    print({key:value for key,value in r.items() if key!='dual_support'},flush=True)
    print('dual support',len(r.get('dual_support',[])),flush=True)
