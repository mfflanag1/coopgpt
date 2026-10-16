#!/usr/bin/env python3
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from waterfill_rule import rule,need
import random,json,hashlib
ROOT=Path(__file__).resolve().parent

def value(profile,group=None):
 if group is None:group=range(len(profile))
 return min(sum(profile[i][0]for i in group),sum(profile[i][1]for i in group))

def run():
 count=dict(exhaustive_profiles=0,random_profiles=0,coalitions=0,own_coordinate_increases=0,whole_bundle_underreports=0,exact_water_equations=0)
 maxratio=Q();maxprofile=None
 for n in range(1,5):
  for profile in product(list(product(range(3),repeat=2)),repeat=n):
   y,info=rule(profile,True);t=value(profile);need(all(z>=0 for z in y),'negative');need(sum(y)<=Q(31,27)*t,'budget');count['exhaustive_profiles']+=1;count['exact_water_equations']+=int(t>0)
   if t and sum(y)/t>maxratio:maxratio=sum(y)/t;maxprofile=profile
   for mask in range(1,1<<n):
    group=[i for i in range(n)if mask>>i&1];need(sum(y[i]for i in group)>=value(profile,group),'coalition');count['coalitions']+=1
   for i in range(n):
    for j in [0,1]:
     alt=[list(z)for z in profile];alt[i][j]+=1;need(rule(alt)[i]>=y[i],'own coordinate decrease');count['own_coordinate_increases']+=1
 rng=random.Random(20261016)
 for case in range(5500):
  n=rng.randint(2,35);profile=[(Q(rng.randint(0,80),rng.choice([1,2,3,7,11])),Q(rng.randint(0,80),rng.choice([1,2,3,7,11])))for _ in range(n)]
  if case%4==0:
   # Adverse derivative cells: one dominant short owner, one small short
   # owner, many independently capped long accounts, some owned jointly.
   profile=[(Q(1),Q()),(Q(1,2),Q())]+[(Q(),Q(2))for _ in range(n-2)]
   if n>3 and case%8==0:profile[1]=(Q(1,2),Q(2))
  y,info=rule(profile,True);t=value(profile);need(all(z>=0 for z in y),'random negative');need(sum(y)<=Q(31,27)*t,'random budget');count['random_profiles']+=1;count['exact_water_equations']+=int(t>0)
  if t and sum(y)/t>maxratio:maxratio=sum(y)/t;maxprofile=profile
  for _ in range(12):
   group=[i for i in range(n)if rng.randrange(2)];need(sum(y[i]for i in group)>=value(profile,group),'random coalition');count['coalitions']+=1
  for i in rng.sample(range(n),min(n,4)):
   alt=[list(z)for z in profile];alt[i]=[x*Q(rng.randrange(6),5)for x in alt[i]];need(rule(alt)[i]<=y[i],'whole-bundle underreport');count['whole_bundle_underreports']+=1
   for j in [0,1]:
    alt=[list(z)for z in profile];alt[i][j]+=Q(1,rng.choice([1,3,100,10000]));need(rule(alt)[i]>=y[i],'rational coordinate decrease');count['own_coordinate_increases']+=1
 sharp=[(1,0),(0,1),(0,1)];need(sum(rule(sharp))==Q(31,27),'sharp budget');need(maxratio==Q(31,27),'not attained')
 # The warning against generic netting is real: this pure short payment can
 # rise by more than its own resource increase, although it stays monotone.
 lip=[(Q(1),Q()),(Q(1,2),Q())]+[(Q(),Q(2))for _ in range(10)]
 alt=list(lip);alt[1]=(Q(5001,10000),Q());lip_gain=rule(alt)[1]-rule(lip)[1]
 need(lip_gain>Q(1,10000),'expected non-Lipschitz warning not reproduced')
 out=dict(status='EXACT RATIONAL PASS',counts=count,max_budget_ratio=str(maxratio),max_profile=[[str(a),str(b)]for a,b in maxprofile],non_lipschitz_increment=str(lip_gain),non_lipschitz_resource_increment='1/10000',scope='Finite exact corroboration; full theorem rests on WATERFILL_PRODUCT_THEOREM.txt. Checks deliberately retain actual mixed owners.',rule_sha256=hashlib.sha256((ROOT/'waterfill_rule.py').read_bytes()).hexdigest(),check_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'waterfill_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':run()
