"""LP relaxation discovery: totally balanced MPH-r games, not claimed packing instances."""
from itertools import combinations
from pathlib import Path
import json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def subsets(S):
    T=S
    while T:
        yield T;T=(T-1)&S

def solve(n,r,p,C):
    v={S:S for S in range(1<<n)}; names=[('v',S) for S in range(1<<n)]
    cores={};hyper={}
    for S in range(1,1<<n):
        for i in range(n):
            if S>>i&1:cores[S,i]=len(names);names.append(('core',S,i))
        for E in subsets(S):
            if E.bit_count()<=r:hyper[S,E]=len(names);names.append(('hyper',S,E))
    ur=[];uc=[];ud=[];ub=[];er=[];ec=[];ed=[];eb=[]
    def row(d,rhs,equal=False):
        rr,cc,dd,bb=(er,ec,ed,eb) if equal else (ur,uc,ud,ub)
        for col,x in d.items():
            if x:rr.append(len(bb));cc.append(col);dd.append(x)
        bb.append(rhs)
    row({v[0]:1},0,True);row({v[C]:1},1,True)
    for S in range(1,1<<n):
        row({**{cores[S,i]:1 for i in range(n) if S>>i&1},v[S]:-1},0,True)
        row({**{hyper[S,E]:1 for E in subsets(S) if E.bit_count()<=r},v[S]:-1},0,True)
        for T in subsets(S):
            row({v[T]:1,**{cores[S,i]:-1 for i in range(n) if T>>i&1}},0)
            row({v[T]:-1,**{hyper[S,E]:1 for E in subsets(T) if E.bit_count()<=r}},0)
    objective=np.zeros(len(names))
    for i in range(n):
        if C>>i&1:
            for S in range(1<<n):
                if not(S>>i&1):
                    w=p**S.bit_count()*(1-p)**(n-1-S.bit_count())
                    objective[v[S|1<<i]]+=w;objective[v[S]]-=w
    A=coo_matrix((ud,(ur,uc)),shape=(len(ub),len(names))).tocsr()
    E=coo_matrix((ed,(er,ec)),shape=(len(eb),len(names))).tocsr()
    result=linprog(objective,A_ub=A,b_ub=ub,A_eq=E,b_eq=eb,bounds=(0,None),method='highs')
    assert result.success,result.message
    threshold=min(1,r*p**(r-1))
    return dict(n=n,r=r,p=p,C=C,value=result.fun,conjectured=threshold,variables=len(names),inequalities=len(ub),equalities=len(eb),values=result.x[:1<<n].tolist(),warning='Abstract balanced MPH relaxation, not an actual arity-r packing realization or exact certificate.')

if __name__=='__main__':
    out=[];started=time.time()
    for n in [4,5,6,7]:
        for c in sorted(set([3,n-1,n])):
            for s in [2,3,4]:
                z=solve(n,3,1/s,(1<<c)-1);out.append(z)
                print(json.dumps({k:v for k,v in z.items() if k!='values'}),flush=True)
    Path(__file__).with_suffix('.json').write_text(json.dumps(dict(status='discovery_only',elapsed=time.time()-started,results=out),indent=2)+'\n')
