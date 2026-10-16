import math,json
from scipy.optimize import differential_evolution
c=1/(2*math.e);K=math.e-1;eta=2/math.e+.5

def k(t):
 if t<=0:return 1.
 return 1-.5*math.exp(1-1/t) if t<=1 else .5*math.exp(1-t)

def probe(mode):
 def obj(x,ret=False):
  g,S,D=x;w=1+eta*(1-g)
  kap=K/2*(math.sqrt(K*K*D*D+4*D*w)-K*D)
  t=max(g-D,S-D-kap)
  val=1+k(t)*(g-D)-.5*math.exp(1-S-c)*(g-S+1)
  vs=[S-1-g,D-g]
  if ret:return dict(mode=mode,value=val,x=list(x),t=t,kappa=kap,violations=vs)
  return -val+1e5*sum(max(0,v)**2 for v in vs)
 r=differential_evolution(obj,[(0,1),(1,2),(0,1)],seed=234,popsize=20,maxiter=500,tol=1e-9)
 return obj(r.x,True)
print(json.dumps(probe(0),indent=2))
