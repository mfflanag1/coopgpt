import random,json
from pathlib import Path
from probe import lp
rng=random.Random(20260907)
best=0;out=[]
for mode,m,tries in [('arbitrary',2,200),('arbitrary',3,400),('compatible',4,500),('compatible',6,500)]:
 for it in range(tries):
  mats=[[[rng.choice([0,0,0,1,2,3])for j in range(m)]for i in range(m)]for k in range(3)]
  if mode=='compatible':
   for A in mats:
    for i in range(m): A[i][i]=max(A[i])
   T=sum(A[i][i]for A in mats for i in range(m))
  else:T=None
  if not any(v for A in mats for row in A for v in row):continue
  r=lp(mats,m,T)
  if r and r['ratio']>best+1e-8:
   best=r['ratio'];d={'mode':mode,'m':m,'iteration':it,'matrices':mats,**r};out.append(d)
   print(json.dumps(d),flush=True);Path(__file__).with_name('search_best.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'mode':mode,'m':m,'completed':tries,'best':best}),flush=True)
