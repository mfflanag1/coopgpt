#!/usr/bin/env python3
from itertools import product
from fractions import Fraction as Q
from functools import lru_cache

def value(h,L,P,a,b):
 dp={(0,0):Q(0)}
 for hi,ai,bi in zip(h,a,b):
  nd={}
  for (ql,gl),v in dp.items():
   for q in range(min(hi,L-ql)+1):
    for g in range(min(hi-q,P-gl)+1):
     key=(ql+q,gl+g);nd[key]=max(nd.get(key,Q(-1)),v+ai*q+bi*g)
  dp=nd
 return max(dp.values(),default=Q(0))

if __name__=='__main__':
 for L,P,h1,h2 in product(range(5),repeat=4):
  h=[h1,h2]
  F=value(h,L,P,[2,0],[3,2])
  rhs=value(h,L,P,[1,0],[1,1])+value(h,L,P,[1,0],[1,0])+value(h,L,P,[0,0],[1,1])
  if F!=rhs:print('FAIL',L,P,h,F,rhs);break
 else:print('PASS 625 capacity profiles')
