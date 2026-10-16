#!/usr/bin/env python3
"""Exact rational count arithmetic and finite Decimal structural corroboration."""
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
from math import factorial
from pathlib import Path
import hashlib
import json
import random

BASE=Path(__file__).resolve().parent
D=Decimal
TOL=D('1e-62')


def require(ok,message):
    if not ok:
        raise RuntimeError(message)


def dec(x):
    return D(x.numerator)/D(x.denominator) if isinstance(x,Fraction) else D(x)


def primitive(a,b):
    a,b=list(map(dec,a)),list(map(dec,b))
    sa,sb=sum(a),sum(b)
    if min(sa,sb)==0:
        return [D(0)]*len(a)
    short,long=(a,b) if sa<=sb else (b,a)
    t=min(sa,sb)
    caps=[min(x,t) for x in long]
    q=(1-sum(caps)/t).exp()/2
    return [(1-q)*x+q*y for x,y in zip(short,caps)]


def aggregate(h,l):
    z=[D(0)]*len(h[0])
    for hr,lr in zip(h,l):
        z=[x+y for x,y in zip(z,primitive(hr,lr))]
    return z


def run():
    e=D(1).exp()
    ceiling_constant=1+(-1/e).exp()/2
    lower=sum(Fraction(1,factorial(k)) for k in range(3))
    upper=sum(Fraction(1,factorial(k)) for k in range(7))+Fraction(1,factorial(7))*Fraction(8,7)
    require(lower>2 and upper<4,'Exact e bounds failed')
    require(Fraction(51,40)+Fraction(3,2)==Fraction(111,40)<3,'Exact count arithmetic failed')
    rng=random.Random(2026101604)
    random_checks=0
    largest=D(0)
    for n in (2,3,7,19):
        for trial in range(200):
            rawh=[rng.randrange(5) for _ in range(n)]
            if sum(rawh)==0:
                rawh[0]=1
            h=[D(x)/sum(rawh) for x in rawh]
            rawl=[rng.randrange(1,6) for _ in range(n-1)]
            scale=D(rng.randrange(4,17))/4
            l=[D(rng.randrange(1,9))/4]+[scale*D(x)/sum(rawl) for x in rawl]
            low=l[:]
            low[0]=D(0)
            fullpay=primitive(h,l)
            lowpay=primitive(h,low)
            # Every opponent is affine in q, so endpoint maxima are exact.
            total=sum(max(fullpay[k],lowpay[k]) for k in range(1,n))
            require(total<=ceiling_constant+TOL,'Sharp branch ceiling inequality failed')
            largest=max(largest,total)
            random_checks+=1

    sharp=[]
    for r in (1,3,7):
        n=3*r+1
        t=D(1)/r
        h,l=[],[]
        for j in range(r):
            hr=[D(0)]*n
            lr=[D(0)]*n
            hr[1+3*j]=t
            lr[0]=t
            lr[2+3*j]=t
            lr[3+3*j]=t/e
            h.append(hr)
            l.append(lr)
        maxima=[D(0)]*n
        count=0
        for bits in product((0,1),repeat=r):
            altered=[row[:] for row in l]
            for j,bit in enumerate(bits):
                altered[j][0]=t*bit
            z=aggregate(h,altered)
            maxima=[max(x,y) for x,y in zip(maxima,z)]
            count+=1
        total=sum(maxima[1:])
        require(abs(total-ceiling_constant)<=TOL,'Sharp replicated ceiling family mismatch')
        sharp.append({'branches':r,'owners':n,'actual_endpoint_reports':count,'sum_individual_maxima':str(total)})

    crossing=[]
    for r in (1,3,7):
        n=2*r+3
        t=Fraction(1,2*r)
        h,l=[],[]
        for group in range(2):
            for j in range(r):
                hr=[Fraction(0)]*n
                lr=[Fraction(0)]*n
                hr[1+group]=t
                lr[0]=t
                lr[3+group*r+j]=t
                h.append(hr)
                l.append(lr)
        p=[D(0)]*n
        p[1]=p[2]=D(5)/8
        patterns=[]
        for full1,full2 in product((False,True),repeat=2):
            altered=[row[:] for row in l]
            for group,full in enumerate((full1,full2)):
                for j in range(r):
                    altered[group*r+j][0]=t if full else t/2
            z=aggregate(h,altered)
            accounts=[x+y for x,y in zip(p,z)]
            pattern=tuple(k for k in range(1,n) if accounts[k]>1)
            expected=tuple(k for k,full in ((1,full1),(2,full2)) if full)
            require(pattern==expected,'Strict four-region family mismatch')
            require(z[0]>0,'Positive owner payment missing')
            require(all(abs(accounts[k]-1)>TOL for k in (1,2)),'Cap tie in strict witness')
            patterns.append(list(pattern))
        require(len({tuple(x) for x in patterns})==4,'Missing cap pattern')
        crossing.append({'branches':2*r,'owners':n,'effective_grid':'5/4','strict_patterns':patterns})
    sources=('JOINT_RESPONSE_CONVEX_LOCAL_FRONTIER.txt','CONVEX_LOCAL_FOUR_PROGRAM_BOUND.txt')
    return {'status':'PASS','arithmetic':'Exact Fraction endpoint/count arithmetic; 90-digit Decimal finite corroboration otherwise',
            'exact_e_lower':str(lower),'exact_e_upper':str(upper),'exact_cap_sum':'111/40 < 3',
            'sharp_ceiling_constant':str(ceiling_constant),'random_branch_checks':random_checks,
            'largest_random_ceiling_sum':str(largest),'sharp_ceiling_families':sharp,'four_region_families':crossing,
            'source_sha256':{name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in sources}}


if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=90
        print(json.dumps(run(),indent=2,sort_keys=True))
