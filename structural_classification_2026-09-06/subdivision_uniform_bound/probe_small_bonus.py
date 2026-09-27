from fractions import Fraction as F
from pathlib import Path
import json
from verify import instance
from raw_core import solve
out=[]
for q in (1,2,3,4):
 r,m,A,B,C=instance(q);M=F(1,100)
 mats=[A,C,[[M*int(i==j) for j in range(m)] for i in range(m)],B]
 result=solve([(0,1),(1,2),(2,3),(0,3)],mats,m,known_T=6*q+1+m*M)
 if result is None:raise RuntimeError('Unexpected empty core')
 out.append({'q':q,'M':str(M),**result})
 Path(__file__).with_name('SMALL_BONUS_PROFILES.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
 print(json.dumps({'q':q,'ratio':result['ratio']}),flush=True)
