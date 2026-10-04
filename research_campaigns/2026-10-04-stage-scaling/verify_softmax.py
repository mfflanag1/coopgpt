"""Rational-interval checks of three-pool normalized exponential payments.

Reuses the audited exp(-q) interval primitive from the preceding campaign.
All ratios are compared after multiplying by their positive denominators.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import importlib.util
import json
import random

HERE=Path(__file__).parent
HELPER=HERE.parent/'2026-10-04-mechanism-frontier'/'verify_frontier.py'
spec=importlib.util.spec_from_file_location('prior_interval_verifier',HELPER)
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)


def multiply(p,q):
    return h.expr(*[(a+b,x*y) for a,x in p.items() for b,y in q.items()])


def groups_for(sizes):
    groups=[];offset=0
    for size in sizes:groups.append(tuple(range(offset,offset+size)));offset+=size
    return groups


def worth(c,groups,mask):
    return min(sum((c[i] for i in g if mask&(1<<i)),F(0)) for g in groups)


def payments(c,sizes):
    groups=groups_for(sizes);T=worth(c,groups,(1<<len(c))-1)
    if not T:return [{} for _ in c],h.expr((0,1))
    weights=[h.expr((sum(min(c[i],T) for i in g)/T-1,1)) for g in groups]
    Z=h.add(*weights);numerators=[{} for _ in c]
    for j,g in enumerate(groups):
        for i in g:numerators[i]=h.scale(weights[j],min(c[i],T))
    return numerators,Z


def compare(high,low,i):
    nh,zh=high;nl,zl=low
    h.nonnegative(h.add(multiply(nh[i],zl),h.scale(multiply(nl[i],zh),-1)),'own-report monotonicity')


def main():
    upper=F(4631,10000);lower=F(463,1000)
    h.nonnegative(h.expr((0,upper),(1+upper,-2)),'upper Lambert root bracket')
    h.nonnegative(h.expr((1+lower,2),(0,-lower)),'lower Lambert root bracket')
    counts=dict(profiles=0,coalitions=0,floors=0,budgets=0,monotonic_comparisons=0)
    def check(c,sizes):
        c=tuple(map(F,c));groups=groups_for(sizes);n=len(c);full=(1<<n)-1;T=worth(c,groups,full)
        pay,Z=payments(c,sizes)
        for i,num in enumerate(pay):
            M=T-worth(c,groups,full^(1<<i))
            h.nonnegative(h.add(num,h.scale(Z,-M/3)),'M/3 floor');counts['floors']+=1
        for mask in range(1,1<<n):
            total=h.add(*(pay[i] for i in range(n) if mask&(1<<i)))
            h.nonnegative(h.add(total,h.scale(Z,-worth(c,groups,mask))),'coalition coverage');counts['coalitions']+=1
        h.nonnegative(h.add(h.scale(Z,(1+upper)*T),h.scale(h.add(*pay),-1)),'three-stage subsidy bound');counts['budgets']+=1
        counts['profiles']+=1
        return pay,Z
    grids=[]
    for sizes in [(1,1,1),(2,1,1),(2,2,1),(2,2,2)]:
        saved={}
        for c in product(range(3),repeat=sum(sizes)):
            current=check(c,sizes);saved[c]=current
            for i,x in enumerate(c):
                if x:
                    low=list(c);low[i]-=1;compare(current,saved[tuple(low)],i);counts['monotonic_comparisons']+=1
        grids.append(dict(sizes=sizes,profiles=3**sum(sizes),grid=[0,1,2]))
    rng=random.Random(20261004)
    for case in range(60):
        sizes=[1,1,1]
        for _ in range(rng.randrange(4)):sizes[rng.randrange(3)]+=1
        c=tuple(F(rng.randrange(13),rng.randrange(1,6)) for _ in range(sum(sizes)))
        current=check(c,sizes)
        for i,x in enumerate(c):
            if x:
                low=list(c);low[i]/=2;compare(current,payments(tuple(low),sizes),i);counts['monotonic_comparisons']+=1
    seams=0
    for base,sizes in [((0,1,1,1,1),(1,2,2)),((0,10,1,2,1),(2,2,1)),((1,0,2,1,3),(1,2,2))]:
        groups=groups_for(sizes)
        for i in range(len(base)):
            own=next(g for g in groups if i in g);a=sum(base[j] for j in own if j!=i)
            B=min(sum(base[j] for j in g) for g in groups if g!=own)
            critical={F(0),F(B),F(max(0,B-a))}
            critical.update(F(max(0,x-a)) for j,x in enumerate(base) if j not in own)
            values=sorted({max(F(0),t+step) for t in critical for step in (F(-1,1000),F(0),F(1,1000))})
            previous=None
            for x in values:
                c=list(map(F,base));c[i]=x;current=payments(tuple(c),sizes)
                if previous is not None:compare(current,previous,i);counts['monotonic_comparisons']+=1;seams+=1
                previous=current
    # rho=1 may be caused by a capped giant; it does not identify a raw short pool.
    check((F(5),F(1),F(1,2),F(1,2)),(1,1,2))
    low=payments((F(99,100),)+(F(2,3),)*9,(1,3,3,3))
    high=payments((F(1),)+(F(2,3),)*9,(1,3,3,3))
    nl,zl=low;nh,zh=high
    h.nonnegative(h.add(multiply(nl[0],zh),h.scale(multiply(nh[0],zl),-1)),'four-stage strict gain from underreport')
    rejected=False
    try:compare(high,low,0)
    except ValueError as error:
        h.require(str(error)=='own-report monotonicity (negative)','correct four-stage rejection');rejected=True
    h.require(rejected,'four-stage negative control fails')
    x=F(99,100);residual_lower=x*(1-F(2,3)*x)
    h.require(residual_lower-F(1,3)==F(49,15000),'exact residual-rule failure margin')
    report=dict(status='PASS',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),interval_helper_sha256=hashlib.sha256(HELPER.read_bytes()).hexdigest(),counts=counts,integer_grids=grids,rational_profiles=60,seam_comparisons=seams,root_bracket=[str(lower),str(upper)],negative_controls=['Unit-rate four-stage softmax: lowering solo report 1 to 99/100 increases payment','Three-stage residual rule: lowering solo report 1 to 99/100 gains at least 49/15000'],sign_certificates=dict(h.SIGN_COUNTS),limitations=['Finite checks supplement the conventional proof.','The upper root bracket is rational; exact optimum for this rule is W(2/e).','No floating-point values decide PASS.'])
    (HERE/'EXACT_SOFTMAX.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
