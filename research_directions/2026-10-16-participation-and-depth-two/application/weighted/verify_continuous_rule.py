"""Exact corroboration of written all-real proof, not a substitute for proof.
Production is computed by the independently implemented max-profit flow oracle.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import json
from flow_oracle import value

def require(ok, reason):
    if not ok:raise RuntimeError(reason)

def rule(b,m,theta):
    P=Q(b[0]);h=list(map(Q,b[1:1+m]));local=list(map(Q,b[1+m:]))
    ell=[min(a,c) for a,c in zip(h,local)];r=[a-c for a,c in zip(h,ell)]
    L=sum(ell);H=sum(h);res=sum(r);G=min(P,H);R=min(P,res);T=L+R;M=T-G
    x=[e*max(Q(0),min(Q(1),(P-res+ri)/L)) for e,ri in zip(ell,r)] if L else [Q(0)]*m
    X=sum(x);c=G-max(Q(0),X-L/4)
    new=[M,c]+x;base=[Q(0),R]+ell
    y=tuple((1-theta)*a+theta*z for a,z in zip(base,new))
    return y,dict(T=T,M=M,L=L,X=X,exact_budget=T+theta*min(X,L/4))

def check(m):
    d=2*m+1;n=m+2;levels=tuple(map(Q,range(3)))
    profiles=list(product(levels,repeat=d));owners=[1]+list(range(2,n))+[0]*m
    edges=[edge for j in range(1,m+1) for edge in [(0,j,1),(j,m+j,1)]]
    @lru_cache(None)
    def val(cap):return value(cap,edges)
    out=[]
    for theta in [Q(0),Q(1,3),Q(1,2),Q(1)]:
        payments={};coalitions=transitions=0;worst=Q(0)
        for b in profiles:
            y,z=rule(b,m,theta);payments[b]=y
            require(z['T']==val(b),'production formula versus independent oracle')
            require(all(v>=0 for v in y),'nonnegative payments')
            require(y[0]==theta*z['M'],'marginal floor')
            require(sum(y)==z['exact_budget'],'exact budget identity')
            require(sum(y)<=(1+theta/4)*z['T'],'global sharp budget')
            if z['T']:worst=max(worst,sum(y)/z['T'])
            for i in range(n):
                if all(b[j]==0 for j in range(d) if owners[j]==i):require(y[i]==0,'zero-own-resource payment')
            for mask in range(1,1<<n):
                cap=tuple(b[j] if mask&(1<<owners[j]) else Q(0) for j in range(d))
                require(sum(y[i] for i in range(n) if mask&(1<<i))>=val(cap),'coalition coverage')
                coalitions+=1
        for b,y in payments.items():
            for j in range(d):
                ix=levels.index(b[j])
                if ix+1<len(levels):
                    nxt=list(b);nxt[j]=levels[ix+1]
                    require(y[owners[j]]<=payments[tuple(nxt)][owners[j]],'own-report monotonicity')
                    transitions+=1
        out.append({'m':m,'theta':str(theta),'profiles':len(profiles),'coalitions':coalitions,'own_adjacent_increases':transitions,'worst_observed_total_factor':str(worst),'status':'PASS'})
    return out

if __name__=='__main__':
    for m in [1,2,3]:
        for result in check(m):print(json.dumps(result),flush=True)
    # Active unbounded family: literal rule evaluation only; general proof is written.
    for m in [2,4,8,16,32,64,128]:
        b=(Q(m,2),)+tuple([Q(1)]*(2*m))
        for theta in [Q(1,3),Q(1)]:
            y,z=rule(b,m,theta)
            require(sum(y)==(1+theta/4)*z['T'],'active even-m sharpness')
    print(json.dumps({'active_even_m_sharpness':[2,4,8,16,32,64,128],'theta':['1/3','1'],'status':'PASS'}))
