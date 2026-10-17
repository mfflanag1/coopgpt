import sys,json,numpy as np
sys.path.insert(0,'/private/tmp/coopgpt-overnight-20261017/unrestricted')
from projection_envelope_milp import diagonal
out={'tested':0,'best_squared':0,'best':None,'counter':None}
for p in [2,3,5]:
 # Projective plane over the prime field: normalized nonzero triples, dot-zero lines.
 points=[]
 for a in range(p):
  for b in range(p):
   for c in range(p):
    v=(a,b,c)
    if not any(v):continue
    first=next(x for x in v if x)
    if first==1:points.append(v)
 m=len(points);lines=[[int(sum(x*y for x,y in zip(u,v))%p==0) for v in points] for u in points]
 for c in np.linspace(0,1,21):
  A=np.array([[1]+l for l in lines]+[[1]+[int(i==j) for i in range(m)] for j in range(m)],float)
  b=np.r_[np.ones(m),np.full(m,c)]
  val=diagonal(A,b,limit=3)
  if val is None:continue
  out['tested']+=1
  if val['squared_ratio']>out['best_squared']:out['best_squared']=val['squared_ratio'];out['best']={'p':p,'c':c,'A':A.tolist(),'b':b.tolist(),**val}
  print(json.dumps({'p':p,'c':c,'sq':val['squared_ratio'],'sum':val['sum_ratio']}),flush=True)
  if val['squared_ratio']>1+1e-7:out['counter']=out['best'];break
 if out['counter']:break
print(json.dumps(out),flush=True)
