import numpy as np
from scipy.optimize import minimize
from pathlib import Path
import json
rng=np.random.default_rng(19231);worst=None
for M in range(2,17):
 for trial in range(1500):
  a=rng.uniform(.001,.999,size=M);b=1-a
  lam=np.exp(rng.uniform(-5,5,size=M))
  c=np.r_[a@lam,b@lam,lam]
  T=np.zeros((M,M+2));T[:,0]=a;T[:,1]=b;T[:,2:]=np.eye(M)
  D=np.diag(1/c)
  K=D-D@T.T@np.linalg.solve(T@D@T.T,T@D)
  coeff=1-(c[:,None]*np.maximum(K,0)).sum(axis=0)
  idx=int(np.argmin(coeff));val=float(coeff[idx])
  if worst is None or val<worst['coefficient']:
   worst={'M':M,'a':a.tolist(),'lambda':lam.tolist(),'c':c.tolist(),'resource':idx,'coefficient':val,'Kcol':K[:,idx].tolist()}
  if val < -1e-6:break
 if worst['coefficient'] < -1e-6:break
print(json.dumps(worst,indent=2))
Path(__file__).with_name('TWO_COMMON_QUADRATIC_SCOUT.json').write_text(json.dumps(worst,indent=2)+'\n')
