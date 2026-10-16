"""Floating scalar relaxation probe, not an actual report counterexample."""
import math,json
from scipy.optimize import differential_evolution
K=math.e-1;c=1/(2*math.e);C=1+c;eta=.5+2/math.e

def obj(x,ret=False):
 a,z,r,G,M=x;g=1-a;S=1+g-G;Z=z+r;delta=C*M-Z
 vio=[G-g,r-(g-G),z-M,Z-C*M,M-Z,z-a-.5,z-a-1.5+Z]
 for h in [.01,.1,.25,.5,1,2,5,10,50,100]:
  Lmax=h+(1+h)/2*math.exp(-h/(1+h))-h*Z
  vio.append(z-a-Lmax)
  vio.append(z-a-(1-Z+Lmax))
  Lmax=(1+h+h/2*math.exp(-1-1/h))*M-h*Z
  vio.append(z-a-Lmax)
  vio.append(z-a-(1-Z+Lmax))
 pen=sum(max(0,v)**2 for v in vio)
 kap=min(K*z,r,1-z+eta*a)
 vv=K*K*r*G
 if vv>=1:pen+=(vv-1)**2+1;vv=.999999
 rr=math.sqrt(1-vv);L=2*math.exp(rr-1)/(1+rr)
 other_floor=max(0,g-G-kap,min(1,g-G-r+max(0,M-2*z)))
 val=1+.5*g*math.exp(-other_floor)-.5*math.exp(-g+G-delta)*G*L
 if ret:return {'upper':val,'C_squared':C*C,'x':list(x),'kappa':kap,'delta':delta,'other_floor':other_floor,'violations':vio,'penalty':pen,'status':'floating relaxation only'}
 return -val+1e5*pen
r=differential_evolution(obj,[(0,1),(0,1),(0,1),(0,1),(0,1)],maxiter=1500,popsize=35,seed=228,polish=True,tol=1e-10)
print(json.dumps(obj(r.x,True),indent=2))
