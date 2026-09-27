from pathlib import Path
from fractions import Fraction as F
import json,numpy as np
from scipy.sparse import hstack,vstack,coo_matrix,csr_matrix
from scipy.optimize import linprog
import two_hub_blocks as tb
from hub_extension_probe import extend

def system(d,j,tight=True):
 m=d['m'];P=[tuple(e)for e in d['P']];old=tb.structure(m,P);v=list(map(F,d['values']));oldlookup={tuple(t):k for k,t in enumerate(d['types'])};oldstride=d['stride'];mm,PP=extend(m,P,j);new=tb.structure(mm,PP);types,stride,rows,rhs,eq,erhs,bounds,A,E=tb.model(mm,PP);n=len(bounds);lookup={tuple(t):k for k,t in enumerate(types)};fixed={}
 for jj in range(m):
  if old[1][jj]!=1 or jj==j:continue
  t=next(s for s in range(3)if s*m+jj in old[0]);e=old[0][t*m+jj]
  for s in range(3):
   if s==t:continue
   k0=oldlookup[old[2][e],t,s];k1=lookup[new[2][e],t,s]
   for ee in range(len(P)):fixed[k1*stride+new[2][ee]]=v[k0*oldstride+old[2][ee]]
 ex=[{i:F(1),n:-w}for i,w in sorted(fixed.items())];br=[F(0)]*len(ex)
 if tight:
  obj={k*stride+b:new[4][b][t]for k,(b,t,s)in enumerate(types)};ex.append(obj);br.append(len(new[5])+2)
 eq=[dict(row)for row in eq]+ex;erhs=list(erhs)+br
 def sparse(rs):
  ii=[];jj=[];vv=[]
  for i,row in enumerate(rs):
   for j,w in row.items():ii.append(i);jj.append(j);vv.append(float(w))
  return coo_matrix((vv,(ii,jj)),shape=(len(rs),n+1)).tocsr()
 return mm,PP,types,stride,rows,rhs,eq,erhs,bounds+[(0,1)],sparse(rows),sparse(eq)

def solve(d,j,tight=True):
 mm,PP,types,stride,rows,rhs,eq,erhs,bounds,A,E=system(d,j,tight);c=np.zeros(len(bounds));c[-1]=-1
 r=linprog(c,A_ub=A,b_ub=rhs,A_eq=E,b_eq=list(map(float,erhs)),bounds=bounds,options={'time_limit':10})
 rec={'seed':d['name'],'root':j,'tight':tight,'status':r.status,'scale':-r.fun if r.success else None,'m':mm,'P':PP}
 return r,rec
if __name__=='__main__':
 records=[]
 for file in ('ONE_HUB_UNIFORM_PARAMETERS.json','BLOCK_ROOT_MIN_False.json','BLOCK_ROOT_MIN_True.json'):
  d=json.loads(Path(__file__).with_name(file).read_text());degree=tb.structure(d['m'],d['P'])[1]
  for j,g in enumerate(degree):
   if g!=1:continue
   r,rec=solve(d,j);records.append(rec);print(rec['seed'],j,r.status,rec['scale'],flush=True)
   if not r.success:
    r2,rec2=solve(d,j,False);records.append(rec2);print('relaxed',r2.status,rec2['scale'],flush=True)
 Path(__file__).with_name('SCALED_EXTENSION_DISCOVERY.json').write_text(json.dumps(records)+'\n')
