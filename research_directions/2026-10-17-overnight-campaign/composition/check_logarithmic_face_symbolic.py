#!/usr/bin/env python3
"""Exact rational envelope checks; numerical log-integral/OUT corroboration."""
from fractions import Fraction as Q
from decimal import Decimal,localcontext
from pathlib import Path
import importlib.util,random,json
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('face',HERE/'logarithmic_face_symbolic.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def check(ok,msg):
 if not ok:raise RuntimeError(msg)
def dec(x):x=Q(x);return Decimal(x.numerator)/Decimal(x.denominator)
def F(forms,c):return min(sum(a*b for a,b in zip(row,c)) for row in forms)

rng=random.Random(17100607);exact=integral=out_checks=0;records=[]
cases=[[[1,0,0],[0,1,0],[0,0,1]],[[1,0,1],[0,2,1],[1,1,0]],[[Q(1,2),2,0],[1,0,1],[0,Q(3,2),2],[1,1,1]],[[2,1]],[[0,0],[1,1]]]
with localcontext() as ctx:
 ctx.prec=85;tol=Decimal('1e-65')
 for rows in cases:
  forms=[list(map(Q,row)) for row in rows];d=len(forms[0])
  for trial in range(5):
   owners=[[Q(rng.randrange(5),rng.randrange(1,4)) for _ in range(d)] for _ in range(3)]
   if trial==0:owners[0]=[Q(0)]*d
   packet=m.symbolic(forms,owners);ev=m.decimal_value(packet,85);C=packet['aggregate'];c=ev['constant'];t0=ev['cutoff']
   for j,face in enumerate(packet['faces']):
    if face is None:continue
    lines=[(a[j]*C[j],sum(a[l]*C[l] for l in range(d) if l!=j)) for a in forms]
    points={Q(0),Q(1),*(s for s,delta in face['hinges'])}
    points.update(Q(rng.randrange(101),100) for _ in range(12))
    for u in points:
     target=min(a+b*u for a,b in lines)
     represented=face['alpha']+face['beta']*u+sum(delta*min(u,s) for s,delta in face['hinges'])
     check(target==represented,'exact envelope identity');exact+=1
    # Independently integrate each affine segment using its antiderivative.
    total=Decimal(0)
    for lo,hi,a,b in face['segments']:
     left=min(dec(lo),t0);right=min(dec(hi),t0)
     def ant(u):return c*(-dec(b)*u-dec(a+b)*(1-u).ln())
     total+=ant(right)-ant(left)
    check(abs(total-ev['face_values'][j])<tol,'analytic integral agreement');integral+=1
   funding=sum(ev['payments']);value=dec(F(forms,C));active=sum(x>0 for x in C)
   check(funding<=(1+c*(active-1))*value+tol if active else funding==0,'funding numerical')
   for mask in range(1,8):
    reduced=[o[:] for o in owners];withheld=[Q(0)]*d
    for i in range(3):
     if mask>>i&1:
      for j in range(d):
       reduction=owners[i][j]*Q(rng.randrange(3),2);reduced[i][j]-=reduction;withheld[j]+=reduction
    low=m.decimal_value(m.symbolic(forms,reduced),85)
    gain=sum(ev['payments'][i]-low['payments'][i] for i in range(3) if mask>>i&1)
    check(gain+tol>=dec(F(forms,withheld)),'numerical full OUT corroboration');out_checks+=1
  records.append({'resources':d,'forms':len(forms),'profiles':5})
print(json.dumps({'status':'PASS','exact_rational_envelope_checks':exact,'analytic_log_integral_checks':integral,
 'numerical_OUT_checks':out_checks,'numerical_precision_digits':85,
 'warning':'Decimal checks corroborate but do not establish the theorem or exact rounded-payment incentives.',
 'cases':records},indent=2))
