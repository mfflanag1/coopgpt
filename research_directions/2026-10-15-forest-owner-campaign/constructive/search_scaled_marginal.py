import numpy as np,json,random
rng=np.random.default_rng(16251);r=random.Random(16251)
def covers(n,edges):
 out=[]
 for mask in range(1<<n):
  if not all((mask>>u&1) or(mask>>v&1) for u,v in edges):continue
  if any(all(((mask^(1<<k))>>u&1)or((mask^(1<<k))>>v&1) for u,v in edges) for k in range(n) if mask>>k&1):continue
  out.append([(mask>>i)&1 for i in range(n)])
 return np.array(out,dtype=np.int64)
def integral(a,b):
 da=a[:,None]-a[None,:];db=b[None,:]-b[:,None]
 with np.errstate(divide='ignore',invalid='ignore'):ts=da/db
 ts=np.unique(np.concatenate(([0.,1.],ts[(ts>0)&(ts<1)])))
 v=np.min(a[:,None]+b[:,None]*ts,axis=0)
 return float(np.sum((v[1:]+v[:-1])*np.diff(ts)/2))
best=(1,None);worst=(0,None);cache={}
for z in range(12000):
 d=r.randrange(2,12);n=r.randrange(2,9);edges=[(r.randrange(v),v) for v in range(1,d)];cv=covers(d,edges)
 b=rng.choice([0,0,0,1,1,2,3,5,10,30],size=(n,d))
 if z%2==0:b*=rng.choice([0,1],size=(n,d),p=[.75,.25])
 if z%5==0:
  b=np.zeros((n,d),dtype=np.int64)
  for j in range(d):b[r.randrange(n),j]=r.choice([1,1,1,2,3,5,10,30])
 h=cv@b.T;tot=h.sum(axis=1);T=min(tot)
 if T==0:continue
 if n not in cache:cache[n]=((np.arange(1<<n)[:,None]>>np.arange(n))&1)
 masks=cache[n];v=np.min(masks@h.T,axis=1)
 D=np.array([integral(h[:,i],tot-h[:,i])-.5*min(tot-h[:,i]) for i in range(n)])
 valid=v>0;ratios=(masks@D)[valid]/v[valid];j=np.argmin(ratios)
 if ratios[j]<best[0]-1e-10:
  S=int(np.flatnonzero(valid)[j]);best=(float(ratios[j]),dict(case=z,edges=edges,bundles=b.tolist(),T=int(T),coalition=[i for i in range(n) if S>>i&1],value=int(v[S]),D=D.tolist(),ratio=float(ratios[j])));print('LOW',json.dumps(best[1]),flush=True)
 if sum(D)/T>worst[0]+1e-10:worst=(sum(D)/T,None)
 if z%2000==0:print('PROGRESS',z,'low',best[0],'high',worst[0],flush=True)
print('FINAL',best[0],worst[0])
