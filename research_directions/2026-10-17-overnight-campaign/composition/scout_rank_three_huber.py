#!/usr/bin/env python3
from fractions import Fraction as Q
from itertools import combinations
from math import lcm,gcd
from functools import reduce
import random,json

def kernel(A,n):
 m=[[Q(x) for x in row] for row in A];r=0;piv=[]
 for j in range(n):
  k=next((k for k in range(r,len(m)) if m[k][j]),None)
  if k is None:continue
  m[r],m[k]=m[k],m[r];d=m[r][j];m[r]=[x/d for x in m[r]]
  for k in range(len(m)):
   if k!=r and m[k][j]:d=m[k][j];m[k]=[x-d*y for x,y in zip(m[k],m[r])]
  piv.append(j);r+=1
  if r==len(m):break
 if r!=n-1:return None
 free=next(j for j in range(n) if j not in piv);z=[Q(0)]*n;z[free]=1
 for k,j in enumerate(piv):z[j]=-m[k][free]
 d=reduce(lcm,(x.denominator for x in z),1);a=[int(x*d) for x in z];g=reduce(gcd,a,0)
 return [x//g for x in a]
rng=random.Random(17100600)
for n in range(5,11):
 possible=list(combinations(range(n),3))
 for trial in range(15000):
  es=rng.sample(possible,n-1)
  if set().union(*map(set,es))!=set(range(n)):continue
  A=[[int(v in e) for v in range(n)] for e in es];z=kernel(A,n)
  if z is None:continue
  for sign in (1,-1):
   zz=[sign*x for x in z];j=max(range(n),key=lambda k:zz[k])
   for k,e in enumerate(es):
    d=sum(zz[v]**2 for v in e);s=sum(max(zz[v],0) for v in e)
    if d<zz[j]*s:
     print(json.dumps({'n':n,'edges':es,'kernel':zz,'increased_vertex':j,'heavy_edge':k,'edge_D':d,'edge_positive_sum':s,'largest_coordinate':zz[j]},indent=2));raise SystemExit
raise RuntimeError('none found in bounded scout')
