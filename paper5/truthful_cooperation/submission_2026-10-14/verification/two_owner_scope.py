#!/usr/bin/env python3
"""Exact finite regression for the full-bundle two-owner comparison repair.
These bounded checks corroborate the written general proof, not replace it.
"""
from fractions import Fraction as Q
from itertools import product
import json

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def value(forms, bundle):
    return min(sum(a*b for a,b in zip(w,bundle)) for w in forms)

def pay(forms, bundles):
    single=[value(forms,b) for b in bundles]
    total=value(forms,tuple(a+b for a,b in zip(*bundles)))
    return tuple((single[i]+total-single[1-i])/2 for i in (0,1))

forms_set=(((Q(1),Q(0)),(Q(1,3),Q(2,3))),
           ((Q(1),Q(0)),(Q(0),Q(1))),
           ((Q(1,2),Q(3)),(Q(2),Q(1,3))),
           ((Q(0),Q(0)),),((Q(2),Q(3)),))
# Reproduce the actual old full-bundle failure.
forms=forms_set[0]
bad=(Q(0),Q(0)),(Q(1),Q(0))
old_second=Q(1,2)*Q(2,3)*min(sum(x) for x in zip(*bad))
require(old_second==0 and value(forms,bad[1])==Q(1,3),'old sentence negative control')
counts={'profiles':0,'coalitions':0,'own_increases':0}
bundles=list(product((Q(0),Q(1,2),Q(1),Q(2)),repeat=2))
for forms in forms_set:
 for b in product(bundles,repeat=2):
    p=pay(forms,b);T=value(forms,tuple(a+c for a,c in zip(*b)))
    require(sum(p)==T,'efficiency')
    require(all(p[i]>=value(forms,b[i])>=0 for i in (0,1)),'singleton coverage')
    counts['profiles']+=1;counts['coalitions']+=4
    for i in (0,1):
     for high in bundles:
      if all(a<=c for a,c in zip(b[i],high)):
       changed=list(b);changed[i]=high
       require(pay(forms,changed)[i]>=p[i],'whole bundle own monotonicity')
       counts['own_increases']+=1
print(json.dumps({'status':'PASS',**counts,'old_rule_counterexample':'b1=(0,0), b2=(1,0), M=3: old P2=0 < v({2})=1/3','scope':'finite exact checks for repaired comparison only'},indent=2))
