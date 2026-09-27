"""Discovery and exact recovery in the compressed leaf-only certificate model."""
from pathlib import Path
from collections import defaultdict
import json,sys,random
from fractions import Fraction as F
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog

def structure(m,P):
 r=len(P);own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};degree=[sum(s*m+j in own for s in range(3))for j in range(m)]
 parent=list(range(r))
 def root(e):
  while parent[e]!=e:e=parent[e]
  return e
 for j in range(m):
  edges=[own[s*m+j]for s in range(3)if s*m+j in own]
  if len(edges)==2:parent[root(edges[0])]=root(edges[1])
 keys=sorted({root(e)for e in range(r)});block=[keys.index(root(e))for e in range(r)];B=len(keys);rb=[block.count(b)for b in range(B)];L=[[0]*3 for _ in range(B)];hubs=[j for j in range(m)if degree[j]==3]
 for j in range(m):
  if degree[j]==1:
   s=next(s for s in range(3)if s*m+j in own);L[block[own[s*m+j]]][s]+=1
 ports=[[block[own[s*m+j]]for s in range(3)]for j in hubs];adj=[set()for _ in range(B+len(hubs))]
 for h,bs in enumerate(ports):
  for b in bs:adj[b].add(B+h);adj[B+h].add(b)
 toward={}
 for b in range(B):
  pa={b:None};queue=[b]
  for v in queue:
   for w in adj[v]-set(pa):pa[w]=v;queue.append(w)
  if len(pa)!=len(adj):raise ValueError('disconnected block tree')
  toward[b]=[pa[B+h]for h in range(len(hubs))]
 return own,degree,block,rb,L,hubs,ports,toward

def model(m,P):
 own,degree,block,rb,L,hubs,ports,toward=structure(m,P);B=len(L);g=len(hubs)
 types=[(b,t,s)for b in range(B)for t in range(3)if L[b][t]for s in range(3)if s!=t];lookup={v:k for k,v in enumerate(types)};N=len(types);stride=2*B+g+1;n=N*stride
 def p(k,b):return k*stride+b
 def f(k,b):return k*stride+B+b
 def hub(k,h):return k*stride+2*B+h
 def z(k):return k*stride+stride-1
 rows=[];rhs=[];eq=[];erhs=[]
 def put(items,b,equality=False):
  out=defaultdict(int)
  for j,v in items:out[j]+=v
  (eq if equality else rows).append(dict(out));(erhs if equality else rhs).append(b)
 for k,(b0,t,s)in enumerate(types):
  for h,bs in enumerate(ports):
   pa=toward[b0][h]
   for b in bs:put([(p(k,b),1),(p(k,pa),-1)],0)
   for a in range(3):
    if a!=s:put([(hub(k,h),1),(p(k,bs[a]),1),(p(k,pa),-1)],0)
  for b in range(B):put([(f(k,b),1),(p(k,b),-1)],0)
  put([(z(k),1),(p(k,b0),1)],1)
  v=3-s-t;partner=lookup[b0,t,v]
  put([(z(k),-1),(p(k,b0),-1),(p(partner,b0),-1)],-1)
  put([(z(k),1)]+[(f(k,b),L[b][s])for b in range(B)]+[(hub(k,h),1)for h in range(g)]+[(p(k,b),-rb[b])for b in range(B)],0)
 for b in range(B):
  for s in range(3):
   put([(p(k,b),L[b0][t])for k,(b0,t,a)in enumerate(types)if a==s],1,True)
   if L[b][s]:
    roottypes=[lookup[b,s,a]for a in range(3)if a!=s]
    put([(f(k,b),-L[b0][t])for k,(b0,t,a)in enumerate(types)if a==s]+[(p(k,b),-1)for k in roottypes],-1)
 for h in range(g):
  for s in range(3):put([(p(k,toward[b0][h]),L[b0][t])for k,(b0,t,a)in enumerate(types)]+[(hub(k,h),-L[b0][t])for k,(b0,t,a)in enumerate(types)if a==s],4)
 bounds=[(0,1)]*n
 for k,(b0,t,s)in enumerate(types):
  for b in range(B):
   if not L[b][s]:bounds[f(k,b)]=(0,0)
 def sparse(items):
  rr=[];cc=[];vv=[]
  for i,row in enumerate(items):
   for j,v in row.items():rr.append(i);cc.append(j);vv.append(v)
  return coo_matrix((vv,(rr,cc)),shape=(len(items),n)).tocsr()
 return types,stride,rows,rhs,eq,erhs,bounds,sparse(rows),sparse(eq)

