#!/usr/bin/env python3
"""Counterfactual-floor refinement. Floating reference, not exact transcendental implementation."""
import math
from verify_envelope_bounds import evaluate,primitive,require
from verify_local_total_envelope import local_ceiling

def floors(rows):
    v=evaluate(rows);n=v['n'];d=v['d'];answer=[[0.0]*n for _ in rows]
    for j in range(d):
        a=[r[1+j] for r in rows];b=[r[1+d+j] for r in rows]
        for i in range(n):
            aa=a.copy();aa[i]=0
            bb=b.copy();bb[i]=0
            delete_a=primitive(aa,b)[0];delete_b=primitive(a,bb)[0]
            for k in range(n):
                if k!=i:answer[i][k]+=delete_b[k] if a[k]>=b[k] else delete_a[k]
    return answer

def optimize_owner(a,base,beta,K,i):
    """Exact closed-form formulas, numerically evaluated; return attaining vector."""
    n=len(a);H=sum(a);P=sum(base)
    if H<=0 or K<=0:return 0.0,base.copy(),'zero'
    if n==1:return min(H,beta),[beta],'single'
    others=[j for j in range(n) if j!=i];hi=a[i];pm=P-base[i];cases=[]
    if P<=H:
        U=min(K,H);T=U if beta<=hi else min(U,beta+pm)
        own=min(beta,max(0.0,T-pm))
        rate=0.0 if T<=0 else .5*math.exp(1-sum(min(x,T) for x in a)/T)
        val=0.0 if T<=0 else own+rate*(min(hi,T)-own)
        w=base.copy();w[i]=own;w[others[0]]+=max(0.0,T-sum(w));cases.append((val,w,'short'))
    if K>=H:
        d=min(beta,H);s=sum(min(base[j],H) for j in others);waste=sum(max(base[j]-H,0) for j in others)
        w=base.copy();w[i]=beta
        if d>=hi:
            rho=max(1.0,(d+s)/H);w[others[0]]+=max(0.0,H-sum(w))
        else:
            rho=min((d+(n-1)*H)/H,(K-waste)/H)
            remaining=max(0.0,K-sum(w))
            for j in others:
                move=min(remaining,max(0.0,H-w[j]));w[j]+=move;remaining-=move
        val=hi+.5*math.exp(1-rho)*(d-hi);cases.append((val,w,'long'))
    require(bool(cases),'empty optimizer regime')
    return max(cases,key=lambda item:item[0])

def floor_range_rule(rows):
    v=evaluate(rows);L=local_ceiling(rows);K=v['P']+L;mf=floors(rows);ans=[];witnesses=[];bases=[]
    for i in range(v['n']):
        base=[v['p'][k]+mf[i][k] for k in range(v['n'])]
        val,w,mode=optimize_owner(v['a'],base,v['B'][i],K,i)
        ans.append(val);witnesses.append(w);bases.append(base)
    return ans,witnesses,bases,mf,K,v
