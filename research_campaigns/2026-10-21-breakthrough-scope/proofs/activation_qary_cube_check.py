#!/usr/bin/env python3
"""Exact stdlib checks for activation_qary_cube_proof.txt.
Finite parameter checks supplement, not replace, its proof for every Q.
Small dimensions exhaustively verify local repair independence/marginals.
"""
from fractions import Fraction as F
from itertools import product, combinations
from math import comb
from collections import defaultdict
import json


def parameter_check(Q):
    d=16*Q*(Q-1)*(Q+2); h=8*Q*(Q-1)
    x=F(h,d); delta=F(1,4*Q*(Q-1))
    mu=F(Q-2, Q-1)+x/(Q-1)
    beta0=mu+delta
    n=Q**d; M=n//Q; m=n-(Q-1)*d-1
    K=beta0.numerator*m//beta0.denominator
    beta=F(K,m); b=1-beta; a=1-mu
    e=(Q-1)**2*comb(d,2)
    fs=[M-1-(Q-1)*comb(d,2)]+[M-d-(Q-2)*comb(d,2)]*(Q-1)
    B=F(Q-1,Q)-2*x/(Q*(Q-1))
    gamma=F(Q-1,Q)-beta0
    assert B-mu==2*delta
    assert B==beta0+delta>beta>mu
    assert M>100*Q**4*d*d
    assert sum(fs)==m-e and min(fs)>0
    assert all(M-Q*d*d<=f<=M for f in fs)
    assert e+Q*d+2<=Q*Q*d*d
    assert gamma>delta>=F(1,4*Q*Q)
    assert Q*beta0-Q+2>F(1,2)
    assert K-e>=(Q-2)*M
    for omitted in range(Q):
        union=sum(fs)-fs[omitted]
        assert K<=union
        assert K-e>=(Q*beta-Q+2)*union
    # Check every corner directly for modest Q; Q−1 corners use worst state.
    for mask in range(1<<Q):
        R=[j for j in range(Q) if (mask>>j)&1]
        if len(R)==Q:
            continue # Full cut is exact expected-size equality.
        demand=beta*sum(fs[j] for j in R)
        # Exact conditional states are not enumerated, but T>=K-e pointwise.
        lower=sum(F(min(K-e,sum(fs[j] for j in R if j!=c)),Q) for c in range(Q))
        assert lower>=demand
    assert m>h and m>1/delta and h*delta==2
    s=(Q-2)*d+h+K; k=n-s
    t=1+(d-h)*a+(m-K)*b
    assert t==1+(Q-1)*d*a*a+m*b*b
    off=d*a+(k-d)*b
    assert off-t==h*(beta-mu)-beta>0
    assert 0<k and (Q-1)*k<n
    assert delta*n>F(d,4*Q)+2
    rho=F(n,k*k); ell=1/t
    assert ell<=rho
    J=F(n,k); H=rho*n
    assert J>Q-1 and H==J*J>(Q-1)**2
    return {'Q':Q,'d':d,'h':h,'beta0':str(beta0),'beta':float(beta),
            'off_gap':float(off-t),'J':float(J),'H':float(H),
            'funding_limit_J_over_2':float(J/2),'all_exact_assertions':'PASS'}


def local_exhaustive_check(Q,d=3,h=1):
    vertices=list(product(range(Q),repeat=d))
    zero=(0,)*d
    neighbors={v for v in vertices if sum(a!=0 for a in v)==1}
    lines=[]
    for j in range(d):
        for fixed in product(range(Q),repeat=d-1):
            line=[]
            for a in range(Q):
                v=list(fixed); v.insert(j,a); line.append(tuple(v))
            lines.append(set(line))
    marg=defaultdict(F); states=0; total=F(0)
    target=(Q-2)*d+h
    def accept(available,p):
        nonlocal states,total
        assert zero not in available
        assert len(available&neighbors)==target
        assert all(not line<=available for line in lines)
        for v in available: marg[v]+=p
        total+=p; states+=1
    for c in range(Q):
        base={v for v in vertices if sum(v)%Q!=c}
        if c==0:
            for chosen in combinations(sorted(neighbors),target):
                accept((base-neighbors)|set(chosen),F(1,Q*comb(len(neighbors),target)))
        else:
            for S in combinations(range(d),h):
                choices=[(j,l) for j in S for l in range(d) if j!=l]
                for aa in product(range(1,Q),repeat=len(choices)):
                    available=base-{zero}
                    for j in S:
                        v=[0]*d; v[j]=c; available.add(tuple(v))
                    for (j,l),a in zip(choices,aa):
                        v=[0]*d; v[j]=c; v[l]=a; available.discard(tuple(v))
                    accept(available,F(1,Q*comb(d,h)*(Q-1)**len(choices)))
    assert total==1
    x=F(h,d); y=F(h*(h-1),d*(d-1)); mu=F(Q-2,Q-1)+x/(Q-1)
    B=F(Q-1,Q)-2*x/(Q*(Q-1))
    for v in vertices:
        nz=[a for a in v if a]
        if not nz: assert marg[v]==0
        elif len(nz)==1: assert marg[v]==mu
        elif len(nz)==2:
            expected=B if nz[0]!=nz[1] else F(Q-1,Q)-(2*x/F(Q-1)-y/F((Q-1)**2))/Q
            assert marg[v]==expected and marg[v]>=B
        else: assert marg[v]==F(Q-1,Q)
    return {'Q':Q,'d':d,'h':h,'states_exhaustively_checked':states,
            'independence_and_all_marginals':'PASS'}

if __name__=='__main__':
    result={'local_exhaustive':[local_exhaustive_check(Q) for Q in (3,4,5)],
            'exact_parameters':[parameter_check(Q) for Q in range(3,11)]}
    print(json.dumps(result,indent=2))
