from fractions import Fraction as Q
from pathlib import Path
import json
z=[Q(-1),Q(1),Q(-3),Q(-5,2),Q(-1,2),Q(3)]
x=[Q(1,2),Q(1,2),Q(7,6),Q(2,3),Q(1,2),Q(11,6)]
z2=z.copy();z2[0]-=Q(1,8)
x2=[Q(1,2),Q(1,2),Q(9,8),Q(3,4),Q(3,8),Q(15,8)]
certs=[(z,x,{3:Q(1,2),36:Q(7,6),40:Q(1,6),56:Q(1,2)}),(z2,x2,{3:Q(1,8),36:Q(9,8),43:Q(3,8),56:Q(3,8)})]
checks=0
for zz,xx,dual in certs:
 def val(mask):return min(sum((max(v,0) for i,v in enumerate(zz) if mask>>i&1),Q(0)),sum((max(-v,0) for i,v in enumerate(zz) if mask>>i&1),Q(0)))
 for mask in range(64):
  paid=sum((v for i,v in enumerate(xx) if mask>>i&1),Q(0))
  assert paid>=val(mask);checks+=1
 for mask,weight in dual.items():
  assert weight>0
  assert sum((v for i,v in enumerate(xx) if mask>>i&1),Q(0))==val(mask)
 for i,v in enumerate(xx):assert v==sum((weight for mask,weight in dual.items() if mask>>i&1),Q(0))
 assert min(xx)>0
loss=x[0]+x[2]-x2[0]-x2[2]
assert loss==Q(1,24)
out={'status':'PASS','exact_coverage_checks':checks,'exact_positive_kkt_multipliers':8,'protected_pair':[0,2],'loss':str(loss),'changed_owner_own_payment_unchanged':x[0]==x2[0],'scope':'Exact pairwise architecture obstruction; no individual-monotonicity impossibility claim.'}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_projection_exact.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
