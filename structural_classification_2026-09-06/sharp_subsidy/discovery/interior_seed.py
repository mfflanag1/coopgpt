from pathlib import Path
import json,numpy as np
from scipy.sparse import hstack,vstack,coo_matrix,csr_matrix
from scipy.optimize import linprog
import two_hub_blocks as tb
from scaled_extension import solve

def interior(same):
 m,P=tb.example(same,0);types,stride,rows,rhs,eq,erhs,bounds,A,E=tb.model(m,P);B=len(tb.structure(m,P)[4]);L=tb.structure(m,P)[4];rb=tb.structure(m,P)[3];n=len(bounds);lookup={tuple(t):k for k,t in enumerate(types)};ex=[];br=[]
 for k,(b,t,s)in enumerate(types):
  for c in range(B):ex.append({k*stride+c:-1,n:1});br.append(0)
  partner=lookup[b,t,3-t-s]
  ex.append({k*stride+b:1,partner*stride+b:1,n:1});br.append(1)
  row={k*stride+c:-rb[c]for c in range(B)};row[k*stride+b]-=1;row[partner*stride+b]=row.get(partner*stride+b,0)-1;row[n]=1;ex.append(row);br.append(-1)
 rr=[];cc=[];vv=[]
 for i,row in enumerate(ex):
  for j,v in row.items():rr.append(i);cc.append(j);vv.append(v)
 AA=vstack([hstack([A,csr_matrix((A.shape[0],1))]),coo_matrix((vv,(rr,cc)),shape=(len(ex),n+1))]).tocsr();obj=np.zeros(n+1);obj[-1]=-1;root=np.zeros(n+1)
 for k,(b,t,s)in enumerate(types):root[k*stride+b]=L[b][t]
 EE=vstack([hstack([E,csr_matrix((E.shape[0],1))]),csr_matrix(root.reshape(1,-1))]).tocsr()
 r=linprog(obj,A_ub=AA,b_ub=rhs+br,A_eq=EE,b_eq=erhs+[4],bounds=bounds+[(0,1)])
 print('interior',same,r.status,-r.fun if r.success else None,flush=True)
 if not r.success:return
 d={'name':'INTERIOR_'+str(same),'m':m,'P':P,'types':types,'stride':stride,'values':[str(float(v))for v in r.x[:-1]],'margin':-r.fun};Path(__file__).with_name(d['name']+'.json').write_text(json.dumps(d)+'\n')
 degree=tb.structure(m,P)[1];out=[]
 for j,g in enumerate(degree):
  if g==1:
   res,rec=solve(d,j);out.append(rec);print('extension',j,res.status,rec['scale'],flush=True)
 Path(__file__).with_name(d['name']+'_EXTENSIONS.json').write_text(json.dumps(out)+'\n')
if __name__=='__main__':
 for same in (False,True):interior(same)
