"""Exact arithmetic and small-prototype checks of the pointwise obstruction.

Finite checks supplement, and do not replace, the parameter-uniform proof.
Standard library only; no huge graph is materialized for the concentration step.
"""
from fractions import Fraction as Q
from math import factorial, comb, ceil
from pathlib import Path
import importlib.util
import json


def ideal(m,x,b):
    alpha=10+1/(x+Q(1,10)); beta=20/(x+Q(1,10))
    return sum((comb(m,j)*alpha**(m-j)*(-beta)**j*b**(m+j+1)/factorial(m+j+1)
                for j in range(m+1)), Q(0))


def convolution_ideal(m,x,b):
    # Convolve polynomial densities on [0,b], then integrate (b-a) f_sum(a).
    alpha=10+1/(x+Q(1,10)); beta=20/(x+Q(1,10))
    poly=[alpha,-beta]
    for _ in range(m-1):
        new=[Q(0)]*(len(poly)+2)
        for i,a in enumerate(poly):
            for j,d in enumerate([alpha,-beta]):
                new[i+j+1]+=a*d*Q(factorial(i)*factorial(j),factorial(i+j+1))
        poly=new
    return sum((a*b**(i+2)/((i+1)*(i+2)) for i,a in enumerate(poly)),Q(0))


def helper():
    parents=Path(__file__).resolve().parents
    repo=parents[3] if len(parents)>3 else Path('/Users/maxf/projects/economics-research/game-theory/coopgpt')
    p=repo/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py'
    if not p.exists():
        p=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt')/p.relative_to(repo)
    spec=importlib.util.spec_from_file_location('v',p)
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    return v


def graph_checks(v,m):
    s,a=0,1; bs=list(range(2,m+2)); q,t=m+2,m+3
    es=[(s,a)]; labels=['x']
    for i,bi in enumerate(bs):
        es += [(s,bi),(a,bi),(bi,q)];labels += [('y',i),('g',i),('h',i)]
    for label,edge in [('Z',(a,q)),('P',(s,q)),('R',(q,t))]:
        es += [edge]*2; labels += [(label,j) for j in range(2)]
    ps=v.paths(t+1,es);cuts=v.cutsets(t+1,es)
    assert cuts==v.path_blockers(ps)
    assert len(cuts)==2**(m+1)+1
    heights=[max(sum(C>>e&1 for e in p) for p in ps) for C in cuts]
    assert max(heights)==2 and sum(heights)==3*2**m
    assert max(map(len,ps))==4
    b=Q(1,100*m)
    for x in [Q(0),Q(1,10),Q(1,2),Q(9,10)]:
        c=[x]+[v for _ in bs for v in [Q(1,10),Q(2),Q(2)]]
        c += [Q(2)]*2+[(1-2*b)/2]*2+[Q(1,2)]*2
        expected=[x]+[v for _ in bs for v in [Q(1,10),x,x+Q(1,10)]]
        expected += [x]*2+[(1-2*b)/2]*2+[Q(1,2)]*2
        assert v.effective(t+1,es,c)==expected
        assert v.maxflow(t+1,es,c)==1
    return dict(branches=m,K=len(cuts),H=sum(heights),profiles=4)


def run():
    j0=ideal(3,Q(1,10),Q(1,20));j1=ideal(3,Q(9,10),Q(1,20))
    assert j0==Q(2299,3225600) and j1==Q(132247,403200000)
    gap=j0-2*j1-Q(37,12*100000)-Q(10**50,factorial(50))
    assert j0-2*j1==Q(7627,134400000)
    assert Q(10**50,factorial(50))<Q(1,10**12)
    assert gap>Q(1161,44800000)-Q(1,10**12)>0
    param=[]
    for m in range(1,21):
        b=Q(1,100*m);q=Q(11)**m*b**(m+1)/factorial(m+1)
        n=ceil(16/q**2);k=2*ceil(8/q)
        assert n>=16/q**2 and Q(1,6*n)<=q*q/64
        assert k>=800 and k%2==0 and Q(1,k)<=q/16
        low=ideal(m,Q(1,10),b);high=ideal(m,Q(9,10),b)
        assert low==convolution_ideal(m,Q(1,10),b)
        assert high==convolution_ideal(m,Q(9,10),b)
        assert low>=Q(14,15)*Q(15,11)**m*q
        assert Q(54,55)*q<=high<=q
        assert high-q/4>=Q(161,220)*q>0
        bound=Q(56,75)*Q(15,11)**m-Q(1,5)
        param.append(dict(m=m,ratio_bound=str(bound),N_digits=len(str(n)),k_digits=len(str(k))))
    v=helper();prototypes=[graph_checks(v,m) for m in range(1,7)]
    return dict(status='PASS',finite_factor_two_gap=str(gap),
                exact_polynomial_parameter_cases=20,prototypes=prototypes,
                ratio_bounds=param,
                scope='Exact finite arithmetic and prototypes; all-parameter proof in POINTWISE_OBSTRUCTION.txt')


if __name__=='__main__':print(json.dumps(run(),indent=2))
