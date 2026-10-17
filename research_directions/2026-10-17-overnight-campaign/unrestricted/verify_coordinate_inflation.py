#!/usr/bin/env python3
from fractions import Fraction as Q
if not __debug__: raise RuntimeError('Assertions required; do not use -O')
checks=0
for t in range(2,101):
 m=t*t;k=t;e=Q(1,m*m);u=(1+(m-1)*e)/(m+1)
 B=e+1+(m-1)*u;b=e+k*u
 s=Q(m+1+k*(m-1),k*k+m+1)*e;v=(b-s)/k
 assert u-e>0 and v-s>0
 assert m*(u-e)+e==1-u
 assert (m+1)*v-k*s==1
 assert s+k*v==b
 assert s/e==Q(t*t+1+t*(t*t-1),2*t*t+1)
 assert s<Q(t+1,2*t**4)
 assert (m+1-k)*(t+1)<2*t**4
 assert B>1+b
 checks+=8
for m in range(3,41):
 for k in range(1,m-1):
  for M in range(2,10):
   e=Q(1,100*M*M*m*m);u=(1+(m-1)*M*e)/(m+1)
   G=e+1+(m-1)*u;b=e+k*u
   D=k*k+(M-1)*(m-1)**2+(m+1)
   delta=(m-1-k)*e/D;s=e+k*delta;a=e+(m-1)*delta;v=u-delta
   assert v-(M-1)*a-s>0
   assert s+k*v==b
   assert a+1+(m-1)*v==G
   assert a+k*v>=b
   assert (m+1)*v-(M-1)*(m-1)*a-k*s==1
   assert s/e<=1+Q(1,4*(M-1))
   checks+=6
print('PASS:',checks,'exact KKT and coupling checks')
