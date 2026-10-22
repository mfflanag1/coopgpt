#!/usr/bin/env python3
"""Finite-grid discovery only. Exact rational certificates are checked separately."""
from itertools import product
from fractions import Fraction as F
from pathlib import Path
import json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def data(forms,levels):
    n=len(forms[0]);forms=tuple(tuple(map(F,a)) for a in forms);levels=tuple(map(F,levels))
    assert all(len(a)==n and all(z>=0 for z in a) for a in forms)
    assert forms and levels==tuple(sorted(set(levels))) and min(levels)>=0
    profiles=list(product(levels,repeat=n));lookup={p:j for j,p in enumerate(profiles)}
    rows=[];rhs=[];tags=[];C=len(profiles)*n
    def worth(p,S):return min(sum(a[i]*p[i] for i in range(n) if S>>i&1) for a in forms)
    def add(row,b,tag):rows.append(row);rhs.append(b);tags.append(tag)
    for j,p in enumerate(profiles):
        T=worth(p,(1<<n)-1)
        add({**{j*n+i:F(1) for i in range(n)},C:-T},F(0),['budget',j])
        for S in range(1,1<<n):
            v=worth(p,S)
            if v:add({j*n+i:F(-1) for i in range(n) if S>>i&1},-v,['cover',j,S])
        for i in range(n):
            pos=levels.index(p[i])
            if pos+1<len(levels):
                pp=list(p);pp[i]=levels[pos+1];k=lookup[tuple(pp)]
                add({j*n+i:F(1),k*n+i:F(-1)},F(0),['monotone',j,k,i])
    return n,profiles,rows,rhs,tags,C

def solve(forms,levels=(1,3),certpath=None):
    start=time.monotonic();n,profiles,rows,rhs,tags,C=data(forms,levels)
    rr=[];cc=[];vv=[]
    for r,row in enumerate(rows):
        for col,z in row.items():rr.append(r);cc.append(col);vv.append(float(z))
    A=coo_matrix((vv,(rr,cc)),shape=(len(rows),C+1)).tocsr();obj=np.zeros(C+1);obj[-1]=1
    ans=linprog(obj,A_ub=A,b_ub=list(map(float,rhs)),bounds=(0,None),method='highs-ds',options={'presolve':False,'time_limit':90})
    out={'n':n,'forms':forms,'levels':levels,'profiles':len(profiles),'rows':len(rows),'status':int(ans.status),'message':ans.message,'elapsed_seconds':round(time.monotonic()-start,3)}
    if not ans.success:return out
    out['float_beta']=float(ans.fun)
    if certpath:
        rat=lambda z:F(float(z)).limit_denominator(10**8)
        xx=list(map(rat,ans.x));ww=[rat(-z) if z< -1e-10 else F(0) for z in ans.ineqlin.marginals]
        combo={};right=F(0)
        for w,row,b in zip(ww,rows,rhs):
            if w:
                for c,z in row.items():combo[c]=combo.get(c,F(0))+w*z
                right+=w*b
        primal=all(z>=0 for z in xx) and all(sum(z*xx[c] for c,z in row.items())<=b for row,b in zip(rows,rhs))
        dual=all(z>=0 for z in ww) and combo.get(C,F(0))<0 and all(z>=0 for c,z in combo.items() if c!=C)
        lower=right/combo[C] if dual else None
        out.update(exact_primal=primal,exact_dual=dual,exact_beta=str(xx[-1]),exact_lower=str(lower),exact_optimal=primal and dual and lower==xx[-1],dual_support=sum(bool(z) for z in ww))
        payload={**out,'forms':[[str(F(z)) for z in a] for a in forms],'levels':list(map(lambda z:str(F(z)),levels)), 'primal':list(map(str,xx)), 'dual':[{'row':r,'tag':tags[r],'weight':str(w)} for r,w in enumerate(ww) if w]}
        Path(certpath).write_text(json.dumps(payload,indent=2)+'\n')
    return out

if __name__=='__main__':
    tests=[('two_pools',[[1,1,0,0],[0,0,1,1]],(1,4)),('three_pools',[[1,1,0,0,0,0],[0,0,1,1,0,0],[0,0,0,0,1,1]],(1,4)),('triangle',[[1,1,0],[1,0,1],[0,1,1]],(1,4)),('veto',[[1,1,0,0],[1,0,1,0],[1,0,0,1]],(1,4))]
    for name,forms,levels in tests:
        out=solve(forms,levels,Path(__file__).parent/(name+'.json'));print(json.dumps({'name':name,**out}),flush=True)
