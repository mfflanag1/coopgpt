from pathlib import Path
import numpy as np,json
from scipy.optimize import milp,LinearConstraint,Bounds
R=Path(__file__).parent;d=np.load(R/'decompose_failure.npz');A=d['mat'];f=d['f'];ps=d['profiles'];n=len(f)
B=np.concatenate([A.T,-A.T],axis=1);ff=np.concatenate([f,-f])[None,:]
r=milp(np.ones(2*n),integrality=np.ones(2*n),bounds=Bounds(np.zeros(2*n),np.full(2*n,8)),constraints=[LinearConstraint(B,np.zeros(A.shape[1]),np.full(A.shape[1],np.inf)),LinearConstraint(ff,-np.inf,-1)],options={'time_limit':25})
print(r.message, r.fun)
if r.x is not None:
 z=np.rint(r.x[:n]-r.x[n:]).astype(int)
 print([(list(ps[i]),int(t),f[i]) for i,t in enumerate(z) if t])
 print('dot',f@z,'minunit',(A.T@z).min())
 out={'status':r.message,'terms':[{'profile_L_P_h':list(map(int,ps[i])),'weight':str(int(t)),'weighted_value':int(f[i])} for i,t in enumerate(z) if t],'weighted_dot':int(f@z)}
 (R/'decomposition_obstruction_simplified_discovery.json').write_text(json.dumps(out,indent=2)+'\n')
