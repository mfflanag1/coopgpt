from fractions import Fraction as Q
from pathlib import Path
import random,sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harmonic_multi_common_full_outside import parameter,production,coalition_payment
from common_cap_arity_mechanism import Radical
rng=random.Random(8661710);counts={'funding':0,'coverage':0,'full_OUT':0,'gamma_inequality':0,'gamma_equality':0}
for t in range(1,7):
 gamma=Q(3*t+1,4*t);B=Q(t)/gamma
 w=[Q(t+1,2*t)]+[Q(1,2*t)]*(t-1) if t>1 else [Q(1)]
 s2=sum(x*x for x in w)
 assert sum(min(x,s2) for x in w)==gamma
 counts['gamma_equality']+=1
 for trial in range(500):
  weights=[Q(rng.randrange(1,30)) for _ in range(t)];total=sum(weights);weights=[x/total for x in weights]
  s2=sum(x*x for x in weights)
  assert sum(min(x,s2) for x in weights)>=gamma
  counts['gamma_inequality']+=1
 for k in range(1,6):
  for trial in range(250):
   M=rng.randrange(1,14);d=t+k*M;C=parameter(t,k,M)
   a=[Q(rng.randrange(1,8),rng.randrange(1,5)) for _ in range(t)]
   outside=[Q(rng.randrange(6),rng.randrange(1,5)) for _ in range(d)]
   own=[Q(rng.randrange(6),rng.randrange(1,5)) for _ in range(d)]
   more=[Q(rng.randrange(6),rng.randrange(1,5)) for _ in range(d)]
   low=[x+y for x,y in zip(outside,own)];high=[x+y for x,y in zip(low,more)]
   ownhi=[x+y for x,y in zip(own,more)]
   yp=coalition_payment(high,ownhi,a,k);ym=coalition_payment(low,own,a,k)
   assert yp.compare(Radical(ym.a+production(more,a,k),ym.b,ym.q,ym.k))>=0
   assert yp.compare(production(ownhi,a,k))>=0
   assert coalition_payment(high,high,a,k).compare((B*C+max(B,k))*production(high,a,k))<=0
   for name in ('funding','coverage','full_OUT'):counts[name]+=1
out={'status':'PASS','checks':counts,'shared_rows':list(range(1,7)),
 'private_arity':list(range(1,6)),'branches_up_to':13,
 'arithmetic':'exact fractions and certified kth-root intervals',
 'limits':'Finite checks supplement directional proof; unresolved radical comparisons raise.'}
Path(__file__).with_name('HARMONIC_FULL_OUTSIDE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
