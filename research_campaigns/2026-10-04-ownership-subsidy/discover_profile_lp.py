from itertools import product
from fractions import Fraction as F
from pathlib import Path
import argparse,json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def worth(c,m):
 return min(sum(c[i] for i in (0,1) if m>>i&1),sum(c[i] for i in (2,3) if m>>i&1))
def run(grid):
 ps=list(product(grid,repeat=4));index={p:j for j,p in enumerate(ps)}
 beta=4*len(ps); rows=[];cols=[];data=[];rhs=[];desc=[]
 def add(terms,b,d):
  j=len(rhs)
  for i,a in terms: rows.append(j);cols.append(i);data.append(-a)
  rhs.append(-b);desc.append(d)
 for j,c in enumerate(ps):
  t=worth(c,15)
  add([(beta,t)]+[(4*j+i,-1) for i in range(4)],-t,{'kind':'budget','profile':c})
  for m in range(1,16):
   v=worth(c,m)
   if v: add([(4*j+i,1) for i in range(4) if m>>i&1],v,{'kind':'cover','profile':c,'coalition':m})
  for i in range(4):
   k=grid.index(c[i])
   if k:
    low=list(c);low[i]=grid[k-1];q=index[tuple(low)]
    add([(4*j+i,1),(4*q+i,-1)],0,{'kind':'monotone','profile':c,'low_profile':low,'owner':i})
 mat=coo_matrix((data,(rows,cols)),shape=(len(rhs),beta+1)).tocsr()
 cost=np.zeros(beta+1);cost[-1]=1
 res=linprog(cost,A_ub=mat,b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':120})
 report={'grid':grid,'profiles':len(ps),'rows':len(rhs),'status':res.message,'objective':res.fun}
 if res.success:
  support=[]
  for d,w in zip(desc,-res.ineqlin.marginals):
   if w>1e-9: support.append(dict(d,multiplier=str(F(float(w)).limit_denominator(1000000))))
  report['dual_support']=support
  report['objective_rational_guess']=str(F(float(res.fun)).limit_denominator(1000000))
 return report
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--grid',default='0,1,2');parser.add_argument('--output',required=True);a=parser.parse_args()
 r=run(list(map(int,a.grid.split(','))));Path(a.output).write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k!='dual_support'});print('support',len(r.get('dual_support',[])))
