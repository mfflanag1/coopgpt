import json
import numpy as np
from scipy.optimize import minimize, LinearConstraint
rng=np.random.default_rng(99334)
out={'trials':0,'max_ratio':0,'counterexample':None}
for trial in range(3000):
 n=int(rng.integers(2,9)); masks=np.array([[int(s>>i&1) for i in range(n)] for s in range(1,1<<n)],float)
 core=rng.exponential(1,n);core/=core.sum()
 v=(masks@core)*rng.beta(.2,.2,len(masks));v[-1]=1
 def solve(A,w):
  rr=minimize(lambda x:np.dot(x,x)/2,core,jac=lambda x:x,constraints=[LinearConstraint(A,w,np.inf)],bounds=[(0,None)]*n,method='SLSQP',options={'ftol':1e-10,'maxiter':500})
  if np.max(w-A@rr.x)>1e-7:return None
  return rr.x
 x=solve(masks,v)
 if x is None:continue
 R=float(x@x); vals=[]
 for i in range(n):
  rows=masks[:,i]==0; z=solve(masks[rows],v[rows])
  if z is None:break
  vals.append(float(z@z))
 if len(vals)<n:continue
 ratio=n*R-sum(vals)
 out['trials']+=1;out['max_ratio']=max(out['max_ratio'],ratio)
 if ratio>1+1e-6:
  out['counterexample']={'n':n,'v':v.tolist(),'core':core.tolist(),'x':x.tolist(),'R2':R,'deletions':vals,'ratio':ratio};break
print(json.dumps(out))
