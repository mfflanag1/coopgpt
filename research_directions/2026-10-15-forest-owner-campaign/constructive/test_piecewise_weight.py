import numpy as np
from math import exp
rng=np.random.default_rng(5262)
for r in (3,4):
 lo=0.;hi=1.
 for _ in range(60):
  mid=(lo+hi)/2
  if mid*exp(-mid)<1/r:lo=mid
  else:hi=mid
 u=(lo+hi)/2;l=1+u;h=1+1/u;A=l*l/(r*u)
 best=(1,None)
 for batch in range(80):
  n=100000;k=rng.choice([0,0,0,0,1,1,2,3],size=(n,r))
  t=rng.exponential(2,size=(n,r));t=np.maximum(t,1-k)
  rho=k+t
  w=np.where(rho<l,np.exp(1-rho),np.where(rho<=h,A/rho-1/r,(u/r)*np.exp(h-rho)))
  minuswp=np.where((rho<l)|(rho>h),w,A/rho**2)
  s=minuswp*t/w
  W=1+w.sum(axis=1);M=(w*s).sum(axis=1)/W
  v=1-M+(w*np.minimum(t,1)*np.minimum(s-M[:,None],0)).sum(axis=1)
  j=np.argmin(v)
  if v[j]<best[0]:best=(float(v[j]),dict(k=k[j].tolist(),t=t[j].tolist(),rho=rho[j].tolist(),w=w[j].tolist(),s=s[j].tolist(),M=float(M[j])))
  if v[j]<-1e-10:print('FAIL',r,batch,best,flush=True);break
 else:print('PASS',r,best,flush=True)
