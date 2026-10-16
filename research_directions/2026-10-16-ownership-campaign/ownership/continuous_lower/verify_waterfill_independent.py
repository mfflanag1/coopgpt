#!/usr/bin/env python3
"""Independent exact rational implementation and checks; no author-code imports."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib,json,random
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent.parent/'mixed/continuous_two_pool/WATERFILL_PRODUCT_THEOREM.txt'

def need(ok,msg):
    if not ok:raise RuntimeError(msg)

def water(caps,target):
    caps=sorted(c for c in caps if c>0)
    need(sum(caps)>=target>0,'water target')
    if sum(caps)==target:return caps[-1]
    subtotal=F(0)
    for j,c in enumerate(caps):
        level=(target-subtotal)/(len(caps)-j)
        if level<=c:
            need(j==0 or level>=caps[j-1],'water interval')
            return level
        subtotal+=c
    raise RuntimeError('water level missing')

def rule(profile,dummy=True):
    A=sum(a for a,b in profile);B=sum(b for a,b in profile)
    if min(A,B)==0:return tuple(F(0) for _ in profile)
    if A<=B:x=[a for a,b in profile];z=[b for a,b in profile]
    else:A,B=B,A;x=[b for a,b in profile];z=[a for a,b in profile]
    M=max(x);d=[min(v,A) for v in z]
    caps=([M] if dummy else [])+d
    level=water(caps,A+(M if dummy else 0))
    p=F(1,2)
    for c in caps:
        if c:p*=min(c,level)/c
    return tuple((1-p)*a+p*b for a,b in zip(x,d))

counts={'profiles':0,'coalitions':0,'own_increases':0}
worst=F(0)

def verify_profile(profile,ys=None):
    global worst
    y=rule(profile) if ys is None else ys
    n=len(profile);T=min(sum(a for a,b in profile),sum(b for a,b in profile))
    need(all(v>=0 for v in y),('negative',profile,y))
    need(sum(y)<=F(31,27)*T,('budget',profile,y))
    if T:worst=max(worst,sum(y)/T)
    for mask in range(1<<n):
        ids=[i for i in range(n) if mask>>i&1]
        v=min(sum(profile[i][0] for i in ids),sum(profile[i][1] for i in ids))
        need(sum(y[i] for i in ids)>=v,('coalition',profile,mask,y))
        counts['coalitions']+=1
    counts['profiles']+=1
    return y

for levels,maxn in [((F(0),F(1),F(2)),4),((F(0),F(1,3),F(1),F(3)),3)]:
    for n in range(1,maxn+1):
        profiles=list(product(tuple(product(levels,repeat=2)),repeat=n))
        table={r:rule(r) for r in profiles}
        for r,y in table.items():
            verify_profile(r,y)
            for i in range(n):
                for side in range(2):
                    j=levels.index(r[i][side])
                    if j==len(levels)-1:continue
                    new=[list(t) for t in r];new[i][side]=levels[j+1]
                    new=tuple(tuple(t) for t in new)
                    need(table[new][i]>=y[i],('grid own IC',r,new,i,y,table[new]))
                    counts['own_increases']+=1

rng=random.Random(20261016)
for sample in range(450):
    n=1+sample%9
    r=tuple((F(rng.randrange(13),rng.randrange(1,10)),F(rng.randrange(13),rng.randrange(1,10))) for _ in range(n))
    y=verify_profile(r)
    for i in range(n):
        for side in range(2):
            new=[list(t) for t in r];new[i][side]+=F(rng.randrange(1,20),rng.randrange(1,11))
            new=tuple(tuple(t) for t in new);z=rule(new)
            need(z[i]>=y[i],('random own IC',r,new,i,y,z))
            counts['own_increases']+=1

attainer=((F(1),F(0)),(F(0),F(1)),(F(0),F(1)))
attainment=sum(rule(attainer))
need(attainment==F(31,27),'attainment')
low=((F(99,100),F(0)),(F(0),F(1,2)),(F(0),F(1,2)))
high=((F(1),F(0)),(F(0),F(1,2)),(F(0),F(1,2)))
need(rule(low,dummy=False)[0]>rule(high,dummy=False)[0],'negative control missing')
need(rule(low)[0]<=rule(high)[0],'corrected boundary case fails')
report={'status':'EXACT PASS','counts':counts,'maximum_observed_factor':str(worst),
        'exact_attainment':str(attainment),'negative_control_no_dummy':
        {'low_payment':str(rule(low,False)[0]),'high_payment':str(rule(high,False)[0])},
        'correct_dummy_boundary':{'low_payment':str(rule(low)[0]),'high_payment':str(rule(high)[0])},
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'scope':'finite exact evidence supports independently rederived all-real proof'}
path=ROOT/('waterfill_independent_optimized.json' if not __debug__ else 'waterfill_independent.json')
path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
