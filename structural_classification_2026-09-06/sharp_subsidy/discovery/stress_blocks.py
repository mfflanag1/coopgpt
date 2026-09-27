import sys,json,random,time
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
import two_hub_blocks as tb
original=tb.structure
rng=random.Random(7301)
results=[];start=time.monotonic()
for same in (False,True):
 m,P=tb.example(same,0);base=original(m,P)
 for case in range(250):
  L=[row[:]for row in base[4]]
  if case<15:L[case//3][case%3]+=1000
  else:
   for b in range(5):
    for s in range(3):L[b][s]+=rng.choice([0,0,1,2,10,100,1000])
  rb=[sum(L[b])+sum(b in bs for bs in base[6])-2 for b in range(5)]
  def replaced(m,P):return (*base[:3],rb,L,*base[5:])
  tb.structure=replaced
  types,stride,rows,rhs,eq,erhs,bounds,A,E=tb.model(m,P)
  r=linprog(np.zeros(len(bounds)),A_ub=A,b_ub=rhs,A_eq=E,b_eq=erhs,bounds=bounds,options={'time_limit':5})
  rec={'same':same,'case':case,'L':L,'status':int(r.status)};results.append(rec)
  if r.status!=0:
   print(json.dumps(rec),flush=True);Path(__file__).with_name('BLOCK_STRESS_FAILURE.json').write_text(json.dumps(rec));break
  if case%50==0:print(same,case,'feasible',round(time.monotonic()-start,2),flush=True)
 tb.structure=original
Path(__file__).with_name('BLOCK_STRESS_RESULTS.json').write_text(json.dumps(results)+'\n')
print('total',len(results),'nonzero',sum(r['status']!=0 for r in results),flush=True)
