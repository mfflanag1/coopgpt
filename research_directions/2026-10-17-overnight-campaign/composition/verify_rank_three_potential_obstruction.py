#!/usr/bin/env python3
"""Exact two-profile KKT/payment certificate and growing-kernel regressions."""
from fractions import Fraction as Q
import json

def require(c,m):
 if not c:raise RuntimeError(m)
def degree(n,edges,lam):
 out=[Q(0)]*n
 for e,x in zip(edges,lam):
  for v in e:out[v]+=x
 return out
edges=[(2,3,5),(2,3,4),(2,4,5),(0,1,2),(0,4,5)]
lo=list(map(Q,[2,1,5,3,3,4]));hi=list(map(Q,[2,2,5,3,3,4]))
p0=[Q(1,3)]*6;p1=[Q(x,35) for x in [13,9,13,11,11,11]]
l0=[Q(x,3) for x in [4,2,2,2,2]];l1=[Q(x,35) for x in [44,22,28,36,16]]
for c,p,lam in [(lo,p0,l0),(hi,p1,l1)]:
 require(all(0<q<Q(1,2) for q in p),'strict quadratic branch')
 require(all(sum(p[v] for v in e)==1 for e in edges),'every cover edge tight')
 require(all(x>0 for x in lam),'positive multipliers')
 require(degree(6,edges,lam)==[2*a*b for a,b in zip(c,p)],'exact KKT')
a0=list(map(Q,[0,1,0,3,3,4]));a1=list(map(Q,[0,2,0,3,3,4]))
pay0=sum(a*b for a,b in zip(a0,p0));pay1=sum(a*b for a,b in zip(a1,p1))
require(pay0==Q(11,3) and pay1==Q(128,35) and pay0-pay1==Q(1,105),'strict report gain')
family=[]
for L in [2,4,6,8]:
 # indices: auxiliary 0, then three vertices per level.
 levels=[[1+3*k+i for i in range(3)] for k in range(L+1)]
 n=4+3*L;es=[(0,levels[0][0],levels[0][1]),(0,levels[0][0],levels[0][2]),(0,levels[0][1],levels[0][2])]
 z=[-2]+[(-2)**k for k in range(L+1) for _ in range(3)]
 for k in range(1,L+1):
  for v in levels[k]:es.append((v,levels[k-1][0],levels[k-1][1]))
 require(len(es)==n-1 and all(sum(z[v] for v in e)==0 for e in es),'explicit kernel')
 # Tiny rational tau suppresses high-level contributions; no floating point.
 tau=Q(1,100*2**(4*L));weights=[Q(1)]+[tau]*(len(es)-1);c=degree(n,es,weights)
 D=sum(c[v]*z[v]**2 for v in range(n));S=sum(c[v]*z[v] for v in range(n) if z[v]>0)
 j=levels[L][0];Z=z[j];derivative=Q(1,3)*(1-Q(Z)*S/D) # h'/h''=1/3 for quadratic
 require(derivative<0,'quadratic negative derivative family')
 require(all(x>0 for x in c) and sum(c[v]*z[v] for v in range(n))==0,'positive balanced degree vector')
 family.append({'L':L,'resources':n,'activities':len(es),'max_positive_kernel':Z,'tau':tau,'S_over_D':S/D,'quadratic_own_derivative':derivative})
print(json.dumps({'status':'PASS','arithmetic':'Fraction; exact KKT and payment identities',
 'prices_low':p0,'prices_high':p1,'multipliers_low':l0,'multipliers_high':l1,
 'payment_low':pay0,'payment_high':pay1,'underreport_gain':pay0-pay1,'growing_family':family},default=str,indent=2))
