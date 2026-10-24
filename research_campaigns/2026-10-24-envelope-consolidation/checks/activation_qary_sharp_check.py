#!/usr/bin/env python3
"""Exact stdlib scalar/KKT checks of the new sharp fixed-Q parameters."""
from fractions import Fraction as F
from math import comb
import json


def check(Q,r):
    h=8*Q*(Q-1); d0=16*Q*(Q-1)*(Q+3); d=r*d0
    x=F(h,d); n=Q**d; M=n//Q; m=n-(Q-1)*d-1
    mu=F(Q-2,Q-1)+x/(Q-1); beta0=F(Q-1,Q)-F(24,d)
    K=beta0.numerator*m//beta0.denominator; beta=F(K,m)
    a=1-mu; b=1-beta; B_avail=F(Q-1,Q)-2*x/(Q*(Q-1))
    assert B_avail==F(Q-1,Q)-F(16,d)
    assert B_avail-beta0==F(8,d)>0
    assert beta0-mu==F(1,Q*(Q-1))-F(8*(Q+3),d)>=F(1,2*Q*(Q-1))
    assert 0<mu<beta<=beta0<B_avail<1
    assert m>h and M>100*Q**4*d**3
    e=(Q-1)**2*comb(d,2)
    fs=[M-1-(Q-1)*comb(d,2)]+[M-d-(Q-2)*comb(d,2)]*(Q-1)
    assert sum(fs)==m-e
    assert all(M-Q*d*d<=f<=M for f in fs)
    assert e+Q*d+2<=Q*Q*d*d
    assert Q*beta0-Q+2>=F(7,8)
    assert K-e>=(Q-2)*M
    for j in range(Q):
        union=sum(fs)-fs[j]
        assert K<=union and K-e>=(Q*beta-Q+2)*union
    for mask in range((1<<Q)-1):
        R=[j for j in range(Q) if mask>>j&1]
        demand=beta*sum(fs[j] for j in R)
        lower=sum(F(min(K-e,sum(fs[j] for j in R if j!=c)),Q) for c in range(Q))
        assert lower>=demand
    s=(Q-2)*d+h+K; k=n-s
    assert k*Q>=n and k<n
    t=1+(d-h)*a+(m-K)*b
    assert t==1+(Q-1)*d*a*a+m*b*b
    gap=d*a+(k-d)*b-t
    assert gap==h*(beta-mu)-beta>2
    rho=F(n,k*k); ell=1/t
    assert ell<=rho and n*rho<=Q*Q
    blocks=k*k//n; N=blocks*n+1
    p=ell/(1+(blocks-1)*rho+ell)
    cap=rho/(1+blocks*rho); veto=blocks*rho/(1+blocks*rho)
    assert p<=cap
    private_lower=blocks*n*p
    private_upper=blocks*n*cap
    assert 4*private_upper**2<=Q*Q*(N-1)
    return {'Q':Q,'dimension_multiple':r,'d':d,
            'beta0':str(beta0),'off_gap':float(gap),
            'funding_lower_ratio_approx':float((private_lower+veto)**2/N)**.5,
            'funding_upper_ratio_approx':float((private_upper+veto)**2/N)**.5,
            'sharp_limit':Q/2,'all_exact_assertions':'PASS'}

if __name__=='__main__':
    print(json.dumps([check(Q,r) for Q in (3,4,5,8) for r in (1,2,4)],indent=2))
