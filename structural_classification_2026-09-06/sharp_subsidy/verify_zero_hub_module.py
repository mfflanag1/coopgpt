from pathlib import Path
from fractions import Fraction as F
import json,sys
from sector_min_core import core_rows
from tree_certificate import check_cover,require

def verify(d):
 m=d['m'];P=[tuple(e) for e in d['P']];U=d['U'];edges,rows,_=core_rows(m,P);idx={e:k for k,e in enumerate(edges)}
 require(m==3 and P==[(1,2,0)] and d['zero_label']==0,'module scope')
 used={s*m+e[s] for e in P for s in range(3)};require(U==sorted(set(range(3*m))-used),'U')
 n=len(edges)+len(U)*(3*m+3);off=len(edges);stride=3*m+3;res=[F(0)]*n
 y=list(map(F,d['y']));z=list(map(F,d['z']));require(len(y)==len(U)*len(rows)+1 and min(y)>=0,'dual rows')
 require(len(z)==1+len(U),'dual equality rows')
 for j in range(m):
  for p in range(3):res[idx[p,j,j]]+=z[0]
 for p in range(3):res[idx[p,0,0]]+=y[-1]
 for k,i in enumerate(U):
  for v in range(3*m):res[off+k*stride+v]+=z[k+1]
  for r,(es,coef) in enumerate(rows):
   v=y[k*len(rows)+r]
   for e in es:res[e]+=v
   for j,c in coef.items():res[off+k*stride+j]+=v*c
 for a,b,c in P:
  for e in ((0,a,b),(1,a,c),(2,b,c)):res[idx[e]]-=1
 for k,i in enumerate(U):res[off+k*stride+i]-=F(1,3)
 require(min(res)>=0,'dual residual');require(sum(z)-1==F(1,18),'dual objective');require(y[-1]==F(17,18),'affine coefficient')
 require(len(d['weights'])==len(edges) and min(d['weights'])>=0,'primal weights')
 require(len(d['witnesses'])==len(U),'primal witness inventory')
 mats=[[[0]*m for _ in range(m)] for _ in range(3)]
 for (p,a,b),w in zip(edges,d['weights']):mats[p][a][b]=w
 T=sum(mats[p][j][j] for p in range(3) for j in range(m))
 require(T==18 and sum(mats[p][0][0] for p in range(3))==0,'primal normalization')
 H=[]
 for i,x in zip(U,d['witnesses']):
  require(sum(x)==T,'core total');check_cover(x,mats,m);H.append(x[i])
 W=sum(mats[0][a][b]+mats[1][a][c]+mats[2][b][c] for a,b,c in P)
 require((F(W)+sum(H)/F(3)-T)/T==F(1,18),'matching lower bound')
 # The universal upper and these feasible coordinate witnesses coincide.
 # Therefore larger actual original ideals cannot raise this objective.
 return {'status':'PASS','module_maximum':'1/18','affine_diagonal_coefficient':'17/18','dual_variables':len(y)+len(z),'primal_team_checks':len(U)*m**3}

if __name__=='__main__':
 root=Path(__file__).parent;p=root/'ZERO_HUB_MODULE.json'
 d=json.loads(p.read_text());print(json.dumps(verify(d)))
 bad=dict(d,y=['0']*len(d['y']))
 try:verify(bad)
 except ValueError:print('negative control PASS')
 else:raise ValueError('empty inequality dual accepted')
