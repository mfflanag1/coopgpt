import sys,json,numpy as np
sys.path.insert(0,'/private/tmp/coopgpt-overnight-20261017/unrestricted')
from projection_envelope_milp import diagonal
out={'tested':0,'best_squared':0,'best_sum':0,'best':None,'counter':None}
for z in [np.array([.5,.5,0.,0.]),np.array([2/3,1/3,0.,0.])]:
 n=len(z);rows=np.array([[int(s>>i&1) for i in range(n)] for s in range(1,(1<<n)-1)],float);rows=rows[rows@z>0]
 for pattern in range(1<<len(rows)):
  A=np.array([rows[j] for j in range(len(rows)) if pattern>>j&1]+[np.ones(n)]);b=A@z
  val=diagonal(A,b,limit=2)
  if val is None:continue
  out['tested']+=1
  if val['squared_ratio']>out['best_squared']:
   out['best_squared']=val['squared_ratio'];out['best']={'A':A.tolist(),'b':b.tolist(),**val}
  out['best_sum']=max(out['best_sum'],val['sum_ratio'])
  if val['squared_ratio']>1+1e-7:
   out['counter']={'A':A.tolist(),'b':b.tolist(),**val};break
  if pattern%200==0:print(json.dumps({'core':z.tolist(),'pattern':pattern,'tested':out['tested'],'best_squared':out['best_squared'],'best_sum':out['best_sum']}),flush=True)
 if out['counter']:break
print(json.dumps(out),flush=True)
