from fractions import Fraction as Q
from itertools import product
import json

def rule(rows):
 out=[]
 for i,(a,b) in enumerate(rows):
  others=[x-y for j,(x,y) in enumerate(rows) if j!=i];positives=[v for v in others if v>0];negatives=[v for v in others if v<0]
  if len(positives)==2:y=min(b,a+sum(positives))
  elif len(negatives)==2:y=min(a,b-sum(negatives))
  elif len(positives)==1 and not negatives:y=(min(a,b)+min(b,a+positives[0]))/2
  elif len(negatives)==1 and not positives:y=(min(a,b)+min(a,b-negatives[0]))/2
  else:y=min(a,b)
  out.append(y)
 return out
levels=tuple(map(Q,range(5)));payments={};coalitions=transitions=0
for flat in product(levels,repeat=6):
 rows=tuple((flat[2*i],flat[2*i+1]) for i in range(3));y=rule(rows);payments[flat]=y
 if sum(y)!=min(sum(r[0] for r in rows),sum(r[1] for r in rows)):raise RuntimeError('budget')
 for mask in range(1,8):
  coalition=[i for i in range(3) if mask&(1<<i)];value=min(sum(rows[i][0] for i in coalition),sum(rows[i][1] for i in coalition))
  if sum(y[i] for i in coalition)<value:raise RuntimeError('coalition')
  coalitions+=1
for flat,y in payments.items():
 for j in range(6):
  if flat[j]<levels[-1]:
   larger=list(flat);larger[j]+=1
   if y[j//2]>payments[tuple(larger)][j//2]:raise RuntimeError('monotonicity')
   transitions+=1
print(json.dumps(dict(status='PASS',profiles=len(payments),coalition_checks=coalitions,adjacent_own_increases=transitions,arithmetic='Fraction',scope='finite corroboration of written all-real-profile three-owner proof')))
