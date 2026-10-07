"""Exact rational checks for the Wheatstone results; finite checks are not proofs.

Standard library only. Independently enumerates graph cuts and coalitions.
Imports the previously audited generic CDF algebra solely for an independent
evaluation of the ideal integral (not of the actual k-bridge payment).
"""
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
from pathlib import Path
import importlib.util
import argparse
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def vertex_cuts(n, edges, s, t):
    cs=set()
    for mask in range(1 << n):
        if mask >> s & 1 and not mask >> t & 1:
            cs.add(sum(1 << i for i,(a,b) in enumerate(edges)
                       if mask >> a & 1 and not mask >> b & 1))
    return cs


def minimal(cs):
    return {a for a in cs if not any(b != a and a & b == b for b in cs)}


def cut_sum(c, mask):
    return sum(v for i,v in enumerate(c) if mask >> i & 1)


def graph_caps(n, edges, c):
    ds=[]
    for i,(a,b) in enumerate(edges):
        limits=[c[i]]
        for s,t in ((0,a),(b,n-1)):
            if s != t:
                limits.append(min(cut_sum(c,m) for m in vertex_cuts(n,edges,s,t)))
        ds.append(min(limits))
    return tuple(ds)


def bridge_caps(c):
    x,y,z,w,h=c
    return (min(x,z+min(h,w)),min(y,w),min(z,x),min(w,y+min(x,h)),min(h,x,w))


BRIDGE_CUTS=(0b00011,0b01100,0b10110,0b01001)


def conditional(c, e, u2):
    d=bridge_caps(c)
    random=tuple(a*b for a,b in zip(d,u2))
    a=min(cut_sum(random,m & ~(1 << e)) for m in BRIDGE_CUTS if m >> e & 1)
    b=min(cut_sum(random,m) for m in BRIDGE_CUTS if not m >> e & 1)
    return min(2*d[e],max(0,b-a))


def closed_conditional(c, e, u2):
    d=bridge_caps(c)
    x,y,z,w,h=(a*b for a,b in zip(d,u2))
    formulas=(z+min(max(0,w-y),h),
              max(0,w-min(max(0,x-z),h)),
              max(0,x-min(max(0,w-y),h)),
              y+min(max(0,x-z),h),
              min(max(0,x-z),max(0,w-y)))
    return min(2*d[e],formulas[e])


def subset_sums(c):
    sums=[0]*(1 << len(c))
    for mask in range(1,len(sums)):
        bit=mask & -mask
        sums[mask]=sums[mask ^ bit]+c[bit.bit_length()-1]
    return sums


def ideal_moments(x):
    eps=Q(1,20);b=x+eps
    def moment(j):
        return Q(1) if not j else eps**j/Q(j+1)-Q(j)*eps**(j+1)/Q((j+1)*(j+2))/b
    def p4(t):
        return sum(Q(comb(4,j))*(-1)**j*t**(4-j)*moment(j) for j in range(5))
    return (p4(Q(1))-2*p4(Q(1,2))-p4(1-x))/6


def cdf_ideal(x, module):
    a=module.minimum(module.uniform(Q(1,20)),module.uniform(x+Q(1,20)))
    p_plus_a=module.convolution(module.uniform(Q(1)),a)
    shifted=module.convolution(p_plus_a,module.atom(x))
    r=module.convolution(module.uniform(Q(1,2)),module.uniform(Q(1,2)))
    return (module.expectation(module.minimum(r,shifted),Q(1))
            -module.expectation(module.minimum(r,p_plus_a),Q(1)))


def run(repo):
    path=repo/'research_campaigns/2026-10-06-series-parallel/verification/verify.py'
    spec=importlib.util.spec_from_file_location('prior_exact_cdf',path)
    cdf=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cdf)
    es=[(0,1),(0,2),(1,3),(2,3),(1,2)]
    require(minimal(vertex_cuts(4,es,0,3)) == set(BRIDGE_CUTS),'bridge cut family')
    pairs=0
    for c in product(range(3),repeat=5):
        require(bridge_caps(c) == graph_caps(4,es,c),'bridge caps versus graph')
        for e in range(5):
            high=list(c);high[e]+=1
            for vals in product(range(3),repeat=4):
                u=list(vals);u.insert(e,0)
                a=conditional(c,e,u);b=conditional(high,e,u)
                require(a == closed_conditional(c,e,u),'low closed conditional formula')
                require(b == closed_conditional(high,e,u),'high closed conditional formula')
                require(a <= b,'five-edge pointwise monotonicity')
                pairs+=1

    k=10
    es=[(0,1),(0,2)]+[(1,3)]*k+[(2,3),(1,2),(0,3),(3,4),(3,4)]
    zmask=sum(1 << i for i in range(2,k+2))
    x,y,w,h,p,r1,r2=(1 << i for i in (0,1,k+2,k+3,k+4,k+5,k+6))
    expected={x|y|p,zmask|w|p,y|zmask|h|p,x|w|p,r1|r2}
    cs=minimal(vertex_cuts(5,es,0,4))
    require(cs == expected,'overlapping-bridge cut family')
    low=(18,1)+(40,)*k+(40,40,40,10,10)
    high=(19,)+low[1:]
    require([i for i in range(len(low)) if low[i] != high[i]] == [0],'fixed-owner unilateral pair')
    coalitions=0;caps_record=[]
    for c in (low,high):
        ds=(c[0],1)+(c[0],)*k+(c[0]+1,c[0],20,10,10)
        require(ds == graph_caps(5,es,c),'all effective capacities independently checked')
        cc,dd=subset_sums(c),subset_sums(ds)
        require(min(cc[m] for m in cs) == 20,'same grand maxflow')
        for mask in range(1 << len(c)):
            cv=min(cc[mask & m] for m in cs)
            dv=min(dd[mask & m] for m in cs)
            require(cv == dv,'coalition flow changed by effective cap')
            coalitions+=1
        caps_record.append(list(ds))

    ideal=[ideal_moments(t) for t in (Q(9,10),Q(19,20))]
    for t,v in zip((Q(9,10),Q(19,20)),ideal):
        require(v == cdf_ideal(t,cdf),'independent CDF integral disagrees')
    drop=ideal[0]-ideal[1]
    require(drop == Q(553,136800000),'ideal drop arithmetic')
    error=Q(10,9)**10/Q(factorial(10))
    certified=drop-error
    require(certified == Q(97726081746439,30050502681578400000),'certificate arithmetic')
    require(certified > 0,'strict payment decrease not certified')
    previous=error
    for k in range(11,101):
        current=Q(10,9)**k/Q(factorial(k))
        require(current < previous,'error bound did not decrease')
        previous=current
    return {'status':'passed','arithmetic':'exact Fraction/integer, explicit exceptions, standard library',
            'five_edge_conditional_pairs':pairs,'coalition_value_checks':coalitions,
            'counterexample':{'owners':len(low),'minimal_cuts':len(cs),'capacity_scale':20,
                              'low_scaled':list(low),'high_scaled':list(high),'effective_caps_scaled':caps_record,
                              'ideal_low_payment':str(ideal[0]),'ideal_high_payment':str(ideal[1]),
                              'ideal_drop':str(drop),'low_profile_error_upper_bound':str(error),
                              'certified_actual_payment_drop_lower_bound':str(certified)},
            'scope':'All-k result follows from the written proof; actual payments are bounded, not evaluated exactly.'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path)
    args=ap.parse_args()
    root=args.repo if args.repo else Path(__file__).resolve().parents[3]
    print(json.dumps(run(root),indent=2))
