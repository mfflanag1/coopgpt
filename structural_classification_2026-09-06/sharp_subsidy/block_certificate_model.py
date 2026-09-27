"""Exact block marginal constraints, without a numerical solver."""
from collections import defaultdict
from two_hub_block_certificate import structure

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
 return types,stride,rows,rhs,eq,erhs,bounds
