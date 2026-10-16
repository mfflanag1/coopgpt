#!/usr/bin/env python3
"""Exact-checked orbit LP: two actual pure owners per resource vertex, path graph.
Owner swaps only within the same vertex preserve the full original domain.
This is a structural small-instance diagnostic, not an unbounded conclusion.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json,gzip,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from structured_lp import value,need

def solve(v):
 states=list(product(range(3),repeat=v));lookup={s:i for i,s in enumerate(states)};N=len(states);dim=2*v;B=N*dim
 choices={0:[(k,0,k) for k in range(3)],1:[(a,b,a+2*b) for a,b in product(range(2),repeat=2)],2:[(k,0,2*k) for k in range(3)]}
 rows=[];rhs=[];tags=[]
 def add(row,b,tag):rows.append({j:a for j,a in row.items() if a});rhs.append(b);tags.append(tag)
 for q,s in enumerate(states):
  caps=[2+t for t in s];T=value(caps);bud={B:-T}
  for j,t in enumerate(s):
   bud[q*dim+2*j]=1 if t==1 else 2
   if t==1:bud[q*dim+2*j+1]=1
  add(bud,0,['budget',q])
  for selected in product(*(choices[t] for t in s)):
   cap=[z[2] for z in selected];val=value(cap)
   if not val:continue
   row={}
   for j,(a,b,c) in enumerate(selected):
    if a:row[q*dim+2*j]=-a
    if b:row[q*dim+2*j+1]=-b
   add(row,-val,['coalition',q,[list(z[:2]) for z in selected]])
  for j,t in enumerate(s):
   if t==2:continue
   high=list(s);high[j]+=1;qq=lookup[tuple(high)]
   before=q*dim+2*j;after=qq*dim+2*j+(1 if t==0 else 0)
   add({before:1,after:-1},0,['monotone',q,qq,j])
 ri=[];ci=[];data=[]
 for r,row in enumerate(rows):
  for j,a in row.items():ri.append(r);ci.append(j);data.append(a)
 mat=coo_matrix((data,(ri,ci)),shape=(len(rows),B+1)).tocsr();obj=np.zeros(B+1);obj[B]=1
 ans=linprog(obj,A_ub=mat,b_ub=np.array(rhs),bounds=(0,None),method='highs');need(ans.success,ans.message)
 x=[Q(float(z)).limit_denominator(10**7) for z in ans.x];primalok=all(sum(Q(a)*x[j] for j,a in row.items())<=b for row,b in zip(rows,rhs))
 weights=[Q(float(-z)).limit_denominator(10**7) if z<-1e-8 else Q() for z in ans.ineqlin.marginals]
 combo={};right=Q();support=[]
 for w,row,b,tag in zip(weights,rows,rhs,tags):
  if not w:continue
  for j,a in row.items():combo[j]=combo.get(j,Q())+w*a
  right+=w*b;support.append({'weight':str(w),'tag':tag})
 valid=combo.get(B,Q())<0 and all(a>=0 for j,a in combo.items() if j!=B)
 lower=right/combo[B] if valid else None
 result=dict(vertices=v,actual_owners=2*v,orbit_profiles=N,rows=len(rows),float_optimum=ans.fun,primal_exact_valid=primalok,primal_factor=str(x[-1]),dual_exact_valid=valid,dual_lower=str(lower),dual=support,primal=list(map(str,x)),scope='Exact finite orbit-domain result, contingent on stated valid actual-owner symmetrization')
 with gzip.open(Path(__file__).with_name('paired_path_'+str(v)+'.json.gz'),'wt') as f:json.dump(result,f)
 print(json.dumps({k:result[k] for k in ['vertices','actual_owners','orbit_profiles','rows','primal_exact_valid','dual_exact_valid','dual_lower']}),flush=True)
 return result
if __name__=='__main__':
 for v in [2,3,4,5]:solve(v)
