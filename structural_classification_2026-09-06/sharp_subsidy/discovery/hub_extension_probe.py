from pathlib import Path
from fractions import Fraction as F
import json
import numpy as np
from scipy.sparse import vstack,coo_matrix,csr_matrix
from scipy.optimize import linprog
import two_hub_blocks as tb

def extend(m,P,j):
 own,deg,*_=tb.structure(m,P);t=next(s for s in range(3)if s*m+j in own);a,b=[s for s in range(3)if s!=t];ea=[None]*3;eb=[None]*3;ea[a]=j;ea[t]=m;ea[b]=m+1;eb[b]=j;eb[t]=m+2;eb[a]=m+3
 return m+4,P+[tuple(ea),tuple(eb)]

def solve(d,j,freeze=True):
 m=d['m'];P=[tuple(e)for e in d['P']];own,degree,block,rb,L,hubs,ports,toward=tb.structure(m,P);v=list(map(F,d['values']));oldlookup={tuple(t):k for k,t in enumerate(d['types'])};oldstride=d['stride']
 mm,PP=extend(m,P,j);new=tb.structure(mm,PP);nb=new[2];LL=new[4];g=len(new[5]);types,stride,rows,rhs,eq,erhs,bounds,A,E=tb.model(mm,PP);lookup={tuple(t):k for k,t in enumerate(types)};extra=[];br=[]
 if freeze:
  for jj in range(m):
   if degree[jj]!=1 or jj==j:continue
   t=next(s for s in range(3)if s*m+jj in own);e=own[t*m+jj];b0=block[e];b1=nb[e]
   for s in range(3):
    if s==t:continue
    k0=oldlookup[b0,t,s];k1=lookup[b1,t,s]
    for e in range(len(P)):extra.append({k1*stride+nb[e]:1});br.append(float(v[k0*oldstride+block[e]]))
 obj=np.zeros(len(bounds))
 for k,(b,t,s)in enumerate(types):obj[k*stride+b]=LL[b][t]
 rr=[];cc=[];vv=[]
 for a,row in enumerate(extra):
  for c,w in row.items():rr.append(a);cc.append(c);vv.append(w)
 C=coo_matrix((vv,(rr,cc)),shape=(len(extra),len(bounds))).tocsr()
 E2=vstack([E,C,csr_matrix(obj.reshape(1,-1))]);b2=erhs+br+[g+2]
 r=linprog(np.zeros(len(bounds)),A_ub=A,b_ub=rhs,A_eq=E2,b_eq=b2,bounds=bounds,options={'time_limit':5})
 return r,dict(m=mm,P=PP,types=types,stride=stride,freeze=freeze,root=j,seed=d['name'])
if __name__=='__main__':
 out=[]
 for same in (False,True):
  d=json.loads(Path(__file__).with_name('BLOCK_ROOT_MIN_'+str(same)+'.json').read_text());degree=tb.structure(d['m'],d['P'])[1]
  for j,g in enumerate(degree):
   if g!=1:continue
   r,rec=solve(d,j);rec['status']=r.status
   if not r.success:
    free,_=solve(d,j,False);rec['unfrozen_status']=free.status
   out.append(rec);print(d['name'],j,r.status,rec.get('unfrozen_status'),flush=True)
 Path(__file__).with_name('HUB_EXTENSION_DISCOVERY.json').write_text(json.dumps(out)+'\n')
