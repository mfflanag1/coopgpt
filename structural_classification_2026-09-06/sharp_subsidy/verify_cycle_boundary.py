"""Exact certificate for loss under a prescribed cycle-pair zero restriction."""
from itertools import product
from fractions import Fraction as F
from pathlib import Path
import json
from verify_cyclic_patterns import check

def upper(d):
 m=d['m'];P=d['P'];pairs=lambda t:((0,t[0],t[1]),(1,t[0],t[2]),(2,t[1],t[2]))
 support=sorted({e for t in [(j,j,j)for j in range(m)]+P for e in pairs(t)})
 idx={e:i for i,e in enumerate(support)};off=len(support)
 U=sorted(set(range(3*m))-{s*m+j for t in P for s,j in enumerate(t)})
 teams=[(t,[idx[e]for e in pairs(t)if e in idx]) for t in product(range(m),repeat=3)]
 teams=[(t,es)for t,es in teams if es]
 residual=[F(0)]*(off+len(U)*3*m)
 for t in P:
  for e in pairs(t):residual[idx[e]]+=1
 for k,i in enumerate(U):residual[off+k*3*m+i]=F(1,3)
 lam=list(map(F,d['ineq']));nu=list(map(F,d['eq']))
 if len(lam)!=len(U)*len(teams) or len(nu)!=len(U)+1 or any(z<0 for z in lam):raise ValueError('dual dimensions/sign')
 for row,z in enumerate(lam):
  k,r=divmod(row,len(teams));t,es=teams[r]
  for e in es:residual[e]-=z
  for s,j in enumerate(t):residual[off+k*3*m+s*m+j]+=z
 for j in range(m):
  for s in range(3):residual[idx[s,j,j]]-=nu[0]
 for k in range(len(U)):
  for j in range(3*m):residual[off+k*3*m+j]-=nu[k+1]
 zero=idx[tuple(d['zero_pair'])]
 return sum(nu)-1+sum(max(F(0),z)for j,z in enumerate(residual)if j!=zero)

def verify(d):
 if d['m']!=6 or d['P']!=[[1,0,2],[3,4,1],[0,5,4]] or d['zero_pair']!=[1,0,4]:raise ValueError('scope mismatch')
 unrestricted=check(d['unrestricted'],check_protected=False)
 if d['unrestricted']['m']!=d['m'] or d['unrestricted']['P']!=d['P']:raise ValueError('different support')
 lower=F(unrestricted['fixed_pattern_lower']);u=upper(d)
 if lower!=F(2,9) or not 0<=u<lower:raise ValueError('strict loss not proved')
 return {'status':'PASS','unrestricted_lower':str(lower),'restricted_upper':str(u),'strict_loss_at_least':str(lower-u),'scope':'prescribed AC(0,4)=0 with all other supported pair weights free; not an adaptive-edge no-go'}
if __name__=='__main__':
 d=json.loads(Path(__file__).with_name('CYCLE_BOUNDARY_COUNTEREXAMPLE.json').read_text());print(json.dumps(verify(d)))
 bad=dict(d,ineq=['0']*len(d['ineq']),eq=['0']*len(d['eq']))
 try:verify(bad)
 except ValueError:pass
 else:raise ValueError('empty dual accepted')
