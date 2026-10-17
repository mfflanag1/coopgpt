from math import exp,log
from itertools import product,combinations
from random import Random
from pathlib import Path
import json
lo,hi=.5,1.
for _ in range(100):
 c=(lo+hi)/2
 if c*(2-exp(-1/c))<1:lo=c
 else:hi=c
K=(lo+hi)/2;T=1-exp(-1/K)
def binary(A,B):
 # prices, Jacobian wrt A,B
 if A<=B:
  t=A/B
  if t>=T:q=K/t;dq=-K/t**2
  else:q=1-K-K*(1-t)*log(1-t)/t;dq=K*(log(1-t)+t)/t**2
  # shortA q; longB Kt
  return [q,K*t],[[dq/B,-dq*t/B],[K/B,-K*t/B]]
 else:
  p,J=binary(B,A)
  return p[::-1],[[J[1][1],J[1][0]],[J[0][1],J[0][0]]]
def rule(C):
 P,*v=C;high=max(range(3),key=lambda j:v[j]);rest=[j for j in range(3) if j!=high]
 # uniform-rank2 principal partition: high singleton iff high>sum rest
 groups=[([high],1),(rest,1)] if v[high]>sum(v[j] for j in rest) else [([0,1,2],2)]
 q=[0.]*4;J=[[0.]*4 for _ in C]
 for group,r in groups:
  p,jac=binary(r*P,sum(v[j] for j in group));q[0]+=r*p[0]
  J[0][0]+=r*r*jac[0][0]
  for j in group:q[j+1]+=p[1];J[0][j+1]+=r*jac[0][1];J[j+1][0]+=r*jac[1][0]
  for j in group:
   for k in group:J[j+1][k+1]+=jac[1][1]
 return q,J,groups
rng=Random(51017);best=(1e9,None)
for z in range(10000):
 C=[exp(rng.uniform(-4,4)) for j in range(4)];q,J,groups=rule(C)
 for mask in range(16):
  a=[C[j] if mask>>j&1 else 0 for j in range(4)]
  w=[q[j]+sum(a[k]*J[k][j] for k in range(4)) for j in range(4)]
  for size in [1,2]:
   for g in combinations(range(1,4),size):
    slack=w[0]+sum(w[j] for j in g)-size
    if slack<best[0]:best=(slack,dict(C=C,a=a,w=w,group=g,groups=groups))
 if best[0]<-.0001:break
out={'c':K,'t0':T,'best':best,'numerical_scout_only':True,'profiles':z+1}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
