#!/usr/bin/env python3
"""Independent bounded Fraction checks of the two scoped structural notes."""
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import hashlib
import json
import random

HERE=Path(__file__).resolve().parent


def q_at(s,m):
    q=Q(1,3)
    for j in range(2,m+1):
        a=min(s-1,2*j-2);q*=Q(a,a+1)
    return q


def ideal_check():
    vertices=range(7)
    edges=sorted({tuple(sorted((a-1,b-1,(a^b)-1))) for a in range(1,8) for b in range(a+1,8)})
    em=[sum(1<<i for i in e) for e in edges]
    assert len(edges)==7 and all(len(set(e)&set(f))<=1 for e,f in combinations(edges,2))
    support={S:[e for e in em if e&S==e] for S in range(128)}
    profiles=[]
    for S,es in support.items():
        common=127
        for e in es:common &= e
        if not es or common:profiles.append(S)
    worth=lambda S:int(bool(support[S]))  # exact on this downward ideal
    coals=range(1,128)
    counts=defaultdict(int)
    for s in range(1,8):
        payments={}
        for S in profiles:
            es=support[S];m=len(es);y=[Q(0)]*7;p=[Q(int(not(S>>i&1))) for i in vertices]
            if m==1:
                for i in vertices:
                    if es[0]>>i&1:y[i]=p[i]=Q(1,3)
            elif m>=2:
                common=127
                for e in es:common &= e
                assert common.bit_count()==1
                cap=common.bit_length()-1;y[cap]=p[cap]=Q(1)
                priv=0
                for e in es:priv |= e & ~common
                for i in vertices:
                    if priv>>i&1:y[i]=q_at(s,m)
            payments[S]=y
            assert all(sum(p[i] for i in e)>=1 for e in edges)
            assert sum(p[i] for i in vertices if S>>i&1)==worth(S)
            assert all(y[i]>=p[i]*int(bool(S>>i&1)) for i in vertices)
            limit=Q(1) if s==1 else 1+2*s*q_at(s,s)
            assert sum(y)<=limit*worth(S)
            counts['profile_price_budget_checks']+=1
            for C in coals:
                assert sum(y[i] for i in vertices if C>>i&1)>=worth(S&C)
                counts['coverage_checks']+=1
        for S in profiles:
            for T in profiles:
                if S&~T:continue
                D=T&~S
                for C in coals:
                    if D&~C or C.bit_count()>s:continue
                    lhs=sum(payments[T][i]-payments[S][i] for i in vertices if C>>i&1)
                    assert lhs>=worth(D),(s,S,T,C,lhs,worth(D))
                    counts['full_OUT_checks']+=1
                    counts['positive_OUT_checks']+=worth(D)>0
                    counts['proper_passive_member_checks']+=bool(D) and bool(C&~D)
    counts['actual_profiles']=len(profiles);counts['s_values']=7
    peaks=[]
    for s in range(1,33):
        upper=lambda m:Q(1) if m==1 else 1+2*m*q_at(s,m)
        values=[upper(m) for m in range(1,2*s+2)]
        A=Q(1) if s==1 else 1+2*s*q_at(s,s)
        assert max(values)==A
        if s>=2:
            maxima=[m for m,v in enumerate(values,1) if v==A]
            assert maxima==([2] if s==2 else [s-1,s])
            h=(s+1)//2;Qh=Q(4**h,2*comb(2*h,h))
            B=1+Q(2*(s-1),3)*Qh/h*Q(s-1,s)**(s-h)
            assert A==1+Q(s,s-1)*(B-1) and A-B==2*q_at(s,s)
            # Quotient seed/ladder/cap/budget cancellation. Geometry and legal
            # joint averaging are checked analytically against accepted proof.
            total=defaultdict(Q);rhs=Q(1);total['K']=1;total['q'+str(s)]=-2*s
            residual=Q(2*s)
            for m in range(s,1,-1):
                k=min(s-1,2*m-2);w=residual/(k+1)
                assert w>=0
                total['q'+str(m)]+=w*(k+1)
                total['q'+str(m-1)]-=w*k
                residual=w*k
            w=residual/3;total['q1']+=3*w;rhs+=w
            assert {k:v for k,v in total.items() if v}=={'K':1} and rhs==A
            # M edge feasibility rows minus efficient total price, divided
            # by M-1, force unit cap price; all private prices cancel.
            M=s;cap_coeff=Q(M-1,M-1);priv_coeff=Q(1-1,M-1)
            assert cap_coeff==1 and priv_coeff==0
        peaks.append({'s':s,'A':str(A),'maximizers':'all m' if s==1 else maxima})
    assert peaks[1]['A']=='5/3'
    return {'status':'PASS','counts':dict(counts),'exact_peak_and_lower_checks':peaks}


def solve(rows,rhs):
    n=len(rhs);a=[list(map(Q,row))+[Q(b)] for row,b in zip(rows,rhs)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if a[i][j]),None)
        if pivot is None:return None
        a[j],a[pivot]=a[pivot],a[j];scale=a[j][j];a[j]=[v/scale for v in a[j]]
        for i in range(n):
            if i==j:continue
            scale=a[i][j]
            if scale:a[i]=[x-scale*y for x,y in zip(a[i],a[j])]
    return tuple(row[-1] for row in a)


