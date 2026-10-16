"""Diagnostic relaxed pointwise state search; NOT an actual counterexample."""
import math,json
from scipy.optimize import differential_evolution
from pathlib import Path
c=1/(2*math.e);C=1+c;K=math.e-1;B2=K*K # CONDITIONAL on independently audited sharp nonlinear theorem

def k(t):
 if t<=0:return 1.
 if t<=1:return 1-.5*math.exp(1-1/t)
 return .5*math.exp(1-t)

def objective(x,ret=False):
 a,z,d,S,M,Z,D=x;g=d-a;delta=C*M-Z
 violations=[a-d,z-d,z-a-.5,M-1,Z-C*M,M-Z,z-Z,Z-z-(S-d),S-d-(1-a),1-S,S-Z<0 and Z-S or 0,1-S+Z-M,D-g,D-z]
 
 for r in [.1,.25,.5,1,2,5,10,50]:
  violations.append(z-a-(r+(1+r)/2*math.exp(-r/(1+r))-r*Z))
  violations.append(z-a-(1-Z+r+(1+r)/2*math.exp(-r/(1+r))-r*Z))
  violations.append(z-a-((1+r+r/2*math.exp(-1-1/r))*M-r*Z))
  violations.append(z-a-(1-Z+(1+r+r/2*math.exp(-1-1/r))*M-r*Z))
 violation=sum(max(0,v)**2 for v in violations)
 out=min(K*z,Z-z,1-z+(2/math.e+.5)*a,math.sqrt(max(0,B2*z*D)))
 t=max(d-D,S-D-out)
 val=1+k(t)*(g-D)-.5*math.exp(1-S-delta)*(g-S+1)
 if ret:return {'upper':val,'violations':violations,'x':list(x),'t':t,'outgoing':out,'delta':delta}
 return -val+1e5*violation
r=differential_evolution(objective,[(0,1),(0,1),(0,1),(1,2),(0,1),(0,C),(0,1)],popsize=30,maxiter=1000,tol=1e-9,polish=True,seed=243)
out=objective(r.x,True)
print(json.dumps(out,indent=2));Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