def run(name,m,P,exact=False):
 types,stride,rows,rhs,eq,erhs,bounds,A,E=model(m,P);n=len(bounds)
 result=linprog(np.zeros(n),A_ub=A,b_ub=rhs,A_eq=E,b_eq=erhs,bounds=bounds,options={'time_limit':60})
 out=dict(name=name,m=m,P=P,status=result.message,variables=n,inequalities=len(rows),leaf_counts=structure(m,P)[4])
 if result.success and exact:
  from sympy import Matrix
  from sympy.polys.matrices import DomainMatrix
  active=[j for j,v in enumerate(result.x)if v>1e-8];idx={j:k for k,j in enumerate(active)};system=[]
  def equation(row,b):system.append([row.get(j,0)for j in active]+[b])
  for row,b in zip(eq,erhs):equation(row,b)
  for row,b in zip(rows,rhs):
   if abs(sum(v*result.x[j]for j,v in row.items())-b)<1e-7:equation(row,b)
  for j in active:
   if abs(result.x[j]-1)<1e-8:equation({j:1},1)
  mat,piv=DomainMatrix.from_Matrix(Matrix(system)).rref();mat=mat.to_Matrix();q=len(active)
  if q in piv:raise ValueError('inconsistent exact active system')
  values=[F(0)]*n
  for j in active:values[j]=F(round(result.x[j]*10**9),10**9)
  free=[k for k in range(q)if k not in piv]
  for z,k in enumerate(piv):values[active[k]]=F(mat[z,q])-sum(F(mat[z,a])*values[active[a]]for a in free)
  if not all(F(lo)<=v<=F(hi)for v,(lo,hi)in zip(values,bounds)):raise ValueError('exact variable bounds')
  if not all(sum(values[j]*v for j,v in row.items())<=b for row,b in zip(rows,rhs)):raise ValueError('exact inequality')
  if not all(sum(values[j]*v for j,v in row.items())==b for row,b in zip(eq,erhs)):raise ValueError('exact equality')
  out.update(exact=True,types=types,values=[str(v)for v in values],stride=stride,active_rank=len(piv))
 Path(__file__).with_name('BLOCK_'+name+'.json').write_text(json.dumps(out)+'\n')
 print(json.dumps({k:v for k,v in out.items()if k not in ('P','values','types')}),flush=True)
 return out

def example(same,seed):
 if same:m=13;P=[(0,2,3),(1,4,2),(5,0,6),(7,8,0),(9,1,10),(11,12,1)]
 else:m=11;P=[(0,1,2),(3,0,4),(5,6,0),(1,7,8),(9,10,1)]
 block=structure(m,P)[2];rng=random.Random(seed)
 for b in range(5):
  for s in range(3):
   for _ in range(rng.randrange(4)if seed else 0):
    e=next(e for e,b1 in enumerate(block)if b1==b);old=P[e];a,c=[j for j in range(3)if j!=s];first=list(old);second=list(old);first[c]=m;second[a]=m;second[s]=m+1;m+=2;P[e]=tuple(first);P.append(tuple(second));block.append(b)
 return m,P

if __name__=='__main__':
 for same in (False,True):
  for seed in (0,1,2):run(f'{same}_{seed}',*example(same,seed),exact=True)
