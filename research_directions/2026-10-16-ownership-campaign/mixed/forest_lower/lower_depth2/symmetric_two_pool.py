#!/usr/bin/env python3
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import gzip,json,time,sys
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)

def solve(m,h=2):
 started=time.time();states=list(product(range(m+1),repeat=2));ix={s:k for k,s in enumerate(states)};vi=4*len(states);rows=[];rhs=[];tags=[]
 def add(row,b,t):rows.append(row);rhs.append(b);tags.append(t)
 for q,(k,l) in enumerate(states):
  counts=(m-k,k,m-l,l);T=min(m+(h-1)*k,m+(h-1)*l)
  add({**{4*q+j:c for j,c in enumerate(counts) if c},vi:-T},0,['budget',k,l])
  for ns in product(*[range(c+1) for c in counts]):
   worth=min(ns[0]+h*ns[1],ns[2]+h*ns[3])
   if worth:add({4*q+j:-c for j,c in enumerate(ns) if c},-worth,['coalition',k,l,*ns])
  if k<m:add({4*q:1,4*ix[(k+1,l)]+1:-1},0,['increase_h',k,l])
  if l<m:add({4*q+2:1,4*ix[(k,l+1)]+3:-1},0,['increase_p',k,l])
 rr=[];cc=[];dd=[]
 for k,row in enumerate(rows):
  for j,a in row.items():rr.append(k);cc.append(j);dd.append(a)
 mat=coo_matrix((dd,(rr,cc)),shape=(len(rows),vi+1)).tocsr();obj=np.zeros(vi+1);obj[-1]=1
 ans=linprog(obj,A_ub=mat,b_ub=np.array(rhs),bounds=(0,None),method='highs');need(ans.success,ans.message)
 combo={};right=Q();dual=[]
 for z,row,b,t in zip(ans.ineqlin.marginals,rows,rhs,tags):
  if z>=-1e-9:continue
  w=Q(float(-z)).limit_denominator(10**8)
  for j,a in row.items():combo[j]=combo.get(j,Q())+w*a
  right+=w*b;dual.append({'weight':str(w),'tag':t})
 valid=combo.get(vi,Q())<0 and all(a>=0 for j,a in combo.items() if j!=vi)
 lower=right/combo[vi] if valid else None
 primal=[Q(float(z)).limit_denominator(10**8) for z in ans.x]
 primalok=all(sum(Q(a)*primal[j] for j,a in row.items())<=b for row,b in zip(rows,rhs))
 result=dict(m=m,h=h,profiles=len(states),rows=len(rows),float_optimum=ans.fun,exact_dual_valid=valid,exact_dual_lower=str(lower),primal_exact_valid=primalok,primal_factor=str(primal[-1]),dual=dual,primal=list(map(str,primal)),elapsed=time.time()-started)
 with gzip.open(ROOT/f'two_pool_m{m}_h{h}.json.gz','wt')as f:json.dump(result,f)
 print(json.dumps({k:v for k,v in result.items() if k not in ('dual','primal')}),flush=True)
 need(valid,'dual failed');need(primalok,'primal failed');return result

if __name__=='__main__':
 for m in [2,3,4,6,8,12]:solve(m)
