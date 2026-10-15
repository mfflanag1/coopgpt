"""Replay selected exact finite-domain primal and dual certificates.
No optimizer dependency; all arithmetic and production values use Fraction.
The discovery LPs used separate exact vertex-cover / dual-vertex oracles.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import json,gzip,sys
from flow_oracle import value as flow_value

def require(t,m):
    if not t:raise RuntimeError(m)

def verify(path):
    raw=Path(path).read_bytes();doc=json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)
    n,d=doc['n'],doc['d'];edges=doc['edges'];C=doc['C_index']
    if doc.get('profile_encoding')=='actual_bundles':
        ps=[tuple(tuple(map(Q,b)) for b in p) for p in doc['all_profiles']]
    else:
        b=[tuple(map(Q,b)) for b in doc['bundles']]
        ps=[tuple(tuple(Q(p[i])*b[i][j] for j in range(d)) for i in range(n)) for p in doc['all_profiles']]
    require(C==len(ps)*n,'factor index')
    @lru_cache(None)
    def val(cap):return flow_value(cap,edges)
    def worth(k,mask):return val(tuple(sum(ps[k][i][j] for i in range(n) if mask>>i&1) for j in range(d)))
    combo={};rhs=Q(0)
    for item in doc['certificate']:
        w=Q(item['weight']);require(w>=0,'negative dual multiplier');tag=item['tag']
        if tag[0]=='budget':
            k=tag[1];row={k*n+i:Q(1) for i in range(n)};row[C]=-worth(k,(1<<n)-1);b=Q(0)
        elif tag[0]=='coalition':
            k,mask=tag[1:];require(0<mask<1<<n,'mask');row={k*n+i:Q(-1) for i in range(n) if mask>>i&1};b=-worth(k,mask)
        elif tag[0]=='monotone':
            k,l,i=tag[1:];require(all(ps[k][j]==ps[l][j] for j in range(n) if j!=i),'changed other owner')
            require(all(a<=b for a,b in zip(ps[k][i],ps[l][i])),'wrong report direction');row={k*n+i:Q(1),l*n+i:Q(-1)};b=Q(0)
        else:raise RuntimeError('constraint tag')
        if 'coefficients' in item:require({j:v for j,v in row.items() if v}=={int(j):Q(v) for j,v in item['coefficients'].items()},'constraint reconstruction')
        if 'rhs' in item:require(b==Q(item['rhs']),'rhs reconstruction')
        rhs+=w*b
        for j,a in row.items():combo[j]=combo.get(j,Q(0))+w*a
    require(combo.get(C,0)<0 and all(a>=0 for j,a in combo.items() if j!=C),'dual sign')
    bound=rhs/combo[C];require(bound==Q(doc['exact_bound']),'claimed bound')
    x=list(map(Q,doc['primal']));require(len(x)==C+1 and all(a>=0 for a in x),'primal shape/sign');factor=x[C]
    coalitions=0;transitions=0
    for k,p in enumerate(ps):
        require(sum(x[k*n+i] for i in range(n))<=factor*worth(k,(1<<n)-1),'budget')
        for mask in range(1,1<<n):
            require(sum(x[k*n+i] for i in range(n) if mask>>i&1)>=worth(k,mask),'coalition coverage');coalitions+=1
    lookup={p:k for k,p in enumerate(ps)};states=[set(p[i] for p in ps) for i in range(n)]
    larger=[{r:[s for s in states[i] if s!=r and all(a<=b for a,b in zip(r,s))] for r in states[i]} for i in range(n)]
    for k,p in enumerate(ps):
        for i in range(n):
            for s in larger[i][p[i]]:
                q=p[:i]+(s,)+p[i+1:]
                if q in lookup:require(x[k*n+i]<=x[lookup[q]*n+i],'own monotonicity');transitions+=1
    require(factor==bound,'finite upper/lower mismatch')
    return dict(name=doc['name'],status='PASS',exact_finite_optimum=str(factor),profiles=len(ps),coalitions=coalitions,all_comparable_own_increases=transitions,dual_constraints=len(doc['certificate']),oracle='independent exact max-profit flow',scope='finite domains only; no claimed all-profile upper bound')

if __name__=='__main__':
    paths=sys.argv[1:] or sorted((Path(__file__).parent/'certificates').glob('*'))
    for path in paths:print(json.dumps(verify(path)),flush=True)
