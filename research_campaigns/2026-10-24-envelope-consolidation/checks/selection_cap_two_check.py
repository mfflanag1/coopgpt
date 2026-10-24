"""Exact KKT scalar checks using the inherited q-ary mixture theorem.
Does not claim to enumerate the huge finite transport distribution.
"""
from fractions import Fraction as F
import json

cases = []
for Q in range(3, 9):
    d0 = 16*Q*(Q-1)*(Q+2)
    for scale in (1,2):
        d = scale*d0
        h = d//(2*(Q+2))
        n = Q**d
        m = n-(Q-1)*d-1
        x = F(h,d)
        mu_old = (Q-2+x)/(Q-1)
        delta = F(1,4*Q*(Q-1))
        beta0 = mu_old+delta
        K = beta0.numerator*m//beta0.denominator
        beta = F(K,m)
        b = 1-beta
        a0 = F(d-h,(Q-1)*d)
        assert a0 == 1-mu_old
        assert h*(a0-b)>1-b
        D = d+h
        p,z = F(h,D),F(1,D)
        C = F((Q-1)*d+2*h,D)
        lam = (p-z)/(1-a0)
        tau = lam-p
        assert p == F(1,2*Q+5)
        assert C == Q-1-F(Q-3,2*Q+5)
        assert 2*p+(d-h)*z == 1
        assert p+d*z == 1
        assert 2*p+(Q-1)*d*z == C
        assert lam>0 and tau>0
        assert lam-tau == p
        assert lam*a0-tau == z
        assert lam*b<tau
        norm = 2*p*p+(Q-1)*d*z*z
        assert norm == lam-tau*C
        if Q == 3:
            assert C == 2 and p == F(1,11)
            assert tau == F(9,121)-F(200,121*d)
            assert lam == F(20,121)-F(200,121*d)
            assert tau-lam*F(49,120) == F(5*d-710,726*d)
        cases.append({'Q':Q,'d':d,'h':h,'cap':str(C),
                      'focal':str(p),'lambda':str(lam),'budget_multiplier':str(tau),
                      'owner_count_bit_length':(n+1).bit_length()})

additive = []
for cap in (F(11,10),F(3,2),F(2),F(3),F(5),F(10)):
    Q = 3
    while Q-1-F(Q-3,2*Q+5)<cap:
        Q += 1
    natural = Q-1-F(Q-3,2*Q+5)
    A = (natural-cap)/(cap-1)
    assert A>=0
    assert cap*(1+A)-A == natural
    coefficient = F(1,2*Q+5)/(1+A)
    assert coefficient>0
    additive.append({'target_cap':str(cap),'Q':Q,'natural_cap':str(natural),
                     'additive_value':str(A),'linear_coefficient':str(coefficient)})
print(json.dumps({'status':'PASS','kkt_cases':cases,'additive_cases':additive},indent=2))
