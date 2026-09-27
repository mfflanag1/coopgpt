"""Fixed matching synthesis on two-matching support, discovery plus rounded dual."""
import sys,json,time
from pathlib import Path
from itertools import product
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from universal_template import junctions,graft

def layout(m,P):
 def pairs(t):
  a,b,c=t;return ((0,a,b),(1,a,c),(2,b,c))
 support=sorted(set(e for t in [(j,j,j)for j in range(m)]+P for e in pairs(t)))
 index={e:k for k,e in enumerate(support)};used={s*m+j for t in P for s,j in enumerate(t)}
 U=[i for i in range(3*m)if i not in used]
 teams=[(t,[index[e]for e in pairs(t)if e in index])for t in product(range(m),repeat=3)]
 teams=[(t,es)for t,es in teams if es]
 return support,index,U,teams

def run(b,g):
 m,P=graft(*junctions(b),1,g);support,index,U,teams=layout(m,P)
 off=len(support);nvar=off+len(U)*3*m
 rr=[];cc=[];vv=[]
 for k,i in enumerate(U):
  for z,(t,es) in enumerate(teams):
   row=k*len(teams)+z
   for e in es:rr.append(row);cc.append(e);vv.append(1)
   for s,j in enumerate(t):rr.append(row);cc.append(off+k*3*m+s*m+j);vv.append(-1)
 A=coo_matrix((vv,(rr,cc)),shape=(len(U)*len(teams),nvar)).tocsr()
 er=[];ec=[]
 for j in range(m):
  for s in range(3):er.append(0);ec.append(index[(s,j,j)])
 for k,i in enumerate(U):
  for v in range(3*m):er.append(k+1);ec.append(off+k*3*m+v)
 E=coo_matrix((np.ones(len(er)),(er,ec)),shape=(len(U)+1,nvar)).tocsr()
 c=np.zeros(nvar)
 for a,b1,c1 in P:
  for e in ((0,a,b1),(1,a,c1),(2,b1,c1)):c[index[e]]+=1
 for k,i in enumerate(U):c[off+k*3*m+i]=1/3
 print(json.dumps({'phase':'built','m':m,'h':m-len(P),'variables':nvar,'constraints':A.shape[0]}),flush=True)
 start=time.monotonic();r=linprog(-c,A_ub=A,b_ub=np.zeros(A.shape[0]),A_eq=E,b_eq=np.ones(E.shape[0]),bounds=(0,1),options={'time_limit':180})
 if not r.success:raise RuntimeError(r.message)
 D=10**9
 cert={'m':m,'P':P,'denominator':D,'inequality_multipliers':[[k,round(-v*D)]for k,v in enumerate(r.ineqlin.marginals)if round(-v*D)>0],'equality_multipliers':[round(-v*D)for v in r.eqlin.marginals],'floating_objective':-r.fun-1,'elapsed_seconds':time.monotonic()-start,'primal_scale':3*m,'primal_integers':[round(v*3*m)for v in r.x]}
 path=Path(__file__).with_name(f'SPARSE_GRAFT_{b}_{g}.json');path.write_text(json.dumps(cert)+'\n')
 print(json.dumps({k:v for k,v in cert.items()if k not in ('P','inequality_multipliers','equality_multipliers','primal_integers')}),flush=True)
if __name__=='__main__':run(int(sys.argv[1]),int(sys.argv[2]))
