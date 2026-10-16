#!/usr/bin/env python3
"""Finite floating diagnostic, not a certificate of the universal support lemma."""
import math,random,json
rng=random.Random(2026101623)
def k(t):
 if t<=0:return 1.0
 return 1-0.5*math.exp(1-1/t) if t<=1 else 0.5*math.exp(1-t)
worst=0.0;cases=0;endpoint_errors=0
for _ in range(20000):
 S=1 if _%7==0 else 1+5*rng.random()
 a=0.95*rng.random(); b=a+(1-a)*rng.random()
 u=1 if _%5==0 else b+(1-b)*rng.random()
 q=.5*math.exp(1-1/u)
 eta=q*(u-b)**2/(u*u*(S-b))
 lam=1-q*(1+(u-b)*(S-u)/(u*u*(S-b)))
 A=lam-eta
 if A<-1e-12:raise RuntimeError(('negative A',S,a,b,u,A))
 ts=[0,b,u,1,min(S,1+b-a),S]+[S*rng.random() for j in range(12)]
 for t in ts:
  lhs=min(1-a,max(0,t-b))*max(0,k(t)-lam)
  rhs=eta*(S-t)
  diff=lhs-rhs;worst=max(worst,diff);cases+=1
  if diff>1e-10:raise RuntimeError(('support failure',S,a,b,u,t,lhs,rhs))
 if abs(min(1-a,u-b)*max(0,k(u)-lam)-eta*(S-u))>1e-10:
  endpoint_errors+=1
if endpoint_errors:raise RuntimeError(('sharp point mismatch',endpoint_errors))
print(json.dumps({'status':'PASS','kind':'finite floating diagnostic only','support_checks':cases,'parameter_cases':20000,'largest_roundoff_excess':worst,'sharp_point_failures':endpoint_errors},indent=2))
