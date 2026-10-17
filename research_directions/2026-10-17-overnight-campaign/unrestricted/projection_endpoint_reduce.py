from pathlib import Path
import json,time,numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
rng=np.random.default_rng(624103)
def solve(A,b,i,T,endpoint=False):
 r,n=A.shape;G=A@A.T;big=A.sum(axis=1)*T-b
 C=[np.hstack([G,np.diag(big)]),np.hstack([np.eye(r),-T*np.eye(r)])]
 lo=[np.full(r,-np.inf),np.full(r,-np.inf)];hi=[b+big,np.zeros(r)]
 off=np.where(A[:,i]==0)[0]
 C.append(np.hstack([G[off],np.zeros((len(off),r))]));lo.append(b[off]);hi.append(np.full(len(off),np.inf))
 if endpoint:
  C.append(np.hstack([G,-np.diag(b)]));lo.append(np.zeros(r));hi.append(np.full(r,np.inf))
 sol=milp(np.r_[-A[:,i],np.zeros(r)],integrality=np.r_[np.zeros(r),np.ones(r)],bounds=Bounds(np.zeros(2*r),np.r_[np.full(r,T),np.ones(r)]),constraints=LinearConstraint(csc_matrix(np.vstack(C)),np.concatenate(lo),np.concatenate(hi)),options={'time_limit':2,'mip_rel_gap':1e-10})
 if sol.x is None:return None
 q=A.T@sol.x[:r]
 return {'value':float(q[i]),'q':q.tolist(),'lambda':sol.x[:r].tolist(),'flags':sol.x[r:].tolist(),'status':int(sol.status),'gap':float(sol.mip_gap)}

data=json.loads(Path('/private/tmp/coopgpt-overnight-20261017/unrestricted/projection_endpoint_structured.jsonl').read_text().splitlines()[-1])
A=np.array(data['A']);b=np.array(data['b']);i=data['owner']
for keep in ([1,4,9,11],[1,4,9],[1,4,9,11,12]):
 AA=A[keep];bb=b[keep];T=linprog(np.ones(7),A_ub=-AA,b_ub=-bb,bounds=(0,None),method='highs').fun
 print(json.dumps({'keep':keep,'T':T,'continuous':solve(AA,bb,i,T),'endpoint':solve(AA,bb,i,T,True)}))
