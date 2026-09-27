"""Recover an exact feasible point from a numerically chosen active basis."""
from itertools import product
from fractions import Fraction as F
from pathlib import Path
import json,numpy as np
from scipy.optimize import linprog
from scipy.linalg import qr
from scipy.sparse import coo_matrix
from sympy import Matrix
from verify_deletion import check

def run():
 m=11;P=[(0,1,2),(3,0,4),(5,6,0),(1,7,8),(9,10,1)];n=3*m
 used={k*m+t[k]for t in P for k in range(3)};U=sorted(set(range(n))-used);u=len(U)
 cols=[(i,t)for i in U for t in product(range(m),repeat=3)if t[i//m]!=i%m]
 def pids(t):
  a,b,c=t;return[a*m+b,m*m+a*m+c,2*m*m+b*m+c]
 demand=[0]*(3*m*m)
 for j in range(m):
  for p in pids((j,)*3):demand[p]+=u-4
 for t in P:
  for p in pids(t):demand[p]+=3
 rr=[];cc=[];vv=[];rhs=[1]*(u*n)+[-d for d in demand]
 for j,(i,t)in enumerate(cols):
  for k,v in enumerate(t):rr.append(U.index(i)*n+k*m+v);cc.append(j);vv.append(1)
  for p in pids(t):rr.append(u*n+p);cc.append(j);vv.append(-1)
 A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),len(cols))).tocsr()
 r=linprog(np.ones(len(cols)),A_ub=A,b_ub=rhs,bounds=(0,None))
 if not r.success:raise ValueError(r.message)
 support=np.flatnonzero(r.x>1e-9);active=np.flatnonzero(np.abs(r.ineqlin.residual)<1e-7)
 Q,R,piv=qr(A[active][:,support].toarray().T,mode='economic',pivoting=True)
 k=len(support)
 if R.shape[0]<k or min(abs(np.diag(R)[:k]))<1e-9:raise ValueError('active basis is rank deficient')
 selected=active[piv[:k]]
 M=Matrix(A[selected][:,support].toarray().astype(int).tolist()).to_DM()
 b=Matrix([rhs[j]for j in selected]).to_DM()
 print('Exact basis dimension',k,flush=True)
 num,den=M.solve_den(b);values=num.to_Matrix()/int(den)
 out=[]
 for col,v in zip(support,values):
  if v<0:raise ValueError('negative exact variable')
  if v:out.append([cols[col][0],list(cols[col][1]),str(v)])
 d={'m':m,'P':P,'packings':out,'method':'exact DomainMatrix active-basis solve; independently verified all inequalities'}
 check(d)
 Path(__file__).with_name('DOUBLE_JUNCTION_DELETION.json').write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps({'status':'EXACT PASS','entries':len(out),'common_denominator_digits':len(str(den))}),flush=True)
if __name__=='__main__':run()
