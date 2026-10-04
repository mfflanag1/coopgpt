from itertools import product
from math import factorial
from fractions import Fraction as F
import random,json,time
from pathlib import Path

def evaluate(c,left):
 n=len(c); count=1<<n
 ls=[0]*count;rs=[0]*count;v=[0]*count
 for mask in range(1,count):
  bit=mask&-mask;i=bit.bit_length()-1;prev=mask^bit
  ls[mask]=ls[prev]+(c[i] if i<left else 0)
  rs[mask]=rs[prev]+(c[i] if i>=left else 0)
  v[mask]=min(ls[mask],rs[mask])
 weights=[factorial(k)*factorial(n-k-1) for k in range(n)]
 nums=[0]*n;den=factorial(n)
 for mask in range(count-1):
  weight=weights[mask.bit_count()]
  remaining=(count-1)^mask
  while remaining:
   bit=remaining&-remaining;remaining^=bit;i=bit.bit_length()-1
   nums[i]+=weight*(v[mask|bit]-v[mask])
 if sum(nums)!=den*v[-1]:raise RuntimeError('efficiency')
 subtotal=[0]*count;best=F(1);coalition=0
 for mask in range(1,count):
  bit=mask&-mask;i=bit.bit_length()-1
  subtotal[mask]=subtotal[mask^bit]+nums[i]
  if v[mask] and subtotal[mask]*best.denominator<best.numerator*den*v[mask]:
   best=F(subtotal[mask],den*v[mask]);coalition=mask
 return best,coalition,nums,den
rng=random.Random(20261004)
runs=[]
for left,right,mode,limit in [(2,3,'grid',4),(3,3,'grid',4),(3,4,'random',1000),(4,4,'random',1500),(5,5,'random',500)]:
 if mode=='grid': profiles=product(range(limit),repeat=left+right)
 else: profiles=(tuple(rng.choice([0,1,2,3,5,8,13,21,55,144]) for _ in range(left+right)) for _ in range(limit))
 best=F(1);witness=None;checked=0
 for c in profiles:
  checked+=1;ratio,mask,nums,den=evaluate(c,left)
  if ratio<best:
   best=ratio;witness={'left':left,'capacities':c,'coalition':mask,'phi':list(map(str,[F(x,den) for x in nums])),'ratio':str(ratio)}
 record={'left':left,'right':right,'mode':mode,'limit':limit,'checked':checked,'best':str(best),'witness':witness}
 runs.append(record);print(json.dumps(record),flush=True)
Path(__file__).with_name('DISCOVERY.json').write_text(json.dumps({'seed':20261004,'runs':runs},indent=2))
