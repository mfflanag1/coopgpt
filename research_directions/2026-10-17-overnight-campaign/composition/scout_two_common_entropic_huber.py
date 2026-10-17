"""Bounded numerical falsification only; no mechanism theorem."""
import numpy as np
from pathlib import Path
import json
rng=np.random.default_rng(45321);best=None;valid=0
for trial in range(50000):
 m=int(rng.integers(2,16));a=rng.beta(.4,.4,m);pcommon=np.exp(rng.uniform(-4,.7,2));priv=1-a*pcommon[0]-(1-a)*pcommon[1]
 if np.any(priv<=1e-5):continue
 p=np.r_[pcommon,priv];hp=np.where(p<.5,p/(1-p),1);hpp=np.where(p<.5,1/(1-p)**2,0)
 lam=np.exp(rng.uniform(-5,5,m));c=np.r_[a@lam,(1-a)@lam,lam]/hp
 B=np.vstack((np.eye(2),-np.c_[a,1-a]));H=B.T@((c*hpp)[:,None]*B)
 if np.linalg.det(H)<1e-12:continue
 K=B@np.linalg.inv(H)@B.T;score=p-hp*(c[:,None]*np.maximum(K,0)).sum(axis=0);valid+=1
 val=float(score.min())
 if best is None or val<best['minimum']:
  best={'minimum':val,'trial':trial,'resource':int(score.argmin()),'a':a.tolist(),'prices':p.tolist(),'capacities':c.tolist(),'multipliers':lam.tolist()}
 if val < -1e-6:break
out={'scope':'numerical local candidate falsification only','valid_profiles':valid,'witness':best}
Path(__file__).with_name('TWO_COMMON_ENTROPIC_HUBER_SCOUT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