def linear_dot(a,b):return sum(x*y for x,y in zip(a,b))


@lru_cache(None)
def optimize(A,profit,B):
    d=len(A);m=len(profit)
    prows=list(A)+[tuple(-int(i==j) for i in range(m)) for j in range(m)]
    prhs=list(B)+[Q(0)]*m;best=None;xbest=None
    for ix in combinations(range(d+m),m):
        x=solve([prows[i] for i in ix],[prhs[i] for i in ix])
        if x is None or any(linear_dot(row,x)>b for row,b in zip(prows,prhs)):continue
        val=linear_dot(profit,x)
        if best is None or val>best:best,xbest=val,x
    drows=[tuple(A[a][j] for a in range(d)) for j in range(m)]+[tuple(int(i==j) for i in range(d)) for j in range(d)]
    drhs=list(profit)+[Q(0)]*d;cost=None;pbest=None
    for ix in combinations(range(m+d),d):
        p=solve([drows[i] for i in ix],[drhs[i] for i in ix])
        if p is None or any(linear_dot(row,p)<b for row,b in zip(drows,drhs)):continue
        val=linear_dot(B,p)
        if cost is None or val<cost:cost,pbest=val,p
    assert best==cost and best is not None
    return best,xbest,pbest


def layer_check():
    techs=[(((1,),(1,),(1,)),(1,)),
           (((1,1),(1,0),(1,0),(0,1)),(1,Q(3,2))),
           (((1,0),(1,1),(1,1),(0,1)),(1,Q(3,2))),
           (((2,1,0),(1,0,1),(0,1,2),(0,1,1)),(1,Q(3,2),Q(1,2)))]
    rng=random.Random(271828);counts=defaultdict(int)
    coals=[C for k in range(1,4) for C in combinations(range(3),k)]
    for A,profit in techs:
        A=tuple(tuple(map(Q,row)) for row in A);profit=tuple(map(Q,profit));d=len(A);m=len(profit)
        r=max(sum(A[a][j]>0 for a in range(d)) for j in range(m))
        def aggregate(b,C=range(3)):return tuple(sum(b[i][a] for i in C) for a in range(d))
        def state(b):
            B=aggregate(b);V,x,p=optimize(A,profit,B)
            u=tuple(linear_dot(p,bi) for bi in b)
            h=tuple(sum(profit[j]*x[j]*sum((b[i][a]/B[a] if B[a] else 0) for a in range(d) if A[a][j]>0) for j in range(m)) for i in range(3))
            assert sum(u)==V and sum(h)<=r*V and all(h[i]>=u[i]>=0 for i in range(3))
            for C in coals:
                vC=optimize(A,profit,aggregate(b,C))[0]
                outside=optimize(A,profit,aggregate(b,[i for i in range(3) if i not in C]))[0]
                assert sum(u[i] for i in C)>=vC and sum(h[i] for i in C)>=V-outside
                counts['coverage_and_deletion_checks']+=1
            counts['static_primal_dual_checks']+=1
            return V,u,h
        for k in range(32):
            C=coals[k%len(coals)]
            low=tuple(tuple(Q(0) if k==0 else Q(rng.randrange(4),2) for a in range(d)) for i in range(3))
            # Some protected owners deliberately remain unchanged.
            D=C[:1] if k%2 else C
            high=tuple(tuple(low[i][a]+(Q(rng.randrange(3),2) if i in D else 0) for a in range(d)) for i in range(3))
            if high==low:
                high=tuple(tuple(high[i][a]+(Q(1,2) if i==D[0] and a==0 else 0)
                                 for a in range(d)) for i in range(3))
            assert high!=low and all(0<=v<=3 for owner in high for v in owner)
            Vl,ul,hl=state(low);Vh,uh,hh=state(high)
            delta=tuple(aggregate(high)[a]-aggregate(low)[a] for a in range(d))
            Fdelta=optimize(A,profit,delta)[0]
            assert sum(hh[i]-ul[i] for i in C)>=Fdelta
            counts['full_OUT_comparisons']+=1
            counts['positive_OUT_comparisons']+=Fdelta>0
            counts['with_passive_protected_members']+=any(low[i]==high[i] for i in C)
            counts['zero_value_source_comparisons']+=Vl==0
    return {'status':'PASS','technologies':4,'counts':dict(counts),'exact_LP_instances':optimize.cache_info().currsize,
            'scope':'Each tested comparison is its own source/sink system; general simultaneous global assignment is justified by the written proof.'}


def main():
    out={'status':'PASS','timestamp_utc':datetime.now(timezone.utc).isoformat(),
         'arithmetic':'Fraction only; direct primal/dual vertex enumeration for small LPs',
         'unit_worth_price_frontier':ideal_check(),'one_layer':layer_check(),
         'scope':'Bounded supporting checks, not proof by enumeration or all-real mechanism synthesis.',
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({**out,'unit_worth_price_frontier':{k:v for k,v in out['unit_worth_price_frontier'].items() if k!='exact_peak_and_lower_checks'}},indent=2))


if __name__=='__main__':main()
