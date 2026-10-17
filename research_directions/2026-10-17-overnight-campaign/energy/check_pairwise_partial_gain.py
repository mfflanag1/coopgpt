from fractions import Fraction as Q
from pathlib import Path
import json
counts={'error_recursions':0,'threshold_identities':0,'merge_magnitude_cases':0}
for eps in (Q(0),Q(1,1000),Q(1,10),Q(1)):
 for beta in (Q(0),Q(1,2),Q(99,100),Q(341,342),Q(999,1000),Q(1)):
  delta=2*(1-beta);E=Q(0)
  for r in (3,4,5):
   E=Q(3,2)*(E+eps+delta)
   assert E==3*(eps+delta)*(Q(3,2)**(r-2)-1)
   if r>=4:
    prior=3*(eps+delta)*(Q(3,2)**(r-3)-1)
    assert 2*eps+delta<=prior+eps+delta
   counts['error_recursions']+=1
  assert 3*E==Q(171,8)*(eps+delta)
  assert Q(1,342)-(1-beta)==beta-Q(341,342)
  counts['threshold_identities']+=1
for a in range(-8,17):
 for b in range(-8,17):
  x=Q(a,4);y=Q(b,4)
  if max(x,0)+max(y,0)<=4 and max(-x,0)+max(-y,0)<=2:
   assert min(abs(x),abs(y))<=2
   counts['merge_magnitude_cases']+=1
old=Q(29,20)
t=Q(1,100)
new=t+(1-t)*(Q(3,2)-(1-t)/20)
assert new<old
out={'status':'PASS','counts':counts,'residual_huber_old_total':str(old),'residual_huber_restored_total':str(new),'residual_huber_pair_monotonicity_loss':str(old-new),'scope':'Exact scalar and finite diagnostics, not a substitute for the all-real proof.'}
Path(__file__).with_name('pairwise_partial_gain_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
