import sys,json
from itertools import product,permutations
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0,'/private/tmp/coopgt-simultaneous-20260907')
from certificates import independent_triangle,ideals

def lp(matrices,m,known_T=None,known_H=None):
 teams=list(product(range(m),repeat=3));n=3*m
 W=np.array([matrices[0][a][b]+matrices[1][a][c]+matrices[2][b][c]for a,b,c in teams],dtype=float)
 A=np.zeros((len(teams),n))
 for row,t in enumerate(teams):
  for k,j in enumerate(t):A[row,k*m+j]=1
 if known_T is None:
  perms=list(permutations(range(m)));T=max(sum(W[teams.index((a,p[a],q[a]))]for a in range(m))for p in perms for q in perms)
 else:T=known_T
 core=linprog(np.ones(n),A_ub=-A,b_ub=-W,bounds=(0,None),method='highs')
 if not core.success or abs(core.fun-T)>1e-7:return None
 H=[]
 if known_H is None:
  for i in range(n):
   c=np.zeros(n);c[i]=-1
   r=linprog(c,A_ub=-A,b_ub=-W,A_eq=np.ones((1,n)),b_eq=[T],bounds=(0,None),method='highs')
   if not r.success:raise ValueError(r.message)
   H.append(-r.fun)
 else:H=list(map(float,known_H))
 r=linprog(np.ones(n),A_ub=-A,b_ub=-W,bounds=[(h/3,None)for h in H],method='highs')
 if not r.success:raise ValueError(r.message)
 return {'T':T,'H':H,'s':r.fun-T,'ratio':(r.fun-T)/T,'y':r.x.tolist(),'dual':[(teams[i],-v)for i,v in enumerate(r.ineqlin.marginals)if abs(v)>1e-8]}
if __name__=='__main__':
 for q in range(1,11):
  g=independent_triangle(q);r=lp(g['matrices'],g['m'],g['T'],ideals(q))
  print(json.dumps({'q':q,**r}),flush=True)
