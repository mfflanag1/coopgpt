#!/usr/bin/env python3
"""Exact bounded checks of candidate sqrt(n) owner upper; not a general proof."""
from fractions import Fraction as Q
from itertools import product
from functools import lru_cache
from math import comb
from pathlib import Path
import json, random

COUNTS={}
def check(condition, tag):
    if not condition: raise AssertionError(tag)
    COUNTS[tag]=COUNTS.get(tag,0)+1

@lru_cache(None)
def integral(k,l,a):
    # (1/a) integral_0^a q^k(1-q)^l dq
    return sum((Q((-1)**h*comb(l,h),k+h+1)*a**(k+h) for h in range(l+1)),Q(0))

def value(V,x): return min(sum(w*t for w,t in zip(v,x)) for v in V)
def totals(b,mask):
    return tuple(sum(b[i][e] for i in range(len(b)) if mask>>i&1) for e in range(len(b[0])))

def payments(V,b,a):
    n=len(b);T=value(V,totals(b,(1<<n)-1));p=[]
    for i in range(n):
        yi=Q(0)
        others=[h for h in range(n) if h!=i]
        for bits in product((0,1),repeat=n-1):
            mask=sum(bit<<h for bit,h in zip(bits,others));x=totals(b,mask)
            # fixed report-independent form priority, exactly as main manuscript
            w=min(enumerate(V),key=lambda z:(sum(t*c for t,c in zip(z[1],x)),z[0]))[1]
            A=min(sum(t*c for t,c in zip(w,b[i])),T)
            D=value(V,tuple(x[e]+b[i][e] for e in range(len(x))))-value(V,x)
            o=sum(bits);c=n-1-o
            check(0<=A<=T and 0<=D<=T,'bounded_terms')
            yi+=integral(c+1,o,a)*A+integral(c,o+1,a)*D
        p.append(yi)
    return tuple(p)

def bound(n,a):return n*a/2+Q(n,n+1)*(1-(1-a)**(n+1))/a

def case(V,b,a):
    n=len(b);T=value(V,totals(b,(1<<n)-1));p=payments(V,b,a)
    check(all(y>=0 for y in p),'nonnegative')
    check(sum(p)<=bound(n,a)*T,'finite_bound')
    check(bound(n,a)<=n*a/2+1/a,'simplified_bound')
    for mask in range(1<<n):
        check(sum(p[i] for i in range(n) if mask>>i&1)>=value(V,totals(b,mask)),'coalition_coverage')
    for i in range(n):
        for e in range(len(b[0])):
            bb=[list(x) for x in b];bb[i][e]+=1
            pp=payments(V,tuple(tuple(x) for x in bb),a)
            check(pp[i]>=p[i],'own_component_monotonicity')

# Grid over all 3-owner, two-resource binary bundle profiles: whole-bundle
# ownership, ties, zero coordinates, zero profiles and overlapping bundles.
Vs=(((1,0),(0,1)),((1,1),),((2,0),(1,1),(0,3)),((0,0),(2,1)))
for V in Vs:
    for flat in product((Q(0),Q(1)),repeat=6):
        b=tuple(tuple(flat[2*i:2*i+2]) for i in range(3))
        for a in (Q(1,2),Q(2,3),Q(1)):
            case(V,b,a)

rng=random.Random(20261015)
for n in range(1,7):
    for z in range(8):
        d=3;V=tuple(tuple(Q(rng.randrange(5)) for e in range(d)) for k in range(5))
        b=tuple(tuple(Q(rng.randrange(5),rng.randrange(1,4)) for e in range(d)) for i in range(n))
        for a in (Q(1,3),Q(1,2)):
            case(V,b,a)

# Independent exact polynomial identity for all-open lower-bound integration.
# g=(1-q)^n gives sum r=nq+n(1-q)^n for the canonical relative-support
# selector on min-coordinate production with one unit-basis owner per resource.
attainment=[]
for n in range(1,41):
    for a in (Q(1,7),Q(1,3),Q(1,2),Q(2,3),Q(1)):
        computed=n*integral(1,0,a)+n*integral(0,n,a)
        check(computed==bound(n,a),'relative_support_attainment_identity')
        I=Q(n,n+1)*(1-(1-a)**(n+1))
        by_parts=1-(1-a)**(n+1)-a*integral(0,n,a)
        check(I==by_parts,'integration_by_parts_identity')
    if n in (1,2,3,4,8,16,40):
        a=Q(1,max(1,round((n/2)**.5)))
        attainment.append({'n':n,'a':str(a),'bound_exact':str(bound(n,a)),'bound_decimal':float(bound(n,a))})


# Exact weighted-profile obstruction, independently summed binomial tails.
mixture=[]
for n in range(2,41):
    m=1
    while m*(m-1)<2*(n-1): m+=1
    S=Q(m*(m+1),2);L=Q(2*n,m+1)
    check(m<=n,'obstruction_fixed_profile_dimension')
    for q in (Q(0),Q(1,100),Q(1,10),Q(1,4),Q(1,2),Q(3,4),Q(1)):
        budgets=[]
        for k in range(1,m+1):
            prob=sum((Q(comb(n-1,c))*q**c*(1-q)**(n-1-c) for c in range(k)),Q(0))
            budgets.append(n*q+Q(n,k)*(1-q)*prob)
        weighted=sum((Q(k)/S*budgets[k-1] for k in range(1,m+1)),Q(0))
        H=n*q+Q(n)/S*(1-q)*max(Q(0),m-(n-1)*q)
        check(weighted>=H,'weighted_binomial_jensen')
        check(H>=L,'mixture_obstruction_rational_lower')
    if n in (2,3,4,8,16,40):mixture.append({'n':n,'m':m,'lower':str(L)})

result={'status':'pass','arithmetic':'exact fractions; no LP solver or numerical acceptance',
        'counts':COUNTS,'relative_support_attainment_examples':attainment,'mixture_obstruction_examples':mixture,
        'scope':'finite checks and exact polynomial identities only; analytic theorem in OWNER_SQRT_BOUND.txt'}
Path(__file__).with_name('OWNER_SQRT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
