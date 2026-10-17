#!/usr/bin/env python3
from fractions import Fraction as Q
from itertools import combinations,product
from pathlib import Path
import importlib.util,json,random
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v',HERE/'verify_two_sparse_lift.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
cases=[('path4',4,[(0,1),(1,2),(2,3)]),('star4',4,[(0,1),(0,2),(0,3)]),('triangle',3,[(0,1),(1,2),(2,0)]),('cycle4',4,[(0,1),(1,2),(2,3),(3,0)]),('path5',5,[(0,1),(1,2),(2,3),(3,4)])]
rng=random.Random(17100625);tested=0
for label,n,edges in cases:
 es=[(n,u,w) for u,w in edges];N=n+1;m=len(es);A=[[Q(int(i in e)) for i in range(N)] for e in es]
 for trial in range(100):
  lam=[Q(rng.randrange(1,11)) for _ in es];c=[sum(lam[k]*A[k][i] for k in range(m)) for i in range(N)]
  L=[[sum(A[k][i]*A[l][i]/c[i] for i in range(N)) for l in range(m)] for k in range(m)]
  for j in range(N):
   x=v.linear_solve(L,[A[k][j] for k in range(m)])
   if x is None:continue
   dp=[Q(1,3)/c[j]*(-int(i==j)+sum(A[k][i]*x[k] for k in range(m))/c[i]) for i in range(N)]
   derivative=Q(1,3)+sum(c[i]*min(dp[i],Q(0)) for i in range(N));tested+=1
   if derivative<0:
    print(json.dumps({'status':'EXACT_NEGATIVE_DERIVATIVE','case':label,'edges':es,'activity_weights':lam,'capacity':c,'increased_resource':j,'price_derivative':dp,'owner_support':[i for i in range(N) if dp[i]<0],'owner_payment_derivative':derivative,'tested':tested},default=str,indent=2));raise SystemExit
print(json.dumps({'status':'NO_VIOLATION_BOUNDED','tested':tested}))
