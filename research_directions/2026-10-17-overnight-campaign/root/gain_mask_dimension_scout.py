"""Numerical scout only: closed-mask gain cost versus resource dimension."""
import numpy as np,json
from pathlib import Path
rng=np.random.default_rng(172032)
records=[]
best=None
for d in [2,3,4,5]:
 for n in [6,9,12]:
  masks=((np.arange(1<<n)[:,None]>>np.arange(n))&1).astype(float)
  for rep in range(30):
   b=rng.lognormal(0,2,(n,d))
   if rep%3==0:b*=rng.random((n,d))>.45
   forms=rng.lognormal(0,2,(20,d))
   raw=b@forms.T;fi=raw.min(axis=1)
   sums=masks@raw;selected=sums.argmin(axis=1)
   F=raw.sum(axis=0).min();G=F-fi.sum()
   if G<=1e-12:continue
   # Fixed priority minimizing form; all forms touch their own profile min.
   price=raw[:,selected].T
   excess=np.minimum(np.maximum(price-fi[None,:],0),G)
   c=((1-masks)*excess).sum(axis=1)
   opened=masks.sum(axis=1)
   for q in [.01,.03,.1,.2,.4,.6]:
    weights=q**(n-opened)*(1-q)**opened
    C=float(weights@c)
    ratio=C/(2*d*q/(1-q)*G)
    rec={'d':d,'n':n,'rep':rep,'q':q,'ratio':ratio}
    records.append(rec)
    if best is None or ratio>best['ratio']:
     best=rec
     if ratio>1+1e-8:
      print(json.dumps({'counterexample':rec,'b':b.tolist(),'forms':forms.tolist()}));raise SystemExit
 print(json.dumps({'done_d':d,'best':best}),flush=True)
Path(__file__).with_suffix('.json').write_text(json.dumps({'status':'finite_scout_only','cases':len(records),'best':best},indent=2))
