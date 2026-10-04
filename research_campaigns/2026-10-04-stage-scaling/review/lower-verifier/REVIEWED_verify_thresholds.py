"""Exact rational integration of owner-threshold payments; no solver or sampling.

Each pool sum of independent uniforms has a piecewise polynomial CDF. Integrate
its density times the other pools' survival functions over their subset-sum knots.
Finite checks supplement, but do not prove, the all-real-capacity theorem.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import comb, factorial
from pathlib import Path
import hashlib
import json
import random


def require(condition,label):
    if not condition:raise ValueError(label)


def poly_add(a,b):
    result=[F(0)]*max(len(a),len(b))
    for i,x in enumerate(a):result[i]+=x
    for i,x in enumerate(b):result[i]+=x
    return result


def poly_mul(a,b):
    result=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):result[i+j]+=x*y
    return result


def integral(p,lo,hi):
    return sum((a*(hi**(i+1)-lo**(i+1))/(i+1) for i,a in enumerate(p)),F(0))


@lru_cache(maxsize=None)
def signed_knots(widths):
    knots=Counter({F(0):1})
    for width in widths:
        old=dict(knots)
        for knot,weight in old.items():knots[knot+width]-=weight
    return tuple((t,w) for t,w in sorted(knots.items()) if w)


@lru_cache(maxsize=None)
def cdf_piece(widths,lo,density):
    m=len(widths);degree=m-1 if density else m
    denominator=F(factorial(degree))
    for width in widths:denominator*=width
    result=[F(0)]*(degree+1)
    for knot,sign in signed_knots(widths):
        if knot>lo:continue
        for power in range(degree+1):
            result[power]+=sign*comb(degree,power)*(-knot)**(degree-power)/denominator
    return tuple(result)


@lru_cache(maxsize=None)
def winner_probabilities(groups):
    require(all(g and min(g)>0 for g in groups),'positive continuous pool sums')
    knots=sorted({F(0),F(1)}|{x for group in groups for x,_ in signed_knots(group) if 0<x<1})
    probabilities=[F(0)]*len(groups)
    for lo,hi in zip(knots,knots[1:]):
        survivals=[poly_add([F(1)],[-a for a in cdf_piece(g,lo,False)]) for g in groups]
        for j,group in enumerate(groups):
            integrand=list(cdf_piece(group,lo,True))
            for h,survival in enumerate(survivals):
                if h!=j:integrand=poly_mul(integrand,survival)
            probabilities[j]+=integral(integrand,lo,hi)
    require(all(0<=p<=1 for p in probabilities),'probability range')
    require(sum(probabilities)==1,'winner probabilities sum to one')
    return tuple(probabilities)


def profile_data(c,sizes):
    groups=[];offset=0
    for size in sizes:groups.append(tuple(range(offset,offset+size)));offset+=size
    require(offset==len(c) and min(sizes)>0 and len(sizes)>=2 and min(c)>=0,'valid profile')
    totals=[sum(c[i] for i in group) for group in groups];T=min(totals)
    return groups,totals,T


def worth(c,groups,mask):
    return min(sum((c[i] for i in group if mask&(1<<i)),F(0)) for group in groups)


def payments(c,sizes,topup=True):
    groups,totals,T=profile_data(c,sizes);k=len(sizes)
    if not T:return [F(0)]*len(c),[F(0)]*k
    widths=tuple(tuple(sorted(min(c[i],T)/T for i in group if c[i])) for group in groups)
    probabilities=winner_probabilities(widths);result=[F(0)]*len(c)
    for j,group in enumerate(groups):
        for i in group:
            base=min(c[i],T)*probabilities[j]
            M=max(F(0),c[i]-(totals[j]-T))
            result[i]=max(base,M/k) if topup else base
    return result,probabilities


def main():
    counts=dict(profiles=0,coalitions=0,floors=0,monotonic_comparisons=0,topup_bounds=0,budget_bounds=0)
    maxima={};grids=[]
    def check(c,sizes):
        c=tuple(map(F,c));groups,totals,T=profile_data(c,sizes);k=len(sizes);n=len(c);full=(1<<n)-1
        pay,probs=payments(c,sizes);base,_=payments(c,sizes,False)
        for i,y in enumerate(pay):
            M=T-worth(c,groups,full^(1<<i));require(y>=M/k,'original marginal/k floor');counts['floors']+=1
        for mask in range(1,1<<n):
            require(sum(pay[i] for i in range(n) if mask&(1<<i))>=worth(c,groups,mask),'coalition coverage')
            counts['coalitions']+=1
        require(sum(pay)-sum(base)<=T,'top-up bound');counts['topup_bounds']+=1
        # A rational corollary of the analytic tail bound: e<3, log R>=1 for
        # integer R>=3. k(3/R)^R<=1 implies beta<=R+1. This is a loose check.
        R=3
        while k*3**R>R**R:R+=1
        require(sum(pay)<=(R+2)*T,'certified loose tail budget');counts['budget_bounds']+=1
        if T:
            b=sum(pay)/T-1;key=str(k)
            if key not in maxima or b>F(maxima[key]['subsidy']):
                maxima[key]=dict(subsidy=str(b),sizes=sizes,profile=list(map(str,c)))
        counts['profiles']+=1
        return pay
    configurations=[(1,1),(2,2),(1,1,1),(2,1,1),(2,2,1),(2,2,2),
                    (1,1,1,1),(2,1,1,1),(2,2,1,1),(1,1,1,1,1),(2,1,1,1,1)]
    for sizes in configurations:
        saved={}
        for c in product(range(3),repeat=sum(sizes)):
            y=check(c,sizes);saved[c]=y
            for i,x in enumerate(c):
                if x:
                    low=list(c);low[i]-=1
                    require(y[i]>=saved[tuple(low)][i],'adjacent-report monotonicity');counts['monotonic_comparisons']+=1
        grids.append(dict(sizes=sizes,grid=[0,1,2],profiles=3**sum(sizes)))
    rng=random.Random(20261004)
    for case in range(60):
        k=rng.randrange(2,6);sizes=[1]*k
        for _ in range(rng.randrange(0,4)):sizes[rng.randrange(k)]+=1
        c=tuple(F(rng.randrange(0,13),rng.randrange(1,5)) for _ in range(sum(sizes)))
        y=check(c,sizes)
        for i,x in enumerate(c):
            if x:
                low=list(c);low[i]/=2
                require(y[i]>=payments(tuple(low),sizes)[0][i],'rational-report monotonicity');counts['monotonic_comparisons']+=1
    # Every ownership position: zero, clipping and bottleneck seams, capped peer.
    seam_count=0
    for base,sizes in [((0,1,1,1,1),(1,2,2)),((0,10,1,2,1),(2,2,1)),
                       ((0,1,2,1,3,1),(2,2,2)),((1,1,0,1,2),(1,1,3))]:
        groups,_,_=profile_data(tuple(map(F,base)),sizes)
        for i in range(len(base)):
            own=next(g for g in groups if i in g);a=sum(base[j] for j in own if j!=i)
            other_totals=[sum(base[j] for j in g) for g in groups if g!=own];B=min(other_totals)
            critical={F(0),F(B),F(max(0,B-a))}
            critical.update(F(max(0,x-a)) for j,x in enumerate(base) if j not in own)
            samples=sorted({max(F(0),t+step) for t in critical for step in (F(-1,100),F(0),F(1,100))})
            last=None
            for x in samples:
                c=list(map(F,base));c[i]=x;y=payments(tuple(c),sizes)[0][i]
                if last is not None:
                    require(y>=last,'seam monotonicity');counts['monotonic_comparisons']+=1;seam_count+=1
                last=y
    c=(F(1),F(1),F(1,2),F(1,2));base,p=payments(c,(1,1,2),False);final,_=payments(c,(1,1,2))
    require(p[2]==F(7,24) and base[2]==F(7,48),'exact floor-failure witness')
    require(base[2]<F(1,6) and final[2]==F(1,6),'floor omission negative control')
    c=(F(1),)*5;base,p=payments(c,(1,2,2),False)
    require(p[0]==F(43,60) and sum(base)-1==F(17,60),'exact simplex-tail witness')
    # Two independently derived probability identities.
    require(winner_probabilities(((F(1),),)*4)==(F(1,4),)*4,'equal single owners')
    require(winner_probabilities(((F(1),),(F(1,2),F(1,2))))==(F(1,2),F(1,2)),'two symmetric distributions around one-half')
    report=dict(status='PASS',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seed=20261004,counts=counts,integer_grids=grids,rational_profiles=60,seam_comparisons=seam_count,observed_maxima=maxima,cached_probability_instances=winner_probabilities.cache_info().currsize,exact_witnesses=['(1|1|1/2,1/2): raw p_3=7/24, payment=7/48<1/6; top-up repairs it','(1|1,1|1,1): p_1=43/60, raw subsidy=17/60'],limitations=['Finite checks do not prove universal quantifiers or asymptotics.','Observed maxima are not worst-case theorems.','Probability integration may require exponentially many subset sums.','No floats or Monte Carlo decide PASS.'])
    here=Path(__file__).parent;(here/'EXACT_THRESHOLDS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
