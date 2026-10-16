import math,json
from scipy.optimize import differential_evolution
c=1/(2*math.e);K=math.e-1;eta=2/math.e+.5

def k(t):
 if t<=0:return 1.
 return 1-.5*math.exp(1-1/t) if t<=1 else .5*math.exp(1-t)

def probe(mode):
 def obj(x,ret=False):
  g,z,S,D=x;M=1
  amin=max(0,z-.5,z-g);amax=1-g
  if mode>=2: amax=min(amax,S-g-1+z)
  astar=min(amax,max(amin,(S-1+z-g)/(1+eta)))
  t=max(g+astar-D,S-D-K*math.sqrt(max(0,z*D)),S-D-1+z-eta*astar)
  val=1+k(t)*(g-D)-.5*math.exp(1-S-c)*(g-S+1)
  vs=[amin-amax,S-1-g,D-g,D-z]
  if mode==1: vs += [g+amin+1-z-S]
  if ret:return dict(mode=mode,value=val,x=list(x),a=astar,t=t,violations=vs)
  return -val+1e5*sum(max(0,v)**2 for v in vs)
 r=differential_evolution(obj,[(0,1),(0,1),(1,2),(0,1)],seed=234,popsize=20,maxiter=500,tol=1e-9)
 return obj(r.x,True)
print(json.dumps([probe(j) for j in range(3)],indent=2))
