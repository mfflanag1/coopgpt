import numpy as np,json,time
from scipy.optimize import milp,linprog,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
rng=np.random.default_rng(704211)
def diagonal(A,b,limit=2):
 n=A.shape[1];r=len(b)
 lp=linprog(np.ones(n),A_ub=-A,b_ub=-b,bounds=(0,None),method='highs')
 if not lp.success or lp.fun<=1e-10:return None
 T=float(lp.fun);G=A@A.T;big=A.sum(axis=1)*T-b
 # q=A^T lambda; active row j (z_j=1) has q(S_j)<=b_j.
 C1=np.hstack([G,np.diag(big)]);C2=np.hstack([np.eye(r),-T*np.eye(r)])
 C=np.vstack([C1,C2]);lo=np.full(2*r,-np.inf);hi=np.r_[b+big,np.zeros(r)]
 Ms=[];witness=[]
 for i in range(n):
  off=np.where(A[:,i]==0)[0]
  cc=np.vstack([C,np.hstack([G[off],np.zeros((len(off),r))])])
  ll=np.r_[lo,b[off]];hh=np.r_[hi,np.full(len(off),np.inf)]
  sol=milp(np.r_[-A[:,i],np.zeros(r)],integrality=np.r_[np.zeros(r),np.ones(r)],bounds=Bounds(np.zeros(2*r),np.r_[np.full(r,T),np.ones(r)]),constraints=LinearConstraint(csc_matrix(cc),ll,hh),options={'time_limit':limit,'mip_rel_gap':1e-9})
  if sol.x is None:return None
  lam=sol.x[:r];q=A.T@lam;active=np.where(lam>1e-7)[0]
  if np.max(b[off]-A[off]@q,initial=0)>1e-6 or np.max(A[active]@q-b[active],initial=0)>1e-6:return None
  Ms.append(float(q[i]));witness.append({'q':q.tolist(),'lambda':lam.tolist(),'status':int(sol.status),'gap':float(sol.mip_gap)})
 return {'T':T,'core':lp.x.tolist(),'M':Ms,'squared_ratio':sum(x*x for x in Ms)/T**2,'sum_ratio':sum(Ms)/(np.sqrt(n)*T),'witnesses':witness}
if __name__=='__main__':
 out={'tested':0,'best_squared':0,'best_sum':0,'best':None,'counter':None}
 for trial in range(1000):
  n=int(rng.integers(3,13));r=int(rng.integers(3,min(22,2*n+6)))
  A=rng.binomial(1,rng.uniform(.15,.85),size=(r,n)).astype(float)
  A=A[A.sum(axis=1)>0]
  if trial%3==0:A[:,0]=1
  if trial%5==0:A=np.vstack([A,np.ones(n)])
  A=np.unique(A,axis=0);b=rng.integers(1,9,len(A)).astype(float)
  if trial%4==0:b[:]=1
  val=diagonal(A,b)
  if val is None:continue
  out['tested']+=1
  if val['squared_ratio']>out['best_squared']:
   out['best_squared']=val['squared_ratio'];out['best']={'A':A.tolist(),'b':b.tolist(),**val}
  out['best_sum']=max(out['best_sum'],val['sum_ratio'])
  if val['squared_ratio']>1+1e-7:
   out['counter']={'A':A.tolist(),'b':b.tolist(),**val};break
  if trial%20==0:print(json.dumps({'trial':trial,'tested':out['tested'],'best_squared':out['best_squared'],'best_sum':out['best_sum']}),flush=True)
 print(json.dumps(out),flush=True)
