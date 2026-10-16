"""Exploratory exact-certified finite LP: K2,m participation floors.
Static funding is computed per profile before own-report constraints are added.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def worth(b, mask, m):
    p=b[0] if mask&2 else 0
    h=[b[1+j] if mask&(1<<(j+2)) else 0 for j in range(m)]
    l=[min(h[j], b[1+m+j]) if mask&1 else 0 for j in range(m)]
    return sum(l)+min(p,sum(h)-sum(l))

def solve(m=2,levels=(0,1,2),theta=Q(1,2),kind='local',normalizer='static'):
    n=m+2; d=2*m+1; bs=list(product(levels,repeat=d)); lookup={b:k for k,b in enumerate(bs)}
    owner=[1]+list(range(2,n))+[0]*m
    floors=[]; statics=[]; static_certs=[]
    for b in bs:
        local=sum(min(b[1+j],b[1+m+j]) for j in range(m))
        T=worth(b,(1<<n)-1,m)
        f=theta if kind=='constant' else theta*(local if kind=='local' else T-worth(b,((1<<n)-1)^1,m))
        floors.append(f)
        A=[];rhs=[]
        for mask in range(1,1<<n):
            A.append([-Q(bool(mask&(1<<i))) for i in range(n)]);rhs.append(-Q(worth(b,mask,m)))
        A.append([-Q(i==0) for i in range(n)]);rhs.append(-f)
        ans=linprog(np.ones(n),A_ub=np.array(A,dtype=float),b_ub=np.array(rhs,dtype=float),bounds=(0,None),method='highs')
        if not ans.success:raise RuntimeError(ans.message)
        x=[Q(float(v)).limit_denominator(100000) for v in ans.x]
        w=[Q(float(-v)).limit_denominator(100000) for v in ans.ineqlin.marginals]
        if not(all(xi>=0 for xi in x) and all(sum(a*y for a,y in zip(row,x))<=r for row,r in zip(A,rhs))):raise RuntimeError('static primal')
        if not(all(wi>=0 for wi in w) and all(sum(wk*A[k][i] for k,wk in enumerate(w))>=-1 for i in range(n))):raise RuntimeError('static dual')
        if sum(x)!=-sum(wi*r for wi,r in zip(w,rhs)):raise RuntimeError('static gap')
        statics.append(sum(x));static_certs.append({'primal':list(map(str,x)),'dual':list(map(str,w))})
    C=n*len(bs); rows=[];rhs=[];tags=[]
    def add(a,r,tag):rows.append({k:Q(v) for k,v in a.items() if v});rhs.append(Q(r));tags.append(tag)
    for k,b in enumerate(bs):
        budget=statics[k] if normalizer=='static' else Q(worth(b,(1<<n)-1,m))
        add({**{k*n+i:1 for i in range(n)},C:-budget},0,['budget',k])
        for mask in range(1,1<<n):
            v=worth(b,mask,m)
            if v:add({k*n+i:-1 for i in range(n) if mask&(1<<i)},-v,['coalition',k,mask])
        if floors[k]:add({k*n:-1},-floors[k],['floor',k])
        for j in range(d):
            ix=levels.index(b[j])
            if ix+1<len(levels):
                c=list(b);c[j]=levels[ix+1];ell=lookup[tuple(c)];i=owner[j]
                add({k*n+i:1,ell*n+i:-1},0,['monotone',k,ell,i])
    ri=[];ci=[];data=[]
    for r,a in enumerate(rows):
        for c,v in a.items():ri.append(r);ci.append(c);data.append(float(v))
    mat=coo_matrix((data,(ri,ci)),shape=(len(rows),C+1)).tocsr();obj=np.zeros(C+1);obj[C]=1
    ans=linprog(obj,A_ub=mat,b_ub=list(map(float,rhs)),bounds=(0,None),method='highs')
    if not ans.success:raise RuntimeError(ans.message)
    x=[Q(float(v)).limit_denominator(1000000) for v in ans.x]
    primal_ok=all(v>=0 for v in x) and all(sum(v*x[j] for j,v in a.items())<=r for a,r in zip(rows,rhs))
    weights=[Q(float(-v)).limit_denominator(1000000) if v < -1e-9 else Q(0) for v in ans.ineqlin.marginals]
    combo={};br=Q(0);cert=[]
    for w,a,r,tag in zip(weights,rows,rhs,tags):
        if not w:continue
        for j,v in a.items():combo[j]=combo.get(j,Q(0))+w*v
        br+=w*r;cert.append({'weight':str(w),'tag':tag})
    dual_ok=combo.get(C,0)<0 and all(v>=0 for j,v in combo.items() if j!=C)
    lower=br/combo[C] if dual_ok else None
    doc={'m':m,'levels':list(levels),'theta':str(theta),'kind':kind,'normalizer':normalizer,'profiles':len(bs),'float_optimum':ans.fun,'exact_primal':str(x[C]) if primal_ok else None,'exact_lower':str(lower),'static_max_factor':str(max(v/Q(worth(b,(1<<n)-1,m)) for b,v in zip(bs,statics) if worth(b,(1<<n)-1,m))),'dual_support':len(cert),'certificate':cert,'all_profiles':bs,'static_funding':list(map(str,statics)),'static_certificates':static_certs,'primal':list(map(str,x)) if primal_ok else None}
    extra='' if normalizer=='static' else '-'+normalizer
    path=Path(__file__).with_name(f'floor-{kind}{extra}-m{m}-levels{len(levels)}-theta{theta.numerator}_{theta.denominator}.json');path.write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps({k:v for k,v in doc.items() if k not in ['certificate','all_profiles','static_funding','static_certificates','primal']}),flush=True)
    return doc

if __name__=='__main__':
    for kind in ['local','marginal']:
        for theta in [Q(1,2),Q(1)]:solve(kind=kind,theta=theta)
