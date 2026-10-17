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

A=np.array([[0,1,0,1],[1,0,1,1],[1,1,0,0],[1,1,0,1]],float);b=np.array([3,3,2,5],float)
fullA=np.array([[int(s>>i&1) for i in range(4)] for s in range(1,16)],float)
fullb=[]
for row in fullA:
 ids=np.where(row)[0];ok=np.where(np.all(A<=row,axis=1))[0]
 val=linprog(np.ones(len(ids)),A_ub=-A[ok][:,ids],b_ub=-b[ok],bounds=(0,None),method='highs')
 fullb.append(val.fun)
fullb=np.array(fullb)
print(json.dumps({'A':fullA.tolist(),'b':fullb.tolist(),'continuous':solve(fullA,fullb,3,5),'endpoint':solve(fullA,fullb,3,5,True)}))
