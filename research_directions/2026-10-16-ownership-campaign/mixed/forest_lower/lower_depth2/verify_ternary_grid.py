#!/usr/bin/env python3
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import random,json,hashlib
ROOT=Path(__file__).resolve().parent

def need(x,msg):
 if not x:raise ValueError(msg)

def primitive(net):
 a=sum(max(x,0)for x in net);b=sum(max(-x,0)for x in net);t=min(a,b)
 if not t:return [Q()for x in net]
 sign=1 if a<=b else -1
 if t==1:
  long=[i for i,x in enumerate(net)if x*sign<0]
  if len(long)==1:return [Q(1,2)if x else Q()for x in net]
  return [Q(1)if x*sign>0 else Q()for x in net]
 q=Q(1,2**(1+abs(a-b)))
 return [(1-q)*abs(x)if x*sign>0 else q*abs(x)for x in net]

def mechanism(profile):
 z=primitive([a-b for a,b in profile]);return [min(a,b)+y for (a,b),y in zip(profile,z)]

def run():
 stats=dict(pure_profiles=0,pure_steps=0,mixed_profiles=0,mixed_coalitions=0,mixed_steps=0,large_random_profiles=0)
 for n in range(1,7):
  for net in product(range(-2,3),repeat=n):
   z=primitive(net);need(all(0<=y<=abs(x)for x,y in zip(net,z)),'own cap');stats['pure_profiles']+=1
   for i,x in enumerate(net):
    for sign in [-1,1]:
     if x and x*sign<0:continue
     if abs(x)==2:continue
     nxt=list(net);nxt[i]=sign*(abs(x)+1);zz=primitive(nxt);gain=zz[i]-z[i]
     need(0<=gain<=1,'pure increment not in[0,1]');stats['pure_steps']+=1
 for n in range(1,5):
  for profile in product(list(product(range(3),repeat=2)),repeat=n):
   y=mechanism(profile);t=min(sum(a for a,b in profile),sum(b for a,b in profile));need(sum(y)<=Q(9,8)*t,'funding');need(all(z>=0 for z in y),'negative');stats['mixed_profiles']+=1
   for mask in range(1,1<<n):
    val=min(sum(profile[i][0]for i in range(n)if mask>>i&1),sum(profile[i][1]for i in range(n)if mask>>i&1));need(sum(y[i]for i in range(n)if mask>>i&1)>=val,'coalition');stats['mixed_coalitions']+=1
   for i in range(n):
    for j in [0,1]:
     if profile[i][j]==2:continue
     alt=[list(z)for z in profile];alt[i][j]+=1;need(mechanism(alt)[i]>=y[i],'mixed own decrease');stats['mixed_steps']+=1
 rng=random.Random(16102026)
 for _ in range(800):
  n=rng.randint(5,80);profile=[(rng.randrange(3),rng.randrange(3))for _ in range(n)];y=mechanism(profile);t=min(sum(a for a,b in profile),sum(b for a,b in profile));need(sum(y)<=Q(9,8)*t,'large funding');stats['large_random_profiles']+=1
  for __ in range(40):
   group=[i for i in range(n)if rng.randrange(2)];val=min(sum(profile[i][0]for i in group),sum(profile[i][1]for i in group));need(sum(y[i]for i in group)>=val,'large coalition');stats['mixed_coalitions']+=1
  for i in rng.sample(range(n),min(n,8)):
   alt=[list(z)for z in profile];alt[i]=[rng.randint(0,z)for z in alt[i]];need(mechanism(alt)[i]<=y[i],'large whole-bundle underreport');stats['mixed_steps']+=1
 sharp=[(1,0),(1,0),(0,1),(0,2)];need(sum(mechanism(sharp))==Q(9,8)*2,'sharp ratio')
 out=dict(status='EXACT RATIONAL PASS',counts=stats,scope='Finite exact corroboration; unrestricted owner-count grid theorem is in TERNARY_GRID_STOPPING_LEMMA.txt; no continuous-domain upper.',sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'ternary_grid_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':run()
