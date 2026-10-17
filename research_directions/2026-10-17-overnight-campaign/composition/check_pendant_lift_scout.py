from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json,random
import numpy as np
from scipy.optimize import linprog
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('flow',H/'exact_huber_solver.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
edges=[(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)]
lift=[(0,7),(1,4),(1,6),(1,7),(2,4),(2,5),(3,5),(3,7)]
color=[0,0,1,2,3,4,5,5]
profiles=((0,1,1,1,0,1),(0,1,1,1,1,1),(1,0,1,1,0,1),(1,0,1,1,1,0),(1,1,0,0,1,1),(1,1,1,1,1,0))
def unit(cap,es,left):
 n=len(cap);s,t=n,n+1;f=m.ExactFlow(n+2)
 for i,c in enumerate(cap):f.add(s,i,c) if i in left else f.add(i,t,c)
 for u,v in es:f.add(u,v,sum(cap)+1)
 return f.solve(s,t)
vals=[unit([c[v] for v in color],lift,set(range(4))) for c in profiles]
print(json.dumps({'exact_six_values':vals,'functional':sum(s*v for s,v in zip((-1,1,1,-1,-1,1),vals))}))
rng=random.Random(17102026)
for eps in [1,.5,.25]:
 w=np.array([1,1,1,1,1,1+eps]);inc=np.zeros((6,6))
 for j,(u,v) in enumerate(edges):inc[u,j]=inc[v,j]=1
 result=None
 for trial in range(10000):
  c=np.array([rng.randrange(12) for i in range(6)])
  target=-linprog(-w,A_ub=inc,b_ub=c,bounds=(0,None),method='highs').fun
  lc=[Q(int(c[v])) for v in color];lc[0]*=Q(eps);lc[6]*=Q(eps)
  lifted=unit(lc,lift,set(range(4)))
  if abs(float(lifted)-target)>1e-7:
   result={'capacity':c.tolist(),'weighted':target,'lifted':str(lifted)};break
 print(json.dumps({'epsilon':eps,'trials':trial+1,'counterexample':result}))
