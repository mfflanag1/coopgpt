#!/usr/bin/env python3
"""Exact rational reference for the candidate31/27 mixed two-pool rule."""
from fractions import Fraction as Q

def need(ok,msg):
 if not ok:raise ValueError(msg)

def water_level(caps,target):
 caps=sorted(Q(x)for x in caps if x>0);target=Q(target)
 need(caps and 0<target<=sum(caps),'invalid waterfill target')
 used=Q();n=len(caps)
 for j,cap in enumerate(caps):
  level=(target-used)/(n-j)
  if level<=cap:return level
  used+=cap
 raise ValueError('waterfill exhaustion')

def rule(profile,details=False):
 profile=[(Q(a),Q(b))for a,b in profile];need(all(a>=0 and b>=0 for a,b in profile),'negative report')
 aa=sum(a for a,b in profile);bb=sum(b for a,b in profile)
 if min(aa,bb)==0:
  out=[Q()for _ in profile];return (out,dict(A=min(aa,bb),p=Q(),level=Q()))if details else out
 short=0 if aa<=bb else 1;xs=[row[short]for row in profile];zs=[row[1-short]for row in profile];a=sum(xs);m=max(xs);ds=[min(z,a)for z in zs]
 level=water_level([m]+ds,a+m);p=Q(1,2)*min(m,level)/m
 for d in ds:
  if d:p*=min(d,level)/d
 out=[(1-p)*x+p*d for x,d in zip(xs,ds)]
 need(sum(min(d,level)for d in ds)+min(m,level)==a+m,'waterfill equation')
 info=dict(A=a,M=m,D=sum(ds),p=p,level=level,short=short)
 return (out,info)if details else out
