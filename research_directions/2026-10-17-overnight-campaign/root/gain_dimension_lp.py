"""Finite original-resource concave-homogeneous gain dimension scout; no proof."""
import sys,json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
rng=np.random.default_rng(172031)
results=[]
for d in range(2,7):
 for n in [d+1,2*d,3*d]:
  for rep in range(12):
   b=rng.integers(0,8,(n,d)).astype(float)
   if np.any(b.sum(axis=0)==0):continue
   C=b.sum(axis=0); X=np.vstack([C,b,C-b]); m=len(X)
   # Variables values v_p and own nonnegative supporting rows a_p.
   obj=np.zeros(m+m*d);obj[1:n+1]=-(d-1);obj[n+1:]=1
   obj[m:]=0
   eq=[];rhs=[]
   for p in range(m):
    row=np.zeros(len(obj));row[p]=-1;row[m+p*d:m+(p+1)*d]=X[p]
    eq.append(row);rhs.append(0)
   row=np.zeros(len(obj));row[0]=1;eq.append(row);rhs.append(1)
   ub=[]
   for p in range(m):
    for q in range(m):
     if p==q:continue
     row=np.zeros(len(obj));row[q]=1;row[m+p*d:m+(p+1)*d]=-X[q];ub.append(row)
   res=linprog(obj,A_ub=np.array(ub),b_ub=np.zeros(len(ub)),A_eq=np.array(eq),b_eq=rhs,bounds=(0,None),method='highs')
   if not res.success:raise RuntimeError(res.message)
   violation=n-d-res.fun
   results.append({'d':d,'n':n,'rep':rep,'violation':violation})
   if violation>1e-7:
    out={'status':'candidate_counterexample','d':d,'n':n,'b':b.tolist(),'values':res.x[:m].tolist(),'support':res.x[m:].reshape(m,d).tolist(),'violation':violation}
    print(json.dumps(out),flush=True)
    Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2));sys.exit(0)
 print(json.dumps({'d_done':d,'max_violation':max(x['violation'] for x in results if x['d']==d)}),flush=True)
Path(__file__).with_suffix('.json').write_text(json.dumps({'status':'finite_scout_no_counterexample','runs':results},indent=2))
