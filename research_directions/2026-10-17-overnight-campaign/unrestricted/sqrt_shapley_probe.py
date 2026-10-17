import json,math
import numpy as np
rng=np.random.default_rng(19281)
out={'trials':0,'min_cover_ratio':1e100,'min_coordinate_ratio':1e100,'counterexample':None}
for trial in range(30000):
 n=int(rng.integers(2,11));k=int(rng.integers(2,2*n+1))
 masks=np.array([[int(s>>i&1) for i in range(n)] for s in range(1<<n)],float)
 forms=rng.integers(0,8,(k,n)).astype(float)
 if trial%3==0:
  forms=rng.binomial(1,rng.uniform(.1,.7),size=(k,n))*rng.integers(1,8,(k,n))
  forms=forms.astype(float)
 if trial%3==1:
  forms[0]=rng.exponential(1,n); forms[0]/=sum(forms[0]);
  forms[1:]*=rng.integers(0,2,(k-1,n))
 vals=np.min(masks@forms.T,axis=1);T=vals[-1]
 if T<=0:continue
 phi=np.zeros(n)
 for s in range(1<<n):
  sz=s.bit_count()
  if sz==n:continue
  weight=1/(n*math.comb(n-1,sz))
  for i in range(n):
   if not (s>>i&1):phi[i]+=weight*(vals[s|(1<<i)]-vals[s])
 assert abs(sum(phi)-T)<1e-7
 pay=np.sqrt(T*np.maximum(phi,0));cover=masks@pay
 valid=vals>1e-10
 ratios=cover[valid]/vals[valid];rr=float(ratios.min())
 out['trials']+=1;out['min_cover_ratio']=min(out['min_cover_ratio'],rr)
 if rr<1-1e-7:
  s=int(np.where(valid)[0][ratios.argmin()])
  out['counterexample']={'n':n,'forms':forms.tolist(),'values':vals.tolist(),'T':T,'phi':phi.tolist(),'payments':pay.tolist(),'coalition':s,'ratio':rr};break
print(json.dumps(out))
