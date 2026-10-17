from fractions import Fraction as F
import itertools,json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
# K={(t,x,y): t>=|x|,t>=|y|}. At C=(1,x,y), common price (a,b,c).
# Coalition vertices solve K-intersection of translated K.
normals=np.array([[1,1,0],[1,-1,0],[1,0,1],[1,0,-1]],float)
def verts(C):
    A=np.concatenate([normals,-normals]);rhs=np.r_[np.zeros(4),-normals@C]
    out=[]
    for idx in itertools.combinations(range(8),3):
        B=A[list(idx)];
        if abs(np.linalg.det(B))<1e-8:continue
        v=np.linalg.solve(B,rhs[list(idx)])
        if np.min(A@v-rhs)>-1e-9 and not any(np.linalg.norm(v-w)<1e-8 for w in out):out.append(v)
    return out
vals=[0,.25,.5,.75,.9,.97] if len(sys.argv)<2 else [float(x) for x in sys.argv[1].split(',')]
# Full signed-permutation orbit grid; prune to x>=y>=0 using symmetry maps.
shapes=[(x,y) for x in vals for y in vals if x>=y]
Cs=[np.array([1.,x,y]) for x,y in shapes]
# Canonical symmetry, choosing any stabilizer is safe if enforce equalities.
def canonical(C):
    x,y=C[1:];sx=1 if x>=0 else -1;sy=1 if y>=0 else -1
    if abs(x)>=abs(y):return (abs(x),abs(y)),np.array([[1,0,0],[0,sx,0],[0,0,sy]])
    return (abs(y),abs(x)),np.array([[1,0,0],[0,0,sy],[0,sx,0]])
orbit=[]
for idx,C in enumerate(Cs):
 for swap in [False,True]:
  for sx,sy in itertools.product([-1,1],repeat=2):
   Q=np.array([[1,0,0],[0,0,sx],[0,sy,0]]) if swap else np.diag([1,sx,sy])
   cc=Q@C
   if not any(np.max(abs(cc-e[1]))<1e-10 for e in orbit):orbit.append((idx,cc,Q))
rows=[];rhs=[];meta=[]
def add(dic,rr,mm):rows.append(dic);rhs.append(rr);meta.append(mm)
for j,C in enumerate(Cs):
 add({3*j:-1},-1,('majorant_center',j))
 for r in itertools.product([-1,1],repeat=2):add({3*j:-1,3*j+1:r[0],3*j+2:r[1]},0,('ray',j,r))
 add({3*j+k:float(C[k]) for k in range(3)}|{3*len(Cs):-(1-max(C[1:]))},0,('budget',j))
 # stabilizers
 if C[1]==C[2]:
  for s in [-1,1]:add({3*j+1:s,3*j+2:-s},0,('stabilizer_diag',j))
 if C[2]==0:
  for s in [-1,1]:add({3*j+2:s},0,('stabilizer_zero',j))
 if C[1]==0:
  for s in [-1,1]:add({3*j+1:s},0,('stabilizer_center',j))
for hi,C in enumerate(Cs):
 for lo,L,Q in orbit:
  # maximum feasible scale obtained from four cone inequalities.
  ratios=[(r@C)/(r@L) for r in normals if r@L>1e-10]
  maxscale=min(ratios)
  for frac in [1,.5]:
   lam=maxscale*frac
   if lam<1e-8:continue
   LC=lam*L;D=C-LC
   for A in verts(LC):
    lowcoef=Q.T@A;highcoef=-(A+D)
    dic={}
    for k in range(3):
     dic[3*lo+k]=dic.get(3*lo+k,0)+lowcoef[k]
     dic[3*hi+k]=dic.get(3*hi+k,0)+highcoef[k]
    add(dic,0,('tcwm',hi,lo,lam,A.tolist(),Q.tolist()))
M=lil_matrix((len(rows),3*len(Cs)+1))
for r,row in enumerate(rows):
 for c,v in row.items():M[r,c]=v
objective=np.zeros(M.shape[1]);objective[-1]=1
res=linprog(objective,A_ub=M.tocsr(),b_ub=np.array(rhs),bounds=[(None,None)]*len(objective),method='highs')
print('shapes',len(Cs),'rows',len(rows),'success',res.success,'objective',res.fun,flush=True)
if res.success:
 for j,C in enumerate(Cs):print(C.tolist(),res.x[3*j:3*j+3].tolist())
 pos=[(i,float(d),meta[i]) for i,d in enumerate(res.ineqlin.marginals) if abs(d)>1e-8]
 print('dual support',len(pos))
 with open('/private/tmp/coopgpt-overnight-20261017/unrestricted/NORM_PRICE_FRESH_COMMON_LP_RESULT.json','w') as f:json.dump({'shapes':shapes,'x':res.x.tolist(),'dual':pos,'meta':meta,'rows':rows,'rhs':rhs},f)
