import json,time,numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
rng=np.random.default_rng(784017)
def solve(A,b,i,T,endpoint=False):
 r,n=A.shape;G=A@A.T;big=A.sum(axis=1)*T-b
 C=[np.hstack([G,np.diag(big)]),np.hstack([np.eye(r),-T*np.eye(r)])]
 lo=[np.full(r,-np.inf),np.full(r,-np.inf)];hi=[b+big,np.zeros(r)]
 off=np.where(A[:,i]==0)[0]
 C.append(np.hstack([G[off],np.zeros((len(off),r))]));lo.append(b[off]);hi.append(np.full(len(off),np.inf))
 if endpoint:
  C.append(np.hstack([G,-np.diag(b)]));lo.append(np.zeros(r));hi.append(np.full(r,np.inf))
 sol=milp(np.r_[-A[:,i],np.zeros(r)],integrality=np.r_[np.zeros(r),np.ones(r)],bounds=Bounds(np.zeros(2*r),np.r_[np.full(r,T),np.ones(r)]),constraints=LinearConstraint(csc_matrix(np.vstack(C)),np.concatenate(lo),np.concatenate(hi)),options={'time_limit':.5,'mip_rel_gap':1e-10})
 if sol.x is None:return None
 q=A.T@sol.x[:r]
 return {'value':float(q[i]),'q':q.tolist(),'lambda':sol.x[:r].tolist(),'flags':sol.x[r:].tolist(),'status':int(sol.status),'gap':float(sol.mip_gap)}
start=time.monotonic();tested=0
for trial in range(2000):
 n=int(rng.integers(4,9));r=int(rng.integers(8,24))
 A=rng.binomial(1,rng.uniform(.2,.8),(r,n));A=A[A.sum(axis=1)>1]
 if trial%3==0:A[:,0]=1
 A=np.unique(A,axis=0).astype(float)
 if trial%5==0:A=np.vstack([A,np.ones(n)])
 core=rng.integers(0,8,n).astype(float);core[0]=4
 b=(A@core)*rng.integers(1,11,len(A))/10
 if trial%4==0:b=A@core
 if trial%7==0:b=np.minimum(b,rng.uniform(1,5))
 lp=linprog(np.ones(n),A_ub=-A,b_ub=-b,bounds=(0,None),method='highs')
 if not lp.success:continue
 T=float(lp.fun)
 for i in range(n):
  full=solve(A,b,i,T);end=solve(A,b,i,T,True)
  if full is None or end is None:continue
  tested+=1
  if full['value']>end['value']+1e-7 and end['status']==0:
   print(json.dumps({'counter':True,'trial':trial,'owner':i,'A':A.tolist(),'b':b.tolist(),'T':T,'continuous':full,'endpoint':end}),flush=True);raise SystemExit
 if trial%10==0:print(json.dumps({'trial':trial,'tested':tested,'seconds':time.monotonic()-start}),flush=True)
 if time.monotonic()-start>480:break
print(json.dumps({'complete':True,'tested':tested,'seconds':time.monotonic()-start}),flush=True)
