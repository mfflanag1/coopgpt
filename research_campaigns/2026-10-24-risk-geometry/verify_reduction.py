"""Exact one-factor translation checks; optional LP check of full selectors."""
from fractions import Fraction as Q
from pathlib import Path
import json
P=Path(__file__).parent

def fib(k):
 a,b=1,1
 for _ in range(k-1):a,b=b,a+b
 return a

def rank(rows):
 A=[[Q(x) for x in row] for row in rows];j=0
 for col in range(len(A[0])):
  p=next((i for i in range(j,len(A)) if A[i][col]),None)
  if p is None:continue
  A[j],A[p]=A[p],A[j]; d=A[j][col];A[j]=[v/d for v in A[j]]
  for i in range(len(A)):
   if i!=j:
    d=A[i][col];A[i]=[v-d*w for v,w in zip(A[i],A[j])]
  j+=1
 return j

def family(m,r):
 F=fib(m+1); a=[Q(fib(m-i+1),F) for i in range(1,m+1)];b=[1-u for u in a]
 U=[Q(r-m)]+a+b+[Q(0)]*r;V=[Q(0)]*(2*m+1)+[Q(1)]*r
 rows=[]
 def row(indices):rows.append([int(i in indices) for i in range(2*m)])
 for i in range(m):row([i,m+i])
 for i in range(m-2):row([i+1,i+2,m+i])
 row([m-2,2*m-1]);row([0,1])
 if rank(rows)!=2*m:raise AssertionError('closure rank')
 if any(sum(c*d for c,d in zip(row,a+b))!=1 for row in rows):raise AssertionError('row equality')
 tm=Q(F,F+1);tz=Q(1,r-m+1)
 x=[tm*u+(1-tm)*v for u,v in zip(U,V)];z=[tz*u+(1-tz)*v for u,v in zip(U,V)]
 return U,V,x,z

def main():
 cases=[];count=0
 for m,r in [(2,3),(2,5),(2,8),(3,4),(3,6),(4,5)]:
  U,V,x,z=family(m,r);n=len(U);a=[(u-v)/2 for u,v in zip(U,V)];T=sum(U)
  if sum(a)!=0 or sum(V)!=T:raise AssertionError('totals')
  for s in range(2**n):
   ix=[i for i in range(n) if (s>>i)&1]
   us=sum(U[i] for i in ix);vs=sum(V[i] for i in ix)
   risk=sum(abs(a[i]) for i in ix)-abs(sum(a[i] for i in ix))
   if risk!=min(us,vs):raise AssertionError('all-coalition reduction')
   if sum(x[i] for i in ix)<risk or sum(z[i] for i in ix)<risk:raise AssertionError('selector feasibility')
   count+=1
  rho=sum(abs(u-v) for u,v in zip(x,z))/T
  expected=2*(Q(fib(m+1),fib(m+1)+1)-Q(1,r-m+1))
  if rho!=expected:raise AssertionError('distance')
  cases.append({'m':m,'r':r,'n':n,'rho':str(rho),'all_coalitions':2**n,'closure_rank':2*m})
 # Independent floating LP recomputes full lexicographic stages for the small embedding.
 import numpy as np
 from explore import core,selector
 lp=[]
 for m,r in [(2,3),(2,4),(3,4)]:
  U,V,x,z=family(m,r);a=np.array([[float((u-v)/2),0.]for u,v in zip(U,V)])
  for e in [0.,0.25]:
   A=a if e==0 else np.vstack([a,[0,e],[0,-e]])
   M,v,T,b=core(A)
   xx,_,_=selector(M,v,T,'ascending');zz,_,_=selector(M,v,T,'descending')
   xe=np.array([float(u)for u in x]+([]if e==0 else[e,e]));ze=np.array([float(u)for u in z]+([]if e==0 else[e,e]))
   err=max(float(np.max(np.abs(xx-xe))),float(np.max(np.abs(zz-ze))))
   if err>1e-7:raise AssertionError('LP selector comparison')
   lp.append({'m':m,'r':r,'e':e,'n':len(A),'max_absolute_error':err})
 results={'evidence':'exact rational all-coalition translation and closure matrix checks; separately labeled floating full-selector checks','exact_coalitions_checked':count,'families':cases,'floating_lp_checks':lp}
 (P/'verification_results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
if __name__=='__main__':main()
