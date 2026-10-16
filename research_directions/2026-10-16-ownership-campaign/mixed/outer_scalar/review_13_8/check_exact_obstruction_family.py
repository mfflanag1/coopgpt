#!/usr/bin/env python3
"""Independent direct-mechanism diagnostics; not the universal proof."""
from fractions import Fraction as F
import math,random,json
rng=random.Random(2026101627)
def require(test,msg):
 if not test:raise RuntimeError(msg)
def primitive(x,y):
 a=sum(x);b=sum(y);T=min(a,b)
 if T==0:return [0.0]*len(x)
 s,l=(x,y) if a<=b else (y,x)
 caps=[min(t,T) for t in l]
 q=.5*math.exp(1-sum(caps)/T)
 return [(1-q)*ss+q*dd for ss,dd in zip(s,caps)]
def nested(h,l,p):
 n=len(p); z=[0.0]*n
 for hj,lj in zip(h,l):
  out=primitive(hj,lj)
  z=[a+b for a,b in zip(z,out)]
 H=[sum(hj[i] for hj in h) for i in range(n)]
 return primitive(H,[a+b for a,b in zip(p,z)])
checks=0;attainments=0;worst=0.0
for r in (1,2,5,9):
 for m in (1,2,4,8):
  for epsq in (F(1,100),F(1,10),F(1,5),F(2,5),F(9,10),F(99,100)):
   eps=float(epsq);n=m+2
   h=[[1/r]+[0.0]*(n-1) for _ in range(r)]
   l=[[0.0,(1-eps)/r]+[eps/(m*r)]*m for _ in range(r)]
   p=[0.0,.4+eps/2]+[(1-eps)/(2*m)]*m
   EB=.25*math.exp(-.1) if epsq<=F(1,5) else (.2+eps/4)*math.exp(.1-eps)
   E=[1-.25*math.exp(-.9),EB]+[math.exp(-.9)/(4*m)]*m
   full=nested(h,l,p)
   require(abs(full[0]-E[0])<1e-12,'A truthful attainment')
   require(all(abs(full[i]-E[i])<1e-12 for i in range(2,n)),'C truthful attainment')
   D=min(.4,(1-eps)/2)
   lbest=[row[:] for row in l]
   for row in lbest:row[1]*=max(0,1-2*D/(1-eps))
   best=nested(h,lbest,p)
   require(abs(best[1]-EB)<1e-12,'B feasible attainment')
   require(abs(sum(E)-(1+EB))<1e-12 and sum(E)<1.25,'exact formula sum')
   attainments+=n
   for i in range(n):
    for repeat in range(20):
     hh=[row[:] for row in h];ll=[row[:] for row in l];pp=p[:]
     for j in range(r):
      hh[j][i]*=rng.randrange(101)/100
      ll[j][i]*=rng.randrange(101)/100
     pp[i]*=rng.randrange(101)/100
     actual=nested(hh,ll,pp)[i]
     worst=max(worst,actual-E[i]);checks+=1
     require(actual<=E[i]+1e-11,'underreport exceeds exact formula')
require(F(2,5)<F(9,20),'B maximum before outer switch')
require(F(9,10)-F(2,5)==F(1,2),'B optimal own opposing account')
require(F(19,10)-2*F(2,5)==F(11,10),'B optimal outer total')
require(F(1,5)+F(1,5)/4==F(1,4),'B piecewise boundary')
require(F(5,4)<F(4,3),'uniform funding comparison')
print(json.dumps({'status':'PASS','scope':'Finite direct-mechanism diagnostic plus exact rational identities; universal family proof is analytical.','underreport_checks':checks,'attainment_checks':attainments,'largest_roundoff_excess':worst},indent=2))
