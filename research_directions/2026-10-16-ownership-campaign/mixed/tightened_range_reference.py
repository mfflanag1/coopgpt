#!/usr/bin/env python3
"""Independent explicit range-rule implementation and finite stress tests.
No finite test is presented as a substitute for the universal analytic proof.
"""
import argparse,json,math,random
from verify_envelope_bounds import evaluate,primitive,require,C
from verify_local_total_envelope import local_ceiling

def tightened_range_rule(rows,attainers=False):
    v=evaluate(rows);n=v['n'];H=v['H'];P=v['P'];K=P+local_ceiling(rows);a=v['a'];beta=v['B'];p=v['p']
    if H<=0 or K<=0:return [0.0]*n,[p.copy() for _ in range(n)],v
    if n==1:return [v['F']],[beta.copy()],v
    answers=[];witnesses=[]
    for i in range(n):
        pm=P-p[i];b=beta[i];hi=a[i];cases=[]
        others=[j for j in range(n) if j!=i]
        if P<=H:
            U=min(K,H);T=U if b<=hi else min(U,b+pm)
            own=min(b,max(0.0,T-pm))
            q=0.0 if T==0 else .5*math.exp(1-sum(min(x,T) for x in a)/T)
            val=0.0 if T==0 else own+q*(min(hi,T)-own)
            w=p.copy();w[i]=own;w[others[0]]+=max(0.0,T-sum(w));cases.append((val,w,'short'))
        if K>=H:
            d=min(b,H);s=sum(min(p[j],H) for j in others);waste=sum(max(p[j]-H,0) for j in others)
            w=p.copy();w[i]=b
            if d>=hi:
                rho=max(1.0,(d+s)/H)
                w[others[0]]+=max(0.0,H-sum(w))
            else:
                rho=min((d+(n-1)*H)/H,(K-waste)/H)
                remaining=max(0.0,K-sum(w))
                for j in others:
                    move=min(remaining,max(0.0,H-w[j]));w[j]+=move;remaining-=move
            val=hi+.5*math.exp(1-rho)*(d-hi);cases.append((val,w,'long'))
        require(bool(cases),'no feasible regime')
        val,w,mode=max(cases,key=lambda x:x[0]);answers.append(val);witnesses.append(w)
    return answers,witnesses,v
