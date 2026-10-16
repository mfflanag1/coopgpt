"""Independent Fraction replay; no SciPy or floor_probe import.
Reconstructs all coalitions by exact primal max-profit flow and all static LP
primal/dual witnesses before replaying the inter-profile mechanism certificate.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from pathlib import Path
import gzip
import json
import sys
from flow_oracle import value

def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)

def verify(path):
    text=gzip.open(path,'rt').read() if str(path).endswith('.gz') else Path(path).read_text()
    doc=json.loads(text);m=doc['m'];require(isinstance(m,int) and not isinstance(m,bool) and m>=1,'invalid pod count')
    n=m+2;d=2*m+1;theta=Q(doc['theta'])
    require(theta>=0,'negative floor parameter')
    require(doc['kind'] in ('constant','local','marginal'),'unknown floor')
    require(doc.get('normalizer','static') in ('static','production'),'unknown normalizer')
    require(doc['kind']!='marginal' or theta<=1,'marginal theorem parameter outside [0,1]')
    levels=tuple(map(Q,doc['levels']))
    require(levels and all(v>=0 for v in levels) and all(a<b for a,b in zip(levels,levels[1:])),'levels must be unique increasing nonnegative rationals')
    profiles=[tuple(map(Q,b)) for b in doc['all_profiles']]
    require(all(len(b)==d for b in profiles),'profile dimension mismatch')
    require(doc['profiles']==len(profiles)==len(levels)**d,'wrong Cartesian-domain size')
    require(len(set(profiles))==len(profiles),'duplicate profiles')
    require(set(profiles)==set(product(levels,repeat=d)),'incomplete or incorrect Cartesian report domain')
    owner=[1]+list(range(2,n))+[0]*m
    edges=[edge for j in range(1,m+1) for edge in [(0,j,1),(j,m+j,1)]]
    C=len(profiles)*n
    @lru_cache(None)
    def coal(k, mask):
        cap=tuple(profiles[k][r] if mask&(1<<owner[r]) else Q(0) for r in range(d))
        return value(cap,edges)
    def floor(k):
        if doc['kind']=='constant':return theta
        if doc['kind']=='local':
            return theta*coal(k,((1<<n)-1)^2)
        require(doc['kind']=='marginal','unknown floor')
        return theta*(coal(k,(1<<n)-1)-coal(k,((1<<n)-1)^1))
    funding=list(map(Q,doc['static_funding']));allmask=(1<<n)-1
    require(len(funding)==len(profiles)==len(doc['static_certificates']),'profile lengths')
    for k,static in enumerate(doc['static_certificates']):
        x=list(map(Q,static['primal']));w=list(map(Q,static['dual']))
        A=[[-Q(bool(mask&(1<<i))) for i in range(n)] for mask in range(1,1<<n)]
        rhs=[-coal(k,mask) for mask in range(1,1<<n)]
        A.append([-Q(i==0) for i in range(n)]);rhs.append(-floor(k))
        require(len(x)==n and len(w)==len(rhs),'static certificate lengths')
        require(all(v>=0 for v in x+w),'negative primal/dual')
        require(all(sum(a*z for a,z in zip(row,x))<=r for row,r in zip(A,rhs)),'static primal infeasible')
        require(all(sum(wj*A[j][i] for j,wj in enumerate(w))>=-1 for i in range(n)),'static dual infeasible')
        require(sum(x)==-sum(wj*r for wj,r in zip(w,rhs))==funding[k],'static funding mismatch')
    def reconstruct(tag):
        kind=tag[0];k=tag[1]
        if kind=='budget':
            budget=funding[k] if doc.get('normalizer','static')=='static' else coal(k,allmask)
            return {**{k*n+i:Q(1) for i in range(n)},C:-budget},Q(0)
        if kind=='floor':return {k*n:Q(-1)},-floor(k)
        if kind=='coalition':
            mask=tag[2]
            return {k*n+i:Q(-1) for i in range(n) if mask&(1<<i)},-coal(k,mask)
        require(kind=='monotone','bad certificate tag')
        ell,i=tag[2:]
        require(all(profiles[k][r]==profiles[ell][r] for r in range(d) if owner[r]!=i),'other owner changed')
        require(all(profiles[k][r]<=profiles[ell][r] for r in range(d) if owner[r]==i),'wrong report order')
        return {k*n+i:Q(1),ell*n+i:Q(-1)},Q(0)
    combo={};rhs=Q(0)
    for item in doc['certificate']:
        w=Q(item['weight']);require(w>=0,'negative dual weight');row,r=reconstruct(item['tag'])
        for j,a in row.items():combo[j]=combo.get(j,Q(0))+w*a
        rhs+=w*r
    require(combo.get(C,0)<0,'missing negative factor coefficient')
    require(all(v>=0 for j,v in combo.items() if j!=C),'negative payment remainder')
    lower=rhs/combo[C];require(lower==Q(doc['exact_lower']),'lower mismatch')
    x=list(map(Q,doc['primal']));require(len(x)==C+1 and all(v>=0 for v in x),'bad primal')
    K=x[C];require(K==lower==Q(doc['exact_primal']),'finite primal-dual gap')
    lookup={b:k for k,b in enumerate(profiles)};count=0
    for k,b in enumerate(profiles):
        pay=x[k*n:(k+1)*n]
        budget=funding[k] if doc.get('normalizer','static')=='static' else coal(k,allmask)
        require(sum(pay)<=K*budget and pay[0]>=floor(k),'mechanism budget/floor')
        for mask in range(1,1<<n):
            require(sum(pay[i] for i in range(n) if mask&(1<<i))>=coal(k,mask),'mechanism coalition')
        for j in range(d):
            ix=levels.index(b[j])
            if ix+1<len(levels):
                nxt=list(b);nxt[j]=levels[ix+1];ell=lookup[tuple(nxt)];i=owner[j]
                require(pay[i]<=x[ell*n+i],'mechanism own monotonicity');count+=1
    return {'file':Path(path).name,'kind':doc['kind'],'theta':str(theta),'normalizer':doc.get('normalizer','static'),'exact_factor':str(K),'profiles':len(profiles),'coalition_checks':len(profiles)*allmask,'static_certificates':len(profiles),'own_adjacent_checks':count,'dual_terms':len(doc['certificate']),'status':'PASS','scope':'finite domain only','oracle':'independent exact Fraction max-profit flow'}

if __name__=='__main__':
    paths=sys.argv[1:] or sorted(Path(__file__).parent.glob('floor-*.json'))
    for path in paths:print(json.dumps(verify(path)),flush=True)
