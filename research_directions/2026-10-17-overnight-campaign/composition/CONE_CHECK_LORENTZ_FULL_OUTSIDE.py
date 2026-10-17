#!/usr/bin/env python3
"""Exact finite coalition-withdrawal certificates in Q(sqrt(5))."""
from pathlib import Path
import runpy,json
from fractions import Fraction as F
from itertools import product
ns=runpy.run_path(str(Path(__file__).with_name('CONE_CHECK_LORENTZ_PHI.py')))
Q,c,b,phi=(ns[k] for k in ['Q','c','b','phi'])
pay,val,sumv,scale=(ns[k] for k in ['pay','val','sumv','scale'])
rays=ns['rays']
counts=dict(temporal_identities=0,temporal_bounds=0,profiles=0,budgets=0,coverage=0,coalition_out=0)
for j in range(101):
 s=F(j,100);D=c+b*s
 assert D**2-4*c*s*(1-s)==(c-(1+c)*s)**2
 assert 1-c*s*(1-s)/(2*D**2)>=F(7,8)
 counts['temporal_identities']+=1;counts['temporal_bounds']+=1
for fs in product([F(0),F(1,3),F(1)],repeat=3):
 for ext in [0,4,13]:
  full=[(1+f,)+x+(F(0),)*ext for f,x in zip(fs,rays)]
  n=3;d=len(full[0]);zero=(F(0),)*d;bymask={};reports={}
  for mask in range(1<<n):
   bs=[full[i] if mask>>i&1 else zero for i in range(n)]
   ys=[F(8,7)*y for y in pay(bs)];C=sumv(bs,d)
   assert sum(ys,Q(0))<=F(8,7)*phi*val(C)
   bymask[mask]=ys;reports[mask]=bs
   counts['profiles']+=1;counts['budgets']+=1
   for coal in range(1<<n):
    inds=[i for i in range(n) if coal>>i&1]
    assert sum((ys[i] for i in inds),Q(0))>=val(sumv([bs[i] for i in inds],d))
    counts['coverage']+=1
  for low in range(1<<n):
   for high in range(1<<n):
    if low&high!=low:continue
    changed=high^low
    withdrawn=sumv([full[i] for i in range(n) if changed>>i&1],d)
    for coal in range(1<<n):
     if coal&changed!=changed:continue
     assert sum((bymask[high][i]-bymask[low][i] for i in range(n) if coal>>i&1),Q(0))>=val(withdrawn)
     counts['coalition_out']+=1
out={'status':'PASS','arithmetic':'exact Q(sqrt(5)) and rational square-root profiles','counts':counts,
     'scope':'Finite certificates supplement the proof for arbitrary real cone reports and withdrawals.'}
Path(__file__).with_name('CONE_LORENTZ_FULL_OUTSIDE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
