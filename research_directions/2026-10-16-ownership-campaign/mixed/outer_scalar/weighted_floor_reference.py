"""Exact threshold-coalition floor; normalized unit hardware, rational reports.
This computes a proved lower bound on opposing capped accounts, not E itself.
"""
from fractions import Fraction as F
from pathlib import Path
import json

def weighted_floor(hardware,local_power,grid,omitted):
 h=tuple(tuple(F(x) for x in row) for row in hardware)
 l=tuple(tuple(F(x) for x in row) for row in local_power)
 p=tuple(F(x) for x in grid)
 n=len(p)
 if not n or len(h)!=n or len(l)!=n or omitted not in range(n):
  raise ValueError('owner arrays or omitted owner mismatch')
 m=len(h[0])
 if any(len(row)!=m for row in h+l):raise ValueError('branch arrays mismatch')
 if any(x<0 for row in h+l for x in row) or any(x<0 for x in p):
  raise ValueError('reports must be nonnegative')
 if sum((sum(row,F(0)) for row in h),F(0))!=1:
  raise ValueError('hardware must be normalized to one')
 ts=tuple(min(sum((h[k][j] for k in range(n)),F(0)),sum((l[k][j] for k in range(n)),F(0))) for j in range(m))
 upper=tuple(sum((min(ts[j],max(h[k][j],l[k][j])) for j in range(m)),F(0)) for k in range(n))
 u=tuple(min(x,F(1)) for x in p)
 w=tuple(min(F(1),(1-u[k])/upper[k]) if upper[k] else F(1) for k in range(n))
 owners=tuple(k for k in range(n) if k!=omitted)
 def value(coalition):
  return sum((min(sum((h[k][j] for k in coalition),F(0)),sum((l[k][j] for k in coalition),F(0))) for j in range(m)),F(0))
 previous=F(0);integral=F(0);layers=[]
 for weight in sorted({w[k] for k in owners if w[k]>0}):
  coalition=tuple(k for k in owners if w[k]>=weight)
  production=value(coalition)
  integral+=(weight-previous)*production
  layers.append(dict(weight=str(weight),coalition=coalition,value=str(production)))
  previous=weight
 fixed_grid=sum((u[k] for k in owners),F(0))
 penalty=sum((max(F(0),upper[k]+u[k]-1) for k in owners),F(0))
 return {'floor':fixed_grid+integral,'fixed_grid':fixed_grid,'weighted_production':integral,'grand_floor':min(F(1),sum((p[k] for k in owners),F(0))+value(owners)),'overlap_relaxation':fixed_grid+value(owners)-penalty,'upper':upper,'weights':w,'layers':layers}

def require(test,label):
 if not test:raise RuntimeError(label)

def main():
 cases=[]
 r=weighted_floor([[0],[F(1,2)],[F(1,2)],[0]],[[1],[0],[0],[1]],[0,F(3,4),0,0],0)
 require(r['floor']==F(3,2),'mixed cap weighted floor')
 require(r['grand_floor']==1,'mixed cap ordinary floor')
 require(r['floor']>r['grand_floor'],'strict truncation improvement')
 cases.append(('mixed_cap_strict_improvement',r))
 r=weighted_floor([[0],[0],[0],[1],[0]],[[0],[0],[0],[0],[1]],[0,2,2,0,0],0)
 require(r['floor']==3,'separated grid exact specialization')
 cases.append(('unbounded_grid_mass_representative',r))
 r=weighted_floor([[0],[1],[0]],[[0],[0],[0]],[0,F(1,3),2],0)
 require(r['floor']==F(4,3),'M zero endpoint')
 cases.append(('zero_local_output',r))
 for name,r in cases:
  require(r['floor']>=r['overlap_relaxation'],name+' overlap relaxation')
 out={'status':'PASS','cases':[{'name':name,**{k:str(v) if isinstance(v,F) else v for k,v in r.items() if k not in ('upper','weights')}} for name,r in cases], 'scope':'Exact reference computation and endpoint checks only; proof is GRID_WEIGHTED_COALITION_FLOOR.txt.'}
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
