"""Exploratory symmetry quotient on capacities 1 and 2; not an exact certificate.
The all-k conclusions rely on LOWER_BOUND_FAMILIES.txt, not these numerical optima.
"""
import hashlib
import json
from pathlib import Path
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from fractions import Fraction

def solve(k):
 states=[(r,s,k-r-s) for r in range(k+1) for s in range(k-r+1)]
 ids={};desc=[]
 for state in states:
  r,s,t=state
  for role,yes in [('a',r),('b',s),('d',s),('e',t)]:
   if yes:ids[(state,role)]=len(ids)
 beta=len(ids);rows=[];cols=[];data=[];rhs=[]
 def add(state,terms,b,label):
  n=len(rhs)
  for var,coef in terms:
   if coef:rows.append(n);cols.append(var);data.append(-coef)
  rhs.append(-b);desc.append((state,label))
 for state in states:
  r,s,t=state;T=2 if r else (3 if s else 4)
  def term(role,m):return (ids[(state,role)],m) if m else (beta,0)
  add(state,[term('a',-2*r),term('b',-s),term('d',-s),term('e',-2*t),(beta,T)],-T,'budget')
  add(state,[term('a',r),term('b',s),term('e',t)],1,'cover1b')
  add(state,[term('a',r),term('d',s),term('e',t)],1,'cover1d')
  add(state,[term('a',2*r),term('d',s),term('e',t)],2,'cover2')
  if not r:add(state,[term('b',s),term('d',s),term('e',2*t)],3,'cover3')
  if not r and not s:add(state,[term('e',2*t)],4,'cover4')
  if r:add(state,[(ids[((r-1,s+1,t),'d')],1),term('a',-1)],0,'mono_a_d')
  if s:add(state,[(ids[((r,s-1,t+1),'e')],1),term('b',-1)],0,'mono_b_e')
 matrix=coo_matrix((data,(rows,cols)),shape=(len(rhs),beta+1)).tocsr();obj=[0]*beta+[1]
 result=linprog(obj,A_ub=matrix,b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':120})
 if not result.success:raise RuntimeError(result.message)
 return dict(k=k,states=len(states),objective=result.fun,rational_guess=str(Fraction(result.fun).limit_denominator(10**6)),dual_support=[dict(state=d[0],kind=d[1],weight=str(Fraction(float(w)).limit_denominator(10**6))) for d,w in zip(desc,-result.ineqlin.marginals) if w>1e-8])

if __name__=='__main__':
 reports=[solve(k) for k in [2,3,4,5,6,8,10,16,32,64]]
 result=dict(status='DISCOVERY_ONLY',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),runs=reports,limitation='No claim of exact primal optimality or independently verified quotient duals; see analytic proof.')
 Path(__file__).with_name('SYMMETRY_DISCOVERY.json').write_text(json.dumps(result,indent=2)+'\n')
 for r in reports:print(r['k'],r['rational_guess'])
