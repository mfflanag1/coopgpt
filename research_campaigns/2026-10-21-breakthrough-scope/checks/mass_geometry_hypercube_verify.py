#!/usr/bin/env python3
"""Exact parameter replay; the all-d combinatorial proof is in the audit note."""
from fractions import Fraction as F
from pathlib import Path
import json


def parameters(d):
    assert isinstance(d, int) and d >= 4
    n = 2**d
    a, b = n//2-1, n//2-d
    m = a+b
    D, Dp = d*(d-1)//2, (d-1)*(d-2)//2
    U = a-D
    K = a*(d-2)//d
    f = F(K, a)
    mu = D*f
    lo, hi = mu.numerator//mu.denominator, -((-mu.numerator)//mu.denominator)
    assert U > 0 and 0 < K <= b and 0 < f < 1
    for P in {lo, hi}:
        assert 0 <= P <= Dp and 0 <= K-P <= U
    pair_marginal = (f + (d-2)*mu/Dp)/(d+1)
    assert pair_marginal == f
    assert (K-mu)/U == f
    assert F(a, m)*f == F(b, m)*F(K, b) == F(K, m)
    k = n-K-1
    theta, gamma = F(d, d+1), 1-F(K, m)
    t = d*theta+(k-d)*gamma
    assert t == (d+1)*theta**2+m*gamma**2
    rho, ell, p = F(n, k*k), 1/t, theta/t
    assert ell <= rho
    H, R = rho*n*theta**2, F(n)*p*p/rho
    return dict(d=d,n=n,K=K,k=k,rho=rho,ell=ell,p=p,H=H,R=R,
                delta=rho-ell,theta=theta,gamma=gamma,t=t,
                pair_count_low=lo,pair_count_high=hi,high_probability=mu-lo)


def certificate(d, J):
    row = parameters(d)
    c = J*row['rho']
    exact = c*c/(1+c)**2+row['R']*c/(1+c-row['delta'])**2
    conservative = (c*c+row['R']*c)/(1+c)**2
    assert exact >= conservative
    return row | dict(J=J,N=J*row['n']+1,c=c,exact=exact,
                      conservative=conservative,decimal=float(exact))


def encode(obj):
    if isinstance(obj,F):
        return str(obj)
    if isinstance(obj,dict):
        return {k:encode(v) for k,v in obj.items()}
    if isinstance(obj,list):
        return [encode(v) for v in obj]
    return obj

if __name__ == '__main__':
    checks = [parameters(d) for d in range(4,101)]
    finite = certificate(10,2000)
    assert finite['exact'] == F(611957943568125807906685665280,
                               604523446437006645738436084369)
    assert finite['conservative'] == F(259896347191099064320,
                                      256739126238730616209)
    assert finite['conservative'] > F(101,100)
    limit_samples = []
    for d in [10,20,40,80,160]:
        rho = parameters(d)['rho']
        target = 2/rho
        J = (target+F(1,2)).numerator//(target+F(1,2)).denominator
        limit_samples.append(certificate(d,J))
    result = dict(status='PASS', finite=finite,
                  all_capacity_marginal_checks_d4_through100=True,
                  scope='Finite arithmetic replay; full all-d proof in audit note.',
                  asymptotic_c2_samples=limit_samples)
    output = Path(__file__).with_suffix('.json')
    output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode(dict(status='PASS',finite=finite,
          samples=[dict(d=r['d'],diagonal=r['decimal']) for r in limit_samples])),indent=2))
