from pathlib import Path
from fractions import Fraction as Q
import numpy as np,json
from scipy.optimize import linprog
R=Path(__file__).parent;d=np.load(R/'decompose_failure.npz');A=d['mat'];f=d['f'];ps=d['profiles'];masks=d['masks'];n=len(f)
r=linprog(np.ones(2*n),A_ub=np.concatenate([-A.T,A.T],axis=1),b_ub=np.zeros(A.shape[1]),A_eq=np.concatenate([f,-f])[None,:],b_eq=[-1],bounds=(0,None),method='highs')
print(r.success,r.fun)
z=r.x[:n]-r.x[n:];terms=[(i,Q(float(t)).limit_denominator(10000)) for i,t in enumerate(z) if abs(t)>1e-7]
print([(list(ps[i]),str(t),f[i]) for i,t in terms])
# Exact checks on integer matrix.
assert sum(t*int(f[i]) for i,t in terms)==-1
for j in range(A.shape[1]):
 assert sum(t*int(A[i,j]) for i,t in terms)>=0
out={'statement':'No fixed nonnegative sum of same-owner same-row unit-valued subgraph production functions represents this weighted production function on all profiles', 'a':[3,0,2],'b':[3,4,5], 'terms':[{'profile_L_P_h':list(map(int,ps[i])),'weight':str(t),'weighted_value':int(f[i])} for i,t in terms], 'weighted_dot':'-1','unit_graphs_checked':len(masks),'evidence':'exact rational witness extracted from floating discovery; independent full recomputation required'}
(R/'decomposition_obstruction.json').write_text(json.dumps(out,indent=2)+'\n')
