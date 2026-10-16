#!/usr/bin/env python3
"""Finite floating stress test of quantitative retention; not a proof."""
from math import exp
from random import Random
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import json

R=Random(715511);BASE=Path(__file__).parent;C0=1/(2*exp(1));C=1+C0

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
    a=[R.random()**2 for _ in range(n)];total=sum(a)
    return [x/total for x in a]

def run():
    profiles=0;deviations=0;maxratio=0.;maxmid=0.;maxerrhigh=0.;maxdefect=0.
    positiveerrors=0;record=None
    for k in range(1800):
        n=R.randrange(3,15)
        rho=R.choice([1.,1.5,1.79,1.8,1.9,1.99,2.,2.01,2.1,2.5,3.])
        if k%2:rho=1+2*R.random()
        s=shares(n)
        if k%3==0:
            s=[0.]*n;s[-1]=1.
            l=[0.]*n;l[0]=1.
            rest=shares(n-1)
            l[1:]=[(rho-1)*x for x in rest]
        else:l=[rho*x for x in shares(n)]
        rho=sum(min(x,1.) for x in l)
        if rho<1-1e-12:raise ArithmeticError('long pool invalid')
        full=phi(s,l);z=sum(full);delta=C-z
        errors=[]
        for i in range(n):
            best=0.
            choices=[(a,b) for a in [0.,.25,.5,.75,.9,.99,1.] for b in [0.,.25,.5,.75,.9,.99,1.]]
            choices.extend((R.random(),R.random()) for _ in range(10))
            for alpha,beta in choices:
                sr=s[:];lr=l[:];sr[i]*=alpha;lr[i]*=beta
                changed=phi(sr,lr)
                defect=(z-sum(changed))/3-(full[i]-changed[i])
                best=max(best,defect);deviations+=1
                if rho>=2-1e-12:
                    maxerrhigh=max(maxerrhigh,defect)
                    require(defect<=2e-11, 'validation failed')
                elif rho>=1.8-1e-12 and defect>2e-11:
                    require(defect<=delta/2+2e-11, 'validation failed')
                    require(s[i]+min(l[i],1.)>=14/15-2e-11, 'validation failed')
                if defect>2e-11:positiveerrors+=1
            errors.append(best)
        defect=sum(errors);maxdefect=max(maxdefect,defect)
        require(defect<=350*max(delta,0.)+2e-10, 'validation failed')
        if rho>=1.8-1e-12:require(defect<=(exp(1)/3)*max(delta,0.)+2e-10, 'validation failed')
        if delta>1e-12:
            ratio=defect/delta
            if ratio>maxratio:maxratio=ratio;record={'s':s,'l':l,'rho':rho,'errors':errors,'slack':delta}
            if rho>=1.8-1e-12:maxmid=max(maxmid,ratio)
        profiles+=1
    lower=sum(Q(4,5)**k/factorial(k) for k in range(6))
    slacklower=Q(16,87)-Q(2,5)/lower
    require(slacklower>Q(1,250), 'validation failed')
    result={'status':'PASS - finite floating corroboration plus rational scalar certificates','profiles':profiles,'individual_underreports':deviations,'positive_defects_tested':positiveerrors,'largest_sampled_aggregate_defect_to_slack':maxratio,'largest_mid_ratio_defect_to_slack':maxmid,'largest_rho_ge_2_defect':maxerrhigh,'largest_aggregate_defect':maxdefect,'scalar_slack_lower_rational':str(slacklower),'scalar_slack_lower_exceeds':'1/250','worst_sample':record,'scope':'Independent random/finite tests only; all-profile proof is QUANTITATIVE_RETENTION_THEOREM.txt.'}
    (BASE/'quantitative-retention-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='worst_sample'},indent=2))

if __name__=='__main__':run()
