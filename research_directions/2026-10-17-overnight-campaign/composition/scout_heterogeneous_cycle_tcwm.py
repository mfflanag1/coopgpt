#!/usr/bin/env python3
"""Bounded finite fixed-owner lower scout; numerical LP is NOT a proof."""
from fractions import Fraction as Q
from itertools import combinations,product
from pathlib import Path
import importlib.util,ast,json,sys,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
H=Path(__file__).resolve().parent
tr=ast.parse((H/'verify_matching_premium_lift.py').read_text());ns={'__file__':str(H/'verify_matching_premium_lift.py')}
exec(compile(ast.Module(body=[z for z in tr.body if isinstance(z,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'defs','exec'),ns)
solve=ns['solve']
def corners(lo,hi):return list(product(*[sorted({a,b}) for a,b in zip(lo,hi)]))
def values(A,w,states):
 r=len(A);rows=[];rhs=[]
 for j in range(r):
  row=[0]*r;row[j]=1;rows.append(row);rhs.append(Q(0))
 for e,z in enumerate(w):rows.append([A[j][e] for j in range(r)]);rhs.append(Q(z))
 verts=[]
 for ids in combinations(range(len(rows)),r):
  p=solve([rows[j] for j in ids],[rhs[j] for j in ids])
  if p is not None and all(sum(a*b for a,b in zip(row,p))>=z for row,z in zip(rows,rhs)):verts.append(p)
 return {s:min(sum(a*b for a,b in zip(s,p)) for p in verts) for s in states}
def scout(A,w,m):
 r=len(A);states=list(product(range(m+1),repeat=r));ix={s:i for i,s in enumerate(states)}
 F=values(A,w,states);nv=2*r*len(states)+1;kappa=nv-1
 ri=[];ci=[];data=[];rhs=[]
 def var(s,j,inactive=False):return 2*r*ix[s]+2*j+int(inactive)
 def row(terms,b):
  terms={k:v for k,v in terms.items() if v}
  z=len(rhs);rhs.append(float(b))
  for k,v in terms.items():ri.append(z);ci.append(k);data.append(float(v))
 for c in states:
  terms={kappa:-F[c]}
  for j in range(r):terms[var(c,j)]=c[j];terms[var(c,j,True)]=m-c[j]
  row(terms,0)
  for a in product(*[range(z+1) for z in c]):
   if any(a):row({var(c,j):-a[j] for j in range(r)},-F[a])
  for d in product(*[range(z+1) for z in c]):
   if not any(d):continue
   after=tuple(c[j]-d[j] for j in range(r))
   for a in corners(d,c):
    for b in corners([0]*r,[m-z for z in c]):
     terms={}
     for j in range(r):
      for index,z in [(var(c,j),-a[j]),(var(c,j,True),-b[j]),(var(after,j),a[j]-d[j]),(var(after,j,True),b[j]+d[j])]:terms[index]=terms.get(index,0)+z
     row(terms,0)
 bounds=[]
 for s in states:
  for j in range(r):bounds.extend([(0,None) if s[j]>0 else (0,0),(0,None) if s[j]<m else (0,0)])
 bounds.append((0,None));objective=np.zeros(nv);objective[-1]=1
 matrix=coo_matrix((data,(ri,ci)),shape=(len(rhs),nv)).tocsr()
 start=time.time();result=linprog(objective,A_ub=matrix,b_ub=rhs,bounds=bounds,method='highs')
 return {'status':result.message,'success':result.success,'kappa':float(result.fun) if result.success else None,
  'resources':r,'fixed_owners_per_resource':m,'variables':nv,'constraints':len(rhs),'solve_seconds':time.time()-start,
  'consumption_matrix':A,'profits':w,'scope':'finite binary pure-owner profiles, full coalition payment monotonicity, numerical only'}
cases=[([[1,0,1],[1,1,0],[0,1,1]],[1,1,1]),
 ([[2,0,1],[1,2,0],[0,1,2]],[1,1,1]),
 ([[10,0,1],[1,10,0],[0,1,10]],[1,1,1]),
 ([[2,0,1],[1,3,0],[0,1,5]],[1,1,1]),
 ([[2,0,1],[1,3,0],[0,1,5]],[1,2,4])]
for A,w in cases:
 print(json.dumps(scout(A,w,3)),flush=True)
