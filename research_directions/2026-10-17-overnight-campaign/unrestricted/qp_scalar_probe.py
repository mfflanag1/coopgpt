import json, itertools
import numpy as np
from scipy.optimize import minimize, LinearConstraint
rng=np.random.default_rng(20261017)
out={'trials':0,'max_ratio':1,'counterexample':None}
for trial in range(1000):
 n=int(rng.integers(3,8)); d=int(rng.integers(2,8)); k=int(rng.integers(2,10))
 forms=rng.integers(0,8,(k,d)).astype(float)
 b=rng.integers(0,8,(n,d)).astype(float)
 masks=np.array([[int(s>>i&1) for i in range(n)] for s in range(1,1<<n)],dtype=float)
 def solve(b):
  v=np.min(masks@b@forms.T,axis=1)
  res=minimize(lambda x:np.dot(x,x)/2,np.full(n,v[-1]),jac=lambda x:x,
       constraints=[LinearConstraint(masks,v,np.inf)],bounds=[(0,None)]*n,
       method='SLSQP',options={'ftol':1e-10,'maxiter':500})
  if not res.success and np.max(v-masks@res.x)>1e-6:return None,v
  return res.x,v
 y,v=solve(b)
 if y is None:continue
 i=int(rng.integers(n)); b1=b.copy(); delta=b1[i]*float(rng.choice([0.1,0.5,1,2]));b1[i]+=delta
 z,w=solve(b1)
 if z is None:continue
 out['trials']+=1
 if v[-1]>0:out['max_ratio']=max(out['max_ratio'],float(sum(y)/v[-1]))
 if z[i]<y[i]-1e-5:
  out['counterexample']={'n':n,'d':d,'forms':forms.tolist(),'b':b.tolist(),'owner':i,'delta':delta.tolist(),'y':y.tolist(),'z':z.tolist(),'v':v.tolist(),'w':w.tolist()};break
print(json.dumps(out))
