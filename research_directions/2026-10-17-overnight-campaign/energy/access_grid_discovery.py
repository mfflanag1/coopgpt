#!/usr/bin/env python3
"""FLOAT finite all-profile LP discovery for unit-profit bipartite access graphs."""
import itertools,json,sys,random
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def solve(ne,nh,edges,k=2,theta=1):
 n=ne+nh;adj=[{v for u,v in edges if u==j} for j in range(ne)]
 cuts=[]
 for mask in range(1<<ne):
  left=[j for j in range(ne) if not mask>>j&1];nb=set().union(*(adj[j] for j in range(ne) if mask>>j&1));cuts.append(left+[ne+i for i in nb])
 @lru_cache(None)
 def F(pr):return min(sum(pr[i] for i in cut) for cut in cuts)
 profiles=list(itertools.product(range(k+1),repeat=n));idx={x:i for i,x in enumerate(profiles)}
 rows=[];cols=[];data=[];rhs=[]
 def row(co,r):
  j=len(rhs);rhs.append(float(r))
  for i,v in co.items():
   if v:rows.append(j);cols.append(i);data.append(float(v))
 for j,pr in enumerate(profiles):
  f=F(pr)
  for mask in range(1<<n):
   val=F(tuple(x if mask>>i&1 else 0 for i,x in enumerate(pr)))
   if val:row({j*n+i:-1 for i in range(n) if mask>>i&1},-val)
  for i in range(ne):
   remove=list(pr);remove[i]=0;m=f-F(tuple(remove))
   if m:row({j*n+i:-1},-theta*m)
  row({**{j*n+i:1 for i in range(n)},len(profiles)*n:-f},0)
  for i in range(n):
   if pr[i]:
    lo=list(pr);lo[i]-=1;row({idx[tuple(lo)]*n+i:1,j*n+i:-1},0)
 A=coo_matrix((data,(rows,cols)),shape=(len(rhs),len(profiles)*n+1)).tocsr();c=np.zeros(A.shape[1]);c[-1]=1
 r=linprog(c,A_ub=A,b_ub=rhs,bounds=(0,None),method='highs')
 return dict(ne=ne,nh=nh,edges=edges,k=k,theta=theta,ratio=r.fun if r.success else None,status=r.message)
if __name__=='__main__':
 out=[]
 # Graphs chosen structurally then independent reproducible masks; this is finite discovery only.
 cases=[(2,2,[(0,0),(0,1),(1,1)]),(3,3,[(0,0),(0,1),(1,1),(1,2),(2,2)]),(3,3,[(0,0),(0,1),(1,1),(1,2),(2,2),(2,0)]),(3,3,[(i,j) for i in range(3) for j in range(3)])]
 rng=random.Random(307)
 for z in range(30):
  edges=[(i,j) for i in range(3) for j in range(3) if rng.random()<.6]
  if all(any(i==u for i,j in edges) for u in range(3)) and all(any(j==v for i,j in edges) for v in range(3)):cases.append((3,3,edges))
 for ne,nh,edges in cases:
  r=solve(ne,nh,edges,2,1);out.append(r);print(r,flush=True)
 Path(__file__).with_name('access_grid_discovery.json').write_text(json.dumps(out,indent=2)+'\n')
