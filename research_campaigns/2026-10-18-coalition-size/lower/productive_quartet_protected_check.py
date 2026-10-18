#!/usr/bin/env python3
from fractions import Fraction as F
from functools import lru_cache
import json
@lru_cache(None)
def bfull(B):
 b=F(4,15)
 for j in range(3,B+1):b*=F(3*(j-1),3*j-1)
 return b
@lru_cache(None)
def pay(B,s):
 if B==0:return (F(1,3),F(0),F(0),F(0),F(0))
 if B==1:return (F(1,3),F(1,3),F(1,3),F(0),F(0))
 B0=max(2,(s+1)//2);b=bfull(B) if B<=B0 else F(B0,B)*bfull(B0)
 return (1-F(3,2)*b,F(3,4)*b,b,F(0),F(0))
def maxloss(x,y,groups,slots):
 loss=F(0)
 for delta,count in sorted([(x[a]-y[b],n) for n,a,b in groups if n],reverse=True):
  if delta<=0 or not slots:break
  use=min(count,slots);slots-=use;loss+=use*delta
 return loss
profiles=transitions=0
for M in [1,2,3,4,8,16,32,64]:
 for s in [2,3,4,7,8,15,16,31,32,63,64,127]:
  B0=max(2,(s+1)//2);assert B0<=s
  C=1+B0*bfull(B0)
  assert bfull(B0)**3<=F(4,15)**3*F(9,(B0+1)**2)
  for f in range(M+1):
   for t in range(M-f+1):
    B=f+t;u=M-B;x=pay(B,s);z,a,b,p,q=x
    assert 3*z>=1
    if f:assert z+2*a>=1
    if t:assert z+2*b>=1
    value=min(F(3),1+F(4,3)*f+t)
    assert (3*z+4*f*a+3*t*b)/value<=C
    profiles+=1
    if u:
     y=pay(B+1,s);groups=[(3,0,0),(4*f,1,1),(3*t,2,2),(u-1,3,3),(1,3,2),(3*u+t-2,4,4)]
     assert 2*(y[2]-x[4])>=maxloss(x,y,groups,s-2);transitions+=1
    if t:
     y=pay(B,s);groups=[(3,0,0),(4*f,1,1),(3*(t-1),2,2),(u,3,3),(3,2,1),(3*u+t-1,4,4)]
     assert y[1]-x[4]>=maxloss(x,y,groups,s-1);transitions+=1
print(json.dumps({'status':'PASS','profiles':profiles,'protected_transition_checks':transitions,'M_max':64,'s_max':127,'uniform_bound':'1+(4/15)*3^(2/3)*s^(1/3)','scope':'Listed productive quartet grid only; not a full-domain mechanism.'}))
