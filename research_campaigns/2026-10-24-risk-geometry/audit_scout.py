from fractions import Fraction as Q
import json
from pathlib import Path
P=Path(__file__).parent
cases=[([5,1,-3,-3],[Q(10,3),Q(2),Q(10,3),Q(10,3)]),([2,1,-1,-1,-1],[Q(2),Q(1),Q(1),Q(1),Q(1)]),([2,1,-1,-1,-1],[Q(4,3),Q(2,3),Q(4,3),Q(4,3),Q(4,3)])]
checks=0
for a,y in cases:
 if sum(y)!=sum(abs(t)for t in a):raise AssertionError('efficiency')
 for s in range(1<<len(a)):
  ix=[i for i in range(len(a))if(s>>i)&1]
  v=sum(abs(a[i])for i in ix)-abs(sum(a[i]for i in ix))
  if sum(y[i]for i in ix)<v:raise AssertionError('core')
  checks+=1
r={'exact_coalition_checks':checks,'n4_pair_23_actual_norm':abs(1-3),'n4_reported_norm':1,'n4_correct_selectors':['10/3','2','10/3','10/3'],'n5_calibration_distance':'1/3','evidence':'Exact feasibility; selector optimality proved in SCOUT_DISPOSITION.txt'}
(P/'scout_checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
