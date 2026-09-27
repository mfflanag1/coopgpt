import affine_blocks as ab
import numpy as np,json
from scipy.optimize import linprog
from pathlib import Path
orig=ab.tb.structure
for same in (False,True):
 def positive(m,P):
  base=orig(m,P);L=[[max(1,v)for v in row]for row in base[4]];rb=[sum(L[b])+sum(b in bs for bs in base[6])-2 for b in range(5)]
  return (*base[:3],rb,L,*base[5:])
 ab.tb.structure=positive
 rows,rhs,eq,erhs,A,E,n=ab.build(same)
 r=linprog(np.zeros(n),A_ub=A,b_ub=rhs,A_eq=E,b_eq=erhs,bounds=(0,None),options={'time_limit':30})
 d={'same':same,'status':r.status,'message':r.message,'baseline':'all 15 leaf counts at least one'}
 if r.success:d['x']=r.x.tolist()
 Path(__file__).with_name('AFFINE_INTERIOR_'+str(same)+'.json').write_text(json.dumps(d)+'\n');print({k:v for k,v in d.items()if k!='x'},flush=True)
 ab.tb.structure=orig
