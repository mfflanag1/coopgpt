from itertools import product
from fractions import Fraction as F
from pathlib import Path
import json,numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def certificate(q, override=None):
 m=2*q+1;n=3*m;P=override or [(a,q+a,a-1 if a else 2*q)for a in range(q)];used={k*m+t[k]for t in P for k in range(3)};U=sorted(set(range(n))-used);u=len(U);teams=list(product(range(m),repeat=3));cols=[(i,t)for i in U for t in teams if t[i//m]!=i%m]
 def pids(t):
  a,b,c=t;return[a*m+b,m*m+a*m+c,2*m*m+b*m+c]
 demand=[0]*(3*m*m)
 for j in range(m):
  for p in pids((j,)*3):demand[p]+=u-4
 for t in P:
  for p in pids(t):demand[p]+=3
 rr=[];cc=[];vv=[];rhs=[1]*(u*n)+[-d for d in demand]
 for j,(i,t)in enumerate(cols):
  for k,v in enumerate(t):rr.append(U.index(i)*n+k*m+v);cc.append(j);vv.append(1)
  for p in pids(t):rr.append(u*n+p);cc.append(j);vv.append(-1)
 A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),len(cols))).tocsr()
 r=linprog(np.ones(len(cols)),A_ub=A,b_ub=rhs,bounds=(0,None))
 if not r.success:raise ValueError(r.message)
 out=[];caps={i:[F(0)]*n for i in U};coverage=[F(0)]*(3*m*m)
 for (i,t),v in zip(cols,r.x):
  if abs(v)<1e-9:continue
  f=F(float(v)).limit_denominator(1000000);out.append([i,list(t),str(f)])
  for k,j in enumerate(t):caps[i][k*m+j]+=f
  for p in pids(t):coverage[p]+=f
 if any(v>1 for cap in caps.values()for v in cap):raise ValueError('rational capacity failed')
 if any(a<b for a,b in zip(coverage,demand)):raise ValueError('rational coverage failed')
 return {'q':q,'m':m,'P':P,'U':U,'packings':out,'claim':'3w(P)+sum_U H<=4T for all pair-additive markets with this diagonal optimal matching and P','status':'exact rational coefficient certificate'}
if __name__=='__main__':
 out=[]
 for q in range(1,5):
  d=certificate(q);out.append(d);print(q,len(d['packings']),'PASS',flush=True)
  Path(__file__).with_name('DELETION_CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')
 d=certificate(3,[(0,1,2),(3,0,4),(5,6,0)]);d['shape']='three-branch star';out.append(d)
 Path(__file__).with_name('DELETION_CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')
 print('star',len(d['packings']),'PASS',flush=True)
