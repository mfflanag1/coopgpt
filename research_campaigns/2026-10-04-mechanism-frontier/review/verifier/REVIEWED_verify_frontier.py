#!/usr/bin/env python3
"""Rational interval checks of the mechanism; solver-free LP dual verification.

For q>=0, bound exp(q) by a Taylor polynomial and a geometric bound on its
positive tail, then invert to enclose exp(-q). See REPRODUCE.txt for the proof.
No floating point decides acceptance, and Python -O cannot disable checks.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json
import random


def require(test, label):
    if not test:
        raise ValueError(label)


def expr(*pairs):
    result=defaultdict(F)
    for exponent, coefficient in pairs:
        result[F(exponent)] += coefficient
    return {q:a for q,a in result.items() if a}


def add(*polys):
    return expr(*[(q,a) for p in polys for q,a in p.items()])


def scale(p, a):
    return expr(*[(q,a*b) for q,b in p.items()])


@lru_cache(maxsize=None)
def exp_interval(q):
    require(q >= 0, 'nonnegative exponential argument')
    if not q:
        return F(1), F(1)
    degree=max(80, (q.numerator+q.denominator-1)//q.denominator + 64)
    term=F(1); partial=term
    for k in range(1,degree+1):
        term*=q/k; partial+=term
    next_term=term*q/(degree+1)
    ratio=q/(degree+2)
    require(ratio < 1, 'valid Taylor tail ratio')
    upper=partial+next_term/(1-ratio)
    return 1/upper,1/partial


SIGN_COUNTS=defaultdict(int)
def nonnegative(p, label):
    if not p:
        SIGN_COUNTS['exact_symbolic_zero']+=1
        return
    if all(a>=0 for a in p.values()):
        SIGN_COUNTS['nonnegative_coefficients']+=1
        return
    lo=F(0);hi=F(0)
    for q,a in p.items():
        lower,upper=exp_interval(q)
        lo+=a*(lower if a>0 else upper)
        hi+=a*(upper if a>0 else lower)
    require(lo >= 0, label+(' (negative)' if hi<0 else ' (unresolved interval)'))
    SIGN_COUNTS['rational_interval']+=1


def worth(c,left,mask):
    return min(sum((c[i] for i in range(left) if mask>>i&1),F(0)),
               sum((c[i] for i in range(left,len(c)) if mask>>i&1),F(0)))


def payments(c,left):
    n=len(c); A=sum(c[:left]);B=sum(c[left:]);T=min(A,B)
    if not T:
        return [{} for _ in c]
    long=range(left,n) if A<=B else range(left)
    long=set(long)
    clipped=[min(x,T) for x in c]
    u=sum(clipped[i] for i in long)/T-1
    require(u>=0,'nonnegative excess capped supply')
    return [expr((u,clipped[i]/2)) if i in long else expr((0,c[i]),(u,-c[i]/2))
            for i in range(n)]


def verify_dual(report):
    left,right=report['left'],report['right'];n=left+right
    require(left>=1 and right>=1,'nonempty pools')
    coefficients=defaultdict(F);rhs=F(0)
    def profile(raw):
        c=tuple(map(F,raw))
        require(len(c)==n and min(c)>=0,'valid capacity profile')
        return c
    require(bool(report['dual_support']),'nonempty dual')
    for row in report['dual_support']:
        c=profile(row['profile']);w=F(row['multiplier'])
        require(w>0,'positive dual weight')
        kind=row['kind']
        if kind=='budget':
            T=worth(c,left,(1<<n)-1)
            coefficients['beta']+=w*T;rhs-=w*T
            for i in range(n):coefficients[(c,i)]-=w
        elif kind=='cover':
            mask=row['coalition'];require(type(mask) is int and 0<mask<(1<<n),'valid coalition')
            rhs+=w*worth(c,left,mask)
            for i in range(n):
                if mask>>i&1:coefficients[(c,i)]+=w
        elif kind=='monotone':
            low=profile(row['low_profile']);i=row['owner']
            require(type(i) is int and 0<=i<n,'valid owner')
            require(c[i]>low[i] and all(c[k]==low[k] for k in range(n) if k!=i),
                    'one-coordinate strict underreport')
            coefficients[(c,i)]+=w;coefficients[(low,i)]-=w
        else:
            raise ValueError('unknown row kind')
    beta=coefficients.pop('beta',F(0))
    require(beta>0,'positive beta coefficient')
    require(all(a<=0 for a in coefficients.values()),'no positive residual payment coefficient')
    lower=rhs/beta
    require(lower==F(report['objective_rational_guess']),'claimed lower bound matches exact combination')
    return dict(lower_bound=str(lower),beta_coefficient=str(beta),rhs=str(rhs),
                rows=len(report['dual_support']),profiles=len({tuple(r['profile']) for r in report['dual_support']}),
                negative_payment_coefficients=sum(a<0 for a in coefficients.values()))


def main():
    here=Path(__file__).parent
    duals=[]
    for path in sorted(here.glob('lp-*.json')):
        r=json.loads(path.read_text());require(r['success'],'discovery completed')
        duals.append(dict(file=path.name,**verify_dual(r)))
    reference=json.loads((here/'lp-2x2-012.json').read_text())
    mutations=[]
    def corrupted(name,fn):
        r=deepcopy(reference);fn(r)
        try: verify_dual(r)
        except (ValueError,KeyError,TypeError):mutations.append(name);return
        raise ValueError('corruption accepted: '+name)
    corrupted('negative multiplier',lambda r:r['dual_support'][0].update(multiplier='-1'))
    corrupted('wrong claim',lambda r:r.update(objective_rational_guess='1/7'))
    corrupted('empty certificate',lambda r:r.update(dual_support=[]))
    corrupted('invalid coalition',lambda r:next(x for x in r['dual_support'] if x['kind']=='cover').update(coalition=0))
    corrupted('negative capacity',lambda r:r['dual_support'][0]['profile'].__setitem__(0,-1))
    corrupted('unknown kind',lambda r:r['dual_support'][0].update(kind='invented'))
    corrupted('multiple reports changed',lambda r:next(x for x in r['dual_support'] if x['kind']=='monotone')['low_profile'].__setitem__(1,99))
    corrupted('inflated cover multiplier',lambda r:next(x for x in r['dual_support'] if x['kind']=='cover').update(multiplier='10'))

    counts=dict(profiles=0,coalitions=0,individual_floors=0,budget_bounds=0,own_report_comparisons=0)
    def check(c,left):
        c=tuple(map(F,c));n=len(c);full=(1<<n)-1;T=worth(c,left,full)
        pay=payments(c,left)
        for i,p in enumerate(pay):
            nonnegative(p,'payment nonnegative')
            M=T-worth(c,left,full^(1<<i))
            nonnegative(add(p,expr((0,-M/2))),'original removal marginal half floor')
            counts['individual_floors']+=1
        total=add(*pay)
        nonnegative(add(expr((0,T),(1,T/2)),scale(total,-1)),'1/(2e) budget')
        counts['budget_bounds']+=1
        for mask in range(1,full+1):
            selected=add(*(pay[i] for i in range(n) if mask>>i&1))
            nonnegative(add(selected,expr((0,-worth(c,left,mask)))),'coalition coverage')
            counts['coalitions']+=1
        counts['profiles']+=1
        return pay

    grids=[]
    for n in range(2,6):
        for left in range(1,n):
            for c in product(range(3),repeat=n):check(c,left)
            grids.append(dict(owners=n,left=left,grid=[0,1,2],profiles=3**n))
    rng=random.Random(20261004)
    for _ in range(200):
        n=rng.randrange(2,9);left=rng.randrange(1,n)
        c=[F(rng.randrange(0,101),rng.randrange(1,14)) for i in range(n)]
        pay=check(c,left)
        for i in range(n):
            if c[i]:
                low=c.copy();low[i]/=2
                nonnegative(add(pay[i],scale(payments(low,left)[i],-1)),'positive-capacity halving')
                counts['own_report_comparisons']+=1
    # Independently target own-pool bottleneck changes and opposite-owner clipping kinks.
    seam_checks=0
    for left in (1,2,3):
        right=3
        for others in [(F(0),)*(left-1),(F(1),)*(left-1)]:
            for opposite in [(F(1),F(2),F(4)),(F(1),F(1),F(1)),(F(0),F(1),F(3))]:
                a=sum(others);B=sum(opposite)
                critical={F(0),B}
                critical.update(t-a for t in (*opposite,B) if t-a>=0)
                samples=sorted({max(F(0),t+d) for t in critical for d in (F(-1,1000),F(0),F(1,1000))})
                last=None
                for x in samples:
                    c=(x,)+others+opposite
                    y=payments(c,left)[0]
                    if last is not None:
                        nonnegative(add(y,scale(last,-1)),'seam/kink monotonicity')
                        counts['own_report_comparisons']+=1;seam_checks+=1
                    last=y
    worst=payments((F(1),F(1),F(1)),2)
    require(add(*worst)==expr((0,1),(1,F(1,2))),'exact budget attainment')
    giant=payments((F(1000000),F(1)),1)
    require(giant==[expr((0,F(1,2))),expr((0,F(1,2)))],'giant saturation')
    # Ownership changes affect payment: capped giant differs from two original owners.
    require(add(*payments((F(2),F(1)),1)) != add(*worst),'ownership-sensitive totals')
    report=dict(status='PASS',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                seed=20261004,counts=counts,integer_grids=grids,rational_profiles=200,
                seam_and_kink_comparisons=seam_checks,sign_certificates=dict(SIGN_COUNTS),
                exact_duals=duals,corruptions_rejected=mutations,
                boundary_identities=['(1,1|1) total=1+1/(2e)','(1000000|1) pays(1/2,1/2)'],
                limitations=['Finite profiles do not prove the continuum theorem.',
                             'Floor tests use M/2 with separately proved H<=M.',
                             'LP duals prove lower bounds only; no finite primal optimality certificate.',
                             'Novelty and human specialist review unresolved.'])
    (here/'EXACT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
