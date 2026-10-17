from fractions import Fraction as Q
from itertools import combinations
import numpy as np
from scipy.spatial import ConvexHull
import random,json
from pathlib import Path
R=random.Random(314171)
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def det(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def solve(mat,rhs):
 D=det(*mat)
 if not D:return None
 return tuple(det(*[tuple(rhs[i] if k==j else mat[i][k] for k in range(3)) for i in range(3)])/D for j in range(3))
def volume(hs):
 vs=set()
 for trip in combinations(hs,3):
  x=solve([a for a,b in trip],[b for a,b in trip])
  if x is not None and all(dot(a,x)<=b for a,b in hs):vs.add(x)
 if len(vs)<4:return Q(0)
 vs=sorted(vs)
 try:h=ConvexHull(np.array(vs,dtype=float))
 except Exception:return Q(0)
 center=tuple(sum(v[j] for v in vs)/len(vs) for j in range(3))
 total=Q(0)
 for tri in h.simplices:
  vec=[tuple(vs[i][j]-center[j] for j in range(3)) for i in tri]
  total+=abs(det(*vec))/6
 return total

def vertices(a,b,w):
 lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0)),*zip(a,b,w)];vs=set()
 for (aa,bb,ww),(aaa,bbb,www) in combinations(lines,2):
  D=aa*bbb-aaa*bb
  if D:
   p=(ww*bbb-www*bb)/D;q=(aa*www-aaa*ww)/D
   if min(p,q)>=0:vs.add((p,q))
 return [(p,q)+tuple(max(Q(0),wj-aj*p-bj*q) for aj,bj,wj in zip(a,b,w)) for p,q in sorted(vs)]
def rule(C,gs):
 P,Qq,*c=C
 aff=[(P*g[0],Qq*g[1],dot(c,g[2:])) for g in gs]
 ans=[Q(0)]*len(C);vv=[]
 cube=[]
 for j in range(3):
  cube.append((tuple(Q(k==j) for k in range(3)),Q(1)))
  cube.append((tuple(Q(-1 if k==j else 0) for k in range(3)),Q(0)))
 for idx,g in enumerate(gs):
  hs=cube+[(tuple(x-y for x,y in zip(aff[idx],aa)),Q(0)) for k,aa in enumerate(aff) if k!=idx]
  v=volume(hs);vv.append(v)
  for j in range(len(C)):ans[j]+=v*g[j]
 assert sum(vv)==1,(C,vv)
 return ans,vv
A=(Q(1),Q(1),Q(1,4));B=(Q(1),Q(1,4),Q(1));A=tuple(a/100 for a in A);W=tuple(a+b for a,b in zip(A,B));gs=vertices(A,B,W)
profiles=[(Q(1),Q(1),Q(1,4),Q(4),Q(1)),(Q(1,4),)*5,(Q(1),Q(1),Q(1),Q(1),Q(1))]
for C in profiles:
 C=(C[0]/100,)+C[1:]
 p,v=rule(C,gs)
 for j in (0,1,2):
  CC=list(C);delta=Q(1,300) if j==0 else Q(1,3);CC[j]+=delta;pp,vv=rule(CC,gs)
  loss=sum((x*max(Q(0),a-b) for x,a,b in zip(C,p,pp)),Q(0));gain=delta*pp[j]
  print('profile',list(map(str,C)),'restore',j,'loss',str(loss),'gain',str(gain),'PASS',gain>=loss,flush=True)
  if loss>gain:
   print('old',p,'new',pp,'oldvol',v,'newvol',vv);raise SystemExit
