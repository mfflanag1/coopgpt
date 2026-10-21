#!/usr/bin/env python3
"""Independent exact audit: small local enumeration and d=10000 scalars.

Uses no scipy, candidate checker, or generated support certificate. The
general transport proof is in mass_search_ternary_cube_audit.txt.
"""
from fractions import Fraction as F
from itertools import combinations, product


def scalar_audit(d=10000):
    h = d // 5
    assert 5*h == d
    n = 3**d
    m = n - 2*d - 1
    k_out = 601*m // 1000
    beta = F(k_out, m)
    exceptional = 2*d*(d-1)
    color = n // 3
    far = [color-1-d*(d-1), color-d-d*(d-1)//2,
           color-d-d*(d-1)//2]
    assert sum(far) == m-exceptional
    assert min(far) > 0
    assert k_out-exceptional >= max(far)
    assert all(k_out <= far[i]+far[j] for i,j in combinations(range(3),2))
    assert all(k_out-exceptional >= (3*beta-1)*(far[i]+far[j])
               for i,j in combinations(range(3),2))
    assert 0 < beta <= F(601,1000) < F(2,3)
    x, y, r = F(h,d), F(h*(h-1),d*(d-1)), F(49,100)
    p_mix = F(2,3)*(1-x*r)
    p_same = F(2,3)-(2*x*(1-r)-y*(1-r)**2)/3
    assert min(p_mix,p_same) > F(601,1000) >= beta
    assert p_mix-F(601,1000) == F(1,3000)
    a, b = F(2,5), 1-beta
    size = d+h+k_out
    row_size = n-size
    t = 1+2*d*a*a+m*b*b
    assert t == 1+(d-h)*a+(m-k_out)*b
    gap = d*a+(row_size-d)*b-t
    assert gap == h*(beta-F(3,5))-beta > 0
    assert a>b>0 and row_size>d
    assert row_size < F(2,5)*n
    rho = F(n,row_size*row_size)
    ell = 1/t
    assert 0<ell<=rho
    assert rho*n > F(25,4)
    # Independent finite common-veto consequence, no asymptotic limit needed.
    blocks = row_size*row_size // n
    owners = blocks*n+1
    selected_private_total = blocks*n*ell/(1+(blocks-1)*rho+ell)
    assert selected_private_total**2 > F(25,16)*owners
    return {"dimension":d,"all_transport_corners":True,
            "availability":True,"strict_off_row_gap":True,
            "J_gt_5_over_2":True,"H_gt_25_over_4":True,
            "private_funding_gt_5_over_4_sqrt_N":True,
            "n_bit_length":n.bit_length()}


def local_enumeration():
    # d=5 permits exhaustive phase, selected-coordinate and repair-coin checks.
    # The large-d availability threshold is checked separately above.
    d,h = 5,1
    vertices=list(product(range(3),repeat=d))
    zero=(0,)*d
    def unit(j,value=1):
        return tuple(value if k==j else 0 for k in range(d))
    neighbors={unit(j,v) for j in range(d) for v in (1,2)}
    exceptional={v for v in vertices if sum(x!=0 for x in v)==2}
    lines=[]
    for j in range(d):
        for fixed in product(range(3),repeat=d-1):
            lines.append(tuple(fixed[:j]+(v,)+fixed[j:] for v in range(3)))
    marg={v:F(0) for v in vertices}
    probability=F(0)
    states=0
    def check(available,weight,phase):
        nonlocal probability,states
        assert zero not in available
        assert len(available & neighbors)==d+h
        assert all(not all(v in available for v in line) for line in lines)
        for v in vertices:
            if sum(x!=0 for x in v)>=3:
                assert (v in available)==(sum(v)%3 != phase)
        for v in available:
            marg[v]+=weight
        probability+=weight
        states+=1
    from math import comb
    base0={v for v in vertices if sum(v)%3!=0}-neighbors
    for chosen in combinations(sorted(neighbors),d+h):
        check(base0|set(chosen),F(1,3*comb(2*d,d+h)),0)
    r=F(49,100)
    for j in range(d):
        axes=[l for l in range(d) if l!=j]
        for coins in product((1,2),repeat=d-1):
            available={v for v in vertices if sum(v)%3!=1}
            available.remove(zero)
            available.add(unit(j))
            weight=F(1,3*d)
            for l,value in zip(axes,coins):
                target=tuple(1 if k==j else value if k==l else 0
                             for k in range(d))
                available.discard(target)
                weight*=r if value==2 else 1-r
            check(available,weight,1)
            check({tuple((-x)%3 for x in v) for v in available},weight,2)
    assert probability==1
    assert all(marg[v]==F(3,5) for v in neighbors)
    x,y=F(h,d),F(h*(h-1),d*(d-1))
    p_mix=F(2,3)*(1-x*r)
    p_same=F(2,3)-(2*x*(1-r)-y*(1-r)**2)/3
    assert all(marg[v]==(p_mix if sum(v)%3==0 else p_same)
               for v in exceptional)
    assert all(marg[v]==F(2,3) for v in vertices
               if sum(x!=0 for x in v)>=3)
    return {"dimension":d,"states":states,"axis_lines":len(lines),
            "exact_marginals":True,"independence":True}


if __name__=="__main__":
    import json
    print(json.dumps({"local":local_enumeration(),"large":scalar_audit()},indent=2))
