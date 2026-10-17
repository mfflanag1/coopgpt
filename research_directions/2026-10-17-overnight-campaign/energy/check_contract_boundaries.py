#!/usr/bin/env python3
"""Exact static/mixed-factor2 checks; floating mixed4/3/partial diagnostics."""
import json,itertools,random,math
from fractions import Fraction as Q
from pathlib import Path

def check(ok,msg):
 if not ok:raise RuntimeError(msg)
def static(e,h,theta):
 E=sum(e);H=sum(h);T=min(E,H)
 if not T:return [Q(0)]*(len(e)+len(h))
 if E<=H:return e+[Q(0)]*len(h)
 d=[min(x,H) for x in e];m=[max(Q(0),H-E+x) for x in e]
 w=max((x/y if y else Q(0) for x,y in zip(m,d)),default=Q(0))
 return [theta*w*x for x in d]+[(1-theta*w)*x for x in h]
def mixed2(e,h):
 E=sum(e);H=sum(h)
 if E<=H:return [x+max(Q(0),E-H+y) for x,y in zip(e,h)]
 return [y+max(Q(0),H-E+x) for x,y in zip(e,h)]
def mixed_partial(e,h,theta,a):
 E=sum(e);H=sum(h);T=min(E,H)
 if not T:return [0.]*len(e)
 R=1/a-1
 if E<=H:
  d=[min(x,E) for x in h];rho=sum(d)/E;r=a*math.exp(1-rho)
  return [max(theta,1-r)*x+r*y for x,y in zip(e,d)]
 d=[min(x,H) for x in e];rho=sum(d)/H;q=1-a*rho if rho<=R else a*math.exp(R-rho)
 return [max(q*z,theta*max(0,H-E+x))+(1-q)*y for x,y,z in zip(e,h,d)]
counts={'static_exact_profiles':0,'mixed_two_exact_profiles':0,'mixed_float_profiles':0,'mixed_float_coalitions':0,'mixed_float_whole_bundle_underreports':0}
for ne,nh in [(1,1),(1,2),(2,1),(2,2),(2,3),(3,2)]:
 for pr in itertools.product([Q(0),Q(1,2),Q(1)],repeat=ne+nh):
  e=list(pr[:ne]);h=list(pr[ne:]);T=min(sum(e),sum(h))
  for theta in [Q(0),Q(1,2),Q(1)]:
   y=static(e,h,theta);counts['static_exact_profiles']+=1
   check(sum(y)<=(1+theta/4)*T,('static budget',pr,theta,y))
   for j in range(ne):check(y[j]>=theta*(T-min(sum(e)-e[j],sum(h))),('static floor',pr,j))
   for mask in range(1<<(ne+nh)):
    W=min(sum(x for j,x in enumerate(e) if mask>>j&1),sum(x for i,x in enumerate(h) if mask>>(ne+i)&1))
    check(sum(x for k,x in enumerate(y) if mask>>k&1)>=W,('static coalition',pr,mask))
for n in [1,2,3]:
 for pr in itertools.product([Q(0),Q(1,2),Q(1)],repeat=2*n):
  e=list(pr[:n]);h=list(pr[n:]);T=min(sum(e),sum(h));y=mixed2(e,h);counts['mixed_two_exact_profiles']+=1
  check(sum(y)<=2*T,('mixed2 budget',pr,y))
  for i in range(n):
   check(y[i]>=T-min(sum(e)-e[i],sum(h)-h[i]),('mixed2 floor',pr,i))
   ee=e[:];hh=h[:];ee[i]/=2;hh[i]/=2
   check(mixed2(ee,hh)[i]<=y[i],('mixed2 IC',pr,i))
  for mask in range(1<<n):
   W=min(sum(x for i,x in enumerate(e) if mask>>i&1),sum(x for i,x in enumerate(h) if mask>>i&1))
   check(sum(x for i,x in enumerate(y) if mask>>i&1)>=W,('mixed2 coalition',pr,mask))
rng=random.Random(197)
for theta in [.8,.9,1.]:
 a=(2-theta)/3+(1-theta)**2/4;K=max(1+a*math.exp(1/a-3),theta+a+(1-theta)**2/(4*a))
 for n in [1,2,3,5,7]:
  for z in range(400):
   e=[rng.random()*3 for _ in range(n)];h=[rng.random()*3 for _ in range(n)];T=min(sum(e),sum(h));y=mixed_partial(e,h,theta,a);counts['mixed_float_profiles']+=1
   check(sum(y)<=K*T+1e-10,('mixed budget',theta,e,h,y))
   for i in range(n):
    check(y[i]+1e-10>=theta*(T-min(sum(e)-e[i],sum(h))),('mixed energy-service floor',theta,i))
    ee=e[:];hh=h[:];ee[i]*=rng.random();hh[i]*=rng.random()
    check(mixed_partial(ee,hh,theta,a)[i]<=y[i]+1e-10,('mixed actual bundle IC',theta,e,h,i));counts['mixed_float_whole_bundle_underreports']+=1
   for mask in range(1<<n):
    W=min(sum(x for i,x in enumerate(e) if mask>>i&1),sum(x for i,x in enumerate(h) if mask>>i&1))
    check(sum(x for i,x in enumerate(y) if mask>>i&1)+1e-10>=W,('mixed coalition',theta,e,h,mask));counts['mixed_float_coalitions']+=1
out={'status':'PASS',**counts,'proof_status':'Finite diagnostics only; exact arithmetic where labelled. General results rely on accompanying analytic proofs.'}
Path(__file__).with_name('contract_boundary_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
