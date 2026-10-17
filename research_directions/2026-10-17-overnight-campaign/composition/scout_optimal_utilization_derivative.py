import numpy as np,itertools,random,json
from scipy.optimize import linprog
rng=random.Random(714)
for trial in range(4000):
 n=rng.randrange(6,13);all_edges=list(itertools.combinations(range(n),3));edges=rng.sample(all_edges,rng.randrange(n,min(3*n,len(all_edges))+1))
 A=np.array([[int(v in e) for e in edges] for v in range(n)],float)
 c=np.array([rng.uniform(1,6) for _ in range(n)]);m=len(edges)
 r0=linprog(-np.ones(m),A_ub=A,b_ub=c,bounds=(0,None),method='highs');F0=-r0.fun
 for j in rng.sample(range(n),min(4,n)):
  cp=c.copy();cp[j]+=0.01
  r1=linprog(-np.ones(m),A_ub=A,b_ub=cp,bounds=(0,None),method='highs');F1=-r1.fun
  if F1<=F0+1e-8:continue
  diff=A@(r1.x-r0.x);owner=[j]+[v for v in range(n) if v!=j and diff[v]<-1e-7]
  if sum(diff[owner])>=-1e-7:continue
  k=A[owner].sum(axis=0)
  lo=linprog(k,A_ub=A,b_ub=c,A_eq=[np.ones(m)],b_eq=[F0],bounds=(0,None),method='highs')
  hi=linprog(-k,A_ub=A,b_ub=cp,A_eq=[np.ones(m)],b_eq=[F1],bounds=(0,None),method='highs')
  if lo.fun+hi.fun>1e-7:
   print(json.dumps({'status':'NUMERIC_CANDIDATE','trial':trial,'edges':edges,'capacities_low':c.tolist(),'capacities_high':cp.tolist(),'owner':owner,'changed':j,'F_low':F0,'F_high':F1,'pay_low_min':lo.fun,'pay_high_max':-hi.fun,'flow_low':lo.x.tolist(),'flow_high':hi.x.tolist(),'dual_low_F':r0.ineqlin.marginals.tolist(),'dual_high_F':r1.ineqlin.marginals.tolist()},indent=2));raise SystemExit
print(json.dumps({'status':'NO_CANDIDATE','trials':4000}))
