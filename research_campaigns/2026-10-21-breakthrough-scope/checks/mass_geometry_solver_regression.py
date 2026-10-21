"""Minimal normalized endpoint MILP regression; exact known feasibility is separate.
SciPy1.18.1/HiGHS presolve=True incorrectly returned objective0 on this fixture.
This checks solver behavior, not a mathematical endpoint counterexample.
"""
import json
from fractions import Fraction as F
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
A=np.array([[0,0,1,1,1],[0,1,0,0,0],[1,0,0,0,0],[1,0,0,1,0],[1,0,0,1,1],[1,0,1,0,0],[1,0,1,1,0]],dtype=int)
i=1;r,n=A.shape;G=A@A.T;dim=2*r+1
rows=[];lo=[];hi=[]
def add(x,l=None,h=None):rows.append(x);lo.append(l);hi.append(h)
x=[0]*dim;x[:r]=[1]*r;add(x,1,1)
for k in range(r):
 x=[0]*dim;x[:r]=G[k].tolist();x[r]=-1;x[r+1+k]=n;add(x,h=n)
 x=[0]*dim;x[:r]=G[k].tolist();x[r]=-1
 if not A[k,i]:add(x,l=0)
 else:x[r+1+k]=-n;add(x,l=-n)
 x=[0]*dim;x[k]=1;x[r+1+k]=-1;add(x,h=0)
known=[F(1,7),F(3,7),F(3,7)]+[F(0)]*4+[F(3,7)]+[F(1)]*3+[F(0)]*4
for row,l,h in zip(rows,lo,hi):
 lhs=sum(F(a)*b for a,b in zip(row,known))
 if l is not None and lhs<l:raise RuntimeError(('known_point_lower_failure',row,l,lhs))
 if h is not None and lhs>h:raise RuntimeError(('known_point_upper_failure',row,h,lhs))
c=np.r_[-A[:,i],np.zeros(r+1)];lb=np.zeros(dim);ub=np.ones(dim);lb[r]=1/n;ub[r]=n
output={'A':A.tolist(),'owner_zero_based':i,'known_alpha':[str(v) for v in known[:r]],'known_t':str(known[r]),'known_theta':'3/7','exact_known_feasibility':'PASS','runs':[]}
for presolve in [True,False]:
 sol=milp(c,integrality=np.r_[np.zeros(r+1),np.ones(r)],bounds=Bounds(lb,ub),constraints=LinearConstraint(np.array(rows,dtype=float),[-np.inf if v is None else v for v in lo],[np.inf if v is None else v for v in hi]),options={'presolve':presolve,'mip_rel_gap':1e-9})
 output['runs'].append({'presolve':presolve,'status':int(sol.status),'reported_objective':float(-sol.fun),'reported_gap':float(sol.mip_gap),'contradicted_by_known_feasible':bool(-sol.fun<float(F(3,7))-1e-8),'solution':sol.x.tolist()})
print(json.dumps(output))
