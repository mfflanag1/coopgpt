from pathlib import Path
from fractions import Fraction as F
import json
from family import construct
from raw_core import solve
r=construct(1,5);s=solve(r['edges'],r['matrices'],r['m'],k=5,known_T=r['T'])
if s is None or F(s['x'][r['target']])!=F(1,10)or F(s['H'][r['target']])!=1:raise RuntimeError('C5 full leximin replay failed')
Path(__file__).with_name('FULL_LEXIMIN_C5_Q1.json').write_text(json.dumps({'status':'PASS','target':r['target'],**s},indent=2,default=str)+'\n')
print(json.dumps({'status':'PASS','target_payoff':s['x'][r['target']],'target_ideal':s['H'][r['target']],'full_levels':s['levels']}))
