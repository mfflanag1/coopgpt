"""Exploratory LP on profiles with at most three pool types; all fairness omitted.
No numerical optimum is an all-profile upper theorem or an exact certificate.
"""
import itertools,json,time,math,sys,hashlib
from pathlib import Path
import scipy
from fractions import Fraction
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def solve(k,m,grid):
 t=2*m-2
 ts=[(1,1)+(2,)*(m-2),(1,)+(2,)*(m-2)+(t,),(2,)*(m-2)+(t,t)]; types={t:i for i,t in enumerate(ts)}
 states=set()
 for t in range(len(ts)): states.add(((t,k),))
 for s in range(len(ts)):
  for t in range(s+1,len(ts)):
   for r in range(1,k):states.add(((s,r),(t,k-r)))
 for a,b,c in itertools.combinations(range(len(ts)),3):
  for na in range(1,k-1):
   for nb in range(1,k-na):states.add(((a,na),(b,nb),(c,k-na-nb)))
 states=sorted(states);ss=set(states);ids={}
 for st in states:
  for t,n in st:
   for cap in set(ts[t]):ids[(st,t,cap)]=len(ids)
 beta=len(ids);rows=[];cols=[];vals=[];rhs=[];desc=[]
 def add(terms,b,d):
  r=len(rhs)
  for v,a in terms.items():
   if a:rows.append(r);cols.append(v);vals.append(-a)
  rhs.append(-b);desc.append(d)
 subs={}
 for t,c in enumerate(ts):
  opts=[]
  for mask in range(1,1<<m):
   counts=tuple((v,sum(1 for i,a in enumerate(c) if a==v and mask>>i&1)) for v in sorted(set(c)))
   opts.append((sum(a for i,a in enumerate(c) if mask>>i&1),counts))
  subs[t]=sorted(set(opts))
 for st in states:
  T=min(sum(ts[t]) for t,n in st);tr={beta:T}
  for t,n in st:
   for c in set(ts[t]):tr[ids[(st,t,c)]]=-n*ts[t].count(c)
  add(tr,-T,('budget',st))
  for opts in itertools.product(*(subs[t] for t,n in st)):
   v=min(o[0] for o in opts)
   if v:
    tr={}
    for (t,n),(val,cs) in zip(st,opts):
     for c,count in cs:
      if count:tr[ids[(st,t,c)]]=n*count
    add(tr,v,('cover',st,opts))
  for t,n in st:
   c=list(ts[t])
   for old in set(c):
    for new in grid:
     if new<=old:continue
     ct=c.copy();ct[ct.index(old)]=new;ct=tuple(sorted(ct));
     if ct not in types:continue
     t1=types[ct]
     st1=dict(st);st1[t]-=1
     if not st1[t]:del st1[t]
     st1[t1]=st1.get(t1,0)+1;st1=tuple(sorted(st1.items()))
     if st1 not in ss:continue
     add({ids[(st1,t1,new)]:1,ids[(st,t,old)]:-1},0,('mono',st,t,old,new,st1))
 a=coo_matrix((vals,(rows,cols)),shape=(len(rhs),beta+1)).tocsr()
 obj=[0]*beta+[1];start=time.monotonic();res=linprog(obj,A_ub=a,b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':120})
 out={'status':'DISCOVERY_ONLY','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scipy':scipy.__version__,'solve_timeout_seconds':120,'k':k,'m':m,'grid':grid,'success':res.success,'message':res.message,'states':len(states),'variables':beta+1,'rows':len(rhs),'seconds':time.monotonic()-start}
 if res.success:
  out.update(objective=res.fun,rational_guess=str(Fraction(res.fun).limit_denominator(10**7)),dual=[{'row':d,'weight':str(Fraction(float(w)).limit_denominator(10**7))} for d,w in zip(desc,-res.ineqlin.marginals) if w>1e-8],types=ts)
 return out
if __name__=='__main__':
 k=int(sys.argv[1]);m=int(sys.argv[2]);grid=sorted(set([1,2,2*m-2]));r=solve(k,m,grid)
 with open(sys.argv[3],'w') as f:json.dump(r,f,indent=2)
 print({a:b for a,b in r.items() if a not in ['dual','types']});print('dual',len(r.get('dual',[])))
