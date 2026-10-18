#!/usr/bin/env python3
"""Independent matrix construction and exact LP witness replay, no author imports."""
from fractions import Fraction as Q
from itertools import product
from random import Random
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.optimize import linprog
P=Path(__file__).resolve().parent;R=Random(20261018)
counts={'lp_primal_dual_pairs':0,'general_affine_cases':0,'capped_cases':0,'owner_map_coalition_cases':0,'linearity_restoration_checks':0}

def optimum(A,c,p):
 z=linprog(-np.array(list(map(float,p))),A_ub=np.array([[float(v) for v in row] for row in A]),b_ub=np.array(list(map(float,c))),bounds=(0,None),method='highs')
 assert z.success,z.message
 x=[Q(float(v)).limit_denominator(10**8) for v in z.x];y=[Q(float(-v)).limit_denominator(10**8) for v in z.ineqlin.marginals]
 assert min(x+y)>=0
 assert all(sum(row[j]*x[j] for j in range(len(p)))<=cap for row,cap in zip(A,c))
 assert all(sum(A[i][j]*y[i] for i in range(len(c)))>=p[j] for j in range(len(p)))
 val=sum(p[j]*x[j] for j in range(len(p)));assert val==sum(c[i]*y[i] for i in range(len(c)))
 counts['lp_primal_dual_pairs']+=1;return val

def gadget(A,c,profits,M):
 d=len(c);n=len(profits);cols=[];rhs=list(c);baseline=Q(0)
 for e in range(n):
  vs=[v for v in range(d) if A[v][e]>0];r=len(vs);stages=[]
  for v in vs:
   stages.append(len(cols));cols.append(({v:A[v][e]},profits[e]))
  for k in range(r-1):
   left=len(rhs);rhs.append(M[e]);right=len(rhs);rhs.append(M[e]);cols[stages[k]][0][left]=1;cols[stages[k+1]][0][right]=1
   cols.append(({left:Q(1),right:Q(1)},profits[e]))
  baseline+=profits[e]*(r-1)*M[e]
 mat=[[Q(col.get(i,0)) for col,p in cols] for i in range(len(rhs))];pp=[p for col,p in cols]
 assert all(1<=sum(v>0 for v in col.values())<=3 for col,p in cols)
 return mat,rhs,pp,baseline

for case in range(18):
 d=4+case%3;n=2+case%2;A=[[Q(R.randrange(5),1+R.randrange(2)) if R.random()<.75 else Q(0) for e in range(n)] for v in range(d)]
 for e in range(n):
  if not any(A[v][e] for v in range(d)):A[e%d][e]=1
 profits=[Q(R.randrange(1,5),R.randrange(1,4)) for e in range(n)]
 reports=[[Q(R.randrange(4),R.randrange(1,4)) for v in range(d)] for i in range(3)];extra=[[Q(R.randrange(3),R.randrange(1,4)) for v in range(d)] for i in range(3)];ends=[[reports[i][v]+extra[i][v] for v in range(d)] for i in range(3)]
 supp=[[v for v in range(d) if A[v][e]] for e in range(n)]
 def mm(b):return [sum((b[v]/A[v][e] for v in supp[e]),Q(0))/len(supp[e]) for e in range(n)]
 for i in range(3):assert mm(ends[i])==[x+y for x,y in zip(mm(reports[i]),mm(extra[i]))];counts['linearity_restoration_checks']+=1
 for mask in range(8):
  C=[i for i in range(3) if mask>>i&1];c=[sum((reports[i][v] for i in C),Q(0)) for v in range(d)];f=optimum(A,c,profits)
  for mode in ['linear','constant']:
   source=reports if mode=='linear' else ends;M=[sum((mm(source[i])[e] for i in C),Q(0)) for e in range(n)];AA,cc,pp,B=gadget(A,c,profits,M);g=optimum(AA,cc,pp);assert g==B+f;counts['general_affine_cases']+=1;counts['owner_map_coalition_cases']+=1
  # Deliberately arbitrary caps, including ones smaller than natural bottlenecks.
  M=[Q(R.randrange(3),R.randrange(1,4)) for e in range(n)];Ac=[list(row) for row in A];capc=list(c)
  for e in range(n):
   if len(supp[e])>1:Ac.append([Q(int(j==e)) for j in range(n)]);capc.append(M[e])
  fm=optimum(Ac,capc,profits);AA,cc,pp,B=gadget(A,c,profits,M);g=optimum(AA,cc,pp);assert g==B+fm;counts['capped_cases']+=1
result={'status':'PASS','counts':counts,'proof_obligations':'Actual expanded matrices, arbitrary rational coefficients/profits, shared original rows, zero and capped profiles, every coalition of three mixed owners, both report maps, exact rational primal-dual equality. No funding-transfer theorem inferred.'}
(P/'INDEPENDENT_AFFINE_LP.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
