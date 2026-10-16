import math,json
from scipy.optimize import differential_evolution
c=1/(2*math.e);K=math.e-1;eta=2/math.e+.5

def k(t):
 if t<=0:return 1.
 return 1-.5*math.exp(1-1/t) if t<=1 else .5*math.exp(1-t)

def obj(v,ret=False):
 g,x=v;D=g-x;w=1+eta*(1-g)
 if D<0:return 1e5*(-D)
 kap=K/2*(math.sqrt(K*K*D*D+4*D*w)-K*D)
 s=max(1,min(g+kap,1+g));t=max(x,s-D-kap)
 B1=1+x*k(t)-.5*math.exp(-g-c)*(1+g-s)
 B2=1+x*k(1+x-kap)
 val=max(B1,B2)
 if ret:return dict(value=val,v=list(v),kappa=kap,terms=[B1,B2])
 return -val
r=differential_evolution(obj,[(0,1),(.4,1)],seed=234,popsize=20,maxiter=500,tol=1e-10)
print(json.dumps(obj(r.x,True),indent=2))
