"""Discovery only: optimize the proved transportation marginal conditions."""
from pathlib import Path
import sys,json
from fractions import Fraction as F
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from universal_template import junctions

def run(b,local):
 from harmonic_sector_test import random_tree
 m,P=junctions(b);r=len(P);owner={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(owner));u=len(U)
 stride=r+2*m+1;nv=u*stride+2;tidx=nv-2;bidx=nv-1
 def p(k,e):return k*stride+e
 def d(k,j):return k*stride+r+j
 def q(k,j):return k*stride+r+m+j
 def R(k):return k*stride+stride-1
 ur=[];uc=[];uv=[];ub=[];er=[];ec=[];ev=[];eb=[]
 def row(items,rhs,eq=False):
  rr,cc,vv,bb=(er,ec,ev,eb)if eq else(ur,uc,uv,ub);z=len(bb);bb.append(rhs)
  for col,val in items:rr.append(z);cc.append(col);vv.append(val)
 for k,i in enumerate(U):
  s,j0=divmod(i,m)
  degree=[sum(a*m+j in owner for a in range(3))for j in range(m)]
  row([(p(k,e),sum(degree[j]==1 and a!=s for a,j in enumerate(team)))for e,team in enumerate(P)],1,True)
  adj=[set()for _ in range(m+r)]
  for e,team in enumerate(P):
   for j in team:adj[j].add(m+e);adj[m+e].add(j)
  parent={j0:None};queue=[j0]
  for j in queue:
   for v in adj[j]:
    if v not in parent:parent[v]=j;queue.append(v)
  for j in range(m):
   if j!=j0:row([(d(k,j),1),(p(k,parent[j]-m),1)],1,True)
  row([(R(k),1)]+[(p(k,e),1)for e in range(r)]+[(d(k,j),1)for j in range(m)],m-1,True)
  row([(q(k,j),1)for j in range(m)]+[(p(k,e),1)for e in range(r)],m-1)
  for j in range(m):
   source=owner.get(s*m+j)
   row([(d(k,j),1)]+([(p(k,source),1)]if source is not None else[]),0 if j==j0 else 1)
   row([(d(k,j),1),(q(k,j),-1)],0)
   for a in range(3):
    if a==s:continue
    e=owner.get(a*m+j);row([(q(k,j),1)]+([(p(k,e),1)]if e is not None else[]),1)
   row([(q(k,j),1),(d(k,j),-2),(R(k),-1)]+([(p(k,source),-1)]if source is not None else[]),0 if j==j0 else -1)
  if local:
   for e,team in enumerate(P):
    count=sum(v%m in team for v in U);adj=j0 in team;coef=1-u/count if adj else 1;constant=3/count if adj else 0
    row([(p(k,e),1),(bidx,-coef)],constant,True)
 for e in range(r):
  for s in range(3):row([(p(k,e),1)for k,i in enumerate(U)if i//m==s],1,True)
 for j in range(m):
  for s in range(3):row([(q(k,j)if i//m==s else d(k,j),-1)for k,i in enumerate(U)]+[(tidx,1)],-(u-5))
 A=coo_matrix((uv,(ur,uc)),shape=(len(ub),nv)).tocsr();E=coo_matrix((ev,(er,ec)),shape=(len(eb),nv)).tocsr();obj=np.zeros(nv);obj[tidx]=-1
 bounds=[(0,None)]*nv;bounds[tidx]=(0,2);bounds[bidx]=(0,3/u)
 res=linprog(obj,A_ub=A,b_ub=ub,A_eq=E,b_eq=eb,bounds=bounds,options={'time_limit':120})
 out={'junctions':b,'m':m,'local':local,'status':res.message,'variables':nv,'constraints':len(ub)+len(eb)}
 if res.success:
  out.update(parameter=float(res.x[tidx]),baseline=float(res.x[bidx]))
  if b==2:
   cert={'m':m,'P':P,'rows':[[i,[str(F(float(res.x[p(k,e)])).limit_denominator(1000000))for e in range(r)],[str(F(float(res.x[d(k,j)])).limit_denominator(1000000))for j in range(m)],[str(F(float(res.x[q(k,j)])).limit_denominator(1000000))for j in range(m)]]for k,i in enumerate(U)]}
   Path(__file__).with_name('STATIONARY_SEED.json').write_text(json.dumps(cert)+'\n')
  if local:
   D=10**12;cert={'m':m,'P':P,'denominator':D,'inequality':[[j,round(-v*D)]for j,v in enumerate(res.ineqlin.marginals)if round(-v*D)>0],'equality':[round(-v*D)for v in res.eqlin.marginals]}
   Path(__file__).with_name(f'MARGINAL_LOCAL_{b}_DUAL.json').write_text(json.dumps(cert)+'\n')
 path=Path(__file__).with_name(f'STATIONARY_BALANCED_{b}.json');path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
if __name__=='__main__':
 for b in (2,):run(b,False)
