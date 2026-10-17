from fractions import Fraction as Q
from pathlib import Path
import random,sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harmonic_multi_common import parameter,production,coalition_payment
rng=random.Random(7601710);counts={'funding':0,'coverage':0,'TCWM':0}
for t in range(1,6):
 for k in range(1,6):
  for trial in range(200):
   M=rng.randrange(1,15);d=t+k*M;C=parameter(t,k,M)
   a=[Q(rng.randrange(1,8),rng.randrange(1,5)) for _ in range(t)]
   outside=[Q(rng.randrange(5),rng.randrange(1,5)) for _ in range(d)]
   own=[Q(rng.randrange(5),rng.randrange(1,5)) for _ in range(d)]
   more=[Q(rng.randrange(5),rng.randrange(1,5)) for _ in range(d)]
   low=[x+y for x,y in zip(outside,own)];high=[x+y for x,y in zip(low,more)]
   ownhi=[x+y for x,y in zip(own,more)]
   assert coalition_payment(high,high,a,k).compare((t*C+max(t,k))*production(high,a,k))<=0
   assert coalition_payment(high,ownhi,a,k).compare(production(ownhi,a,k))>=0
   assert coalition_payment(high,ownhi,a,k).compare(coalition_payment(low,own,a,k))>=0
   for name in counts:counts[name]+=1
out={'status':'PASS','checks':counts,'shared_rows':list(range(1,6)),
 'private_arity':list(range(1,6)),'branches_up_to':14,
 'arithmetic':'exact fractions and certified kth-root intervals',
 'limits':'TCWM only. No full OUT or continuous coefficient-type-independent claim.'}
Path(__file__).with_name('HARMONIC_MULTI_COMMON_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
