"""Diagnostic only; continuous state relaxation, not an actual profile search."""
import math,json
from scipy.optimize import differential_evolution
from pathlib import Path
c=1/(2*math.e);K=math.e-1;eta=2/math.e+.5

def k(t):
 if t<=0:return 1.
 return 1-.5*math.exp(1-1/t) if t<=1 else .5*math.exp(1-t)

def objective(x,ret=False):
 a,z,d,S,M,D=x;g=d-a
 v=[a-d,z-d,z-a-.5,z-M,d+M-z-S,S-1-d+a,D-g,D-z]
 out=min(K*z,1-z+eta*a,K*math.sqrt(max(0,z*D)))
 t=max(d-D,S-D-out)
 val=1+k(t)*(g-D)-.5*math.exp(1-S-c*M)*(g-S+1)
 if ret:return {'upper':val,'violations':v,'x':list(x),'t':t,'outgoing':out}
 return -val+1e5*sum(max(0,w)**2 for w in v)
r=differential_evolution(objective,[(0,1),(0,1),(0,1),(1,2),(0,1),(0,1)],popsize=25,maxiter=1000,tol=1e-9,seed=143,polish=True)
out=objective(r.x,True);print(json.dumps(out,indent=2));Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
