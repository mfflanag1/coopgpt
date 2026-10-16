#!/usr/bin/env python3
"""Fixed-owner depth-two finite report LP, exact reconstructed primal/dual."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import gzip,json,sys,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)

def value(cap):
 m=(len(cap)-1)//2
 h=cap[:m];l=cap[m:2*m];p=cap[-1]
 return min(sum(h),p+sum(min(x,y) for x,y in zip(h,l)))

def order_edges(domain):
 # Hasse edges in the finite actual-owner partial order suffice by transitivity.
 edges=[]
 for lo,a in enumerate(domain):
  for hi,b in enumerate(domain):
   if lo==hi or not all(x<=y for x,y in zip(a,b)):continue
   if any(k not in (lo,hi) and all(x<=z<=y for x,z,y in zip(a,c,b)) for k,c in enumerate(domain)):continue
   edges.append((lo,hi))
 return edges

def solve(name,domains):
 started=time.time();n=len(domains);v=len(domains[0][0]);states=list(product(*[range(len(d)) for d in domains]));index={s:k for k,s in enumerate(states)}
 N=len(states);vi=N*n;rows=[];rhs=[];tags=[]
 def add(row,b,tag):rows.append(row);rhs.append(b);tags.append(tag)
 profiles=[tuple(domains[i][s[i]] for i in range(n)) for s in states]
 for q,p in enumerate(profiles):
  cap=[sum(row[j] for row in p) for j in range(v)];T=value(cap)
  add({**{q*n+i:1 for i in range(n)},vi:-T},0,['budget',q])
  for mask in range(1,1<<n):
   val=value([sum(p[i][j] for i in range(n) if mask>>i&1) for j in range(v)])
   if val:add({q*n+i:-1 for i in range(n) if mask>>i&1},-val,['coalition',q,mask])
 for i,domain in enumerate(domains):
  edges=order_edges(domain)
  for s in states:
   for lo,hi in edges:
    if s[i]!=lo:continue
    t=list(s);t[i]=hi;q=index[s];r=index[tuple(t)]
    add({q*n+i:1,r*n+i:-1},0,['monotone',q,r,i])
 rr=[];cc=[];dd=[]
 for k,row in enumerate(rows):
  for j,a in row.items():rr.append(k);cc.append(j);dd.append(a)
 mat=coo_matrix((dd,(rr,cc)),shape=(len(rows),vi+1)).tocsr();obj=np.zeros(vi+1);obj[-1]=1
 ans=linprog(obj,A_ub=mat,b_ub=np.array(rhs),bounds=(0,None),method='highs')
 need(ans.success,ans.message)
 combo={};right=Q();dual=[]
 for x,row,b,tag in zip(ans.ineqlin.marginals,rows,rhs,tags):
  if x>=-1e-9:continue
  w=Q(float(-x)).limit_denominator(10**8)
  for j,a in row.items():combo[j]=combo.get(j,Q())+w*a
  right+=w*b;dual.append({'weight':str(w),'tag':tag})
 valid=combo.get(vi,Q())<0 and all(a>=0 for j,a in combo.items() if j!=vi)
 lower=right/combo[vi] if valid else None
 primal=[Q(float(x)).limit_denominator(10**8) for x in ans.x]
 primalok=all(sum(Q(a)*primal[j] for j,a in row.items())<=b for row,b in zip(rows,rhs))
 result=dict(name=name,owners=n,resources=v,profiles=N,rows=len(rows),float_optimum=ans.fun,exact_dual_valid=valid,exact_dual_lower=str(lower),primal_exact_valid=primalok,primal_factor=str(primal[-1]),domains=domains,states=states,dual=dual,primal=list(map(str,primal)),scope='Finite rectangular report domain; exact dual restricts all-real fixed-owner mechanisms, feasible primal only solves this finite restriction.',elapsed=time.time()-started)
 with gzip.open(ROOT/(name+'.json.gz'),'wt') as f:json.dump(result,f)
 print(json.dumps({k:result[k] for k in ['name','owners','resources','profiles','rows','float_optimum','exact_dual_valid','exact_dual_lower','primal_exact_valid','primal_factor','elapsed']}),flush=True)
 need(valid,'exact dual reconstruction failed');need(primalok,'exact primal reconstruction failed')
 return result

def four_roles(levels=(1,2),hw_scale=(1,1),loc_scale=(1,1),p_scale=1,coupled=False):
 pairs=list(product(levels,repeat=2)) if not coupled else [(t,t) for t in levels]
 A=[(hw_scale[0]*x,hw_scale[1]*y,0,0,0) for x,y in pairs]
 B=A
 W=[(0,0,loc_scale[0]*x,loc_scale[1]*y,0) for x,y in pairs]
 C=[(0,0,0,0,p_scale*t) for t in levels]
 return [A,B,W,C]

if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'first'
 if mode=='first':
  solve('calibration_one_branch', [[(t,0,0) for t in (1,2)],[(t,0,0) for t in (1,2)],[(0,t,0) for t in (1,2)],[(0,0,t) for t in (1,2)]])
  solve('two_branch_coupled',four_roles(p_scale=2,coupled=True))
  solve('two_branch_coordinate_12',four_roles())
  solve('two_branch_coordinate_012',four_roles((0,1,2)))
