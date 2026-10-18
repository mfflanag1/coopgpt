import numpy as np
from scipy.optimize import minimize,LinearConstraint
import random,json
from pathlib import Path

def game(b):
 n,d=b.shape
 A=np.array([[(m>>i)&1 for i in range(n)] for m in range(1,1<<n)],float)
 return A,np.min(A@b,axis=1)

def pay(b,s):
 b=np.array(b,float);n,d=b.shape;A,v=game(b);T=v[-1]
 if T==0:return np.zeros(n),{'T':0}
 floor=np.min(b,axis=1); v=v-A@floor; g=np.minimum(T,np.max(b,axis=1))-floor; active=np.flatnonzero(g>0); w=np.minimum(T/g[active]**2,s/g[active]); initial_floor=floor.copy(); lam=1/s; Ffloor=float(sum(floor))
 
 if len(active)==0:return floor,{'T':T,'g':g.tolist()}
 B=A[:,active];initial=b[active,np.argmin(np.sum(b,axis=0))]-floor[active]
 ans=minimize(lambda z:.5*np.dot(w*z,z)+lam*(Ffloor+sum(z))**2/(2*T),initial,jac=lambda z:w*z+lam*(Ffloor+sum(z))/T,method='SLSQP',bounds=[(0,None)]*len(active),constraints=[LinearConstraint(B,v,np.inf)],options={'ftol':1e-11,'maxiter':500})
 if not ans.success or np.min(B@ans.x-v)<-1e-6:raise RuntimeError((ans.message, np.min(B@ans.x-v)))
 y=initial_floor.copy();y[active]+=ans.x
 return y,dict(T=T,g=g.tolist(),w=w.tolist(),active=active.tolist(),tight_masks=[k+1 for k,z in enumerate(A@(y-floor)-v) if abs(z)<1e-7])

def run(seed=1324,trials=5000):
 rng=random.Random(seed);best=0
 for t in range(trials):
  n=rng.choice([3,4,5,6]);d=rng.choice([2,3]);s=rng.choice([2,3,4]);b=np.array([[rng.randrange(5) for _ in range(d)] for _ in range(n)],int)
  if t%2:b=np.array([[z if rng.random()<.5 else 0 for z in row] for row in b])
  y,info=pay(b,s);i=rng.randrange(n);j=rng.randrange(d);hi=b.copy();hi[i,j]+=rng.choice([1,2,7]);yy,iinfo=pay(hi,s);dy=yy-y
  others=sorted((dy[k],k) for k in range(n) if k!=i);C=[i]+[k for z,k in others[:s-1] if z<0]
  if info['T']:best=max(best,float(sum(y)/info['T']))
  if sum(dy[k] for k in C)<-1e-7:
   return dict(status='numerical_counterexample_needs_exact_replay',trial=t,seed=seed,s=s,b=b.tolist(),high=hi.tolist(),coalition=C,old=y.tolist(),new=yy.tolist(),delta=float(sum(dy[k] for k in C)),old_info=info,new_info=iinfo,best_ratio=best)
 return dict(status='no_failure_in_bounded_probe',trials=trials,seed=seed,best_ratio=best)
if __name__=='__main__':
 r=run();Path(__file__).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
