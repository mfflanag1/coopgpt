from itertools import product
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import random,json
rng=random.Random(1083)
def synth(m,P):
 n=3*m;used={s*m+t[s]for t in P for s in range(3)};U=sorted(set(range(n))-used);nw=len(U);offset=3*m*m;nv=offset+n*nw
 # Matrix blocks AB,AC,BC followed by an entire-core witness per unmatched player.
 def pairids(t):
  a,b,c=t;return [a*m+b,m*m+a*m+c,2*m*m+b*m+c]
 rr=[];cc=[];vv=[];rhs=[]
 def row(items,b):
  j=len(rhs);rhs.append(b)
  for k,v in items:rr.append(j);cc.append(k);vv.append(v)
 for widx in range(nw):
  for t in product(range(m),repeat=3):
   row([(k,1)for k in pairids(t)]+[(offset+widx*n+s*m+t[s],-1)for s in range(3)],0)
 A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),nv)).tocsr()
 eq=np.zeros((nw+1,nv));eq[0,[k for j in range(m)for k in pairids((j,j,j))]]=1
 for widx in range(nw):eq[1+widx,offset+widx*n:offset+(widx+1)*n]=1
 c=np.zeros(nv)
 for t in P:
  for k in pairids(t):c[k]-=1
 for widx,i in enumerate(U):c[offset+widx*n+i]-=1/3
 r=linprog(c,A_ub=A,b_ub=rhs,A_eq=eq,b_eq=np.ones(nw+1),bounds=(0,None),method='highs')
 if not r.success:raise RuntimeError(r.message)
 mats=r.x[:offset].reshape(3,m,m).tolist()
 return -r.fun-1,mats
out=[];best=0
for m,num in [(3,100),(4,250),(5,250),(6,100)]:
 for it in range(num):
  r=rng.randrange(1,m)
  bs=rng.sample(range(m),r);cs=rng.sample(range(m),r);P=[(a,bs[a],cs[a])for a in range(r)]
  v,M=synth(m,P)
  if v>best+1e-8:
   best=v;d={'m':m,'iteration':it,'matching':P,'ratio_lower':v,'matrices':M};out.append(d)
   print(json.dumps(d),flush=True);Path(__file__).with_name('synthesis_best.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'m':m,'completed':num,'best':best}),flush=True)
