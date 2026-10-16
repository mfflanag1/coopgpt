import math,random,json
from scipy.optimize import differential_evolution

def phi(a,b):
 A=sum(a);B=sum(b);T=min(A,B)
 if not T:return [0.]*len(a)
 s,l=(a,b) if A<=B else (b,a);d=[min(x,T) for x in l];q=.5*math.exp(1-sum(d)/T)
 return [(1-q)*x+q*y for x,y in zip(s,d)]
n=6
def obj(x,ret=False):
 h=list(x[:n]);h[0]=0;l=list(x[n:2*n]);ll=l.copy();ll[0]*=x[-1];z=phi(h,l);zz=phi(h,ll);H=sum(h)
 v=sum(max(0,z[i]-zz[i]) for i in range(1,n))/max(H,1e-10)
 return {'value':v,'h':h,'l':l,'lprime':ll,'z':z,'zprime':zz} if ret else -v
r=differential_evolution(obj,[(0,1)]*(2*n)+[(0,1)],seed=126,popsize=20,maxiter=1200,tol=1e-10,polish=True)
print(json.dumps(obj(r.x,True),indent=2))
