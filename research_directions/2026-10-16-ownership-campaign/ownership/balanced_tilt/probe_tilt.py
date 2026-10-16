from fractions import Fraction as F
from itertools import product
import random

def prod(xs):
 p=F(1)
 for x in xs:p*=x
 return p

def rule(r):
 A=sum(x for x,y in r);B=sum(y for x,y in r)
 if min(A,B)==0:return (F(0),)*len(r)
 if A<=B:x=[a for a,b in r];z=[b for a,b in r]
 else:A,B=B,A;x=[b for a,b in r];z=[a for a,b in r]
 M=max(x);d=[min(v,A) for v in z];D=sum(d);L=max(d)
 caps=sorted([M]+[v for v in d if v]);target=A+M
 if sum(caps)==target:lev=max(caps)
 else:
  small=F(0)
  for j,c in enumerate(caps):
   lev=(target-small)/(len(caps)-j)
   if lev<=c:break
   small+=c
 phi=lambda t:max(t-F(2,3),0)**2
 h=F(1,2)+F(1,4)*(phi(L/D)-phi(M/A))
 p=h*prod(min(c,lev)/c for c in caps)
 return tuple((1-p)*a+p*b for a,b in zip(x,d))

count=0;worst=(F(0),None)
for n in range(1,5):
 states=list(product(tuple(product((F(0),F(1),F(2)),repeat=2)),repeat=n))
 ys={r:rule(r) for r in states}
 for r,y in ys.items():
  T=min(sum(a for a,b in r),sum(b for a,b in r))
  if T and sum(y)/T>worst[0]:worst=(sum(y)/T,r)
  for i in range(n):
   for side in (0,1):
    if r[i][side]>=2:continue
    rr=[list(t) for t in r];rr[i][side]+=1;rr=tuple(tuple(t) for t in rr)
    if ys[rr][i]<y[i]:print('FAILgrid',r,rr,i,y,ys[rr]);raise SystemExit
    count+=1
print('gridPASS',count,'worst',worst,flush=True)
rng=random.Random(739)
for trial in range(20000):
 n=2+trial%9
 r=tuple((F(rng.randrange(21),rng.randrange(1,15)),F(rng.randrange(21),rng.randrange(1,15))) for _ in range(n))
 y=rule(r)
 T=min(sum(a for a,b in r),sum(b for a,b in r))
 if T and sum(y)/T>worst[0]:worst=(sum(y)/T,r)
 i=rng.randrange(n);side=rng.randrange(2);delta=F(1,rng.choice((100,1000,10000)))
 rr=[list(t) for t in r];rr[i][side]+=delta;rr=tuple(tuple(t) for t in rr)
 z=rule(rr)
 if z[i]<y[i]:print('FAILsmall',r,rr,i,y,z,'trial',trial,flush=True);raise SystemExit
 count+=1
print('allPASS',count,'worst',worst,flush=True)
