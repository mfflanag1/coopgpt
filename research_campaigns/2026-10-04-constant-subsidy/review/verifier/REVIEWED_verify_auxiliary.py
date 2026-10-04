"""Supplementary exact checks; universal claims rest on the written proofs."""
import hashlib
import itertools
import json
import math
import random
from fractions import Fraction as F
from pathlib import Path


def require(ok, why):
    if not ok: raise ValueError(why)


def worth(c, pool_ids, k, mask):
    totals = [0]*k
    for i, capacity in enumerate(c):
        if mask >> i & 1: totals[pool_ids[i]] += capacity
    return min(totals)


def capped(c, pools, k):
    total = worth(c,pools,k,(1<<len(c))-1)
    return tuple(F(min(a,total),k) for a in c), total


def main():
    counts = dict(profiles=0,coalitions=0,floors=0,own_comparisons=0,knapsack_equivalences=0)
    for shape in [(1,1),(2,2),(3,1,1),(2,2,2),(2,1,1,1)]:
        k=len(shape);n=sum(shape);pools=[j for j,s in enumerate(shape) for _ in range(s)]
        full=(1<<n)-1
        for c in itertools.product(range(3),repeat=n):
            y,T=capped(c,pools,k);counts['profiles']+=1
            require(sum(y)<=F(1+(k-1)*max(shape),k)*T,'owner-count budget')
            for mask in range(1<<n):
                require(sum(y[i] for i in range(n) if mask>>i&1)>=worth(c,pools,k,mask),'coverage')
                counts['coalitions']+=1
            for i in range(n):
                marginal=T-worth(c,pools,k,full^(1<<i))
                require(y[i]>=F(marginal,k),'M/k floor');counts['floors']+=1
                if c[i]:
                    low=list(c);low[i]-=1;yl,_=capped(low,pools,k)
                    require(y[i]>=yl[i],'own monotonicity');counts['own_comparisons']+=1
    rng=random.Random(20261004)
    for _ in range(200):
        shape=rng.choice([(2,2),(2,2,2),(3,1,1),(2,1,1,1)])
        k=len(shape);n=sum(shape);pools=[j for j,s in enumerate(shape) for _ in range(s)]
        c=tuple(rng.randrange(4) for _ in range(n));y=tuple(F(rng.randrange(7),3) for _ in range(n))
        T=worth(c,pools,k,(1<<n)-1)
        brute=all(sum(y[i] for i in range(n) if mask>>i&1)>=worth(c,pools,k,mask) for mask in range(1<<n))
        options=[]
        for j in range(k):
            ids=[i for i in range(n) if pools[i]==j]
            options.append([(sum(c[i] for h,i in enumerate(ids) if mask>>h&1),sum(y[i] for h,i in enumerate(ids) if mask>>h&1)) for mask in range(1<<len(ids))])
        levels={a for opts in options for a,b in opts if 0<a<=T}
        reduced=all(sum(min(b for a,b in opts if a>=level) for opts in options)>=level for level in levels)
        require(brute==reduced,'knapsack equivalence');counts['knapsack_equivalences']+=1
    thresholds=[]
    for r in [2,3,4]:
        k=2*r**r+1
        integrated=sum((-1)**h*math.comb(k-1,h)*F(1,(h+1)*r**(r*h)) for h in range(k))
        closed=F(r**r,k)*(1-(1-F(1,r**r))**k)
        require(integrated==closed,'max-statistic integral')
        lower=F(1,2)*(1-(1-F(1,2*r**r))**(k-1))
        require(1-closed>=lower>=F(1,4),'class witness bound')
        thresholds.append({'r':r,'k':k,'short_winner_probability':str(closed),
                           'subsidy':str((r-1)*(1-closed)),'required_lower':str(F(r-1,4))})
    # For constant equal statistics, the least-favored median pool always loses.
    priorities=list(range(5));winner=min(priorities)
    require(max(priorities)!=winner,'least-favored tie witness')
    require(not (min(priorities)!=winner),'most-favored choice must fail')
    envelopes=[]
    for r in [1,2,3,4,8,16]:
        # lambda=2 log 2, k-1=4^r, R=r+1 makes the softmax weight exactly one.
        k=4**r+1;R=r+1
        base=F(1+R,2)
        require(base==F(r+2,2),'fixed-rate softmax witness')
        # lambda(k)=2 log(k-1) makes each lowered tight-profile payment 1/12.
        tight_envelope_lower=F(k,6)
        envelopes.append({'r':r,'k':k,'spread_base_budget':str(base),
                          'steep_rate_tight_envelope_budget_lower':str(tight_envelope_lower)})
    result={'status':'PASS','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'counts':counts,'max_statistic_witnesses':thresholds,'softmax_witnesses':envelopes,
            'negative_control':'Choosing the most-favored tied median fails; least-favored succeeds.',
            'limitations':['Finite checks do not prove arbitrary-statistic or all-real statements.',
                           'Envelope examples bound total payments divided by T, not subsidy alone.']}
    Path(__file__).with_name('EXACT_AUXILIARY.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',counts)


if __name__=='__main__': main()
