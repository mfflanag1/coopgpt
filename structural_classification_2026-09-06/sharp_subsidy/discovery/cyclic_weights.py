"""Optimize all retained pair weights for a specified cyclic obstruction."""
from pathlib import Path
import sys,json,time
from fractions import Fraction
from math import lcm
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from sparse_fixed_probe import layout

def solve(m,P,name):
 support,index,U,teams=layout(m,P)
 off=len(support);n=off+len(U)*3*m
 rr=[];cc=[];vv=[]
 for k,i in enumerate(U):
  for z,(t,es) in enumerate(teams):
   row=k*len(teams)+z
   for e in es:rr.append(row);cc.append(e);vv.append(1)
   for s,j in enumerate(t):rr.append(row);cc.append(off+k*3*m+s*m+j);vv.append(-1)
 A=coo_matrix((vv,(rr,cc)),shape=(len(U)*len(teams),n)).tocsr()
 er=[];ec=[]
 for j in range(m):
  for s in range(3):er.append(0);ec.append(index[s,j,j])
 for k in range(len(U)):
  for v in range(3*m):er.append(k+1);ec.append(off+k*3*m+v)
 E=coo_matrix((np.ones(len(er)),(er,ec)),shape=(len(U)+1,n)).tocsr()
 c=np.zeros(n)
 for a,bb,d in P:
  for e in ((0,a,bb),(1,a,d),(2,bb,d)):c[index[e]]+=1
 for k,i in enumerate(U):c[off+k*3*m+i]=1/3
 print(json.dumps(dict(phase='built',name=name,variables=n,constraints=A.shape[0])),flush=True)
 start=time.monotonic()
 r=linprog(-c,A_ub=A,b_ub=np.zeros(A.shape[0]),A_eq=E,b_eq=np.ones(E.shape[0]),bounds=(0,1),options={'time_limit':120})
 if not r.success:raise RuntimeError(r.message)
 D=10**9
 primal=[Fraction(float(v)).limit_denominator(10000) for v in r.x]
 scale=lcm(*(v.denominator for v in primal))
 cert=dict(m=m,P=P,denominator=D,inequality_multipliers=[[k,round(-v*D)]for k,v in enumerate(r.ineqlin.marginals)if round(-v*D)>0],equality_multipliers=[round(-v*D)for v in r.eqlin.marginals],floating_objective=-r.fun-1,elapsed_seconds=time.monotonic()-start,primal_scale=scale,primal_integers=[int(v*scale)for v in primal],primal_float=r.x.tolist())
 Path(__file__).with_name(f'{name}.json').write_text(json.dumps(cert)+'\n')
 print(json.dumps({k:cert[k]for k in ['m','floating_objective','elapsed_seconds']}),flush=True)
def run(b):
 m=4*b
 P=[(j,(j+1)%b,b+j) for j in range(b)]+[(2*b+2*j,2*b+2*j+1,j) for j in range(b)]
 solve(m,P,f'CYCLIC_WEIGHTS_{b}')
if __name__=='__main__':run(int(sys.argv[1]))
