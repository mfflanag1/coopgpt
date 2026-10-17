import numpy as np,json,itertools
from scipy.optimize import linprog
rng=np.random.default_rng(414)
for trial in range(400):
 n=int(rng.integers(3,7));d=int(rng.integers(3,8));allE=list(itertools.combinations(range(d),3));inds=rng.choice(len(allE),size=int(rng.integers(1,len(allE)+1)),replace=False);es=[allE[j]for j in inds];a=np.zeros((d,len(es)))
 for j,e in enumerate(es):a[list(e),j]=1
 b=rng.integers(0,4,(n,d));M=np.array([[s>>i&1 for i in range(n)]for s in range(1<<n)]);v=np.array([-linprog(-np.ones(len(es)),A_ub=a,b_ub=c,bounds=(0,None),method='highs').fun for c in M@b])
 u=np.array([v[-1]-v[((1<<n)-1)^(1<<i)]for i in range(n)])
 y=np.array([min(u[i],max(v[s|(1<<i)]-v[s]for s in range(1<<i)))for i in range(n)])
 viol=v-M@y
 if max(viol)>1e-7:
  print(json.dumps({'trial':trial,'n':n,'es':es,'b':b.tolist(),'v':v.tolist(),'u':u.tolist(),'y':y.tolist(),'bad':int(np.argmax(viol))}));break
else:print('no violation')
