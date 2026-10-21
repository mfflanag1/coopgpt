#!/usr/bin/env python3
"""Exact integer/Fraction audit of activation_ternary_cube_candidate.txt.
No numerical optimization or third-party dependencies. This checks every
scalar condition; the finite support and flow proofs are in the companion.
"""
from fractions import Fraction as F
import json


def check(d=10000):
    assert d % 5 == 0
    h = d // 5
    n = 3 ** d
    q = n // 3
    m = n - 2*d - 1
    K = 601*m // 1000
    beta = F(K,m)
    b = 1-beta
    a = F(2,5)
    s = d+h+K
    k = n-s
    e = 2*d*(d-1)
    fs = [q-1-d*(d-1), q-d-d*(d-1)//2, q-d-d*(d-1)//2]
    assert sum(fs) == m-e
    x = F(h,d)
    y = F(h*(h-1),d*(d-1))
    r = F(49,100)
    pmix = F(2,3)*(1-x*r)
    psame = F(2,3)-(2*x*(1-r)-y*(1-r)**2)/3
    assert pmix == F(451,750)
    assert beta <= F(601,1000)
    assert min(pmix,psame) > beta > F(3,5)
    assert min(fs)>0
    # Strong bounds sufficient for every conditional state and all cuts.
    assert K-e >= max(fs)
    pairs = [fs[i]+fs[j] for i in range(3) for j in range(i+1,3)]
    assert K <= min(pairs)
    assert all(K-e >= (3*beta-1)*pair for pair in pairs)
    assert beta <= F(2,3)
    # Phase-averaged neighbor marginal, using exact fixed neighbor counts.
    assert (F(d+h,2*d)+F(h,d)+1)/3 == F(3,5)
    assert 2*d*F(3,5) == d+h
    # Fixed support row cardinality and row-potential identities.
    assert k-1-(d-h) == m-K
    t = 1+F(d-h)*a+F(k-1-d+h)*b
    assert t == 1+2*d*a*a+m*b*b
    off_min = d*a+(k-d)*b
    gap = off_min-t
    assert gap == h*(beta-F(3,5))-beta
    assert gap > 0
    assert a>b>0
    assert 0 < k < F(n,2)
    assert 5*k < 2*n
    rho = F(n,k*k)
    ell = 1/t
    # Independent inequality ell<=rho; useful amplification sanity check.
    assert ell <= rho
    H = rho*n
    J = F(n,k)
    assert H == J*J and H>F(25,4) and J>F(5,2)
    return {
        'd':d,'h':h,'number_of_vertices':'3^%d'%d,
        'beta':float(beta),'row_density':float(F(k,n)),
        'mixed_availability':str(pmix),'same_sign_availability':str(psame),
        'off_row_gap':float(gap),'H':float(H),'J':float(J),
        'asymptotic_funding_coefficient_J_over_2':float(J/2),
        'ell_over_rho':float(ell/rho),
        'transport_checks':'all three singleton and all three two-color cuts plus full equality',
        'status':'ALL EXACT ASSERTIONS PASS',
    }

if __name__=='__main__':
    print(json.dumps(check(),indent=2))
