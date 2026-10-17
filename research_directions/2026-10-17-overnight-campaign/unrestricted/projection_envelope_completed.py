import sys,json,numpy as np
from scipy.optimize import linprog
sys.path.insert(0,'/private/tmp/coopgpt-overnight-20261017/unrestricted')
from projection_envelope_milp import diagonal
rng=np.random.default_rng(429001);out={'tested':0,'best_squared':0,'best_sum':0,'best':None,'counter':None}
for trial in range(200):
 n=int(rng.integers(3,7));r=int(rng.integers(3,12))
 sparse=rng.binomial(1,rng.uniform(.3,.8),(r,n)).astype(float);sparse=sparse[sparse.sum(axis=1)>0]
 if trial%3==0:sparse[:,0]=1
 sparse=np.unique(sparse,axis=0);dem=rng.integers(1,7,len(sparse)).astype(float)
 if trial%4==0:dem[:]=1
 A=[];b=[]
 for s in range(1,1<<n):
  row=np.array([int(s>>i&1) for i in range(n)],float);contained=np.where(np.all(sparse<=row,axis=1))[0]
  if not len(contained):continue
  lp=linprog(row,A_ub=-sparse[contained],b_ub=-dem[contained],bounds=[(0,None) if row[i] else(0,0) for i in range(n)],method='highs');assert lp.success
  if lp.fun>1e-10:A.append(row);b.append(lp.fun)
 if not A:continue
 A=np.array(A);b=np.array(b);val=diagonal(A,b,limit=2)
 if val is None:continue
 out['tested']+=1
 if val['squared_ratio']>out['best_squared']:out['best_squared']=val['squared_ratio'];out['best']={'A':A.tolist(),'b':b.tolist(),**val}
 out['best_sum']=max(out['best_sum'],val['sum_ratio'])
 if val['squared_ratio']>1+1e-7:out['counter']={'A':A.tolist(),'b':b.tolist(),**val};break
 if trial%10==0:print(json.dumps({'trial':trial,'tested':out['tested'],'best_squared':out['best_squared'],'best_sum':out['best_sum']}),flush=True)
print(json.dumps(out),flush=True)
