import sys,json
import numpy as np
sys.path.insert(0,'/Users/maxf/.codex/visualizations/2026/09/04/01a06e8a-dcbb-7c81-9929-e72831a14ac8/research-campaigns/2026-10-24-risk-geometry')
from explore import calc,P
results=[]
for m in [2,3,4,5,6]:
 for a in [1,2,3,4,6,8,12]:
  for b in [1,2,3]:
   A=np.array([[a,0]]+[[0,b]]*m+[[-a,-m*b]])
   z=calc(A)
   if z['rho']>1e-8:z.update(family='orthogonal',m=m,a=a,b=b);results.append(z)
for a in [1,2,3]:
 for b in [1,2,3]:
  for c in [-2,-1,1,2]:
   for d in [0,1,2]:
    A=np.array([[a,b],[a,-b],[c,d],[c,-d],[-2*a-2*c,0]])
    z=calc(A)
    if z and z['rho']>1e-8:z.update(family='reflection',params=[a,b,c,d]);results.append(z)
results.sort(key=lambda z:z['rho'],reverse=True)
(P/'structured_exploration.json').write_text(json.dumps({'evidence':'exploratory adaptive search after initial output','results':results},indent=2)+'\n')
for z in results[:5]:print(json.dumps(z))
print('separated',len(results))
