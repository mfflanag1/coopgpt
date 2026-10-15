import numpy as np,json,random,time
rng=np.random.default_rng(231562);r=random.Random(231562)
def covers(n,edges):
 out=[]
 for mask in range(1<<n):
  if not all((mask>>u&1) or(mask>>v&1) for u,v in edges):continue
  if any(all(((mask^(1<<k))>>u&1)or((mask^(1<<k))>>v&1) for u,v in edges) for k in range(n) if mask>>k&1):continue
  out.append([(mask>>i)&1 for i in range(n)])
 return np.array(out,dtype=np.int64)
qs=np.array([.05,.1,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.8,.9])
best=np.zeros(len(qs));cases=[None]*len(qs)
cache={}
for z in range(40000):
 d=r.randrange(2,13);n=r.randrange(2,10)
 edges=[(r.randrange(v),v) for v in range(1,d)]
 cv=covers(d,edges)
 b=rng.choice([0,0,0,1,1,2,3,5,10,30],size=(n,d))
 if z%3==0:
  b*=rng.choice([0,1],size=(n,d),p=[.75,.25])
 if z%5==0:
  b=np.zeros((n,d),dtype=np.int64)
  for j in range(d):b[r.randrange(n),j]=r.choice([1,1,1,2,3,5,10,30])
 h=cv@b.T;T=min(h.sum(axis=1))
 if T==0:continue
 if n not in cache:
  masks=((np.arange(1<<n)[:,None]>>np.arange(n))&1);on=masks.sum(axis=1)
  probs=qs[None,:]**(n-on[:,None])*(1-qs[None,:])**on[:,None]
  der=probs*((n-on[:,None])/qs[None,:]-on[:,None]/(1-qs[None,:]))
  cache[n]=(masks,probs,der)
 masks,probs,der=cache[n]
 values=masks@h.T;selected=np.argmin(values,axis=1);v=np.min(values,axis=1)
 V=np.array([max(v[(np.arange(1<<n)&(1<<i))==0 | False]) for i in []]) if False else np.zeros(n,dtype=np.int64)
 for i in range(n):
  off=np.arange(1<<n)[masks[:,i]==0];V[i]=max(v[off|(1<<i)]-v[off])
 capped=np.minimum(h,V).sum(axis=1)
 Z=capped[selected]@probs;g=v@probs;gp=v@der
 R=(Z-g-(1-qs)*gp)/T
 for j in np.flatnonzero(R>best):
  best[j]=R[j];cases[j]=dict(case=z,edges=edges,bundles=b.tolist(),V=V.tolist(),T=int(T),q=float(qs[j]),ratio=float(R[j]))
 if z%2000==0:print(json.dumps({'case':z,'best':best.tolist()}),flush=True)
print(json.dumps({'best':best.tolist(),'cases':cases}))
