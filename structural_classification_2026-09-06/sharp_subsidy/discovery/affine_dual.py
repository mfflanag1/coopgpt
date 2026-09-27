import affine_blocks as ab
import numpy as np,json
from scipy.sparse import hstack,csr_matrix
from scipy.optimize import linprog
from pathlib import Path
from fractions import Fraction as F
for same in (False,True):
 rows,rhs,eq,erhs,A,E,n=ab.build(same);nr=len(rows);ne=len(eq)
 C=hstack([A.T,E.T],format='csr');b=np.array(rhs+erhs)
 r=linprog(np.zeros(nr+ne),A_ub=-C,b_ub=np.zeros(n),A_eq=csr_matrix(b.reshape(1,-1)),b_eq=[-1],bounds=[(0,None)]*nr+[(None,None)]*ne,options={'time_limit':30})
 print(same,r.status,flush=True)
 if not r.success:continue
 v={j:F(float(x)).limit_denominator(1000000)for j,x in enumerate(r.x)if abs(x)>1e-9};lhs=[F(0)]*n;bound=F(0)
 for j,w in v.items():
  row=(rows+eq)[j];bound+=w*int(b[j])
  for k,a in row.items():lhs[k]+=w*a
 if not all(x>=0 for x in lhs)or bound>=0 or any(w<0 for j,w in v.items()if j<nr):raise ValueError('inexact dual')
 out={'same':same,'multipliers':[[j,str(w)]for j,w in sorted(v.items())],'bound':str(bound),'support':len(v)}
 Path(__file__).with_name('AFFINE_DUAL_'+str(same)+'.json').write_text(json.dumps(out)+'\n');print(out,flush=True)
