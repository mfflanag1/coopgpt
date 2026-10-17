"""Bounded feasibility gate: translated, null-zero pairwise TCWM necessary
conditions on signed profiles{-2,-1,0,1,2} with five fixed owners.
Feasibility is NOT an all-real mechanism construction.
"""
from itertools import combinations_with_replacement,product
from collections import Counter
from pathlib import Path
import json,numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
n=5;types=list(range(-2,3));states=list(combinations_with_replacement(types,n))
def can(s,t):return min((s,t),(tuple(sorted(-x for x in s)),-t))
keys=sorted({can(s,t) for s in states for t in set(s) if t})
index={x:i for i,x in enumerate(keys)};ki=len(keys)
rr=[];cc=[];vv=[];rhs=[];labels=[]
def add(row,b,label):
 j=len(rhs)
 for k,v in row.items():
  if v:rr.append(j);cc.append(k);vv.append(v)
 rhs.append(b);labels.append(label)
def p(row,s,t,c):
 if t:
  k=index[can(s,t)];row[k]=row.get(k,0)+c
bounds=[(0,None)]*len(keys)+[(1,None)]
for s in states:
 ct=Counter(s);present=sorted(ct)
 T=min(sum(max(t,0) for t in s),sum(max(-t,0) for t in s))
 row={ki:-T}
 for t in s:p(row,s,t,1)
 add(row,0,['budget',s])
 for counts in product(*(range(ct[t]+1) for t in present)):
  if not sum(counts):continue
  worth=min(sum(c*max(t,0) for t,c in zip(present,counts)),sum(c*max(-t,0) for t,c in zip(present,counts)))
  row={}
  for t,c in zip(present,counts):p(row,s,t,-c)
  add(row,-worth,['coverage',s,list(zip(present,counts))])
 if sum(t!=0 for t in s)<=2:
  row={}
  for t in s:p(row,s,t,1)
  add(row,T,['two_active_upper',s])
 for size in (1,2):
  for old in combinations_with_replacement(present,size):
   oldct=Counter(old)
   if any(oldct[t]>ct[t] for t in oldct):continue
   for new in product(types,repeat=size):
    ns=list(s)
    for t in old:ns.remove(t)
    ns+=list(new);ns=tuple(sorted(ns))
    if ns==s and Counter(old)==Counter(new):continue
    delta=[new[j]-old[j] for j in range(size)]
    N=sum(max(-x,0) for x in delta)
    dm=sum(min(t,0) for t in new)-sum(min(t,0) for t in old)
    row={}
    for t in old:p(row,s,t,1)
    for t in new:p(row,ns,t,-1)
    # beta0: DeltaH>=-N.
    add(row,N+dm,['tcwm',s,old,ns,new])
A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),ki+1)).tocsr()
c=np.zeros(ki+1);c[ki]=1
res=linprog(c,A_ub=A,b_ub=np.array(rhs),bounds=bounds,method='highs',options={'time_limit':30})
out={'status':res.status,'message':res.message,'states':len(states),'variables':ki+1,'constraints':len(rhs),'interpretation':'Necessary finite-profile relaxation only; feasibility does not imply a general mechanism.'}
if res.success:
 out['finite_gain_coefficient']=float(res.fun)
 out['payments']=[{'state':s,'type':t,'pay':float(res.x[j])} for (s,t),j in index.items()]
 out['dual']=[{'label':labels[j],'multiplier':float(v)} for j,v in enumerate(res.ineqlin.marginals) if abs(v)>1e-9]
Path(__file__).with_name('pairwise_tcwm_null_scout.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['payments','dual']},indent=2))
