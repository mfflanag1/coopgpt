from itertools import product
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import numpy as np,json,random

def test(m,P):
 n=3*m;teams=list(product(range(m),repeat=3));used={k*m+t[k]for t in P for k in range(3)};U=sorted(set(range(n))-used);u=len(U);cols=[]
 for i in U:
  cols.extend((i,t)for t in teams if t[i//m]!=i%m)
 rr=[];cc=[];vv=[];rhs=[1]*(u*n)
 demand=[0]*(3*m*m)
 def pids(t):
  a,b,c=t;return [a*m+b,m*m+a*m+c,2*m*m+b*m+c]
 for j in range(m):
  for p in pids((j,j,j)):demand[p]+=u-4
 for t in P:
  for p in pids(t):demand[p]+=3
 rhs.extend(-x for x in demand)
 for col,(i,t)in enumerate(cols):
  base=U.index(i)*n
  for k,j in enumerate(t):rr.append(base+k*m+j);cc.append(col);vv.append(1)
  for p in pids(t):rr.append(u*n+p);cc.append(col);vv.append(-1)
 A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),len(cols))).tocsr()
 r=linprog(np.zeros(len(cols)),A_ub=A,b_ub=rhs,bounds=(0,None))
 return r.success,r.message
if __name__=='__main__':
 rng=random.Random(3890)
 for m in range(3,9):
  for it in range(30):
   r=rng.randrange(1,m-1);b=rng.sample(range(m),r);c=rng.sample(range(m),r);P=[(a,b[a],c[a])for a in range(r)]
   ok,msg=test(m,P)
   if not ok:print(json.dumps({'m':m,'P':P,'status':msg}),flush=True);raise SystemExit
  print(m,'passed 30 templates',flush=True)
