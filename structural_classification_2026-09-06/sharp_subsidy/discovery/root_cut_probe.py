"""Discovery only: optimize the proved transportation marginal conditions."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from universal_template import junctions

def run(name,m,P):
 r=len(P);owner={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(owner));u=len(U)
 stride=r+2*m+3;nv=u*stride+2;tidx=nv-2;bidx=nv-1
 def p(k,e):return k*stride+e
 def d(k,j):return k*stride+r+j
 def q(k,j):return k*stride+r+m+j
 def R(k):return k*stride+r+2*m
 def base(k):return k*stride+r+2*m+1
 def tilt(k):return k*stride+r+2*m+2
 ur=[];uc=[];uv=[];ub=[];er=[];ec=[];ev=[];eb=[]
 def row(items,rhs,eq=False):
  rr,cc,vv,bb=(er,ec,ev,eb)if eq else(ur,uc,uv,ub);z=len(bb);bb.append(rhs)
  for col,val in items:rr.append(z);cc.append(col);vv.append(val)
 for k,i in enumerate(U):
  s,j0=divmod(i,m)
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
  for e,team in enumerate(P):
   blocked=m+e;seen={j0};todo=[j0]
   for vertex in todo:
    for neighbor in adj[vertex]:
     if neighbor!=blocked and neighbor not in seen:seen.add(neighbor);todo.append(neighbor)
   count=sum(v%m in seen for v in U)
   row([(p(k,e),1),(base(k),-1),(tilt(k),-1/count)],0,True)

 for e in range(r):row([(p(k,e),1)for k in range(u)],3,True)
 for j in range(m):
  for s in range(3):row([(q(k,j)if i//m==s else d(k,j),-1)for k,i in enumerate(U)]+[(tidx,1)],-(u-5))
 A=coo_matrix((uv,(ur,uc)),shape=(len(ub),nv)).tocsr();E=coo_matrix((ev,(er,ec)),shape=(len(eb),nv)).tocsr();obj=np.zeros(nv);obj[tidx]=-1
 bounds=[(0,None)]*nv;bounds[tidx]=(0,2);bounds[bidx]=(0,3/u)
 res=linprog(obj,A_ub=A,b_ub=ub,A_eq=E,b_eq=eb,bounds=bounds,options={'time_limit':120})
 out={'name':name,'m':m,'P':P,'status':res.message,'variables':nv,'constraints':len(ub)+len(eb)}
 if res.success:out.update(parameter=float(res.x[tidx]),base=[float(res.x[base(k)])for k in range(u)],tilt=[float(res.x[tilt(k)])for k in range(u)])
 Path(__file__).with_name('ROOT_CUT_'+name+'.json').write_text(json.dumps(out)+'\n')
 print(json.dumps({k:v for k,v in out.items()if k not in ('P','base','tilt')}),flush=True)
if __name__=='__main__':
 from harmonic_sector_test import random_tree
 run('random12_0',*random_tree(12,0))
 run('junction8',*junctions(8))
 run('chain24',49,[(25+j,j,j+1)for j in range(24)])
