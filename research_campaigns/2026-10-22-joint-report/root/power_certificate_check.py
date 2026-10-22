"""Independent scalar checks for the fixed-power certificate.

Exact rational arithmetic, including exponents 1+1/k via h=H**k.
Uses the proved conservative marginal bound b < 1-mu-delta/2;
does not enumerate or certify the inherited transport distribution.
"""
from fractions import Fraction as F
import json

cases=[]
for Q in (3,4,5,8):
    H=8*Q*(Q-1)
    a=F(2*Q+3,2*(Q+2)*(Q-1))
    delta=F(1,4*Q*(Q-1))
    b_upper=a-delta/2
    assert 0 < b_upper < a < 1
    # Multiply every gradient coordinate by D**(r-1): the two positive
    # values are h**(r-1) and 1. This common scale preserves optimality.
    for k in (1,2,3,8,100):
        h=H**k
        d=2*(Q+2)*h
        gradient=F(H)
        lam=(gradient-1)/(1-a)
        tau=lam-gradient
        nu_lower=tau-lam*b_upper
        assert lam>0 and tau>0 and nu_lower>=0
        assert lam-tau == gradient
        assert lam*a-tau == 1
        D=d+h
        p,z=F(h,D),F(1,D)
        cap=2*p+(Q-1)*d*z
        assert 2*p+(d-h)*z==1
        assert p+d*z==1
        # Equalities at the candidate, with gradient scaled as above.
        assert 2*gradient*p+(Q-1)*d*z==lam-tau*cap
        assert cap==Q-1-F(Q-3,2*Q+5)
        cases.append({'Q':Q,'power':str(1+F(1,k)),
                      'h_digits':len(str(h)),
                      'outside_slack_lower':str(nu_lower),
                      'cap':str(cap),'focal':str(p)})
    for r in (3,4,5):
        h=H; d=2*(Q+2)*h; D=d+h
        gradient=F(h)**(r-1)
        lam=(gradient-1)/(1-a); tau=lam-gradient
        assert tau-lam*b_upper>0
        assert 2*gradient*F(h,D)+(Q-1)*d*F(1,D)==lam-tau*(Q-1-F(Q-3,2*Q+5))
        cases.append({'Q':Q,'power':str(r),'check':'scaled gradient and outside slack'})
print(json.dumps({'status':'PASS','case_count':len(cases),'cases':cases,
                  'limitation':'scalar KKT checks conditional on the written inherited row-distribution proof'},indent=2))
