"""Exact fixed-mask/gain-only checks. Assertions intentionally active (-I, no -O)."""
from fractions import Fraction as Q
from itertools import product
from math import comb
from pathlib import Path
from random import Random
import json

rng=Random(202610170730)
counts=dict(profiles=0,mask_coverage_checks=0,mixture_coverage_checks=0,
            individual_outside_checks=0,mask_individual_outside_checks=0,
            complement_deficit_checks=0,residual_mask_identities=0,
            exact_weight_sums=0)

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def total(rows,d): return [sum(row[j] for row in rows) for j in range(d)]
def value(c,forms): return min(dot(p,c) for p in forms)
def rank(rows):
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

def mask_pay(rows,forms,mask):
    n,d=len(rows),len(rows[0])
    c=total(rows,d)
    t=value(c,forms)
    own=[value(row,forms) for row in rows]
    s=sum(own)
    cb=total([rows[i] for i in range(n) if mask>>i&1],d)
    p=min(forms,key=lambda p:dot(p,cb))
    out=[]
    for i,row in enumerate(rows):
        if mask>>i&1:
            out.append(value(cb,forms)-value([cb[j]-row[j] for j in range(d)],forms))
        else:
            out.append(min(dot(p,row),t-s+own[i]))
    return out

def weight(n,k,a):
    return sum((-1)**ell*comb(k,ell)*a**(n-k+ell)/Q(n-k+ell+1)
               for ell in range(k+1))

def mixture(rows,forms,a):
    n=len(rows)
    out=[Q(0)]*n
    for mask in range(1<<n):
        w=weight(n,mask.bit_count(),a)
        y=mask_pay(rows,forms,mask)
        for i in range(n): out[i]+=w*y[i]
    return out

for n in range(1,7):
    for a in [Q(1,4),Q(1,2),Q(2,3),Q(1)]:
        ws=[weight(n,mask.bit_count(),a) for mask in range(1<<n)]
        assert min(ws)>=0 and sum(ws)==1
        counts['exact_weight_sums']+=1

for n in range(1,6):
    for d in range(1,5):
        for trial in range(12):
            forms=[[Q(rng.randrange(7),rng.randrange(1,4)) for j in range(d)]
                   for _ in range(1+rng.randrange(6))]
            rows=[[Q(rng.randrange(8),rng.randrange(1,5)) for j in range(d)] for i in range(n)]
            c=total(rows,d)
            t=value(c,forms)
            own=[value(row,forms) for row in rows]
            s=sum(own)
            g=t-s
            assert g>=0
            a=[Q(1,2),Q(2,3),Q(1)][trial%3]
            y=mixture(rows,forms,a)
            bn=n*a/2+Q(n,n+1)*(1-(1-a)**(n+1))/a
            assert sum(y)<=s+bn*g
            if g==0: assert y==own
            for mask in range(1<<n):
                ym=mask_pay(rows,forms,mask)
                assert all(ym[i]>=own[i] for i in range(n))
                for coal in range(1<<n):
                    members=[i for i in range(n) if coal>>i&1]
                    worth=value(total([rows[i] for i in members],d),forms)
                    assert sum(ym[i] for i in members)>=worth
                    counts['mask_coverage_checks']+=1
                    if mask==0:
                        assert sum(y[i] for i in members)>=worth
                        counts['mixture_coverage_checks']+=1
            for i in range(n):
                for choice in range(5):
                    removed=[row*Q(rng.randrange(5),4) for row in rows[i]]
                    low=[list(row) for row in rows]
                    low[i]=[rows[i][j]-removed[j] for j in range(d)]
                    worth=value(removed,forms)
                    ylow=mixture(low,forms,a)
                    assert y[i]-ylow[i]>=worth
                    counts['individual_outside_checks']+=1
                    for mask in range(1<<n):
                        assert mask_pay(rows,forms,mask)[i]-mask_pay(low,forms,mask)[i]>=worth
                        counts['mask_individual_outside_checks']+=1
            p=min(forms,key=lambda p:dot(p,c))
            def h(x): return dot(p,x)-value(x,forms)
            rk=rank(rows)
            deficit=sum(h(row) for row in rows)
            complement=sum(h([c[j]-row[j] for j in range(d)]) for row in rows)
            assert deficit==g
            assert complement<=(rk-1)*g
            m=[t-value([c[j]-row[j] for j in range(d)],forms) for row in rows]
            assert sum(m)<=s+rk*g
            counts['complement_deficit_checks']+=1
            counts['profiles']+=1

for n in range(1,6):
    for r in range(1,6):
        forms=[[Q(int(j==k)) for j in range(r)] for k in range(r)]
        for trial in range(10):
            rows=[[Q(rng.randrange(12),3) for j in range(r)] for i in range(n)]
            own=[min(row) for row in rows]
            residual=[[v-fi for v in row] for row,fi in zip(rows,own)]
            # Standard mask has cap residual grand value; residual standalone is0.
            for mask in range(1<<n):
                original=mask_pay(rows,forms,mask)
                wrapped=[fi+yi for fi,yi in zip(own,mask_pay(residual,forms,mask))]
                assert original==wrapped
                counts['residual_mask_identities']+=1

result={'status':'PASS','arithmetic':'exact Fraction values and mask weights',**counts}
Path(__file__).with_name('gain_only_mask_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
