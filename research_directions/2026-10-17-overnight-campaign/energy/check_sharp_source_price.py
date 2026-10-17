#!/usr/bin/env python3
"""Bounded exact value checks plus floating payment diagnostics, not proof."""
from itertools import product
from fractions import Fraction as Q
from math import exp
from functools import lru_cache
import random,json,pathlib,hashlib
R=pathlib.Path(__file__).parent

def require(ok,msg):
 if not ok:raise RuntimeError(msg)

def unit(e,h):
 E=sum(e);H=sum(h);T=min(E,H)
 if not T:return [0.]*len(e),[0.]*len(h)
 if E<=H:
  d=[min(z,T) for z in h];rho=sum(d)/T;q=exp(1-rho)/3
  pe=list(map(float,e));ph=[q*x for x in d]
 else:
  d=[min(x,T) for x in e];rho=sum(d)/T
  q=1-rho/3 if rho<=2 else exp(2-rho)/3
  pe=[max(q*dd,T-min(H,E-x)) for x,dd in zip(e,d)];ph=[(1-q)*z for z in h]
 return pe,ph

def layers(e,h,c,v):
 edges=sorted(set([Q(0)]+list(map(Q,c))+list(map(Q,v))))
 out=[0.]*(len(e)+len(h));F=Q(0)
 for lo,hi in zip(edges,edges[1:]):
  t=(lo+hi)/2;ee=[x if cc<=t else 0 for x,cc in zip(e,c)];hh=[z if vv>=t else 0 for z,vv in zip(h,v)]
  F+=(hi-lo)*min(sum(ee),sum(hh));pe,ph=unit(ee,hh)
  out=[x+float(hi-lo)*y for x,y in zip(out,pe+ph)]
 return F,out

def direct(e,h,c,v):
 @lru_cache(None)
 def rec(i,remaining):
  if i==len(h):return 0
  best=0
  for use in product(*(range(min(x,h[i])+1) for x in remaining)):
   if sum(use)>h[i]:continue
   val=sum((v[i]-c[j])*x for j,x in enumerate(use))
   val+=rec(i+1,tuple(x-y for x,y in zip(remaining,use)))
   best=max(best,val)
  return best
 return rec(0,tuple(e))

def main():
 rng=random.Random(20261017);counts={'profiles':0,'coalitions':0,'deviations':0};maxratio=0
 for ne,nh in [(1,1),(1,3),(2,2),(2,3),(3,2),(3,3)]:
  for _ in range(80):
   e=[rng.randrange(4) for _ in range(ne)];h=[rng.randrange(4) for _ in range(nh)]
   c=[rng.randrange(5) for _ in range(ne)];v=[rng.randrange(8) for _ in range(nh)]
   F,pay=layers(e,h,c,v);exact=direct(e,h,c,v)
   require(F==exact,('price identity',e,h,c,v,F,exact))
   require(all(x>=-1e-12 for x in pay),'negative payment')
   require(sum(pay)<=(4/3)*float(F)+1e-10,'4/3 bound')
   if F:maxratio=max(maxratio,sum(pay)/float(F))
   for j in range(ne):
    ee=list(e);ee[j]=0;Fm,_=layers(ee,h,c,v)
    require(pay[j]+1e-10>=float(F-Fm),'energy floor')
   for mask in range(1<<(ne+nh)):
    ee=[x if mask&(1<<j) else 0 for j,x in enumerate(e)]
    hh=[x if mask&(1<<(ne+i)) else 0 for i,x in enumerate(h)]
    Fs,_=layers(ee,hh,c,v);ds=direct(ee,hh,c,v)
    require(Fs==ds,'coalition price identity')
    require(sum(x for j,x in enumerate(pay) if mask&(1<<j))+1e-10>=float(Fs),'coverage')
    counts['coalitions']+=1
   for j,x in enumerate(e):
    for low in range(x+1):
     ee=list(e);ee[j]=low;_,pd=layers(ee,h,c,v)
     require(pd[j]<=pay[j]+1e-10,'energy incentive');counts['deviations']+=1
   for i,x in enumerate(h):
    for low in range(x+1):
     hh=list(h);hh[i]=low;_,pd=layers(e,hh,c,v)
     require(pd[ne+i]<=pay[ne+i]+1e-10,'hardware incentive');counts['deviations']+=1
   counts['profiles']+=1
 # More owner counts and cap regimes, random real capacities: diagnostic only.
 extra=0
 for _ in range(10000):
  ne=rng.randrange(1,25);nh=rng.randrange(1,25)
  ee=[10**rng.uniform(-5,3) for _ in range(ne)]
  hh=[10**rng.uniform(-5,3) for _ in range(nh)]
  pe,ph=unit(ee,hh);T=min(sum(ee),sum(hh))
  require(sum(pe)+sum(ph)<=(4/3)*T+1e-8*max(1,T),'real capacity budget')
  extra+=1
 out={'extra_real_capacity_profiles':extra,'status':'PASS' ,'evidence':'exact finite price identity; floating payment diagnostics only; analytic theorem separate','counts':counts,'max_sample_ratio':maxratio,'checker_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
 (R/'sharp_source_price_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
