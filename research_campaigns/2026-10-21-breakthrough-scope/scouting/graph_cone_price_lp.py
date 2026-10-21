"""Finite necessary homogeneous P4-cone price LP; discovery, not a theorem."""
import argparse
import itertools
import json
from pathlib import Path
import time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

parser=argparse.ArgumentParser()
parser.add_argument('--levels',default='0,.5,.9,.97')
parser.add_argument('--contract',choices=['TCWM','OUT'],default='OUT')
parser.add_argument('--output',required=True)
args=parser.parse_args()
normals=np.array([[1,1,0],[1,-1,0],[1,0,1],[1,0,-1]],float)
def value(C):return max(0.,C[0]-max(abs(C[1]),C[2]))
def verts(C):
    A=np.concatenate([normals,-normals]);rhs=np.r_[np.zeros(4),-normals@C]
    out=[]
    for idx in itertools.combinations(range(8),3):
        B=A[list(idx)]
        if abs(np.linalg.det(B))<1e-8:continue
        v=np.linalg.solve(B,rhs[list(idx)])
        if np.min(A@v-rhs)>-1e-9 and not any(np.linalg.norm(v-w)<1e-8 for w in out):out.append(v)
    return out
vals=[float(x) for x in args.levels.split(',')]
yvals=sorted(set(vals+[-x for x in vals]))
Cs=[np.array([1.,x,y]) for x in vals for y in yvals]
orbit=[]
for idx,C in enumerate(Cs):
    for sign in ([1,-1] if C[1] else [1]):
        Q=np.diag([1,sign,1]);cc=Q@C
        orbit.append((idx,cc,Q,[Q@A for A in verts(C)]))
rows=[];cols=[];data=[];rhs=[];meta=[]
def add(dic,bound,description):
    rr=len(rhs)
    for k,v in dic.items():
        if abs(v)>1e-14:rows.append(rr);cols.append(k);data.append(v)
    rhs.append(bound);meta.append(description)
for j,C in enumerate(Cs):
    add({3*j:-1},-1,('coverage_reserve',j))
    add({3*j:-1,3*j+2:1},-1,('coverage_middle',j))
    for sx,sy in itertools.product([-1,1],repeat=2):
        add({3*j:-1,3*j+1:sx,3*j+2:sy},0,('ray',j,sx,sy))
    add({3*j+k:float(C[k]) for k in range(3)}|{3*len(Cs):-value(C)},0,('budget',j))
    if C[1]==0:
        for sign in [-1,1]:add({3*j+1:sign},0,('reflection',j))
for hi,C in enumerate(Cs):
    for lo,L,Q,V in orbit:
        maxscale=min((r@C)/(r@L) for r in normals if r@L>1e-10)
        for frac in [1,.5]:
            lam=maxscale*frac
            if lam<1e-8:continue
            LC=lam*L;D=C-LC
            for unscaled in V:
                A=lam*unscaled
                lowcoef=Q.T@A;highcoef=-(A+D)
                dic={}
                for k in range(3):
                    dic[3*lo+k]=dic.get(3*lo+k,0)+lowcoef[k]
                    dic[3*hi+k]=dic.get(3*hi+k,0)+highcoef[k]
                gain=value(D) if args.contract=='OUT' else 0.
                add(dic,-gain,('restore',hi,lo,lam,A.tolist(),Q.diagonal().tolist(),gain))
M=coo_matrix((data,(rows,cols)),shape=(len(rhs),3*len(Cs)+1)).tocsr()
obj=np.zeros(M.shape[1]);obj[-1]=1
start=time.monotonic()
res=linprog(obj,A_ub=M,b_ub=np.array(rhs),bounds=[(None,None)]*len(obj),method='highs',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
report={'scope':'finite necessary homogeneous common-cone-price LP; floating output is not a theorem','contract':args.contract,'levels':vals,'shapes':[C.tolist() for C in Cs],'rows':len(rhs),'success':res.success,'message':res.message,'factor':res.fun,'seconds':time.monotonic()-start}
if res.success:
    report['prices']=res.x.tolist()
    support=np.flatnonzero(abs(res.ineqlin.marginals)>1e-9)
    report['dual']=[{'row':int(i),'weight':float(res.ineqlin.marginals[i]),'meta':meta[i],'coeffs':{str(int(k)):float(v) for k,v in zip(M.getrow(i).indices,M.getrow(i).data)},'rhs':rhs[i]} for i in support]
    report['max_residual']=float(np.max(M@res.x-np.array(rhs)))
Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['prices','shapes','dual']},indent=2))
print('dual rows',len(report.get('dual',[])))
