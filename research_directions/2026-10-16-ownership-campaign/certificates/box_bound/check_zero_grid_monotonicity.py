#!/usr/bin/env python3
"""Bounded falsification of a narrower P=0 composition-monotonicity lemma."""
import sys,random,json
from pathlib import Path
sys.path.insert(0,'/private/tmp/coopgpt-ownership-20261016/mixed')
from verify_envelope_bounds import evaluate
rng=random.Random(161091);count=0;best=None
for case in range(5000):
 n=rng.randrange(2,7);m=rng.randrange(1,5)
 rr=[[0.]+[rng.choice([0.,0.,.125,.25,.5,1.,2.,5.,20.]) for _ in range(2*m)] for _ in range(n)]
 v=evaluate(rr)
 for i in range(n):
  for j in range(1,1+2*m):
   if not rr[i][j]:continue
   small=[row.copy() for row in rr];small[i][j]*=.75
   sv=evaluate(small);count+=1;gain=sv['N'][i]-v['N'][i]
   if gain>1e-10*max(1.,v['F']):
    obj={'rows':rr,'owner':i,'coordinate':j,'underreported_value':small[i][j],'full':v,'altered':sv,'gain':gain,'case':case}
    if best is None or gain/v['F']>best['gain']/best['full']['F']:best=obj
 if best is not None and case>1000:break
out={'scope':'FLOAT DIAGNOSTIC; a failure refutes only the P=0 monotonicity sublemma','checks':count,'witness':best}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
