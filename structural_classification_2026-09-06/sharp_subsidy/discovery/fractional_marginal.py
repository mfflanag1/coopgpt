from itertools import product
from pathlib import Path
import numpy as np,json
from scipy.optimize import linprog
from scipy.sparse import csr_matrix,vstack

def solve(m,P):
 n=3*m;off=3*m*m;nt=m**3;teams=list(product(range(m),repeat=3));inc=np.zeros((n,nt));pair=np.zeros((off,nt))
 for z,(a,b,c)in enumerate(teams):
  inc[[a,m+b,2*m+c],z]=1;pair[[a*m+b,m*m+a*m+c,2*m*m+b*m+c],z]=1
 used={k*m+t[k]for t in P for k in range(3)};U=sorted(set(range(n))-used)
 rows=[];rhs=[]
 for z in range(nt):rows.append(np.r_[pair[:,z],-inc[:,z],np.zeros(n)]);rhs.append(0)
 for i in U:
  row=np.zeros(off+2*n);row[off+n+i]=1;row[:off]-=pair[:,teams.index((i%m,)*3)];rows.append(row);rhs.append(0)
 eq=np.zeros((2,off+2*n));eq[0,:off]=sum(pair[:,teams.index((j,)*3)]for j in range(m));eq[1,off:off+n]=1
 obj=np.zeros(off+2*n)
 for t in P:obj[:off]-=pair[:,teams.index(t)]
 obj[off+n+np.array(U)]=-1/3
 A=csr_matrix(np.array(rows));bounds=np.ones(n)
 for iteration in range(150):
  r=linprog(obj,A_ub=A,b_ub=rhs,A_eq=eq,b_eq=[1,1],bounds=(0,None))
  if not r.success:raise ValueError(r.message)
  W=pair.T@r.x[:off];cuts=[]
  for i in U:
   cap=bounds.copy();cap[i]=0
   d=linprog(-W,A_ub=inc,b_ub=cap,bounds=(0,None))
   if not d.success:raise ValueError(d.message)
   if r.x[off+n+i]>1+d.fun+1e-8:
    cut=np.zeros(off+2*n);cut[:off]=pair@d.x;cut[off+n+i]=1;cuts.append(cut)
  if not cuts:
   return {'m':m,'P':P,'ratio':-r.fun-1,'iterations':iteration,'matrices':r.x[:off].reshape(3,m,m).tolist(),'core':r.x[off:off+n].tolist(),'claims':r.x[off+n:].tolist(),'status':'converged floating fractional-marginal relaxation'}
  A=vstack([A,csr_matrix(np.array(cuts))]);rhs.extend([1]*len(cuts))
 raise RuntimeError('cut iteration limit')
if __name__=='__main__':
 results=[]
 for q in range(1,7):
  m=2*q+1;P=[(s,q+s,s-1 if s else 2*q)for s in range(q)]
  r=solve(m,P);results.append(r);print(json.dumps({k:v for k,v in r.items()if k not in ['matrices','core','claims']}),flush=True)
  Path(__file__).with_name('FRACTIONAL_MARGINAL.json').write_text(json.dumps(results,indent=2)+'\n')
