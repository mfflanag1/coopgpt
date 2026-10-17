import json
import numpy as np
from scipy.optimize import minimize, LinearConstraint,linprog
rng=np.random.default_rng(66641)
out={'trials':0,'max_ratio':0,'counterexample':None}
for trial in range(5000):
 n=int(rng.integers(2,10)); nr=int(rng.integers(1,3*n))
 A=rng.integers(0,2,(nr,n)).astype(float); A=A[A.sum(axis=1)>0]
 if len(A)==0:continue
 # Frequent shared veto coordinates make the nearly extremal cell visible.
 if trial%3==0:A[:,0]=1
 w=rng.integers(1,6,len(A)).astype(float)
 lp=linprog(np.ones(n),A_ub=-A,b_ub=-w,bounds=(0,None),method='highs')
 if not lp.success:continue
 T=lp.fun
 def solve(A,w):
  if len(A)==0:return np.zeros(n)
  rr=minimize(lambda x:np.dot(x,x)/2,np.full(n,w.max()),jac=lambda x:x,constraints=[LinearConstraint(A,w,np.inf)],bounds=[(0,None)]*n,method='SLSQP',options={'ftol':1e-10,'maxiter':500})
  if np.max(w-A@rr.x)>1e-7:return None
  return rr.x
 x=solve(A,w)
 if x is None:continue
 R=float(x@x); vals=[]
 for i in range(n):
  rows=A[:,i]==0; z=solve(A[rows],w[rows])
  if z is None:break
  vals.append(float(z@z))
 if len(vals)<n:continue
 ratio=(n*R-sum(vals))/T**2
 out['trials']+=1;out['max_ratio']=max(out['max_ratio'],ratio)
 if ratio>1+1e-6:
  out['counterexample']={'n':n,'A':A.tolist(),'w':w.tolist(),'core':lp.x.tolist(),'x':x.tolist(),'T':T,'R2':R,'deletions':vals,'ratio':ratio};break
print(json.dumps(out))
