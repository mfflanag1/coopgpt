import json
import numpy as np
from scipy.optimize import minimize, LinearConstraint
rng=np.random.default_rng(17733)
out={'trials':0,'max_ratio':0,'counterexample':None}
for trial in range(1000):
 n=int(rng.integers(2,8));d=int(rng.integers(2,8));k=int(rng.integers(2,10))
 forms=rng.integers(0,8,(k,d)).astype(float); b=rng.integers(0,8,(n,d)).astype(float)
 masks=np.array([[int(s>>i&1) for i in range(n)] for s in range(1,1<<n)],float)
 def solve(bb):
  v=np.min(masks@bb@forms.T,axis=1);T=v[-1]
  if T==0:return np.zeros(n),v
  rr=minimize(lambda x:np.dot(x,x)/2,np.full(n,T/n),jac=lambda x:x,
       constraints=[LinearConstraint(masks,v,np.inf)],bounds=[(0,None)]*n,
       method='SLSQP',options={'ftol':1e-9,'maxiter':500})
  if np.max(v-masks@rr.x)>1e-5:return None,v
  return rr.x,v
 x,v=solve(b)
 if x is None or v[-1]<=0:continue
 R=float(x@x); vals=[]
 for i in range(n):
  bb=b.copy();bb[i]=0;z,w=solve(bb)
  if z is None:break
  vals.append(float(z@z))
 if len(vals)<n:continue
 lhs=n*R-sum(vals);ratio=lhs/v[-1]**2
 out['trials']+=1;out['max_ratio']=max(out['max_ratio'],ratio)
 if ratio>1+1e-6:
  out['counterexample']={'n':n,'d':d,'forms':forms.tolist(),'b':b.tolist(),'x':x.tolist(),'T':v[-1],'R2':R,'deletions':vals,'ratio':ratio};break
print(json.dumps(out))
