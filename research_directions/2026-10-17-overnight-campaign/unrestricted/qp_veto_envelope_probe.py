import json,itertools
import numpy as np
from scipy.optimize import minimize,LinearConstraint,linprog
rng=np.random.default_rng(162734)
out={'trials':0,'max_ratio':0,'max_squared_ratio':0,'counterexample':None}
for trial in range(1000):
 n=int(rng.integers(3,9));nr=int(rng.integers(2,9))
 A=rng.integers(0,2,(nr,n)).astype(float);A=A[A.sum(axis=1)>0]
 A[:,0]=1
 w=rng.integers(1,5,len(A)).astype(float)
 lp=linprog(np.ones(n),A_ub=-A,b_ub=-w,bounds=(0,None),method='highs')
 if not lp.success:continue
 T=lp.fun
 def solve(rows):
  if not len(rows):return np.zeros(n)
  AA=A[rows];ww=w[rows]
  rr=minimize(lambda x:np.dot(x,x)/2,np.full(n,ww.max()),jac=lambda x:x,constraints=[LinearConstraint(AA,ww,np.inf)],bounds=[(0,None)]*n,method='SLSQP',options={'ftol':1e-9,'maxiter':300})
  if np.max(ww-AA@rr.x)>1e-6:return None
  return rr.x
 M=[];witness=[]
 for i in range(n):
  fixed=list(np.where(A[:,i]==0)[0]);vary=list(np.where(A[:,i]>0)[0]);best=0;arg=None
  for pattern in range(1<<len(vary)):
   rows=fixed+[j for t,j in enumerate(vary) if pattern>>t&1]
   xx=solve(rows)
   if xx is not None and xx[i]>best:best=float(xx[i]);arg=[int(j) for j in rows]
  M.append(best);witness.append(arg)
 ratio=sum(M)/(np.sqrt(n)*T)
 out['trials']+=1;out['max_ratio']=max(out['max_ratio'],ratio)
 out['max_squared_ratio']=max(out['max_squared_ratio'],sum(x*x for x in M)/T**2)
 if sum(x*x for x in M)>T*M[0]+1e-5:
  out['counterexample']={'n':n,'A':A.tolist(),'w':w.tolist(),'T':T,'M':M,'witness':witness,'ratio':ratio,'norm2':sum(x*x for x in M),'T_M0':T*M[0]};break
print(json.dumps(out))
