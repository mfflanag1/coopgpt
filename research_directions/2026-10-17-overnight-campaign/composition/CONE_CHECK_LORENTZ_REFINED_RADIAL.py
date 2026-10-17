#!/usr/bin/env python3
"""Exact polynomial certificate, root isolation, and whole-coalition tests."""
from pathlib import Path
import runpy,json,contextlib,io
from fractions import Fraction as F
from itertools import product
with contextlib.redirect_stdout(io.StringIO()):
    ns=runpy.run_path(str(Path(__file__).with_name('lorentz_radial_polynomial_scout.py')))
Q,c,b=ns['Q'],ns['c'],ns['b'];phi=1+c
add,mul,power,sc,sub=(*(ns[k] for k in ['add','mul','power','sc','sub']),)
s,D=ns['s'],ns['D'];R=ns['DD']
assert len(R)==8 and all(r>0 for r in R)
Rexpected=[124*c-76,136-216*c,(47*c-14)/4,(725*c-436)/4,
           (109-172*c)/2,22-35*c,(125*c-77)/4,(13-21*c)/4]
assert R==Rexpected
left=sub(sc(mul(ns['AA'],ns['CC']),Q(4)),power(ns['BB'],2))
right=mul(mul(mul(power(s,2),power([Q(1),Q(-1)],3)),power(D,2)),R)
assert left==right
assert F(77,125)<c<F(13,21)
# Exact unique-root bracket; uniqueness is analytic in the theorem.
def H(t):return b*(1-2*t)*(c+t)**3+c*c-c*(1+2*c)*t
lo,hi=F(0),F(1)
assert H(lo)>0 and H(hi)<0
for _ in range(70):
 mid=(lo+hi)/2
 if H(mid)>0:lo=mid
 else:hi=mid
assert H(lo)>0 and H(hi)<0
upper=hi*(1-lo)*(c/(c+lo)**2+b)/2
lower=lo*(1-hi)*(c/(c+hi)**2+b)/2
assert lower<=upper<F(237,2000)
assert phi/(1-upper)<F(459,250)
counts=dict(polynomial_identities=1,positive_coefficients=8,root_bisections=70,
            profiles=0,budgets=0,coverage=0,coalition_tcwm=0,coalition_out=0)
# Reuse exact quadratic-field arithmetic and rational-norm profiles.
with contextlib.redirect_stdout(io.StringIO()):
    old=runpy.run_path(str(Path(__file__).with_name('CONE_CHECK_LORENTZ_PHI.py')))
# Q is a separate class from the second replay, so retain the first Q for calculations.
val,sumv,norm,rays=(old[k] for k in ['val','sumv','norm','rays'])
def pay(bs):
 C=sumv(bs,len(bs[0]));T=C[0];X=C[1:];rr=norm(X)
 if not T:return [Q(0) for _ in bs]
 coeff=1/(c*T+rr)+b/T
 return [Q(z[0])-sum((a*bb for a,bb in zip(z[1:],X)),F(0))*coeff for z in bs]
lam=F(2000,1763)
for fs in product([F(0),F(1,3),F(1)],repeat=3):
 for ext in [0,4,13]:
  full=[(1+f,)+x+(F(0),)*ext for f,x in zip(fs,rays)]
  n=3;dim=len(full[0]);zero=(F(0),)*dim;bymask={}
  for mask in range(1<<n):
   bs=[full[i] if mask>>i&1 else zero for i in range(n)]
   ys=pay(bs);bymask[mask]=ys;C=sumv(bs,dim)
   assert all(y>=0 for y in ys)
   assert sum(ys,Q(0))<=phi*val(C)
   assert lam*sum(ys,Q(0))<F(459,250)*val(C) or val(C)==0
   counts['profiles']+=1;counts['budgets']+=1
   for coal in range(1<<n):
    inds=[i for i in range(n) if coal>>i&1]
    assert sum((ys[i] for i in inds),Q(0))>=val(sumv([bs[i] for i in inds],dim))
    counts['coverage']+=1
  for low in range(1<<n):
   for high in range(1<<n):
    if low&high!=low:continue
    changed=high^low
    withdrew=sumv([full[i] for i in range(n) if changed>>i&1],dim)
    for coal in range(1<<n):
     if coal&changed!=changed:continue
     inc=sum((bymask[high][i]-bymask[low][i] for i in range(n) if coal>>i&1),Q(0))
     assert inc>=0
     assert lam*inc>=val(withdrew)
     counts['coalition_tcwm']+=1;counts['coalition_out']+=1
out={'status':'PASS','arithmetic':'exact Q(c), c^2+c=1, Fraction rational norm profiles',
     'counts':counts,'maximizer_interval':[str(lo),str(hi)],
     'certified_deficit_upper':'237/2000','tested_full_out_multiplier':'2000/1763',
     'certified_funding_upper':'2000 phi/1763 < 459/250',
     'scope':'Polynomial identity proves all s; finite transitions supplement analytic all-profile proof. Root-defined best multiplier for this curve is not claimed globally optimal.'}
Path(__file__).with_name('CONE_LORENTZ_REFINED_RADIAL_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
