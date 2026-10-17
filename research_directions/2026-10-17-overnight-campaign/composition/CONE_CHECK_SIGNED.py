"""Exact rational tests of cone-order reports; not a replacement for the cone proof."""
from fractions import Fraction as Q
from itertools import product
from math import comb
from random import Random
from pathlib import Path
import json
rng=Random(2610170710)
counts=dict(profiles=0,mask_coverage=0,individual_out=0,grand_rank=0,low_rank_sampling=0)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def add(rows,d):return [sum(row[j] for row in rows) for j in range(d)]
def forms(m):
 out=[]
 for j in range(m):
  for sign in [-1,1]:
   x=[Q(0)]*(m+1);x[0]=1;x[j+1]=sign;out.append(x)
 return out
def rank(rows):
 a=[list(row) for row in rows];k=0
 for j in range(len(a[0])):
  p=next((i for i in range(k,len(a)) if a[i][j]),None)
  if p is None:continue
  a[k],a[p]=a[p],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
  for i in range(len(a)):
   if i!=k:
    v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
  k+=1
  if k==len(a):break
 return k
def weights(n,k,a):return sum((-1)**ell*comb(k,ell)*a**(n-k+ell)/Q(n-k+ell+1) for ell in range(k+1))
def rule(rows,ff,mask):
 n=len(rows);d=len(rows[0]);C=add(rows,d);f=lambda x:min(dot(p,x) for p in ff);T=f(C);own=list(map(f,rows));G=T-sum(own)
 CB=add([rows[i] for i in range(n) if mask>>i&1],d);p=min(ff,key=lambda z:dot(z,CB));y=[]
 for i,b in enumerate(rows):
  y.append(f(CB)-f([x-z for x,z in zip(CB,b)]) if mask>>i&1 else min(dot(p,b),own[i]+G))
 return y
def mixture(rows,ff,a):
 n=len(rows);y=[Q(0)]*n
 for mask in range(1<<n):
  w=weights(n,mask.bit_count(),a)
  for i,x in enumerate(rule(rows,ff,mask)):y[i]+=w*x
 return y
def bundle(m):
 e=[Q(rng.randrange(-7,8),rng.randrange(1,4)) for _ in range(m)]
 return [max(map(abs,e))+Q(rng.randrange(4),3)]+e
for m in range(1,6):
 d=m+1;ff=forms(m);f=lambda x:min(dot(p,x) for p in ff)
 for n in range(1,5):
  for trial in range(8):
   retained=[bundle(m) for _ in range(n)];withdrawn=[bundle(m) for _ in range(n)]
   rows=[[x+y for x,y in zip(retained[i],withdrawn[i])] for i in range(n)]
   C=add(rows,d);own=list(map(f,rows));S=sum(own);T=f(C);G=T-S;assert G>=0
   a=Q(1,2);y=mixture(rows,ff,a);bn=n*a/2+Q(n,n+1)*(1-(1-a)**(n+1))/a
   assert sum(y)<=S+bn*G
   for mask in range(1<<n):
    ym=rule(rows,ff,mask)
    for coal in range(1<<n):
     members=[i for i in range(n) if coal>>i&1]
     assert sum(ym[i] for i in members)>=f(add([rows[i] for i in members],d))
     counts['mask_coverage']+=1
   for i in range(n):
    low=list(rows);low[i]=retained[i];ylow=mixture(low,ff,a)
    assert y[i]-ylow[i]>=f(withdrawn[i]);counts['individual_out']+=1
   rk=rank(rows);marg=[T-f([x-z for x,z in zip(C,b)]) for b in rows]
   assert sum(marg)<=S+rk*G;counts['grand_rank']+=1
   for q in [Q(1,4),Q(1,2),Q(3,4)]:
    closed=Q(0)
    for mask in range(1<<n):
     CB=add([rows[i] for i in range(n) if mask>>i&1],d);p=min(ff,key=lambda z:dot(z,CB))
     excess=sum(min(dot(p,rows[i])-own[i],G) for i in range(n) if not(mask>>i&1))
     closed+=q**(n-mask.bit_count())*(1-q)**mask.bit_count()*excess
    assert closed<=2*(d+1)*q/(1-q)*G;counts['low_rank_sampling']+=1
   counts['profiles']+=1
out={'status':'PASS','arithmetic':'exact Fraction','model':'signed reserve cone r>=max|e|, dimensions2..6',**counts}
Path(__file__).with_name('CONE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
