"""Exact low-rank trace and boundary-surrogate tests (-I, assertions enabled)."""
from fractions import Fraction as Q
from random import Random
from pathlib import Path
import json

rng=Random(202610170748)
counts=dict(vector_families=0,trace_matrices=0,conditioning_identities=0,
            boundary_profiles=0,boundary_mask_surrogates=0,
            exact_sampling_bounds=0)

def rank(rows):
    if not rows: return 0
    a=[list(map(Q,row)) for row in rows]
    k=0
    for j in range(len(a[0])):
        pivot=next((i for i in range(k,len(a)) if a[i][j]),None)
        if pivot is None: continue
        a[k],a[pivot]=a[pivot],a[k]
        lead=a[k][j]
        a[k]=[v/lead for v in a[k]]
        for i in range(len(a)):
            if i!=k:
                multiple=a[i][j]
                a[i]=[x-multiple*y for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a): break
    return k

def test_family(a,n,g,dimension):
    assert g>0
    assert rank(list(a.values()))<=dimension
    for mask in range(1<<n):
        assert min(a[mask])>=0
        assert sum(a[mask][i] for i in range(n) if mask>>i&1)<=g
        members=[i for i in range(n) if mask>>i&1]
        mat=[[Q(0)]*len(members) for _ in members]
        lhs=Q(0)
        for col,i in enumerate(members):
            av=a[mask^(1<<i)]
            denom=sum(av[j] for j in members)
            if denom:
                for row,j in enumerate(members): mat[row][col]=av[j]/denom
            z=av[i]
            lhs+=min(z/g,1)
            diag=mat[col][col]
            assert min(z/g,1)<=2*z/(g+z)<=2*diag
        trace=sum(mat[i][i] for i in range(len(members)))
        assert 0<=trace<=rank(mat)<=dimension
        assert lhs<=2*trace<=2*dimension
        counts['trace_matrices']+=1
    for p in [Q(1,3),Q(1,2),Q(3,4)]:
        q=1-p
        outside=Q(0)
        leaveout=Q(0)
        for mask in range(1<<n):
            k=mask.bit_count()
            probability=p**k*q**(n-k)
            outside+=probability*sum(min(a[mask][i]/g,1) for i in range(n) if not mask>>i&1)
            leaveout+=probability*sum(min(a[mask^(1<<i)][i]/g,1) for i in range(n) if mask>>i&1)
        assert outside==q/p*leaveout
        assert outside<=2*dimension*q/p
        counts['conditioning_identities']+=1
        counts['exact_sampling_bounds']+=1
    counts['vector_families']+=1

for n in range(1,8):
    for d in range(1,min(n,4)+1):
        for trial in range(5):
            basis=[[Q(rng.randrange(6)) for _ in range(n)] for _ in range(d)]
            a={}
            for mask in range(1<<n):
                weights=[Q(rng.randrange(5)) for _ in range(d)]
                vec=[sum(weights[j]*basis[j][i] for j in range(d)) for i in range(n)]
                train=sum(vec[i] for i in range(n) if mask>>i&1)
                if train:
                    scale=Q(1,rng.randrange(1,4))/train
                    vec=[scale*v for v in vec]
                a[mask]=vec
            test_family(a,n,Q(1),d)

# Boundary-discontinuous technology F(x)=x0 if every auxiliary coordinate is
# strictly positive, and0 otherwise. Supports are finite on each active face
# and infinity off it; finite profilewise surrogates must exactly preserve caps.
for d in [2,3,4]:
    for n in range(1,7):
        for trial in range(12):
            rows=[[Q(rng.randrange(4)) for _ in range(d)] for _ in range(n)]
            def f(x): return x[0] if all(x[j]>0 for j in range(1,d)) else Q(0)
            def total(indices): return [sum(rows[i][j] for i in indices) for j in range(d)]
            c=total(range(n))
            own=[f(row) for row in rows]
            g=f(c)-sum(own)
            if not g: continue
            supports={}
            required=Q(0)
            for mask in range(1<<n):
                members=[i for i in range(n) if mask>>i&1]
                cb=total(members)
                active=[j for j in range(d) if cb[j]>0]
                # F vanishes identically on this face unless all coordinates
                # are positive; an active coordinate0 has coefficient1 only then.
                p=[Q(int(j==0 and all(cb[k]>0 for k in range(d)))) for j in range(d)]
                supports[mask]=(active,p)
                for i,row in enumerate(rows):
                    off=sum(row[j] for j in range(d) if j not in active)
                    raw=sum(p[j]*row[j] for j in active)
                    if off: required=max(required,(g+own[i]-raw)/off)
                    else: assert raw>=own[i]
            big=max(Q(0),required)+1
            a={}
            for mask,(active,p) in supports.items():
                vec=[]
                for i,row in enumerate(rows):
                    off=sum(row[j] for j in range(d) if j not in active)
                    finite=sum(p[j]*row[j] for j in active)+big*off-own[i]
                    assert finite>=0
                    if off: assert finite>=g and min(finite,g)==g
                    else: assert finite==sum(p[j]*row[j] for j in active)-own[i]
                    vec.append(finite)
                a[mask]=vec
                members=[i for i in range(n) if mask>>i&1]
                assert sum(vec[i] for i in members)==f(total(members))-sum(own[i] for i in members)
                counts['boundary_mask_surrogates']+=1
            test_family(a,n,g,d+1)
            counts['boundary_profiles']+=1

result={'status':'PASS','arithmetic':'exact rational matrices, ranks and probabilities',**counts}
Path(__file__).with_name('low_rank_sampling_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
