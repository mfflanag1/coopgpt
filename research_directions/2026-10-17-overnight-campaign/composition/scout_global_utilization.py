import numpy as np, scipy.sparse as sp,itertools,random,json
from scipy.optimize import linprog
rng=random.Random(171714)
for trial in range(120):
 n=6 if trial<60 else 7
 m=rng.randrange(n,min(2*n,len(list(itertools.combinations(range(n),3))))+1)
 edges=rng.sample(list(itertools.combinations(range(n),3)),m)
 owners=[0,0,1,1,2,2]+([rng.randrange(3)] if n==7 else [])
 rng.shuffle(owners)
 A=np.array([[int(v in e) for e in edges] for v in range(n)],float)
 emasks=[sum(1<<v for v in e) for e in edges]
 profiles=[];index={};Fs=[];Fcert=[]
 for mask in range(1<<n):
  es=[e for e,em in enumerate(emasks) if mask&em==em]
  if not es:continue
  cap=np.array([int(mask>>v&1) for v in range(n)])
  r=linprog(-np.ones(len(es)),A_ub=A[:,es],b_ub=cap,bounds=(0,None),method='highs')
  for e in es:index[mask,e]=len(index)
  profiles.append((mask,es));Fs.append(-r.fun);Fcert.append({'mask':mask,'edges':es,'flow':r.x.tolist(),'dual':(-r.ineqlin.marginals).tolist(),'F':-r.fun})
 # t is common additive IC violation allowance, objective minimize t.
 tindex=len(index);D=tindex+1
 ur=[];uc=[];uv=[];ub=[];utags=[];er=[];ec=[];ev=[];eb=[]
 def addub(coeff,rhs,tag):
  row=len(ub);ub.append(rhs);utags.append(tag)
  for k,v in coeff.items():
   if v:ur.append(row);uc.append(k);uv.append(v)
 for (mask,es),F in zip(profiles,Fs):
  row=len(eb);eb.append(F)
  for e in es:er.append(row);ec.append(index[mask,e]);ev.append(1)
  for v in range(n):
   addub({index[mask,e]:1 for e in es if v in edges[e]},int(mask>>v&1),['capacity',mask,v])
 for mask,es in profiles:
  for v in range(n):
   if not(mask>>v&1):continue
   low=mask^(1<<v)
   for S in range(1,8):
    if not(S>>owners[v]&1) or S==7:continue
    coeff={tindex:-1}
    for e in range(m):
     k=sum(int(S>>owners[u]&1) for u in edges[e])
     if (low,e) in index:coeff[index[low,e]]=k
     if (mask,e) in index:coeff[index[mask,e]]=-k
    addub(coeff,0,['monotone',mask,low,S])
 AA=sp.coo_matrix((uv,(ur,uc)),shape=(len(ub),D)).tocsr();EE=sp.coo_matrix((ev,(er,ec)),shape=(len(eb),D)).tocsr()
 obj=np.zeros(D);obj[tindex]=1
 rr=linprog(obj,A_ub=AA,b_ub=ub,A_eq=EE,b_eq=eb,bounds=(0,None),method='highs')
 if not rr.success:raise RuntimeError(rr.message)
 if rr.fun>1e-7:
  print(json.dumps({'status':'NUMERIC_CANDIDATE','trial':trial,'n':n,'edges':edges,'owners':owners,'gap':rr.fun,'Fcert':Fcert,'constraints':utags,'inequality_dual':rr.ineqlin.marginals.tolist(),'equality_dual':rr.eqlin.marginals.tolist()},indent=2));break
else:print(json.dumps({'status':'NO_CANDIDATE','trials':120}))
