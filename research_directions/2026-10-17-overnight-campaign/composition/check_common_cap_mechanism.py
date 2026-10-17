#!/usr/bin/env python3
from fractions import Fraction as Q
import sys,json,itertools,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common_cap_mechanism import coalition_payment,production,parameter,Quadratic,sign_two

def require(test,msg):
 if not test:raise RuntimeError(msg)
# Exact algebraic zero/nonzero identities, including mixed square roots.
require(sign_two(Q(0),Q(1),Q(2),Q(-2),Q(1,2))==0,'equal radical forms')
require(sign_two(Q(-3),Q(1),Q(4),Q(1),Q(1))==0,'nonzero rational part equality')
require(sign_two(Q(-3),Q(1),Q(2),Q(1),Q(3))==1,'strict two-radical sign')
values=coverage=transitions=0
M=2;d=1+2*M;C=parameter(M)
for c0 in itertools.product(range(3),repeat=d):
 c=list(map(Q,c0));F=production(c)
 require(coalition_payment(c,c).compare((C+2)*F)<=0,'exact funding')
 values+=1
 # Every supported activity is covered by aggregate prices. Unit proportional
 # holdings normalized by max coefficient yield the triple price-sum test.
 for j in range(M):
  vs=[0,2*j+1,2*j+2]
  if all(c[v]>0 for v in vs):
   amount=min(c[v] for v in vs);s=[Q(0)]*d
   for v in vs:s[v]=amount
   require(coalition_payment(c,s).compare(amount)>=0,'exact activity-cover coalition')
   coverage+=1
 for mask in range(1<<d):
  s=[c[v] if mask>>v&1 else Q(0) for v in range(d)]
  high=coalition_payment(c,s)
  for v in range(d):
   if not s[v]:continue
   lowc=c.copy();lows=s.copy();lowc[v]-=1;lows[v]-=1
   require(high.compare(coalition_payment(lowc,lows))>=0,'exact corner-coalition finite restoration')
   transitions+=1
rng=random.Random(171801)
for trial in range(1500):
 M=rng.randrange(1,13);d=1+2*M;C=parameter(M)
 outsider=[Q(rng.randrange(5),rng.choice([1,2,3])) for _ in range(d)]
 retained=[Q(rng.randrange(5),rng.choice([1,2,3])) for _ in range(d)]
 restored=[Q(rng.randrange(4),rng.choice([1,2,3])) for _ in range(d)]
 lo=[x+y for x,y in zip(outsider,retained)]
 hi=[x+y for x,y in zip(lo,restored)]
 ownhi=[x+y for x,y in zip(retained,restored)]
 require(coalition_payment(hi,ownhi).compare(coalition_payment(lo,retained))>=0,'mixed coalition simultaneous restoration')
 require(coalition_payment(hi,hi).compare((C+2)*production(hi))<=0,'random exact funding')
 require(coalition_payment(hi,ownhi).compare(production(ownhi))>=0,'random exact coalition coverage')
 transitions+=1;values+=1;coverage+=1
print(json.dumps({'status':'PASS','arithmetic':'exact rational coefficients plus certified algebraic comparisons; no rounded payment comparisons','value_funding_profiles':values,'coverage_checks':coverage,'TCWM_finite_comparisons':transitions,'grid_branches':2,'random_branches_up_to':12,'public_parameter':'smallest integer C>=1 with27C^3>=16M; funding C+2'},indent=2))
