#!/usr/bin/env python3
"""Exact finite common-veto certificate checks, stdlib only."""
from fractions import Fraction as F
import json


def check(Q, multiple=1):
    d=16*Q*(Q-1)*(Q+2)*multiple
    h=d//(2*(Q+2)); n=Q**d; m=n-(Q-1)*d-1
    mu=F(Q-2,Q-1)+F(h,d*(Q-1)); delta=F(1,4*Q*(Q-1))
    beta0=mu+delta; K=beta0.numerator*m//beta0.denominator
    beta=F(K,m); k=n-(Q-2)*d-h-K
    t=1+(Q-1)*d*(1-mu)**2+m*(1-beta)**2
    rho=F(n,k*k); ell=1/t
    assert h*delta>=2 and h*(beta-mu)-beta>0
    B=k*k//n; N=B*n+1
    assert B>0
    p=ell/(1+(B-1)*rho+ell); pv=B*rho/(1+B*rho)
    private_sum=B*n*p
    selected_diagonal=B*n*p*p+pv*pv
    assert 4*private_sum*private_sum>(Q-1)**2*N
    # This is already a finite actual-funding lower certificate, no limit.
    return {'Q':Q,'dimension_multiple':multiple,'d':d,
            'exact_finite_claim':'private selected funding > (Q-1)*sqrt(N)/2',
            'private_funding_over_sqrtN_approx':float(private_sum*private_sum/N)**.5,
            'selected_diagonal_approx':float(selected_diagonal),
            'all_assertions':'PASS'}

if __name__=='__main__':
    print(json.dumps([check(Q) for Q in (3,4,5,10)]+[check(3,2)],indent=2))
