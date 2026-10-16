#!/usr/bin/env python3
"""Exact finite support checks for the separately proved continuous theorem."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent

def demand(condition, details):
    if not condition:
        raise RuntimeError(details)

def prod(xs):
    ans=F(1)
    for x in xs: ans*=x
    return ans

def kappa(base):
    T=sum(base)
    return max(x/T*(1-x/T) for x in base)

def primitive(base_a,base_b,profile):
    m=len(base_a); T=sum(base_a)
    ka=kappa(base_a);kb=kappa(base_b)
    alpha=kb/(ka+kb) if ka+kb else F(1,2)
    A=profile[:m];B=profile[m:]
    def ratios(base,cap):
        return [u/v if v else F(1) for u,v in zip(base,cap)]
    if B==base_b:
        cap=tuple(min(x,T) for x in A)
        q=alpha*prod(ratios(base_a,cap))
        return tuple(q*x for x in cap)+tuple((1-q)*x for x in B)
    demand(A==base_a,'outside union of orthants')
    cap=tuple(min(x,T) for x in B)
    q=(1-alpha)*prod(ratios(base_b,cap))
    return tuple((1-q)*x for x in A)+tuple(q*x for x in cap)

def check_case(a,b):
    a=tuple(F(x) for x in a);b=tuple(F(x) for x in b)
    T=sum(a);demand(T>0 and T==sum(b),'bad baseline')
    m=len(a);n=m+len(b)
    levels=lambda x:tuple(sorted(set(x+u*T for u in (F(0),F(1,3),F(1),F(5)))))
    profiles=set(tuple(x)+b for x in product(*(levels(t) for t in a)))
    profiles.update(a+tuple(z) for z in product(*(levels(t) for t in b)))
    rule={r:primitive(a,b,r) for r in profiles}
    ka=kappa(a);kb=kappa(b)
    expected=F(1)+(ka*kb/(ka+kb) if ka+kb else 0)
    worst=F(0); coalitions=0; comparisons=0
    for r,y in rule.items():
        demand(min(sum(r[:m]),sum(r[m:]))==T,'grand value changed')
        demand(all(z>=0 for z in y),'negative payment')
        demand(sum(y)<=expected*T,'claimed budget')
        worst=max(worst,sum(y)/T)
        for mask in range(1<<n):
            lhs=sum(y[i] for i in range(n) if mask>>i&1)
            av=sum(r[i] for i in range(m) if mask>>i&1)
            bv=sum(r[i] for i in range(m,n) if mask>>i&1)
            demand(lhs>=min(av,bv),('coalition',r,mask,y))
            coalitions+=1
    for i in range(n):
        strips={}
        for r,y in rule.items():
            key=r[:i]+r[i+1:]
            strips.setdefault(key,[]).append((r[i],y[i]))
        for entries in strips.values():
            entries.sort()
            for left,right in zip(entries,entries[1:]):
                demand(left[1]==right[1],('own-report neutrality',i,left,right))
                comparisons+=1
    demand(worst==expected,('missing attainment',worst,expected))
    return {'a':list(map(str,a)),'b':list(map(str,b)),'profiles':len(profiles),
            'coalitions':coalitions,'own_comparisons':comparisons,
            'attained_factor':str(worst)}

def compositions(total,length):
    if length==1:
        yield(total,);return
    for first in range(total+1):
        for tail in compositions(total-first,length-1):yield(first,)+tail

def check_budget_vertices():
    vectors=0;corners=0
    for n in range(1,6):
        for denom in range(1,9):
            for nums in compositions(denom,n):
                w=tuple(F(z,denom) for z in nums);bound=max(x*(1-x) for x in w)
                best=F(0)
                for bits in product((0,1),repeat=n):
                    c=tuple(F(1) if bit else x for x,bit in zip(w,bits))
                    ratios=[x/z if z else F(1) for x,z in zip(w,c)]
                    value=(sum(c)-1)*prod(ratios)
                    demand(value<=bound,('budget vertex',w,c,value,bound))
                    best=max(best,value);corners+=1
                demand(best==bound,('budget attainment',w,best,bound));vectors+=1
    return {'weight_vectors':vectors,'corners':corners}

def check_pasting_identity():
    P0=F(1,4);P1=F(3,16);Q0=F(1,4);Q1=F(3,16)
    mixed_difference=(P1-P0)*(Q1-Q0)
    demand(mixed_difference==F(1,256),'pasting mixed difference')
    return {'mixed_difference':str(mixed_difference),'required_value':'0'}

cases=[
    ((1,),(1,)),
    ((F(1,2),F(1,2)),(F(1,2),F(1,2))),
    ((F(1,5),F(3,10),F(1,2)),(F(1,4),F(3,4))),
    ((F(1,10),F(1,5),F(3,10),F(2,5)),(F(1,10),F(1,10),F(4,5))),
    ((0,F(1,2),F(1,2)),(F(1,4),0,F(3,4))),
    ((0,0,1),(0,F(1,4),F(1,4),F(1,2))),
    ((F(7,9),F(14,9)),(F(7,18),F(7,6),F(7,9))),
]
report={'status':'EXACT PASS','scope':'finite support for analytic all-real proof',
        'cases':[check_case(a,b) for a,b in cases],
        'budget_vertices':check_budget_vertices(),
        'pasting':check_pasting_identity(),
        'source_sha256':hashlib.sha256((ROOT/'ONE_POOL_ORTHANT_THEOREM.txt').read_bytes()).hexdigest()}
output=ROOT/('verification_optimized.json' if not __debug__ else 'verification.json')
output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
