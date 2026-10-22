#!/usr/bin/env python3
"""Independent stdlib replay from semantic constraints, not solver matrices."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,sys

def verify(path):
    z=json.loads(Path(path).read_text());forms=[tuple(map(F,a)) for a in z['forms']];levels=tuple(map(F,z['levels']));n=len(forms[0])
    if not forms or not levels or levels!=tuple(sorted(set(levels))) or min(levels)<0:raise ValueError('Bad domain')
    if any(len(a)!=n or any(x<0 for x in a) for a in forms):raise ValueError('Bad technology')
    P=list(product(levels,repeat=n));lookup={p:j for j,p in enumerate(P)};K=n*len(P)
    X=list(map(F,z['primal']));assert len(X)==K+1 and all(x>=0 for x in X)
    def v(j,S):return min(sum(a[i]*P[j][i] for i in range(n) if S>>i&1) for a in forms)
    beta=X[-1];count=0
    for j,p in enumerate(P):
        assert sum(X[j*n:(j+1)*n])<=beta*v(j,(1<<n)-1);count+=1
        for S in range(1,1<<n):
            assert sum(X[j*n+i] for i in range(n) if S>>i&1)>=v(j,S);count+=1
        for i in range(n):
            for high in levels:
                if high<=p[i]:continue
                pp=list(p);pp[i]=high;k=lookup[tuple(pp)]
                assert X[j*n+i]<=X[k*n+i];count+=1
    coeff=[F(0)]*K;bc=F(0);rhs=F(0)
    for row in z['dual']:
        w=F(row['weight']);tag=row['tag'];assert w>=0
        if tag[0]=='budget':
            _,j=tag;assert 0<=j<len(P)
            for i in range(n):coeff[j*n+i]+=w
            bc-=w*v(j,(1<<n)-1)
        elif tag[0]=='cover':
            _,j,S=tag;assert 0<=j<len(P) and 0<S<(1<<n)
            for i in range(n):
                if S>>i&1:coeff[j*n+i]-=w
            rhs-=w*v(j,S)
        elif tag[0]=='monotone':
            _,j,k,i=tag;assert 0<=j<len(P) and 0<=k<len(P) and 0<=i<n
            assert all(P[j][h]==P[k][h] for h in range(n) if h!=i) and P[j][i]<=P[k][i]
            coeff[j*n+i]+=w;coeff[k*n+i]-=w
        else:raise ValueError('Unknown constraint')
    assert bc<0 and all(c>=0 for c in coeff)
    lower=rhs/bc;assert lower==beta
    return {'file':str(path),'status':'PASS','exact_optimum':str(beta),'primal_checks':count,'dual_rows':len(z['dual']),'scope':'Exact finite grid optimum, not an all-real upper bound.'}

if __name__=='__main__':
    for name in sys.argv[1:]:print(json.dumps(verify(name)))
