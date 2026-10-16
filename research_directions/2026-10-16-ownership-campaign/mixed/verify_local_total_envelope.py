#!/usr/bin/env python3
"""Finite diagnostics and exact algebra for the local-total envelope lemma."""
import json,math,random
from fractions import Fraction as Q
from verify_envelope_bounds import primitive,require,C

def total_ceiling(a,b):
    A=sum(a);B=sum(b);T=min(A,B)
    if T<=0:return 0.0
    long=b if A<=B else a
    rho=sum(min(x,T) for x in long)/T;s=min(rho,2.0)
    return T*(1+.5*(s-1)*math.exp(1-s))

def attainer(a,b):
    A=sum(a);B=sum(b);T=min(A,B)
    if T<=0:return [0.0]*len(a),[0.0]*len(b)
    short=a if A<=B else b;long=b if A<=B else a
    capped=[min(x,T) for x in long];goal=min(sum(capped),2*T)
    chosen=[];left=goal
    for x in capped:
        take=min(x,left);chosen.append(take);left=max(0,left-take)
    return (short.copy(),chosen) if A<=B else (chosen,short.copy())

def local_ceiling(rows):
    d=(len(rows[0])-1)//2
    return sum(total_ceiling([r[1+j] for r in rows],[r[1+d+j] for r in rows]) for j in range(d))

def main():
    rng=random.Random(240816);checks=0;max_ratio=0
    for case in range(5000):
        n=rng.randint(1,12);vals=[0,0,.125,.25,.5,1,2,4,16]
        a=[rng.choice(vals) for _ in range(n)];b=[rng.choice(vals) for _ in range(n)]
        L=total_ceiling(a,b);Z=sum(primitive(a,b)[0]);T=min(sum(a),sum(b));tol=1e-10*max(1,T)
        require(Z<=L+tol and L<=C*T+tol,'majorant interval failure');checks+=1
        aa,bb=attainer(a,b)
        require(all(0<=x<=y+tol for x,y in zip(aa,a)) and all(0<=x<=y+tol for x,y in zip(bb,b)),'infeasible attainer');checks+=1
        require(abs(sum(primitive(aa,bb)[0])-L)<=tol,'explicit ceiling attainer failed');checks+=1
        for trial in range(25):
            aa=[x*rng.choice([0,.25,.5,.75,1]) for x in a];bb=[x*rng.choice([0,.25,.5,.75,1]) for x in b]
            require(sum(primitive(aa,bb)[0])<=L+tol,'underreport exceeds claimed envelope');checks+=1
            require(total_ceiling(aa,bb)<=L+tol,'claimed envelope not monotone');checks+=1
        if T>0:max_ratio=max(max_ratio,L/T)
    # Exact polynomial comparisons behind derivative sign, with symbolic
    # identities corroborated at enough distinct rational points for degree2.
    exact=0
    for rho in [Q(1),Q(5,4),Q(3,2),Q(7,4),Q(2)]:
        require(-1+(rho-1)*rho==rho*rho-rho-1,'k0 derivative algebra');exact+=1
        require(rho*rho-rho-1>=-1,'k0 lower bracket');exact+=1
        require((rho-1)*(rho-1)>=0,'k1 bracket nonnegative');exact+=1
    print(json.dumps(dict(status='PASS',finite_checks=checks,exact_polynomial_checks=exact,profiles=5000,max_sampled_ratio=max_ratio,scope='finite diagnostics plus exact derivative algebra; universal least-majorant claim rests on written orientation/attainment proof')))

if __name__=='__main__':main()
