#!/usr/bin/env python3
"""Floating discovery of random weighted lexicographic cover funding, not proof."""
import numpy as np
from scipy.optimize import linprog
from itertools import combinations
import json

def lex(A,v,w):
    n=len(w);free=np.ones(n,dtype=bool);x=np.zeros(n)
    for step in range(n):
        denom=A[:,free]@w[free];res=v-A@x
        rat=np.divide(res,denom,out=np.full(len(v),-np.inf),where=denom>1e-13)
        delta=max(0,float(rat.max()))
        if delta<=1e-12:break
        tight=np.flatnonzero(rat>=delta-1e-10*max(1,delta));U=free & (A[tight].max(axis=0)>0)
        assert U.any()
        x[U]=delta*w[U];free[U]=False
    if np.min(A@x-v)<-1e-6:raise ValueError('Uncovered')
    return x

def sample(A,v,ns=1000,seed=1):
    rng=np.random.default_rng(seed);n=A.shape[1]
    opt=linprog(np.ones(n),A_ub=-A,b_ub=-v,bounds=(0,None),method='highs-ds',options={'presolve':False})
    assert opt.success
    vals=[]
    for _ in range(ns): vals.append(float(lex(A,v,rng.exponential(size=n)).sum()/opt.fun))
    return {'n':n,'constraints':len(v),'samples':ns,'mean':float(np.mean(vals)),'se':float(np.std(vals,ddof=1)/np.sqrt(ns)),'max':max(vals),'static_opt':float(opt.fun),'minsum_cover':opt.x.tolist(),'seed':seed,'status':'NUMERICAL DISCOVERY ONLY'}

if __name__=='__main__':
    for n in [4,8,16,32,64]:
        A=np.zeros((n-1,n));A[:,0]=1
        for j in range(n-1):A[j,j+1]=1
        print(json.dumps({'family':'star',**sample(A,np.ones(n-1),2000)}),flush=True)
