import sys,time,json
from pathlib import Path
sys.path.insert(0,'/private/tmp/coopgpt-ownership-20261016/root/actual_envelope_search')
from probe_v2 import phi,actual
import numpy as np
from scipy.optimize import differential_evolution
n=4;m=2;size=n*(2*m+1);start=time.monotonic();best=[0,None]
def objective(xx):
 x=np.asarray(xx);x=x.T if x.ndim==2 else x[None,:]
 base=x[:,:size].reshape(-1,n,2*m+1);frac=x[:,size:].reshape(-1,n,2*m+1)
 _,pay,F=actual(base,frac,n,m);_,full,_=actual(base,np.ones_like(frac),n,m)
 H=base[...,:m].sum(axis=(1,2));M=np.minimum(base[...,:m].sum(axis=1),base[...,m:2*m].sum(axis=1)).sum(axis=1);P=base[...,-1].sum(axis=1)
 ratio=np.maximum(pay,full).sum(axis=1)/np.maximum(F,1e-12)
 feasible=P+M>=H
 score=np.where(feasible,ratio,1-10*(H-P-M))
 at=int(score.argmax())
 if feasible[at] and ratio[at]>best[0]:
  best[:]=[float(ratio[at]),{'base':base[at].tolist(),'fractions':frac[at].tolist(),'payments':np.maximum(pay,full)[at].tolist(),'full_payments':full[at].tolist(),'H':float(H[at]),'P':float(P[at]),'M':float(M[at])}]
 return -score if np.asarray(xx).ndim==2 else -float(score[0])
for rep in range(10):
 rng=np.random.default_rng(111+rep)
 center=np.zeros((n,2*m+1));center[0,0]=1;center[1,m]=center[2,m]=1;center[1,-1]=center[2,-1]=1
 ff=np.ones_like(center);ff[1,m]=ff[2,m]=0
 flat=np.r_[center.ravel(),ff.ravel()]
 init=np.clip(flat+rng.normal(0,.15,(8*2*size,2*size)),0,1);init[0]=flat
 res=differential_evolution(objective,[(0.,1.)]*(2*size),seed=111+rep,maxiter=2500,tol=1e-10,init=init,vectorized=True,updating='deferred',polish=False,callback=lambda x,c:time.monotonic()-start>90)
 if time.monotonic()-start>90:break
out={'status':'floating lower witness only; not proof','best_ratio':best[0],'witness':best[1],'elapsed':time.monotonic()-start}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
