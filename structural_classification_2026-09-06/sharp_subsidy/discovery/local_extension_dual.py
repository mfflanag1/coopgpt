from pathlib import Path
from fractions import Fraction as F
import json,numpy as np
from scipy.sparse import coo_matrix,hstack,csr_matrix
from scipy.optimize import linprog
import two_hub_blocks as tb
from hub_extension_probe import extend

def system():
 m=7;P=[(0,1,2),(3,0,4),(5,6,0)];mm,PP=extend(m,P,1);old=tb.structure(m,P);new=tb.structure(mm,PP);types,stride,rows,rhs,eq,erhs,bounds,_,_=tb.model(mm,PP);rows=[dict(r)for r in rows];rhs=list(rhs);eq=[dict(r)for r in eq];erhs=list(erhs);lookup={tuple(t):k for k,t in enumerate(types)};fixed=set()
 for j in range(2,7):
  t=next(s for s in range(3)if s*m+j in old[0]);e=old[0][t*m+j];b0=new[2][e]
  for s in range(3):
   if s==t:continue
   k=lookup[b0,t,s]
   for e in range(3):fixed.add(k*stride+new[2][e])
 for v in sorted(fixed):eq.append({v:4});erhs.append(1)
 for v,(lo,hi)in enumerate(bounds):rows.append({v:1});rhs.append(hi)
 return mm,PP,types,stride,rows,rhs,eq,erhs,len(bounds)
if __name__=='__main__':
 mm,PP,types,stride,rows,rhs,eq,erhs,n=system();rs=rows+eq;nr=len(rows);ne=len(eq)
 ii=[];jj=[];vv=[]
 for j,row in enumerate(rs):
  for i,v in row.items():ii.append(i);jj.append(j);vv.append(v)
 C=coo_matrix((vv,(ii,jj)),shape=(n,len(rs))).tocsr();C=hstack([C,-C[:,nr:]],format='csr');bs=np.array(rhs+erhs+[-v for v in erhs])
 r=linprog(np.ones(nr+2*ne),A_ub=-C,b_ub=np.zeros(n),A_eq=csr_matrix(bs.reshape(1,-1)),b_eq=[-1],bounds=(0,None),options={'time_limit':30})
 print('status',r.status,flush=True)
 if not r.success:raise ValueError('no dual')
 v={}
 for j,x in enumerate(r.x):
  if abs(x)<1e-8:continue
  k=j if j<nr+ne else j-ne;v[k]=v.get(k,F(0))+(1 if j<nr+ne else-1)*F(float(x)).limit_denominator(10000)
 v={j:x for j,x in v.items()if x};lhs=[F(0)]*n;bound=F(0)
 for j,w in v.items():
  bound+=w*(rhs+erhs)[j]
  for i,a in rs[j].items():lhs[i]+=w*a
 exact=bound<0 and all(w>=0 for j,w in v.items()if j<nr)and all(x>=0 for x in lhs)
 out={'m':mm,'P':PP,'multipliers':[[j,str(w)]for j,w in sorted(v.items())],'exact':exact,'bound':str(bound),'support':len(v)}
 Path(__file__).with_name('LOCAL_EXTENSION_DUAL.json').write_text(json.dumps(out)+'\n');print(exact,len(v),float(bound),float(min(lhs)),flush=True)
 if not exact:raise ValueError('inexact contradiction')
 def name(i):
  k,q=divmod(i,stride);B=5
  return str((types[k],('p',q)if q<B else('f',q-B)if q<2*B else('hub',q-2*B)if q<2*B+2 else('z',0)))
 for j,w in sorted(v.items()):print('le'if j<nr else'eq',str(w),(rhs+erhs)[j],[(name(i),a)for i,a in sorted(rs[j].items())],flush=True)
