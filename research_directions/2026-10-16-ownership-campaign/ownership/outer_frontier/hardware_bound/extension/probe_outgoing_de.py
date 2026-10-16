import numpy as np,json
from scipy.optimize import differential_evolution

def phi(a,b):
 A=a.sum(axis=-1,keepdims=True);B=b.sum(axis=-1,keepdims=True);T=np.minimum(A,B)
 s=np.where(A<=B,a,b);l=np.where(A<=B,b,a);d=np.minimum(l,T)
 r=np.divide(d.sum(axis=-1,keepdims=True),T,out=np.ones_like(T),where=T>0)
 return np.where(T>0,(1-.5*np.exp(1-r))*s+.5*np.exp(1-r)*d,0.)
n=8

def unpack(x):
 y=np.asarray(x);y=y.T if y.ndim==2 else y[None,:]
 h=y[:,:n];l=y[:,n:2*n];hp=h.copy();lp=l.copy();hp[:,0]*=y[:,2*n];lp[:,0]*=y[:,2*n+1]
 z=phi(h,l);zp=phi(hp,lp);v=np.maximum(0,z[:,1:]-zp[:,1:]).sum(axis=1)/np.maximum(h.sum(axis=1),1e-10)
 return v,h,l,hp,lp,z,zp

def obj(x):
 v,*_=unpack(x);return -v if np.asarray(x).ndim==2 else -v[0]
r=differential_evolution(obj,[(0,1)]*(2*n+2),maxiter=600,popsize=8,seed=389,vectorized=True,updating='deferred',polish=False)
v,h,l,hp,lp,z,zp=unpack(r.x)
print(json.dumps({'ratio':float(v[0]),'h':h[0].tolist(),'l':l[0].tolist(),'hp':hp[0].tolist(),'lp':lp[0].tolist(),'z':z[0].tolist(),'zp':zp[0].tolist()},indent=2))
