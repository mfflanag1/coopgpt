"""Discovery: per-coordinate core LPs of two already-opened diagnostic markets."""
import json,sys
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

root=Path(__file__).resolve().parents[1]
out={}
for name in ('CW-01','CW-04'):
 d=json.loads((root/'paired'/f'{name}_relaxed.json').read_text());m=d['m'];w=[[[Q(v) for v in row] for row in mat] for mat in d['matrices']]
 teams=list(product(range(m),repeat=3));val=[w[0][a][b]+w[1][a][c]+w[2][b][c] for a,b,c in teams]
 diag=[w[0][j][j]+w[1][j][j]+w[2][j][j] for j in range(m)]
 rr=[];cc=[]
 for k,t in enumerate(teams):
  for s,j in enumerate(t):rr.append(k);cc.append(s*m+j)
 A=coo_matrix((-np.ones(len(rr)),(rr,cc)),shape=(len(teams),3*m)).tocsr();E=np.zeros((m,3*m))
 for j in range(m):E[j,[j,m+j,2*m+j]]=1
 U=sorted(set(range(3*m))-{s*m+t[s] for t in d['P'] for s in range(3)})
 rows=[]
 for i in U:
  c=np.zeros(3*m);c[i]=-1
  res=linprog(c,A_ub=A,b_ub=-np.array(list(map(float,val))),A_eq=E,b_eq=list(map(float,diag)),bounds=(0,None),options={'time_limit':60})
  if not res.success:raise ValueError(res.message)
  x=[Q(float(v)).limit_denominator(10**6) for v in res.x]
  lam=[max(Q(0),Q(float(-v)).limit_denominator(10**6)) for v in res.ineqlin.marginals]
  nu=[Q(float(-v)).limit_denominator(10**6) for v in res.eqlin.marginals]
  if min(x)<0 or any(sum(x[s*m+j] for s,j in enumerate(t))<v for t,v in zip(teams,val)) or any(sum(x[s*m+j] for s in range(3))!=diag[j] for j in range(m)):raise ValueError('primal recovery')
  coeff=[nu[j%m] for j in range(3*m)]
  for t,mass in zip(teams,lam):
   for s,j in enumerate(t):coeff[s*m+j]-=mass
  if any(coeff[j] < int(j==i) for j in range(3*m)):raise ValueError('dual recovery')
  upper=sum(v*z for v,z in zip(nu,diag))-sum(v*z for v,z in zip(lam,val))
  if x[i]!=upper:raise ValueError('gap')
  rows.append({'target':i,'H':str(x[i]),'relaxed_h':d['h'][i],'witness':list(map(str,x)),'dual_teams':[[*t,str(mass)] for t,mass in zip(teams,lam) if mass],'dual_diagonal':list(map(str,nu))})
 out[name]={'m':m,'results':rows,'scope':'fixed diagnostic market coordinate ideals only; exact generator checks, independent review pending'}
 print(name,[(r['target'],r['H'],len(r['dual_teams'])) for r in rows],flush=True)
(root/'interpretation/DIAGNOSTIC_IDEALS.json').write_text(json.dumps(out,indent=2)+'\n')
