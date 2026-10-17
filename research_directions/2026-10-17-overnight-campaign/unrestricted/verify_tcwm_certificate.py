if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
"""Exact standalone lower-certificate audit; no numerical libraries."""
from fractions import Fraction as Q
from collections import defaultdict
import json,sys
p=sys.argv[1] if len(sys.argv)>1 else '/private/tmp/coopgpt-overnight-20261017/unrestricted/rank3_tcwm_4.json'
z=json.load(open(p));r=z['r'];n=z['n'];coeff=defaultdict(Q);rhs=Q(0);T=lambda c:min(sum(a for t,a in enumerate(c)if t>>e&1)for e in range(r))
for item in z['dual']:
 w=Q(item['weight']).limit_denominator(1000000);label=item['label'];kind=label[0];c=tuple(label[1]);assert sum(c)==n and w>=0
 if kind=='budget':
  coeff['kappa']-=w*T(c)
  for t,a in enumerate(c):
   if a:coeff[c,t]+=w*a
 elif kind=='cover':
  k=label[2];assert all(0<=k[t]<=c[t]for t in range(1<<r));rhs-=w*T(k)
  for t,a in enumerate(k):
   if a:coeff[c,t]-=w*a
 elif kind=='mono':
  t,e,k=label[2:];assert c[t]>0 and k[t]>0 and not(t>>e&1);assert all(0<=k[j]<=c[j]for j in range(1<<r))
  u=t|(1<<e);c2=list(c);c2[t]-=1;c2[u]+=1;c2=tuple(c2);k2=list(k);k2[t]-=1;k2[u]+=1
  for j,a in enumerate(k):
   if a:coeff[c,j]+=w*a
  for j,a in enumerate(k2):
   if a:coeff[c2,j]-=w*a
 else:raise ValueError(kind)
assert coeff['kappa']<0
bad={str(k):str(v)for k,v in coeff.items()if k!='kappa'and v<0};assert not bad,bad
B=rhs/coeff['kappa']
print(json.dumps({'status':'PASS','r':r,'owners':n,'dual_rows':len(z['dual']),'budget_coefficient':str(coeff['kappa']),'rhs':str(rhs),'exact_lower':str(B),'nonzero_payment_coefficients':sum(v!=0 for k,v in coeff.items()if k!='kappa')}))
