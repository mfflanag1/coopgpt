import two_hub_blocks as tb
from pathlib import Path
import random,json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import vstack,csr_matrix

def tree(r,seed):
 rng=random.Random(seed);P=[];avail=[(s,0)for s in range(3)];m=1
 for e in range(r):
  s,j=avail.pop(rng.randrange(len(avail)));t=[None]*3;t[s]=j
  for a in range(3):
   if a!=s:t[a]=m;avail.extend((b,m)for b in range(3)if b!=a);m+=1
  P.append(tuple(t))
 return m,P
records=[]
for r in (12,24,40):
 for seed in range(40):
  m,P=tree(r,seed);g=len(tb.structure(m,P)[5])
  if g<1:continue
  types,stride,rows,rhs,eq,erhs,bounds,A,E=tb.model(m,P);L=tb.structure(m,P)[4];obj=np.zeros(len(bounds))
  for k,(b,t,s)in enumerate(types):obj[k*stride+b]=L[b][t]
  res=linprog(np.zeros(len(bounds)),A_ub=A,b_ub=rhs,A_eq=vstack([E,csr_matrix(obj.reshape(1,-1))]),b_eq=erhs+[g+2],bounds=bounds,options={'time_limit':5})
  d={'r':r,'seed':seed,'hubs':g,'status':res.status};records.append(d)
  if res.status!=0:
   free=linprog(np.zeros(len(bounds)),A_ub=A,b_ub=rhs,A_eq=E,b_eq=erhs,bounds=bounds,options={'time_limit':5});d.update(free_status=free.status,m=m,P=P)
   print(json.dumps(d),flush=True);Path(__file__).with_name('MULTIHUB_ROOT_FAILURE.json').write_text(json.dumps(d)+'\n');break
  if seed%10==0:print(r,seed,g,'tight feasible',flush=True)
 if records[-1]['status']!=0:break
Path(__file__).with_name('MULTIHUB_ROOT_RESULTS.json').write_text(json.dumps(records)+'\n');print('tested',len(records),flush=True)
