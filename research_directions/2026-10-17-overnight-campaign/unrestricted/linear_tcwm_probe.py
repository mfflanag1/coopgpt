from math import comb
import numpy as np
from scipy.optimize import linprog

def C(n,k):return comb(n,k) if 0<=k<=n else 0
for n in (2,3,4,5,6,8,10,15,20,30,40):
 # normalized coefficients: a[k] = coefficient * C(n-1,k-1)
 # b[k] = coefficient * C(n-1,k), for k<n
 nv=2*n; K=nv-1; rows=[]; rhs=[]
 for k in range(1,n):
  r=np.zeros(nv);r[k-1]=-1;r[n+k-1]=-k
  rows.append(r);rhs.append(0) # a_raw+(n-k)b_raw>=0 => a_norm+k*b_norm>=0
 for m in range(1,n+1):
  A=np.zeros(nv); B=np.zeros(nv)
  for k in range(m,n+1):
   A[k-1]=C(n-m,k-m)/C(n-1,k-1)
   if m<n:
    B[k-1]=C(n-m-1,k-m-1)/C(n-1,k-1)
    if k<n:B[n+k-1]=C(n-m-1,k-m)/C(n-1,k)
  rows.extend([-m*A,-B]);rhs.extend([-1,0])
  r=m*A+(n-m)*B;r[K]=-1;rows.append(r);rhs.append(0)
 obj=np.zeros(nv);obj[K]=1
 res=linprog(obj,A_ub=np.array(rows),b_ub=rhs,bounds=[(0,None)]*n+[(None,None)]*(n-1)+[(1,None)],method='highs')
 print(n,res.fun if res.success else res.message,flush=True)
 if n==10:
  print(res.x,flush=True)
  print([(j,float(q)) for j,q in enumerate(res.ineqlin.marginals) if abs(q)>1e-8],flush=True)
