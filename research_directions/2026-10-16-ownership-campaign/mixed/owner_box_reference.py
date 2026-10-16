#!/usr/bin/env python3
"""Explicit recipient-box range mechanism; floating reference implementation."""
import math
from verify_envelope_bounds import evaluate,primitive,require
from verify_local_total_envelope import local_ceiling

def counterfactual_ranges(rows):
    v=evaluate(rows);n=v['n'];d=v['d'];lower=[[0.0]*n for _ in rows];upper=[[0.0]*n for _ in rows]
    for j in range(d):
        a=[r[1+j] for r in rows];b=[r[1+d+j] for r in rows]
        for i in range(n):
            aa=a.copy();aa[i]=0
            bb=b.copy();bb[i]=0
            da=primitive(aa,b)[0];db=primitive(a,bb)[0]
            for k in range(n):
                if k!=i:
                    lo,up=(db[k],da[k]) if a[k]>=b[k] else (da[k],db[k])
                    lower[i][k]+=lo;upper[i][k]+=up
    return lower,upper

def optimize_box_owner(a,lo,up,beta,K,i):
    n=len(a);H=sum(a);P=sum(lo)
    if H<=0 or K<=0:return 0.0,lo.copy(),'zero'
    if n==1:return min(H,beta),[beta],'single'
    others=[k for k in range(n) if k!=i];pm=P-lo[i];um=sum(up[k] for k in others);hi=a[i];cases=[]
    if P<=H:
        U=min(K,H,beta+um);T=U if beta<=hi else min(U,beta+pm)
        own=min(beta,max(0.0,T-pm));w=lo.copy();w[i]=own
        remain=max(0.0,T-sum(w))
        for k in others:
            step=min(remain,max(0.0,up[k]-w[k]));w[k]+=step;remain-=step
        rate=0.0 if T<=0 else .5*math.exp(1-sum(min(x,T) for x in a)/T)
        val=0.0 if T<=0 else own+rate*(min(hi,T)-own)
        cases.append((val,w,'short'))
    if K>=H and beta+um>=H:
        d=min(beta,H);s=sum(min(lo[k],H) for k in others);waste=sum(max(lo[k]-H,0) for k in others);v=sum(min(up[k],H) for k in others)
        w=lo.copy();w[i]=beta
        if d>=hi:
            rho=max(1.0,(d+s)/H);remain=max(0.0,H-sum(w))
            for k in others:
                step=min(remain,max(0.0,up[k]-w[k]));w[k]+=step;remain-=step
        else:
            rho=min((d+v)/H,(K-waste)/H);remain=max(0.0,K-sum(w))
            for k in others:
                step=min(remain,max(0.0,min(up[k],H)-w[k]));w[k]+=step;remain-=step
        val=hi+.5*math.exp(1-rho)*(d-hi);cases.append((val,w,'long'))
    require(bool(cases),'empty box optimizer regime')
    return max(cases,key=lambda item:item[0])

def box_range_rule(rows):
    v=evaluate(rows);K=v['P']+local_ceiling(rows);mins,maxs=counterfactual_ranges(rows);ans=[];witnesses=[];lows=[];ups=[]
    for i in range(v['n']):
        lo=[v['p'][k]+mins[i][k] for k in range(v['n'])]
        up=[v['p'][k]+maxs[i][k] for k in range(v['n'])];up[i]=v['B'][i]
        val,w,mode=optimize_box_owner(v['a'],lo,up,v['B'][i],K,i)
        ans.append(val);witnesses.append(w);lows.append(lo);ups.append(up)
    return ans,witnesses,lows,ups,K,v
