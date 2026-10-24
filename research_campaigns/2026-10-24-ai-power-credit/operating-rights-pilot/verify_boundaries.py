#!/usr/bin/env python3
"""Exact synthetic checks. Not a model proof or issuer recovery estimate."""
from fractions import Fraction as F
from pathlib import Path
import hashlib, json

def objective(t,w,f,a,p,mu,delta,rho,c):
    q=1-p
    expanded=mu*t+p*w+q*(rho*(a*(delta-c)-f)+(1-rho)*(-f))
    reduced=mu*t+p*w+q*(a*rho*(delta-c)-f)
    assert expanded==reduced
    return reduced

n=0
for p in (F(1,4),F(1,2),F(3,4)):
 for rho in (F(0),F(1,3),F(2,3),F(1)):
  for c in (F(0),F(2),F(6)):
   for mu in (F(1),F(2)):
    for a in (0,1):
     objective(F(-1),F(2),F(3),a,p,mu,F(6),rho,c)
     n+=1
# Feasible original economic calibration; changed access need not preserve welfare assumptions.
p,pL,B,A,R,I,PM,delta=F(3,4),F(1,4),F(1),F(2),F(12),F(10),F(0),F(6)
q=1-p;k=B/(p-pL);PV=PM+delta
G=I-A-p*(R-k)-q*PM;Gamma=G+max(A-p*k,F(0));d=I-A-PM
assert p*R+q*PV>I and pL*R+B+(1-pL)*PV<I and 0<G and Gamma<=d
assert Gamma==1
threshold=Gamma/(q*delta)
assert threshold==F(2,3)
assert q*delta*F(1)-Gamma>0 and q*delta*F(1,3)-Gamma<0
# Rights may each exist without a common operator/time witness.
identity=[{('Alpha',0)},{('Beta',0)}]
timing=[{('Alpha',0),('Alpha',1)},{('Alpha',2),('Alpha',3)}]
positive=[{('Alpha',0),('Beta',0)},{('Alpha',0)}]
for menus in (identity,timing):
 assert all(menus) and not set.intersection(*menus)
assert set.intersection(*positive)=={('Alpha',0)}
print(json.dumps({'status':'PASS','objective_identity_checks':n,'synthetic_threshold':str(threshold),'incompatible_rights_examples':2,'compatible_example':1,'issuer_calibration':False,'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
