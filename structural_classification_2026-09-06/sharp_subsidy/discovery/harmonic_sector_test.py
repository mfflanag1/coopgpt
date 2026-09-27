"""Sector-dependent harmonic weights with fully flexible diagonal marginals."""
from pathlib import Path
import sys,json,random
import numpy as np
from fractions import Fraction as F
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
from harmonic_exact import probabilities
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from universal_template import junctions

def random_tree(r,seed):
 rng=random.Random(seed);P=[];available=[(s,0)for s in range(3)];m=1
 for e in range(r):
  s,j=available.pop(rng.randrange(len(available)));t=[None]*3;t[s]=j
  for a in range(3):
   if a==s:continue
   t[a]=m;available.extend((b,m)for b in range(3)if b!=a);m+=1
  P.append(tuple(t))
 return m,P

def run(name,m,P):
 r=len(P);own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(own));u=len(U);h=u//3;H=probabilities(m,P)
 stride=2*m+1;nv=u*stride+4;tidx=nv-4
 def d(k,j):return k*stride+j
 def q(k,j):return k*stride+m+j
 def R(k):return k*stride+2*m
 def theta(s):return nv-3+s
 ur=[];uc=[];uv=[];ub=[];er=[];ec=[];ev=[];eb=[]
 def row(items,rhs,eq=False):
  rr,cc,vv,bb=(er,ec,ev,eb)if eq else(ur,uc,uv,ub);z=len(bb);bb.append(float(rhs))
  for col,val in items:rr.append(z);cc.append(col);vv.append(float(val))
 for k,i in enumerate(U):
  s,j0=divmod(i,m);sumh=sum(H[i]);slope=sumh-F(r,h)
  row([(R(k),1)]+[(d(k,j),1)for j in range(m)]+[(theta(s),slope)],m-1-F(r,h),True)
  row([(q(k,j),1)for j in range(m)]+[(theta(s),slope)],m-1-F(r,h))
  for j in range(m):
   e=own.get(s*m+j);offset=F(1,h)if e is not None else F(0);a=H[i][e]-offset if e is not None else F(0)
   row([(d(k,j),1),(theta(s),a)],(0 if j==j0 else 1)-offset)
   row([(d(k,j),1),(q(k,j),-1)],0)
   for z in range(3):
    if z==s:continue
    e1=own.get(z*m+j);off1=F(1,h)if e1 is not None else F(0);a1=H[i][e1]-off1 if e1 is not None else F(0)
    row([(q(k,j),1),(theta(s),a1)],1-off1)
   row([(q(k,j),1),(d(k,j),-2),(R(k),-1),(theta(s),-a)],(0 if j==j0 else -1)+offset)
 for j in range(m):
  for s in range(3):row([(q(k,j)if i//m==s else d(k,j),-1)for k,i in enumerate(U)]+[(tidx,1)],-(u-5))
 A=coo_matrix((uv,(ur,uc)),shape=(len(ub),nv)).tocsr();E=coo_matrix((ev,(er,ec)),shape=(len(eb),nv)).tocsr();obj=np.zeros(nv);obj[tidx]=-1
 bounds=[(0,1)]*nv
 for k in range(u):bounds[R(k)]=(0,m-1)
 bounds[tidx]=(0,2)
 res=linprog(obj,A_ub=A,b_ub=ub,A_eq=E,b_eq=eb,bounds=bounds,options={'time_limit':90})
 out=dict(name=name,m=m,P=P,status=res.message)
 if res.success:
  out.update(parameter=res.x[tidx],theta=res.x[-3:].tolist())
  if name=='random12_0':
   D=10**12
   cert=dict(m=m,P=P,harmonic=[[i,[str(v)for v in H[i]]]for i in U],denominator=D,inequality=[[k,round(-v*D)]for k,v in enumerate(res.ineqlin.marginals)if round(-v*D)>0],equality=[round(-v*D)for v in res.eqlin.marginals])
   Path(__file__).with_name('HARMONIC_SECTOR_NO_GO.json').write_text(json.dumps(cert)+'\n')
 Path(__file__).with_name(name+'_HSECTOR.json').write_text(json.dumps(out)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='P'}),flush=True)
 return out
if __name__=='__main__':run('random12_0',*random_tree(12,0))
