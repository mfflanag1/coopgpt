import numpy as np,json,random
rng=np.random.default_rng(5319);r=random.Random(5319)
def covers(n,edges):
 out=[]
 for mask in range(1<<n):
  if not all((mask>>u&1) or(mask>>v&1) for u,v in edges):continue
  if any(all(((mask^(1<<k))>>u&1)or((mask^(1<<k))>>v&1) for u,v in edges) for k in range(n) if mask>>k&1):continue
  out.append([(mask>>i)&1 for i in range(n)])
 return np.array(out,dtype=np.int64)
best=(0,None)
for z in range(20000):
 d=r.randrange(3,12);n=r.randrange(2,9)
 edges=[(r.randrange(v),v) for v in range(1,d)]
 cv=covers(d,edges)
 b=rng.choice([0,0,0,1,1,2,3,5,10,30],size=(n,d))
 if z%3==0:
  b*=rng.choice([0,1],size=(n,d),p=[.75,.25])
 h=cv@b.T;T=min(h.sum(axis=1))
 if T==0:continue
 masks=((np.arange(1<<n)[:,None]>>np.arange(n))&1)
 on=masks.sum(axis=1)
 selected=np.argmin(masks@h.T,axis=1)
 capped=np.minimum(h,T).sum(axis=1)
 for q in [.1,.2,.3,.4,.5,.7,.9]:
  probs=q**(n-on)*(1-q)**on
  Z=float(probs@capped[selected]);ratio=(1-q)*Z/T
  if ratio>best[0]:best=(ratio,dict(case=z,edges=edges,bundles=b.tolist(),T=int(T),q=q,Z=Z,ratio=ratio))
  if ratio>1+1e-10:
   print(json.dumps(best[1]));raise SystemExit
print(json.dumps({'result':'NO FAILURE','best':best[1]}))
