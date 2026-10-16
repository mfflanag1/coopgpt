#!/usr/bin/env python3
"""Bounded diagnostic report LP on actual fixed owners; exact reconstructed dual."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def need(x,msg):
 if not x:raise ValueError(msg)

def value(cap):
 inc,out=cap[0],0
 for c in cap[1:]:inc,out=c+min(inc,out),inc
 return min(inc,out)

def solve(name,bundles,levels=(1,2),custom=None):
 n=len(bundles);v=len(bundles[0])
 if custom is None:
  states=list(product(levels,repeat=n));profiles=[tuple(tuple(t*b for b in bundle) for t,bundle in zip(s,bundles)) for s in states]
 else:profiles=custom
 N=len(profiles);vi=N*n;rows=[];rhs=[];tags=[]
 def add(row,b,tag):rows.append(row);rhs.append(b);tags.append(tag)
 for q,p in enumerate(profiles):
  sums=[sum(row[j] for row in p) for j in range(v)];T=value(sums)
  add({**{q*n+i:1 for i in range(n)},vi:-T},0,['budget',q])
  for mask in range(1,1<<n):
   val=value([sum(p[i][j] for i in range(n) if mask>>i&1) for j in range(v)])
   if val:add({q*n+i:-1 for i in range(n) if mask>>i&1},-val,['coalition',q,mask])
 # Direct actual-profile comparison, no role relabeling.
 for lo in range(N):
  for hi in range(lo+1,N):
   change=[i for i in range(n) if profiles[lo][i]!=profiles[hi][i]]
   if len(change)!=1:continue
   i=change[0];a=profiles[lo][i];b=profiles[hi][i]
   if all(x<=y for x,y in zip(a,b)):add({lo*n+i:1,hi*n+i:-1},0,['monotone',lo,hi,i])
   elif all(x>=y for x,y in zip(a,b)):add({hi*n+i:1,lo*n+i:-1},0,['monotone',hi,lo,i])
 rr=[];cc=[];dd=[]
 for k,r in enumerate(rows):
  for j,a in r.items():rr.append(k);cc.append(j);dd.append(a)
 mat=coo_matrix((dd,(rr,cc)),shape=(len(rows),vi+1)).tocsr();obj=np.zeros(vi+1);obj[-1]=1
 ans=linprog(obj,A_ub=mat,b_ub=np.array(rhs),bounds=(0,None),method='highs')
 need(ans.success,ans.message)
 weights=[Q(float(-x)).limit_denominator(10**7) if x<-1e-8 else Q() for x in ans.ineqlin.marginals]
 combo={};right=Q();dual=[]
 for w,r,b,tag in zip(weights,rows,rhs,tags):
  if not w:continue
  for j,a in r.items():combo[j]=combo.get(j,Q())+w*a
  right+=w*b;dual.append({'weight':str(w),'tag':tag})
 need(combo.get(vi,Q())<0 and all(a>=0 for j,a in combo.items() if j!=vi),'exact dual invalid')
 lower=right/combo[vi]
 primal=[Q(float(x)).limit_denominator(10**7) for x in ans.x]
 primalok=all(sum(Q(a)*primal[j] for j,a in r.items())<=b for r,b in zip(rows,rhs))
 result=dict(name=name,owners=n,vertices=v,profiles=N,rows=len(rows),float_optimum=ans.fun,exact_dual_lower=str(lower),primal_exact_valid=primalok,primal_factor=str(primal[-1]),dual=dual,all_profiles=profiles,primal=list(map(str,primal)),scope='finite diagnostic; dual restricts all-real actual-owner mechanisms')
 Path(__file__).with_name(name+'.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['name','owners','vertices','profiles','exact_dual_lower','primal_exact_valid']}),flush=True)
 return result

if __name__=='__main__':
 solve('two_pool_calibration',[[1,0],[1,0],[0,1],[0,1]],levels=(1,2))
 for v in [4,5,6]:solve('path_singletons_'+str(v),[[int(i==j) for j in range(v)] for i in range(v)],levels=(0,1,2))
 # Interlaced actual owners; each row specifies fixed eligible resources.
 for name,owners in [('path_endpoints',(0,1,2,3,0)),('path_alt_bundle',(0,1,2,3,0,4,2,5,0)),('path_mixed_bundle',(0,1,2,0,3,2,1)),('path_repeat3',(0,1,2,0,1,2,0))]:
  n=max(owners)+1;v=len(owners);bundles=[[int(owners[j]==i) for j in range(v)] for i in range(n)]
  solve(name,bundles,levels=(0,1,2))
