#!/usr/bin/env python3
"""Independent stdlib replay for q-ary local repairs and exact parameters.

The all-Q proofs, transport theorem and asymptotic quantifiers are in the
accompanying audit. This checker imports no author checker or certificate.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb


def local_audit(alphabet, d, h):
    q=alphabet
    vertices=list(product(range(q),repeat=d))
    index={v:i for i,v in enumerate(vertices)}
    zero=(0,)*d
    def unit(j,c):
        return tuple(c if k==j else 0 for k in range(d))
    neighbors={unit(j,c) for j in range(d) for c in range(1,q)}
    far=[v for v in vertices if sum(c!=0 for c in v)>=3]
    lines=[]
    for j in range(d):
        for fixed in product(range(q),repeat=d-1):
            lines.append(tuple(fixed[:j]+(c,)+fixed[j:] for c in range(q)))
    count_neighbors=(q-2)*d+h
    counts_zero=[0]*len(vertices)
    counts_nonzero=[0]*len(vertices)
    state_counts=[0,0]
    def check(available,phase):
        assert zero not in available
        assert len(available & neighbors)==count_neighbors
        assert all(not all(v in available for v in line) for line in lines)
        assert all((v in available)==(sum(v)%q != phase) for v in far)
        target=counts_zero if phase==0 else counts_nonzero
        for v in available:
            target[index[v]]+=1
        state_counts[phase!=0]+=1
    base0={v for v in vertices if sum(v)%q!=0}-neighbors
    for chosen in combinations(sorted(neighbors),count_neighbors):
        check(base0|set(chosen),0)
    for phase in range(1,q):
        for chosen in combinations(range(d),h):
            repairs=[(j,l) for j in chosen for l in range(d) if j!=l]
            for choices in product(range(1,q),repeat=len(repairs)):
                available={v for v in vertices if sum(v)%q!=phase}
                available.discard(zero)
                available.update(unit(j,phase) for j in chosen)
                for (j,l),c in zip(repairs,choices):
                    removed=tuple(phase if a==j else c if a==l else 0
                                  for a in range(d))
                    available.discard(removed)
                check(available,phase)
    denom_zero=q*comb((q-1)*d,count_neighbors)
    denom_nonzero=q*comb(d,h)*(q-1)**(h*(d-1))
    assert F(state_counts[0],denom_zero)+F(state_counts[1],denom_nonzero)==1
    marg=[F(a,denom_zero)+F(b,denom_nonzero)
          for a,b in zip(counts_zero,counts_nonzero)]
    x,y=F(h,d),F(h*(h-1),d*(d-1))
    mu=F(q-2, q-1)+x/(q-1)
    lower=F(q-1,q)-2*x/(q*(q-1))
    for v in vertices:
        nonzero=[c for c in v if c]
        if len(nonzero)==1:
            assert marg[index[v]]==mu
        elif len(nonzero)==2:
            expected=lower+(y/F(q*(q-1)**2) if nonzero[0]==nonzero[1] else 0)
            assert marg[index[v]]==expected
        elif len(nonzero)>=3:
            assert marg[index[v]]==F(q-1,q)
    return {"Q":q,"d":d,"h":h,"states":sum(state_counts),
            "lines":len(lines),"independence_and_exact_marginals":True}


def parameter_audit(alphabet, multiple=1):
    q=alphabet
    d=multiple*16*q*(q-1)*(q+2)
    h=d//(2*(q+2))
    x=F(h,d)
    mu=F(q-2,q-1)+x/(q-1)
    delta=F(1,4*q*(q-1))
    beta0=mu+delta
    b0=1-beta0
    n=q**d
    big=n//q
    m=n-(q-1)*d-1
    k_out=(beta0.numerator*m)//beta0.denominator
    beta=F(k_out,m)
    e=(q-1)**2*comb(d,2)
    far=[big-1-(q-1)*comb(d,2)]+[big-d-(q-2)*comb(d,2)]*(q-1)
    assert sum(far)==m-e
    assert big>100*q**4*d*d
    assert e+q*d+2<=q*q*d*d
    assert min(far)>0 and max(far)<=big
    assert k_out-e >= (q-2)*big
    for excluded in range(q):
        remaining=sum(far)-far[excluded]
        assert k_out<=remaining
        assert k_out-e >= (q*beta-q+2)*remaining
    lower=F(q-1,q)-2*x/(q*(q-1))
    assert lower-mu==2*delta
    assert 0<beta<=beta0<lower<F(q-1,q)
    assert beta>mu and m>h and m>1/delta
    assert h*delta>=2
    row_size=n-(q-2)*d-h-k_out
    a,b=1-mu,1-beta
    t=1+(q-1)*d*a*a+m*b*b
    assert t==1+(d-h)*a+(m-k_out)*b
    gap=d*a+(row_size-d)*b-t
    assert gap==h*(beta-mu)-beta>0
    assert F(n,q)<=row_size<F(n,q-1)
    rho=F(n,row_size*row_size)
    ell=1/t
    assert 0<ell<=rho
    assert b0==F(4*q*q+5*q-2,4*q*(q-1)*(q+2))
    blocks=row_size*row_size//n
    owners=blocks*n+1
    veto=blocks*rho/(1+blocks*rho)
    selected=ell/(1+(blocks-1)*rho+ell)
    cap=rho/(1+blocks*rho)
    assert selected<=cap
    lower_total=blocks*n*selected+veto
    upper_total=blocks*n*cap+veto
    assert lower_total<=upper_total
    # A finite strict threshold stronger than merely J>Q-1 for these examples.
    assert lower_total*lower_total>F((q-1)**2,4)*owners
    raw_total=veto+F(blocks*n,row_size)/(1+blocks*rho)
    assert lower_total>(q-1)*raw_total
    return {"Q":q,"dimension_multiple":multiple,"d":d,
            "n_bits":n.bit_length(),"all_cut_scalar_conditions":True,
            "J_gt_Q_minus_1":True,"exact_KKT_identities":True,
            "funding_gt_half_Q_minus_1_sqrt_N":True,
            "envelope_to_raw_gt_Q_minus_1":True}


if __name__=="__main__":
    import json
    result={"local":[local_audit(3,4,2),local_audit(4,3,2),local_audit(6,3,1)],
            "parameters":[parameter_audit(q) for q in (3,4,5,6,7,8,10,12,16)],
            "dimension_extension":[parameter_audit(3,2),parameter_audit(4,2)]}
    print(json.dumps(result,indent=2))
