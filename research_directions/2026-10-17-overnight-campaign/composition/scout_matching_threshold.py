from fractions import Fraction as Q
import random,json
import numpy as np
from scipy.optimize import linprog
rng=random.Random(17102026)
for trial in range(10000):
 n=4
 heavy=[(i,n+i) for i in range(n)]
 ordinary=[(i,n+j) for i in range(n) for j in range(n) if i!=j and rng.random()<.5]
 edges=heavy+ordinary
 c=[rng.randrange(5) for _ in range(2*n)]
 theta=[Q(rng.randrange(1,4),4) for _ in heavy]
 incidence=np.zeros((2*n,len(edges)))
 for j,(u,v) in enumerate(edges):incidence[u,j]=incidence[v,j]=1
 def value(w):
  r=linprog(-np.array(w,dtype=float),A_ub=incidence,b_ub=c,bounds=(0,None),method='highs')
  if not r.success:raise RuntimeError(r.message)
  return -r.fun,r.x.tolist()
 true,x=value([1+t for t in theta]+[1]*len(ordinary));total=0;layers=[]
 endpoints=sorted({Q(0),Q(1),*theta})
 for a,b in zip(endpoints,endpoints[1:]):
  t=(a+b)/2;w=[2 if s>=t else 1 for s in theta]+[1]*len(ordinary)
  z,flow=value(w);total+=float(b-a)*z
  layers.append({'length':str(b-a),'weights':w,'value':z,'flow':flow})
 if total>true+1e-8:
  print(json.dumps({'trial':trial,'capacity':c,'edges':edges,'heavy_premiums':list(map(str,theta)),
   'weighted_value':true,'weighted_flow':x,'layer_sum':total,'layers':layers},indent=2));break
else:print(json.dumps({'trials':trial+1,'result':'no finite counterexample'}))
