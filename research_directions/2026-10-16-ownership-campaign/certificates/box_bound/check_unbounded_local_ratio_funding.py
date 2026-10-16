#!/usr/bin/env python3
"""Floating falsification checks and rational scalar checks, not a theorem certificate."""
from math import exp,factorial
from fractions import Fraction as Q
from random import Random
from pathlib import Path
import json
R=Random(16610031);BASE=Path(__file__).parent;c=.5/exp(1);C=1+c;kappa=.7-exp(1)/5

def require(ok,message='validation failed'):
    if not ok:raise AssertionError(message)

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
    t=R.choice([.1,.5,1.,3.]);rho=R.choice([r for r in [1.8,1.9,2.,2.1,2.5,3.,4.,min(n,8.),float(n)] if r<=n])
    s=[t*x for x in shares(n)];l=[0.]*n;remaining=rho
    for i in R.sample(range(n),n):
        x=R.random()*min(1.,remaining);l[i]=x;remaining-=x
    for i in range(n):
        x=min(1.-l[i],remaining);l[i]+=x;remaining-=x
    require(abs(remaining)<1e-10)
    l=[t*(x+(R.choice([0.,.5,2.]) if x>1-1e-12 else 0.)) for x in l]
    return (s,l) if R.randrange(2) else (l,s)

def evaluate(h,l):
    n=len(h);m=len(h[0]);z=[0.]*n;M=0.;dlow=0.;dhigh=0.;rhos=[]
    for j in range(m):
        a=[h[i][j] for i in range(n)];b=[l[i][j] for i in range(n)]
        t=min(sum(a),sum(b));M+=t;v=phi(a,b);z=[x+y for x,y in zip(z,v)]
        if t:
            long=b if sum(a)<=sum(b) else a
            rho=sum(min(x,t) for x in long)/t;rhos.append(rho)
            delta=(1+c)*t-sum(v)
            if rho<=2+1e-10:dlow+=delta
            else:dhigh+=delta
    hw=[sum(row) for row in h]
    return phi(hw,z),z,hw,M,dlow,dhigh,rhos

def run():
    scalarchecks=0
    for r in [1.8+k*.01 for k in range(1000)]+[16.,32.,64.,100.,1000.]:
        q=.5*exp(1-r);delta=c-q*(r-1)
        b=2*c*(1-q)-(1-c)*(1+q*(r-1))/3
        require(b<=((.8*delta) if r>=2 else 0.)+1e-12)
        scalarchecks+=1
    x=Q(5591,3311);lower=sum(x**k/factorial(k) for k in range(5))
    require(lower>Q(301,58))
    quadchecks=0;worstquad=-1e99
    for _ in range(1200):
        n=R.randrange(3,15);z=shares(n);h=[R.random()*1.5 for _ in range(n)]
        deficit=max(0.,2.-sum(min(x,1.) for x in h))
        for i in range(n):
            add=min(max(0.,1.-h[i]),deficit);h[i]+=add;deficit-=add
        full=phi(h,z)
        for _ in range(20):
            i=R.randrange(n);b=z[i]*R.random();t=b+(1-b)*R.random()
            opponents=shares(n-1);accounts=[0.]*n;accounts[i]=b
            for k,j in enumerate(j for j in range(n) if j!=i):accounts[j]=(t-b)*opponents[k]
            gain=phi(h,accounts)[i]-full[i];u=1-t;D=z[i]-b;eps=max(0.,u/3-D)
            B=2*c*(z[i]-h[i])-(1-c)/3
            bound=3*max(0.,B)**2/(8*c)+C*eps
            worstquad=max(worstquad,gain-bound);require(gain<=bound+2e-11)
            quadchecks+=1
    count=0;checks=0;badaccount=0;largestA=0.;maxratio=0.;maxrho=0.;worstbudget=-1e99;positive_total=0
    for profile in range(360):
        n=R.randrange(3,25);m=R.randrange(1,7);h=[[] for _ in range(n)];l=[[] for _ in range(n)]
        for j in range(m):
            a,b=branch(n)
            if profile%4==0:
                # Stress pure local ownership with many hardware counterparts.
                t=min(sum(a),sum(b));long=b if sum(a)<=sum(b) else a
                a=long;b=[0.]*n;b[-1]=t
                a[-1]=0.
                # This special projection might lower rho; fill it back to>=1.8.
                missing=max(0.,1.8*t-sum(min(x,t) for x in a))
                for k in range(n-1):
                    add=min(max(0.,t-a[k]),missing);a[k]+=add;missing-=add
                require(missing<1e-10)
            for i in range(n):h[i].append(a[i]);l[i].append(b[i])
        for i in range(n):h[i].append(0.);l[i].append(0.)
        full,z,hw,M,dl,dh,rhos=evaluate(h,l);Z=sum(z)
        deficit=max(0.,2*Z-sum(min(x,Z) for x in hw))
        for i in range(n):
            add=min(max(0.,Z-hw[i]),deficit);h[i][-1]+=add;hw[i]+=add;deficit-=add
        require(deficit<1e-9)
        full,z,hw,M,dl,dh,rhos=evaluate(h,l);Z=sum(z)
        require(min(rhos)>=1.8-1e-9)
        A=max(max(0.,x-y)/Z for x,y in zip(z,hw));largestA=max(largestA,A)
        badaccount+=int(A>(1-c)/(6*c));maxrho=max(maxrho,max(rhos));finite=full[:]
        for i in range(n):
            for trial in range(35):
                hh=[row[:] for row in h];ll=[row[:] for row in l]
                if trial<2*(m+1):
                    target=hh if trial<m+1 else ll;target[i][trial%(m+1)]*=R.choice([0.,.5,.99,.999])
                else:
                    hh[i]=[x*R.choice([0.,.25,.5,.75,1.]) for x in hh[i]]
                    ll[i]=[x*R.choice([0.,.25,.5,.75,1.]) for x in ll[i]]
                pay,zz,_,_,_,_,_=evaluate(hh,ll);finite[i]=max(finite[i],pay[i]);checks+=1
                if sum(zz)>Z+1e-10:positive_total+=1
        bound=C*Z+(C*exp(1)/3)*dl+(1+kappa)*dh
        residual=sum(finite)-bound;worstbudget=max(worstbudget,residual)
        require(residual<=3e-9)
        maxratio=max(maxratio,sum(finite)/M);count+=1
    result={'status':'PASS - finite floating corroboration plus exact scalar Taylor comparison','scalar_float_checks':scalarchecks,'outer_quadratic_checks':quadchecks,'largest_quadratic_residual':worstquad,'full_profiles':count,'whole_owner_underreports':checks,'total_increasing_underreports':positive_total,'profiles_violating_old_account_condition':badaccount,'largest_account_excess_ratio':largestA,'largest_local_rho':maxrho,'largest_sampled_funding_ratio':maxratio,'largest_funding_residual':worstbudget,'exact_taylor_lower':str(lower),'exact_taylor_target':'301/58','scope':'Continuous proof is UNBOUNDED_LOCAL_RATIO_FUNDING_THEOREM.txt; finite envelope maxima are lower bounds only.'}
    (BASE/'unbounded-local-ratio-funding-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':run()
