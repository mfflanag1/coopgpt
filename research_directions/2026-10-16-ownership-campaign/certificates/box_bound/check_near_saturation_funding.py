#!/usr/bin/env python3
"""Independent floating stress tests for the restricted funding theorem."""
from math import exp
from random import Random
from pathlib import Path
import json
R=Random(484611);BASE=Path(__file__).parent;c=1/(2*exp(1));C=1+c

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
    a=[R.random()**2 for _ in range(n)];s=sum(a)
    return [x/s for x in a]

def branch(n):
    t=R.choice([.1,.5,1.,2.]);rho=R.choice([1.8,1.9,1.99,2.])
    short=[t*x for x in shares(n)]
    long=[0.]*n;remaining=rho
    for i in R.sample(range(n),n):
        x=min(1.,remaining) if sum(v>0 for v in long)==n-1 else R.random()*min(1.,remaining)
        long[i]=x;remaining-=x
    for i in range(n):
        x=min(1.-long[i],remaining);long[i]+=x;remaining-=x
    require(abs(remaining)<1e-12, 'validation failed')
    long=[t*(x+(R.choice([0.,1.,3.]) if x>1-1e-12 else 0.)) for x in long]
    return (short,long) if R.randrange(2) else (long,short)

def evaluate(h,l):
    n=len(h);m=len(h[0]);z=[0.]*n;M=0.
    for j in range(m):
        a=[h[i][j] for i in range(n)];b=[l[i][j] for i in range(n)]
        M+=min(sum(a),sum(b));v=phi(a,b);z=[x+y for x,y in zip(z,v)]
    hw=[sum(row) for row in h]
    return phi(hw,z),z,hw,M

def run():
    count=0;checks=0;worstgain=0.;worstbudget=-1e99;maxratio=0.;maxraw=0.;below_two=0
    q=.5*exp(-.9);zz=2+.9*q+c
    hh=[[0.,0.,0.],[1.,1.,0.],[0.,1.,0.],[0.,0.,2*zz-3]]
    ll=[[1.,1.,0.],[0.,0.,0.],[0.,0.,0.],[.9,0.,0.]]
    fixedpay,local,hw,prod=evaluate(hh,ll)
    ll[0][0]=.999
    fixedchanged,changedlocal,_,_=evaluate(hh,ll)
    positivegain=fixedchanged[0]-fixedpay[0]
    require(positivegain>0, 'validation failed')
    defect=max(0.,(sum(local)-sum(changedlocal))/3-(local[0]-changedlocal[0]))
    require(positivegain<=defect+1e-12, 'validation failed')
    worstgain=positivegain
    for k in range(500):
        n=R.randrange(2,11);m=R.randrange(1,7)
        h=[[] for _ in range(n)];l=[[] for _ in range(n)]
        for j in range(m):
            a,b=branch(n)
            for i in range(n):h[i].append(a[i]);l[i].append(b[i])
        for i in range(n):h[i].append(0.);l[i].append(0.)
        full,z,hw,M=evaluate(h,l);Z=sum(z)
        target=1.95 if k%2 else R.uniform(1.95,min(float(n),4.))
        deficit=max(0.,target*Z-sum(min(x,Z) for x in hw))
        for i in R.sample(range(n),n):
            add=min(max(0.,Z-hw[i]),deficit)
            h[i][-1]+=add;hw[i]+=add;deficit-=add
        require(deficit<1e-10, 'validation failed')
        full,z,hw,M=evaluate(h,l);Z=sum(z);delta=C*M-Z
        r0=sum(min(x,Z) for x in hw)/Z
        require(r0>=1.95-1e-10, 'validation failed')
        below_two+=int(r0<2-1e-10)
        q0=.5*exp(1-r0);a0=(1-c)*M/Z;lip=max(1/exp(1),2/(exp(1)*r0))
        require(q0*a0<=1/6+1e-12 and lip*a0<=(1-q0)/3+1e-12, 'validation failed')
        finite=full[:]
        for i in range(n):
            for trial in range(55):
                hh=[row[:] for row in h];ll=[row[:] for row in l]
                if trial<2*(m+1):
                    targetrows=hh if trial<m+1 else ll
                    targetrows[i][trial%(m+1)]*=R.choice([0.,.5,.99,.9999])
                else:
                    hh[i]=[x*R.choice([0.,.25,.5,.75,.99,1.]) for x in hh[i]]
                    ll[i]=[x*R.choice([0.,.25,.5,.75,.99,1.]) for x in ll[i]]
                pay,zz,_,_=evaluate(hh,ll)
                defect=max(0.,(Z-sum(zz))/3-(z[i]-zz[i]))
                require(sum(zz)<=Z+2e-10, 'validation failed')
                require(pay[i]<=full[i]+defect+2e-10, 'validation failed')
                finite[i]=max(finite[i],pay[i]);checks+=1
                worstgain=max(worstgain,pay[i]-full[i])
        limit=C*Z+(exp(1)/3)*delta
        residual=sum(finite)-limit
        require(residual<=3e-10, 'validation failed')
        worstbudget=max(worstbudget,residual)
        maxratio=max(maxratio,sum(finite)/M);maxraw=max(maxraw,sum(full)/M)
        count+=1
    result={'status':'PASS - finite floating checks only','full_profiles':count,'whole_owner_underreports':checks,'profiles_with_outer_ratio_below_two':below_two,'largest_sampled_gain_over_raw':worstgain,'explicit_raw_incentive_failure_gain':positivegain,'largest_budget_residual':worstbudget,'largest_sampled_envelope_ratio':maxratio,'largest_raw_ratio':maxraw,'class':'P=0; all local full rho in[9/5,2]; outer full capped hardware ratio>=39/20','scope':'Finite deviation maxima are lower bounds on E; tests corroborate but do not establish the theorem.'}
    (BASE/'near-saturation-funding-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':run()
