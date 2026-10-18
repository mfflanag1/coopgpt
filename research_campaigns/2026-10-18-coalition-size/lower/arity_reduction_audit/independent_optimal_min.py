#!/usr/bin/env python3
"""Independent expanded LP and sparse shared-lift witness verification."""
from fractions import Fraction as Q
from pathlib import Path
from random import Random
import json, ast, hashlib
import numpy as np
from scipy.optimize import linprog
P=Path(__file__).resolve().parent;SRC=P.parent.parent/'constructive'/'arity_reduction';rng=Random(20261019);count=0

def solve(A,c,p):
 z=linprog(-np.array(list(map(float,p))),A_ub=np.array([[float(v) for v in row] for row in A]),b_ub=np.array(list(map(float,c))),bounds=(0,None),method='highs');assert z.success
 x=[Q(float(v)).limit_denominator(10**8) for v in z.x];y=[Q(float(-v)).limit_denominator(10**8) for v in z.ineqlin.marginals];assert min(x+y)>=0
 assert all(sum(a*t for a,t in zip(row,x))<=cap for row,cap in zip(A,c))
 assert all(sum(A[i][j]*y[i] for i in range(len(c)))>=p[j] for j in range(len(p)))
 value=sum(a*b for a,b in zip(p,x));assert value==sum(a*b for a,b in zip(c,y));return value
for r in range(3,9):
 beta=Q(1,r*(r-2));rows=[(i,j) for i in range(r) for j in range(r) if i!=j]
 A=[[Q(int(col==i or col==r+j)) for col in range(2*r)] for i,j in rows];profits=[beta]*r+[(r-1)*beta]*r
 assert all(sum(row[j]>0 for row in A)==r-1 for j in range(2*r))
 for case in range(5):
  owners=[[Q(rng.randrange(5),rng.randrange(1,5)) for i in range(r)] for o in range(4)]
  for C in range(16):
   c=[sum((owners[o][i] for o in range(4) if C>>o&1),Q(0)) for i in range(r)];caps=[c[i] for i,j in rows]
   val=solve(A,caps,profits);assert val==beta*sum(c)+min(c);count+=1
 # Recompute rank-deletion equality at the pure-owner unanimity seed.
 B=r*beta;assert B+r==(r-1)*(B+1) and B==Q(1,r-2)
raw=(SRC/'shared_lift_r4_counterexample.json').read_bytes();w=json.loads(raw);caps={ast.literal_eval(k):Q(v) for k,v in w['row_capacities'].items()};price=Q(w['dual_price_every_row']);columns=[]
for name,col in w['columns'].items():
 rows=[ast.literal_eval(t) for t in col['rows']];profit=Q(col['profit']);amount=Q(col['primal_amount']);assert len(rows)==len(set(rows))==3 and amount>=0
 assert all(row in caps for row in rows) and len(rows)*price>=profit;columns.append((rows,profit,amount))
assert all(sum(x for used,p,x in columns if row in used)<=cap for row,cap in caps.items())
primal=sum(p*x for used,p,x in columns);dual=sum(caps.values())*price
assert primal==dual==Q(3,2) and Q(w['baseline'])==Q(1,2) and primal-Q(w['baseline'])==1
result={'status':'PASS','independent_expanded_LP_pairs':count,'r_range':[3,8],'coalitions_per_four_owner_instance':16,'shared_lift_r4_exact_value':str(primal),'shared_lift_r4_baseline':w['baseline'],'shared_witness_sha256':hashlib.sha256(raw).hexdigest(),'scope':'Sampled exact LP certificates supplement the audited all-real proof. No general overlapping reduction or ordinary funding transfer is inferred.'}
(P/'INDEPENDENT_OPTIMAL_MIN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
