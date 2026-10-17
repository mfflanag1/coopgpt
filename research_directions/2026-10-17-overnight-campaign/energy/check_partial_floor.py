#!/usr/bin/env python3
"""Float diagnostics; exact rational architecture obstruction. Not a proof."""
import itertools,json,math,random
from fractions import Fraction as Q
from pathlib import Path

def rule(e,h,theta,a):
 E=sum(e);H=sum(h);T=min(E,H)
 if not T:return [0.]*(len(e)+len(h))
 R=1/a-1
 if E<=H:
  d=[min(x,E) for x in h];rho=sum(d)/E;r=a*math.exp(1-rho)
  return [max(theta,1-r)*x for x in e]+[r*x for x in d]
 d=[min(x,H) for x in e];rho=sum(d)/H
 q=1-a*rho if rho<=R else a*math.exp(R-rho)
 return [max(q*y,theta*max(0,H-E+x)) for x,y in zip(e,d)]+[(1-q)*x for x in h]
def bound(theta,a):return max(1+a*math.exp(1/a-3),theta+a+(1-theta)**2/(4*a))
def check(condition,label):
 if not condition:raise RuntimeError(label)
rng=random.Random(1700);checks=0;own=0;coverage=0;ratios={};rows=[]
for theta in [.8,.85,.9,.95,1.]:
 a=(2-theta)/3+(1-theta)**2/4;K=bound(theta,a);worst=0
 for ne,nh in [(1,1),(1,3),(2,2),(2,3),(3,2),(3,3)]:
  for z in range(500):
   e=[rng.random()*3 for _ in range(ne)];h=[rng.random()*3 for _ in range(nh)]
   if z<100:e=[rng.randrange(4)/2 for _ in e];h=[rng.randrange(4)/2 for _ in h]
   y=rule(e,h,theta,a);T=min(sum(e),sum(h));checks+=1
   check(sum(y)<=K*T+1e-10,('budget',theta,e,h,y,K));worst=max(worst,sum(y)/T if T else 0)
   for j in range(ne):check(y[j]+1e-10>=theta*(T-min(sum(h),sum(e)-e[j])),('floor',theta,j))
   for mask in range(1<<(ne+nh)):
    worth=min(sum(e[j] for j in range(ne) if mask>>j&1),sum(h[i] for i in range(nh) if mask>>(ne+i)&1))
    check(sum(v for k,v in enumerate(y) if mask>>k&1)+1e-10>=worth,('coalition',theta,e,h,mask));coverage+=1
   for k in range(ne+nh):
    ee=e[:];hh=h[:]
    if k<ne:ee[k]*=rng.random()
    else:hh[k-ne]*=rng.random()
    yy=rule(ee,hh,theta,a)
    check(yy[k]<=y[k]+1e-10,('IC',theta,e,h,k,yy[k],y[k]));own+=1
 rows.append({'theta':theta,'a_explicit':a,'bound':K,'worst_sample':worst,'linear_lower':2*(1+theta)/3})
exact=[]
for theta in [Q(4,5),Q(9,10),Q(19,20),Q(99,100)]:
 a=(2-theta)/3;x=(1-a)/(2*a);full=1-2*a;low=x*(1-a*(1+x));gain=low-full
 check(0<x<1 and gain==(1-3*a)**2/(4*a)>0,('exact obstruction',theta))
 exact.append({k:str(v) for k,v in dict(theta=theta,a=a,x=x,full=full,underreport=low,gain=gain).items()})
out={'status':'PASS','profiles':checks,'coalitions':coverage,'underreports':own,'floating_diagnostics':rows,'exact_rational_architecture_obstructions':exact}
Path(__file__).with_name('partial_floor_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
