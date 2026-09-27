from itertools import product
from fractions import Fraction as F
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
P=(1,2,0);U=[0,2,3,4,7,8]
def pairs(t):
 a,b,c=t;return ((0,a,b),(1,a,c),(2,b,c))
edges=sorted({e for t in [(j,j,j) for j in range(3)]+[P] for e in pairs(t)})
idx={e:k for k,e in enumerate(edges)};off=len(edges);n=off+54
A=[];E=[]
row=np.zeros(n)
for j in range(3):
 for p in range(3):row[idx[p,j,j]]=1
E.append(row)
for k,i in enumerate(U):
 row=np.zeros(n);row[off+9*k:off+9*(k+1)]=1;E.append(row)
 for t in product(range(3),repeat=3):
  row=np.zeros(n)
  for e in pairs(t):
   if e in idx:row[idx[e]]+=1
  for s,j in enumerate(t):row[off+9*k+s*3+j]-=1
  A.append(row)
A=np.array(A);E=np.array(E)
def probe(coef):
 objective=np.zeros(n)
 for e in pairs(P):objective[idx[e]]+=1
 for k,i in enumerate(U):objective[off+k*9+i]+=1/3
 for p in range(3):objective[idx[p,0,0]]-=float(coef)
 sol=linprog(-objective,A_ub=A,b_ub=np.zeros(len(A)),A_eq=E,b_eq=np.ones(len(E)),bounds=(0,None),method='highs')
 if not sol.success:raise RuntimeError(sol.message)
 x=[F(float(v)).limit_denominator(1000000) for v in sol.x]
 # Exact primal checks: valid witnesses give a lower bound even without attainment certification.
 if min(x)<0:raise ValueError('negative primal')
 for row in A:
  if sum(F(int(a))*b for a,b in zip(row,x))>0:raise ValueError('team failure')
 for row in E:
  if sum(F(int(a))*b for a,b in zip(row,x))!=1:raise ValueError('total failure')
 y=[F(-float(v)).limit_denominator(1000000) for v in sol.ineqlin.marginals]
 z=[F(-float(v)).limit_denominator(1000000) for v in sol.eqlin.marginals]
 target=[F(0)]*n
 for e in pairs(P):target[idx[e]]+=1
 for k,i in enumerate(U):target[off+k*9+i]+=F(1,3)
 for p in range(3):target[idx[p,0,0]]-=coef
 if min(y)<0:raise ValueError('negative dual')
 residual=[sum(F(int(A[r,j]))*y[r] for r in range(len(A)))+sum(F(int(E[r,j]))*z[r] for r in range(len(E)))-target[j] for j in range(n)]
 if min(residual)<0:raise ValueError('dual failure')
 J=sum(x[idx[e]] for e in pairs(P))+sum(x[off+k*9+i] for k,i in enumerate(U))/3-1
 d0=sum(x[idx[p,0,0]] for p in range(3))
 return {'coefficient':str(coef),'objective':str(J-coef*d0),'J_witness':str(J),'d0':str(d0),'primal':list(map(str,x)),'edges':[list(e) for e in edges],'numerical_optimum':-sol.fun-1,'dual_upper':str(sum(z)-1),'dual_y':list(map(str,y)),'dual_z':list(map(str,z))}
if __name__=='__main__':
 import sys
 coefs=[F(a) for a in sys.argv[1:]] or [F(17,18)]
 result=[probe(c) for c in coefs]
 print(json.dumps(result,indent=2))
