import numpy as np,json,random,math
rng=np.random.default_rng(19526);r=random.Random(19526)
def covers(n,edges):
 out=[]
 for mask in range(1<<n):
  if not all((mask>>u&1) or(mask>>v&1) for u,v in edges):continue
  if any(all(((mask^(1<<k))>>u&1)or((mask^(1<<k))>>v&1) for u,v in edges) for k in range(n) if mask>>k&1):continue
  out.append([(mask>>i)&1 for i in range(n)])
 return np.array(out,dtype=np.int64)
best=(1,None);cache={}
for z in range(30000):
 d=r.randrange(2,13);n=r.randrange(2,10)
 edges=[(r.randrange(v),v) for v in range(1,d)]
 cv=covers(d,edges)
 b=rng.choice([0,0,0,1,1,2,3,5,10,30],size=(n,d))
 if z%2==0:b*=rng.choice([0,1],size=(n,d),p=[.75,.25])
 if z%5==0:
  b=np.zeros((n,d),dtype=np.int64)
  for j in range(d):b[r.randrange(n),j]=r.choice([1,1,1,2,3,5,10,30])
 h=cv@b.T;T=min(h.sum(axis=1))
 if T==0:continue
 if n not in cache:
  masks=((np.arange(1<<n)[:,None]>>np.arange(n))&1);on=masks.sum(axis=1)
  sw=np.array([1/(n*math.comb(n-1,k)) if k<n else 0 for k in on]);cache[n]=(masks,sw)
 masks,sw=cache[n];v=np.min(masks@h.T,axis=1)
 U=np.array([T-v[(1<<n)-1-(1<<i)] for i in range(n)])
 Sh=np.zeros(n)
 for i in range(n):
  off=np.arange(1<<n)[masks[:,i]==0];Sh[i]=sum(sw[off]*(v[off|(1<<i)]-v[off]))
 vals=masks@(.5*U+.6*Sh);valid=v>0;ratios=vals[valid]/v[valid];j=np.argmin(ratios)
 if ratios[j]<best[0]-1e-12:
  S=int(np.flatnonzero(valid)[j]);best=(float(ratios[j]),dict(case=z,edges=edges,bundles=b.tolist(),T=int(T),coalition=[i for i in range(n) if S>>i&1],value=int(v[S]),U=U.tolist(),Sh=Sh.tolist(),ratio=float(ratios[j])))
  print(json.dumps(best[1]),flush=True)
 if best[0]<.999999:break
print('FINAL',best[0])
