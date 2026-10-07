"""Exact checks supporting the analytic shared-random-cut envelope proof."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial,prod
import importlib.util,json,random


def cdf(weights,q):
    w=[x for x in weights if x]
    if not w:return Q(int(q>=0))
    n=len(w);s=Q(0)
    for mask in range(1<<n):
        v=q-sum((w[i] for i in range(n) if mask>>i&1),Q(0))
        if v>0:s+=(-1)**mask.bit_count()*v**n
    return s/(factorial(n)*prod(w))


def comparison(a,b):
    A=sum(a);B=sum(b);weights=[abs(x-y) for x,y in zip(a,b)]
    N=sum(max(y-x,0) for x,y in zip(a,b));p=cdf(weights,N)
    assert 0<=p<=1 and A*p<=B
    if A>B:assert p<=Q(N,A-B+2*N)<=Q(B,A+B)
    return p


def run():
    rng=random.Random(71070625);comparisons=0
    explicit=[([1],[1]),([0],[0]),([2],[0]),([0],[2]),
              ([1,0],[0,1]),([5,1],[2,3]),([3,4,0],[3,0,2])]
    for a,b in explicit:
        comparison(list(map(Q,a)),list(map(Q,b)));comparisons+=1
    for n in range(1,9):
        for _ in range(80):
            a=[Q(rng.randrange(10),rng.randrange(1,6)) for _ in range(n)]
            b=[Q(rng.randrange(10),rng.randrange(1,6)) for _ in range(n)]
            comparison(a,b);comparisons+=1
    dependency=Path(__file__).resolve().parents[2]/'2026-10-06-monotone-envelope/verification/verify.py'
    spec=importlib.util.spec_from_file_location('flow_verify',dependency)
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    profiles=0;hinges=0;events=0
    for n in range(3,8):
        for _ in range(10):
            edges=[(i,j) for i in range(n) for j in range(i+1,n)
                   if j==i+1 or rng.random()<.35]
            c=[Q(rng.randrange(0,10),3) for e in edges]
            D=v.effective(n,edges,c);T=v.maxflow(n,edges,c);cuts=v.cutsets(n,edges)
            dc={C:v.weighted_sum(D,C) for C in cuts}
            assert min(dc.values())==T;profiles+=1
            if T==0:assert not any(D);continue
            A=min(cuts,key=lambda C:(dc[C],C))
            bound=[T*D[e]*sum((1/dc[C] for C in cuts if C>>e&1),Q(0)) for e in range(len(edges))]
            assert sum(bound)==len(cuts)*T
            for e,De in enumerate(D):
                if not De:continue
                for x in [Q(1,5),Q(1,2),Q(1)]:
                    ct=list(c);ct[e]=x*De;Dt=v.effective(n,edges,ct)
                    assert Dt[e]==ct[e]
                    assert all(x*dh<=dht<=dh for dh,dht in zip(D,Dt));hinges+=1
                    for _ in range(3):
                        U=[Q(rng.randrange(11),10) for h in edges]
                        current=[dh*u for dh,u in zip(Dt,U)]
                        original=[dh*u for dh,u in zip(D,U)]
                        C=min(cuts,key=lambda B:(v.weighted_sum(current,B),B))
                        assert x*v.weighted_sum(original,C)<=v.weighted_sum(current,C)<=v.weighted_sum(current,A)<=v.weighted_sum(original,A)
                        events+=1
    return dict(status='PASS',exact_uniform_comparisons=comparisons,flow_profiles=profiles,
                unilateral_homothety_checks=hinges,exact_coupled_cut_event_checks=events,
                scope='Independent inclusion-exclusion uniform integrals plus rational flow checks; the all-profile supremum theorem is proved analytically.')


if __name__=='__main__':print(json.dumps(run(),indent=2))
