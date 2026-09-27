"""Search coefficientwise sufficient affine-over-total-count certificates."""
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
import two_hub_blocks as tb

def build(same):
 m,P=tb.example(same,0);own,degree,block,rb,L,hubs,ports,toward=tb.structure(m,P)
 types=[(b,t,s)for b in range(5)for t in range(3)for s in range(3)if s!=t];lookup={v:k for k,v in enumerate(types)}
 stride=12;nbase=30*stride;dim=16;n=nbase*dim
 def X(k,b):return k*stride+b
 def F(k,b):return k*stride+5+b
 def H(k,h):return k*stride+10+h
 def leaf(b,t):return {():L[b][t],(3*b+t,):1}
 D={():sum(map(sum,L)),**{(j,):1 for j in range(15)}}
 def times(a,b):
  out=defaultdict(int)
  for x,v in a.items():
   for y,w in b.items():out[tuple(sorted(x+y))]+=v*w
  return out
 rows=[];rhs=[];eq=[];erhs=[]
 # inequalities sum(poly*variable_numerator)<=rhs_poly*D
 def put(terms,right,equality=False):
  out=defaultdict(lambda:defaultdict(int))
  for v,poly in terms:
   for mon,c in poly.items():
    for q in range(dim):
     product=tuple(sorted(mon+(()if q==0 else(q-1,))))
     out[product][v*dim+q]+=c
  rr=times(right,D)
  for mon in set(out)|set(rr):
   row={j:v for j,v in out[mon].items()if v};b=rr.get(mon,0)
   if not row and b==0:continue
   (eq if equality else rows).append(row);(erhs if equality else rhs).append(b)
 def c(v):return {():v}
 def neg(p):return {m:-v for m,v in p.items()}
 for k,(b0,t,s)in enumerate(types):
  nk=leaf(b0,t);partner=lookup[b0,t,3-t-s]
  for b in range(5):
   put([(X(k,b),c(1))],nk)
   put([(F(k,b),c(1)),(X(k,b),c(-1))],{})
  # z=n-X_root-X_partner; enforce z>=0
  put([(X(k,b0),c(1)),(X(partner,b0),c(1))],nk)
  for h,bs in enumerate(ports):
   pa=toward[b0][h]
   for b in bs:put([(X(k,b),c(1)),(X(k,pa),c(-1))],{})
   for a in range(3):
    if a!=s:put([(H(k,h),c(1)),(X(k,bs[a]),c(1)),(X(k,pa),c(-1))],{})
  terms=[(X(k,b0),c(-1)),(X(partner,b0),c(-1))]+[(H(k,h),c(1))for h in range(2)]
  for b in range(5):
   r={():rb[b],**{(3*b+t,):1 for t in range(3)}}
   terms.extend([(X(k,b),neg(r)),(F(k,b),leaf(b,s))])
  put(terms,neg(nk))
 for b in range(5):
  for s in range(3):
   put([(X(k,b),c(1))for k,(_,_,a)in enumerate(types)if a==s],c(1),True)
   nk=leaf(b,s);roots=[lookup[b,s,a]for a in range(3)if a!=s]
   put([(F(k,b),neg(nk))for k,(_,_,a)in enumerate(types)if a==s]+[(X(k,b),c(-1))for k in roots],neg(nk))
 for h in range(2):
  for s in range(3):put([(X(k,toward[b0][h]),c(1))for k,(b0,t,a)in enumerate(types)]+[(H(k,h),c(-1))for k,(_,_,a)in enumerate(types)if a==s],c(4))
 def sparse(rs):
  ii=[];jj=[];vv=[]
  for i,r in enumerate(rs):
   for j,v in r.items():ii.append(i);jj.append(j);vv.append(v)
  return coo_matrix((vv,(ii,jj)),shape=(len(rs),n)).tocsr()
 return rows,rhs,eq,erhs,sparse(rows),sparse(eq),n
if __name__=='__main__':
 for same in (False,True):
  rows,rhs,eq,erhs,A,E,n=build(same)
  print('model',same,n,len(rows),len(eq),A.nnz,flush=True)
  r=linprog(np.zeros(n),A_ub=A,b_ub=rhs,A_eq=E,b_eq=erhs,bounds=(0,None),options={'time_limit':45})
  out={'same':same,'status':r.status,'message':r.message,'variables':n,'inequalities':len(rows),'equalities':len(eq)}
  if r.success:out['x']=r.x.tolist()
  Path(__file__).with_name('AFFINE_BLOCK_'+str(same)+'.json').write_text(json.dumps(out)+'\n');print({k:v for k,v in out.items()if k!='x'},flush=True)
