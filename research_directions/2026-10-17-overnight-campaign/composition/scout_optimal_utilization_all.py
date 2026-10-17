import numpy as np, itertools, random, json
from scipy.optimize import linprog
rng=random.Random(173841)
def optimize(A,c,owner):
 m=A.shape[1];res=linprog(-np.ones(m),A_ub=A,b_ub=c,bounds=(0,None),method='highs')
 if not res.success: raise RuntimeError(res.message)
 F=-res.fun;k=A[owner].sum(axis=0);out=[]
 for sign in [1,-1]:
  r=linprog(sign*k,A_ub=A,b_ub=c,A_eq=[np.ones(m)],b_eq=[F],bounds=(0,None),method='highs')
  if not r.success:raise RuntimeError(r.message)
  out.append((sign*r.fun,r.x.tolist(),r.ineqlin.marginals.tolist(),r.eqlin.marginals.tolist()))
 return F,out,res.x.tolist(),res.ineqlin.marginals.tolist()
for trial in range(12000):
 n=rng.randrange(6,12);edges=rng.sample(list(itertools.combinations(range(n),3)),rng.randrange(n,min(2*n,len(list(itertools.combinations(range(n),3))))+1))
 A=np.array([[int(v in e) for e in edges] for v in range(n)],dtype=float)
 c=np.array([rng.randrange(1,5) for _ in range(n)],dtype=float)
 owner=sorted(rng.sample(list(range(n)),rng.randrange(2,n-1)));j=rng.choice(owner)
 cp=c.copy();cp[j]+=rng.choice([1,2,3,5])
 old=optimize(A,c,owner);new=optimize(A,cp,owner)
 if old[1][0][0]>new[1][1][0]+1e-7:
  print(json.dumps({'status':'NUMERIC_CANDIDATE','trial':trial,'edges':edges,'capacities_low':c.tolist(),'capacities_high':cp.tolist(),'owner':owner,'changed':j,'low':old,'high':new},indent=2));break
else:print(json.dumps({'status':'NO_CANDIDATE','trials':12000}))
