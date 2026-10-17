"""Bounded falsification search for the residual minimum-L2-cover candidate."""
import numpy as np,json,time
from scipy.optimize import minimize,LinearConstraint
from pathlib import Path
rng=np.random.default_rng(2026101701);start=time.monotonic();checked=0

def pay(b):
 f=np.min(b,axis=1);z=b[:,0]-b[:,1];ids=np.flatnonzero(z);n=len(ids)
 if n==0:return f.copy(),None
 zz=z[ids];pos=np.maximum(zz,0);neg=np.maximum(-zz,0)
 A=np.array([[float(mask>>j&1) for j in range(n)] for mask in range(1,1<<n)])
 vals=np.minimum(A@pos,A@neg)
 T=min(sum(pos),sum(neg))
 if T<1e-12:return f.copy(),None
 x0=np.array([T-min(sum(pos)-pos[j],sum(neg)-neg[j]) for j in range(n)])
 res=minimize(lambda x:.5*x@x,x0,jac=lambda x:x,method='SLSQP',bounds=[(0,None)]*n,constraints=[LinearConstraint(A,vals,np.inf)],options={'ftol':1e-11,'maxiter':500})
 if not res.success or min(A@res.x-vals)<-1e-7:raise RuntimeError(str(res.message))
 out=f.copy();out[ids]+=res.x
 return out,{'residual':zz.tolist(),'residual_pay':res.x.tolist(),'tight_coalitions':[int(j+1) for j in range(len(vals)) if abs(A[j]@res.x-vals[j])<1e-7]}
result=None
for trial in range(120):
 n=3+trial%4
 b=rng.integers(0,9,size=(n,2))/2
 low,ld=pay(b)
 for j in range(n):
  for e in (0,1):
   high=b.copy();high[j,e]+=.125
   yp,hd=pay(high);checked+=1
   for i in range(n):
    sub=[j] if i==j else [i,j]
    loss=float(sum(low[sub])-sum(yp[sub]))
    if loss>1e-6:
     result={'status':'COUNTEREXAMPLE_NUMERICAL','trial':trial,'owner_count':n,'reports':b.tolist(),'changed_owner':j,'changed_coordinate':e,'restoration':.125,'protected_pair':sub,'low_pay':low.tolist(),'high_pay':yp.tolist(),'loss':loss,'low_details':ld,'high_details':hd};break
   if result:break
  if result:break
 if result or time.monotonic()-start>25:break
if not result:result={'status':'NO_COUNTEREXAMPLE_IN_BOUNDED_SCOUT','no_general_conclusion':True}
result['restorations_checked']=checked;result['elapsed_seconds']=time.monotonic()-start
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_projection_scout.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
