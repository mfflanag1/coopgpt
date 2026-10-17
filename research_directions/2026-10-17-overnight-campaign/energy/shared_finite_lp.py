#!/usr/bin/env python3
"""Discovery ONLY. Floating HiGHS all-profile grid for shared A,C energy."""
import sys,json,pathlib,itertools, numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix,coo_matrix
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from shared_discovery import value

def solve(a,b,k=2,theta=0,both_floor=False):
 m=len(a);n=m+2;profiles=list(itertools.product(range(k+1),repeat=n));idx={x:i for i,x in enumerate(profiles)}
 vals=[];rows=[];cols=[];data=[];rhs=[]
 def row(co,r):
  j=len(rhs);rhs.append(float(r))
  for i,v in co.items():
   if v: rows.append(j);cols.append(i);data.append(float(v))
 for j,pr in enumerate(profiles):
  L,P,*h=pr;F=value(h,L,P,a,b);vals.append(F)
  for mask in range(1<<n):
   hh=[x if mask&(1<<(i+2)) else 0 for i,x in enumerate(h)]
   f=value(hh,L if mask&1 else 0,P if mask&2 else 0,a,b)
   if f:row({j*n+i:-1 for i in range(n) if mask&(1<<i)},-f)
  if theta:
   G=value(h,0,P,a,b);row({j*n:-1},-theta*(F-G))
   if both_floor:
    FA=value(h,L,0,a,b);row({j*n+1:-1},-theta*(F-FA))
  row({**{j*n+i:1 for i in range(n)},len(profiles)*n:-float(F)},0)
  for i in range(n):
   if pr[i]>0:
    low=list(pr);low[i]-=1;z=idx[tuple(low)]
    row({z*n+i:1,j*n+i:-1},0)
 A=coo_matrix((data,(rows,cols)),shape=(len(rhs),len(profiles)*n+1)).tocsr()
 c=np.zeros(A.shape[1]);c[-1]=1
 r=linprog(c,A_ub=A,b_ub=np.array(rhs),bounds=(0,None),method='highs')
 return {'a':a,'b':b,'theta':theta,'grid':k,'profiles':len(profiles),'success':r.success,'ratio':r.fun if r.success else None,'message':r.message}
if __name__=='__main__':
 import random
 rng=random.Random(17);out=[]
 pairs=[([1,1],[1,1]),([2,0],[3,2]),([1,0],[0,1]),([1,3],[3,1]),([2,1],[1,2])]
 pairs += [([rng.randrange(1,5) for _ in range(2)],[rng.randrange(1,5) for _ in range(2)]) for _ in range(12)]
 for a,b in pairs:
  for theta in [0,1]:
   z=solve(a,b,2,theta);out.append(z);print(z,flush=True)
 pathlib.Path(__file__).with_name('shared_finite_lp.json').write_text(json.dumps(out,indent=2)+'\n')
