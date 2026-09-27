"""Floating full-objective cross-check of the synthesized markets."""
import json
from fractions import Fraction
from math import lcm
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from sparse_fixed_probe import layout

def run(name):
 d=json.loads(Path(__file__).with_name(name+'.json').read_text());m=d['m'];support,idx,U,teams=layout(m,d['P'])
 w=np.array(d['primal_integers'][:len(support)],dtype=float)/d['primal_scale']
 rhs=np.array([sum(w[e]for e in es)for t,es in teams]);rr=[];cc=[]
 for k,(t,es)in enumerate(teams):
  for s,j in enumerate(t):rr.append(k);cc.append(s*m+j)
 A=coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(teams),3*m)).tocsr()
 H=[]
 for i in range(3*m):
  c=np.zeros(3*m);c[i]=-1
  r=linprog(c,A_ub=-A,b_ub=-rhs,A_eq=np.ones((1,3*m)),b_eq=[1],bounds=(0,None))
  if not r.success:raise ValueError(r.message)
  H.append(-r.fun)
 r=linprog(np.ones(3*m),A_ub=-A,b_ub=-rhs,bounds=[(v/3,None)for v in H])
 if not r.success:raise ValueError(r.message)
 out=dict(pattern=name,subsidy=r.fun-1,H=H,y=r.x.tolist(),evidence='floating discovery only, full original core and all nonzero triple inequalities')
 y=[Fraction(float(v)).limit_denominator(10000)for v in r.x];scale=lcm(*(v.denominator for v in y))
 d['protected_payoff_scale']=scale;d['protected_payoff_integers']=[int(v*scale)for v in y]
 Path(__file__).with_name(name+'.json').write_text(json.dumps(d)+'\n')
 Path(__file__).with_name(name+'_ACTUAL.json').write_text(json.dumps(out)+'\n')
 print(json.dumps({k:out[k]for k in ['pattern','subsidy','evidence']}),flush=True)
if __name__=='__main__':
 for name in ['CYCLIC_WEIGHTS_2','CYCLIC_WEIGHTS_3','CYCLIC_WEIGHTS_4','MULTICYCLE_k33','MULTICYCLE_prism','MULTICYCLE_cube']:run(name)
