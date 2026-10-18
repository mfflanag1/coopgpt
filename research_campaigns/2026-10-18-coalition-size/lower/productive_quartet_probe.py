#!/usr/bin/env python3
"""Bounded necessary relaxation; numerical feasible points are NOT mechanisms."""
import argparse,json,time
from collections import defaultdict
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def run(M,s=None,limit=50):
 n=4*M+3;s=n if s is None else s; start=time.monotonic()
 states=[(f,t) for f in range(M+1) for t in range(M-f+1)]
 ix={st:5*i for i,st in enumerate(states)};K=5*len(states)
 rows=[];rhs=[];seen=set()
 def add(row,b=0):
  row={j:c for j,c in row.items() if c};key=(tuple(sorted(row.items())),b)
  if key in seen:return False
  seen.add(key);rows.append(row);rhs.append(b);return True
 def v(st,k):return ix[st]+k
 # Per profile orbit variables: cap z, full a, partial b, singleton p, zero q.
 for st in states:
  f,t=st;u=M-f-t;z,a,b,p,q=[v(st,k) for k in range(5)]
  val=min(3,1+4*f/3+t)
  add({z:3,a:4*f,b:3*t,p:u,q:3*u+t,K:-val})
  add({z:-3},-1)
  if f:add({z:-1,a:-2},-1)
  if t:add({z:-1,b:-2},-1)
  if st==(1,0):add({z:1,a:-1});add({a:1,z:-1})
  if st==(0,1):add({z:1,b:-1});add({b:1,z:-1})
 transitions=[]
 for st in states:
  f,t=st;u=M-f-t
  if u and s>=2:
   nxt=(f,t+1);groups=[(3,0,0),(4*f,1,1),(3*t,2,2),(u-1,3,3),(1,3,2),(3*u+t-2,4,4)]
   transitions.append((st,nxt,2,2,groups))
  if t and s>=1:
   nxt=(f+1,t-1);groups=[(3,0,0),(4*f,1,1),(3*(t-1),2,2),(u,3,3),(3,2,1),(3*u+t-1,4,4)]
   transitions.append((st,nxt,1,1,groups))
 history=[]
 for it in range(150):
  rr=[];cc=[];dd=[]
  for i,row in enumerate(rows):
   for j,c in row.items():rr.append(i);cc.append(j);dd.append(c)
  A=coo_matrix((dd,(rr,cc)),shape=(len(rows),K+1)).tocsr()
  obj=np.zeros(K+1);obj[K]=1
  res=linprog(obj,A_ub=A,b_ub=np.array(rhs),bounds=(0,None),method='highs',options={'time_limit':max(1,limit-(time.monotonic()-start))})
  if not res.success:return {'M':M,'s':s,'status':res.message,'history':history}
  x=res.x;cuts=0;worst=0
  for st,nxt,c,newkind,groups in transitions:
   row=defaultdict(int);row[v(st,4)]+=c;row[v(nxt,newkind)]-=c
   loss=sorted([(x[v(st,k)]-x[v(nxt,l)],num,k,l) for num,k,l in groups if num],reverse=True)
   rem=s-c
   for delta,num,k,l in loss:
    if delta<=1e-9 or rem<=0:break
    take=min(num,rem);rem-=take;row[v(st,k)]+=take;row[v(nxt,l)]-=take
   violation=sum(cj*x[j] for j,cj in row.items());worst=max(worst,violation)
   if violation>1e-8:cuts+=add(row)
  history.append({'iteration':it,'factor':x[K],'cuts':cuts,'violation':worst,'elapsed':time.monotonic()-start})
  if not cuts:
   return {'M':M,'n':n,'s':s,'factor':x[K],'sqrt_normalized':x[K]/M**.5,'three_quarter_normalized':x[K]/M**.75,'status':'FINITE_RELAXATION_OPTIMUM','history':history,'payments':{str(st):list(x[ix[st]:ix[st]+5]) for st in states},'scope':'Necessary constraints only. No full-domain upper or asymptotic claim.'}
  if time.monotonic()-start>limit:break
 return {'M':M,'s':s,'status':'TIME_LIMIT','history':history}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('M',type=int);p.add_argument('--s',type=int);p.add_argument('--limit',type=int,default=50);p.add_argument('--out');a=p.parse_args()
 result=run(a.M,a.s,a.limit)
 if a.out:open(a.out,'w').write(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('payments','history')}));print(json.dumps(result['history'][-3:]))
