"""Reused floating selector implementation from the sealed preceding gate.
Only core and selector are called here; original exploratory driver retained for provenance.
"""
"""Exploratory floating-point LPs. Written certificates are separate."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
P=Path(__file__).parent
SEED=20261024
COUNTS={3:20,4:60,5:60,6:40,7:20,8:10}
def core(A):
 n=len(A); M=np.array([[(s>>i)&1 for i in range(n)] for s in range(1,2**n-1)],dtype=float)
 b=np.linalg.norm(A,axis=1); T=float(b.sum()-np.linalg.norm(A.sum(axis=0)))
 v=M@b-np.linalg.norm(M@A,axis=1)
 return M,v,T,b

def selector(M,v,T,which):
 n=M.shape[1]; active=list(range(n)); bounds=[(0,None)]*n; stages=[]
 while active:
  obj=np.zeros(n+1); obj[-1]=-1 if which=='ascending' else 1
  rows=np.zeros((len(M)+len(active),n+1)); rows[:len(M),:n]=-M
  rhs=np.concatenate([-v,np.zeros(len(active))])
  for j,i in enumerate(active):
   rows[len(M)+j,i]=-1 if which=='ascending' else 1
   rows[len(M)+j,-1]=1 if which=='ascending' else -1
  eq=np.zeros((1,n+1));eq[0,:n]=1
  r=linprog(obj,A_ub=rows,b_ub=rhs,A_eq=eq,b_eq=[T],bounds=bounds+[(0,None)],method='highs')
  if not r.success: raise RuntimeError(r.message)
  t=float(r.x[-1]); face=list(bounds)
  for i in active:face[i]=(t,face[i][1]) if which=='ascending' else (face[i][0],t)
  frozen=[]
  for i in active:
   c=np.zeros(n);c[i]=-1 if which=='ascending' else 1
   f=linprog(c,A_ub=-M,b_ub=-v,A_eq=np.ones((1,n)),b_eq=[T],bounds=face,method='highs')
   if not f.success:raise RuntimeError(f.message)
   if abs(f.x[i]-t)<1e-7*max(1,T):frozen.append(i)
  if not frozen:raise RuntimeError('no universally binding coordinate')
  for i in frozen:face[i]=(t,t)
  stages.append({'level':t,'fixed':frozen});bounds=face;active=[i for i in active if i not in frozen]
 x=np.array([u[0] for u in bounds]);err=max(abs(x.sum()-T),float(np.max(v-M@x)),0)
 if err>1e-6*max(1,T):raise RuntimeError('core residual')
 return x,stages,err

def calc(A):
 M,v,T,b=core(A)
 if T<=1e-10:return None
 x,sx,ex=selector(M,v,T,'ascending');z,sz,ez=selector(M,v,T,'descending')
 return {'exposures':A.astype(int).tolist(),'standalone':b.tolist(),'T':T,'x':x.tolist(),'z':z.tolist(),'rho':float(np.abs(x-z).sum()/T),'stages_x':sx,'stages_z':sz,'max_residual':max(ex,ez)}

def main():
 rng=np.random.default_rng(SEED); results=[]
 calibrations=[]
 for A in [np.array([[1,0],[-1,0]]),np.array([[3,0],[1,0],[-4,0]]),np.array([[3,0],[0,4],[-3,-4]]),np.array([[1,0],[-1,0],[0,1],[0,-1]])]:
  out=calc(A);calibrations.append(out)
  if out['rho']>1e-8:raise RuntimeError('coincidence calibration failed')
 for n,count in COUNTS.items():
  for rep in range(count):
   A=rng.integers(-5,6,size=(n-1,2));A=np.vstack([A,-A.sum(axis=0)])
   out=calc(A)
   if out is not None:out.update(n=n,rep=rep);results.append(out)
  best=max((r for r in results if r['n']==n),key=lambda r:r['rho'])
  print(json.dumps({'n':n,'cases':count,'max_rho':best['rho'],'witness':best['exposures']}),flush=True)
 payload={'evidence':'exploratory floating LP, not proof','seed':SEED,'counts':COUNTS,'calibrations':calibrations,'results':results,'best':max(results,key=lambda r:r['rho'])}
 (P/'exploration.json').write_text(json.dumps(payload,indent=2)+'\n')
if __name__=='__main__':main()
