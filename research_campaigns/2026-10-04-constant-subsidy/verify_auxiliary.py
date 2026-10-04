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
    counts = dict(profiles=0,coalitions=0,floors=0,own_comparisons=0,knapsack_equivalences=0,knapsack_positive_T=0,knapsack_true=0,knapsack_false=0)
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
        counts['knapsack_positive_T']+=int(T>0)
        counts['knapsack_true' if brute else 'knapsack_false']+=1
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
    require(counts['knapsack_true'] and counts['knapsack_false'] and counts['knapsack_positive_T']>=50,'nonvacuous knapsack cases')
    # Evaluate a deterministic constant-statistic winner rule, including payments.
    tie_cases=[]
    for short in [8,0]:
        caps=[(F(1,2),F(1,2)) if j==short else (F(1),F(1)) for j in range(9)]
        scores=[(lambda coordinates:F(0))(tuple(F(1,3)*d for d in pool)) for pool in caps]
        winner=min(range(9),key=lambda j:(scores[j],j))
        payments=[tuple(d if j==winner else F(0) for d in pool) for j,pool in enumerate(caps)]
        subsidy=sum(map(sum,payments))-1
        tie_cases.append({'short_pool':short,'winner':winner,'subsidy':str(subsidy)})
        require((subsidy>=F(1,4))==(short==8),'least-favored priority is essential')
    envelopes=[]
    def grouped_softmax(groups, exponential_base, exponent_scale):
        # groups contain (number of pools, original capacity tuple).
        T=min(sum(c) for multiplicity,c in groups)
        capped_groups=[(n,tuple(min(ci,T) for ci in c)) for n,c in groups]
        rhos=[sum(c)/T for n,c in capped_groups]
        exponents=[-exponent_scale*(rho-1) for rho in rhos]
        require(all(e.denominator==1 for e in exponents),'exact exponential powers')
        weights=[F(exponential_base)**int(e) for e in exponents]
        Z=sum(n*w for (n,c),w in zip(capped_groups,weights))
        payments=[tuple(ci*w/Z for ci in c) for (n,c),w in zip(capped_groups,weights)]
        total=sum(n*sum(y) for (n,c),y in zip(capped_groups,payments))
        return T,rhos,payments,total
    for r in [1,2,3,4,8,16]:
        k=4**r+1;R=r+1
        spread=[(1,(F(1),)+(F(0),)*(R-1)),(k-1,(F(1),)*R)]
        T,rhos,payments,total=grouped_softmax(spread,4,F(1))
        require(T==1 and rhos==[F(1),F(R)],'spread capacities and ratios')
        require(total/T==F(r+2,2),'fixed-rate softmax payment witness')
        tight_original=(F(1,2),F(1,2))+(F(0),)*(R-2)
        tight_low=(F(1,6),F(1,2))+(F(0),)*(R-2)
        low=[(1,tight_low),(k-1,tight_original)]
        TL,rl,yl,totl=grouped_softmax(low,k-1,F(2))
        require(TL==F(2,3) and rl==[F(1),F(3,2)],'tight deviation ratios')
        require(yl[0][0]==F(1,12),'actual deviating owner payment')
        original_T=sum(tight_original)
        envelope_lower=2*k*yl[0][0]/original_T
        require(envelope_lower==F(k,6),'steep-rate envelope witness')
        envelopes.append({'r':r,'k':k,'spread_base_budget':str(total/T),
                          'lowered_owner_payment':str(yl[0][0]),
                          'steep_rate_tight_envelope_budget_lower':str(envelope_lower),
                          'representation':'pool multiplicities; fixed padded ownership'})
    marginal_envelopes=[]
    for k in range(2,9):
        c=(F(1,2),)*(2*k);pools=[j for j in range(k) for _ in range(2)];full=(1<<len(c))-1
        T=worth(c,pools,k,full)
        M=[T-worth(c,pools,k,full^(1<<i)) for i in range(len(c))]
        require(sum(M)==k*T,'bottleneck-envelope attained budget')
        marginal_envelopes.append({'k':k,'total_over_T':str(sum(M)/T)})
    result={'status':'PASS','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'counts':counts,'max_statistic_witnesses':thresholds,'softmax_witnesses':envelopes,
            'tie_rule_negative_control':tie_cases,'marginal_envelope_witnesses':marginal_envelopes,
            'limitations':['Finite checks do not prove arbitrary-statistic or all-real statements.',
                           'Envelope examples bound total payments divided by T, not subsidy alone.']}
    Path(__file__).with_name('EXACT_AUXILIARY.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',counts)


if __name__=='__main__': main()
