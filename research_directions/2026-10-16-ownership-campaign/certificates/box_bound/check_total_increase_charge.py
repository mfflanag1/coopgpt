#!/usr/bin/env python3
"""Independent finite float stress test for the high-ratio gain charge."""
from math import exp
from random import Random
from pathlib import Path
import json
R=Random(912711);BASE=Path(__file__).parent;c=.5/exp(1)

def require(condition, message='validation failed'):
    if not condition:
        raise AssertionError(message)

def phi(a,b):
    t=min(sum(a),sum(b))
    if t<=0:return [0.]*len(a)
    s,l=(a,b) if sum(a)<=sum(b) else (b,a)
    q=.5*exp(1-sum(min(x,t) for x in l)/t)
    return [(1-q)*x+q*min(y,t) for x,y in zip(s,l)]

def shares(n):
    a=[R.random() for _ in range(n)];s=sum(a)
    return [x/s for x in a]

def run():
    checks=0;largest=0.;positive_profiles=0;largestowners=0
    for profile in range(800):
        n=R.randrange(3,14);epsilon=R.choice([0.,.001,.01,.05,.1,.2])
        l=[1.]+[(1+epsilon)*x for x in shares(n-1)]
        if max(l[1:])>1:continue
        s=shares(n)
        if profile%2:s[0]=0.;a=sum(s);s=[x/a for x in s]
        if profile%5==0:l[0]+=R.random()*3
        full=phi(s,l);Z=sum(full);delta=1+c-Z;gains=[]
        for i in range(n):
            best=0.
            for alpha in [0.,.25,.5,.75,.9,.95,.99,1.]:
                for beta in [0.,.25,.5,.75,.9,.95,.99,1.]:
                    ss=s[:];ll=l[:];ss[i]*=alpha;ll[i]*=beta
                    v=phi(ss,ll)
                    gain=(sum(v)-Z)-(full[i]-v[i])
                    best=max(best,gain);checks+=1
            gains.append(best)
        positives=sum(g>2e-11 for g in gains)
        require(positives<=2, 'validation failed')
        require(sum(gains)<=exp(epsilon)*max(delta,0.)+2e-10, 'validation failed')
        largestowners=max(largestowners,positives)
        if positives:positive_profiles+=1
        if delta>1e-12:largest=max(largest,sum(gains)/delta)
    result={'status':'PASS - finite floating corroboration only','individual_underreports':checks,'profiles_with_positive_charge':positive_profiles,'largest_positive_owner_count':largestowners,'largest_observed_charge_to_slack':largest,'theorem':'TWO_SIDED_LOCAL_FUNDING_THEOREM.txt, TS_gain','scope':'Finite diagnostic; continuous all-profile proof is in theorem file.'}
    (BASE/'total-increase-charge-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':run()
