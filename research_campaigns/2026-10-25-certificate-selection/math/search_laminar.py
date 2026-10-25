"""Bounded numerical discovery; outputs are not exact certificates."""
import itertools as it
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog, milp, Bounds, LinearConstraint
from scipy.sparse import lil_matrix, csr_matrix, vstack, hstack


def solve(name, profiles, f, s):
    n = len(profiles[0]); q = len(profiles)
    masks = list(range(1, 1 << n))
    value = lambda p, S: f(tuple(p[i] if S >> i & 1 else 0 for i in range(n)))
    fs = [f(p) for p in profiles]
    assert min(fs) > 0
    cols = [('cov', p, S) for p in range(q) for S in masks]
    rhs = [value(profiles[p], S) for _, p, S in cols]
    for l, a in enumerate(profiles):
        for h, b in enumerate(profiles):
            if l == h or any(x > y for x, y in zip(a, b)): continue
            changed = sum(1 << i for i in range(n) if a[i] != b[i])
            for C in masks:
                if C.bit_count() <= s and C & changed == changed:
                    cols.append(('cmp', l, h, C))
                    rhs.append(f(tuple(y-x for x,y in zip(a,b))))
    cols += [('bud', p) for p in range(q)]; rhs += [0] * q
    count = len(cols)
    a = lil_matrix((q*n+1, count))
    for j, col in enumerate(cols):
        if col[0] == 'cov':
            _, p, S = col
            for i in range(n):
                if S >> i & 1: a[p*n+i,j] = 1
        elif col[0] == 'cmp':
            _, l, h, C = col
            for i in range(n):
                if C >> i & 1: a[l*n+i,j] = -1; a[h*n+i,j] = 1
        else:
            _, p = col
            for i in range(n): a[p*n+i,j] = -1
            a[-1,j] = fs[p]
    a = a.tocsr(); b = np.array([0.]*(q*n)+[1.]); obj = -np.array(rhs)
    full = linprog(obj,A_ub=a,b_ub=b,bounds=(0,None),method='highs')
    assert full.success, full.message
    # D<=1 and positive f imply sum nu<=1/min f. Summing g<=nu
    # over all profiles gives each owner's total coverage incidence<=sum nu.
    # Thus this is a valid coverage big-M; mu need not be bounded.
    M = 1/min(fs)
    binary_cols = [j for j,c in enumerate(cols) if c[0]=='cov' and 1<c[2].bit_count()<n]
    binary_index = {j:k for k,j in enumerate(binary_cols)}
    extra = []
    for j in binary_cols:
        row={j:1, count+binary_index[j]:-M};extra.append((row,0))
    for x,j in enumerate(binary_cols):
        _,p,S=cols[j]
        for k in binary_cols[x+1:]:
            _,p2,T=cols[k]
            if p==p2 and S&T and S&~T and T&~S:
                extra.append(({count+binary_index[j]:1,count+binary_index[k]:1},1))
    aa = lil_matrix((len(extra),count+len(binary_cols)))
    bb=[]
    for row,(entry,bound) in enumerate(extra):
        for j,v in entry.items(): aa[row,j]=v
        bb.append(bound)
    matrix=vstack([hstack([a,csr_matrix((a.shape[0],len(binary_cols)))]),aa.tocsr()]).tocsr()
    bb=np.concatenate([b,bb])
    integ=np.array([0]*count+[1]*len(binary_cols))
    upper=np.array([np.inf]*count+[1]*len(binary_cols))
    result=milp(np.concatenate([obj,np.zeros(len(binary_cols))]),integrality=integ,
                bounds=Bounds(0,upper),constraints=LinearConstraint(matrix,-np.inf,bb),
                options={'time_limit':20,'mip_rel_gap':1e-9})
    record={'name':name,'s':s,'profiles':profiles,'full':-full.fun,
            'laminar':-result.fun if result.fun is not None else None,
            'status':int(result.status),'message':result.message,
            'laminar_upper_bound':-float(result.mip_dual_bound) if result.mip_dual_bound is not None else None,
            'full_support':[(cols[j],float(x)) for j,x in enumerate(full.x) if x>1e-8],
            'primal_payments':(-full.ineqlin.marginals[:-1]).reshape(q,n).tolist()}
    print(json.dumps({k:v for k,v in record.items() if k not in ['profiles','full_support','primal_payments']}),flush=True)
    return record


if __name__=='__main__':
    records=[]
    models=[('min2_star',3,lambda c:min(c[0],c[1]+c[2])),
            ('triangle',3,lambda c:min(sum(c)/2,sum(c)-max(c))),
            ('path4',4,lambda c:min(c[0]+c[2],c[1]+c[2],c[1]+c[3])),
            ('min3_mixed',4,lambda c:min(c[0],c[1],c[2]+c[3]))]
    for name,n,f in models:
        for s in [1,2]:
            profiles=list(it.product([1,2],repeat=n))
            records.append(solve(name,profiles,f,s))
    Path(__file__).with_name('LAMINAR_DISCOVERY.json').write_text(json.dumps(records,indent=2)+'\n')
