from fractions import Fraction as F
from itertools import combinations,product
import numpy as np
normals=np.array([[1,1,0],[1,-1,0],[1,0,1],[1,0,-1]],float)
def vertices(C):
 A=np.concatenate([normals,-normals]);rhs=np.r_[np.zeros(4),-normals@C];out=[]
 for ids in combinations(range(8),3):
  M=A[list(ids)]
  if abs(np.linalg.det(M))<1e-7:continue
  u=np.linalg.solve(M,rhs[list(ids)])
  if min(A@u-rhs)>-1e-7 and not any(np.linalg.norm(u-v)<1e-8 for v in out):out.append(u)
 return out
worst=(1,None)
for x in np.linspace(.01,.99,50):
 for y in np.linspace(0,x,30):
  H=1-y*y; aa=(1-x)/H;at=(2*x-1-y*y)/H**2
  for u,v,w in vertices(np.array([1.,x,y])):
   Z=v-y*w
   gt=1+aa*v+Z*at
   gx=-1+aa-Z/H
   gy=-aa*(y+w)+2*y*aa*Z/H
   slack=gt-abs(gx)-abs(gy)
   if slack<worst[0]:worst=(slack,(x,y,u,v,w,gt,gx,gy))
print(worst)
