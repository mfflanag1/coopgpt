"""Exact Fraction calibration of CEA sums for one min technology.

Analytic all-real proof: CEA_MINIMUM_FULL_OUT.txt.
The checks exhaust all binary endpoint pairs for n=r=3, then use fixed
rational mixed-owner boxes, ties, zeros, simultaneous restoration, and passive
protected owners. Finite checks do not replace the all-real proof.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import random

COUNTS=dict(profiles=0,coverage_comparisons=0,restoration_comparisons=0,
            comparisons_with_unchanged_protected_members=0,
            positive_outside_worth_comparisons=0,
            water_level_increases=0,water_level_decreases=0,
            cell_formula_checks=0,path_segments=0)

def cea(claims,estate):
    assert all(c>=0 for c in claims)
    assert 0<=estate<=sum(claims)
    if estate==0:
        level=Q(0)
    else:
        prefix=Q(0)
        for k,cap in enumerate(sorted(claims)):
            level=(estate-prefix)/(len(claims)-k)
            if level<=cap:
                break
            prefix+=cap
        else:
            raise AssertionError("CEA water filling did not stop")
    awards=tuple(min(c,level) for c in claims)
    assert level>=0 and sum(awards)==estate
    assert all(0<=t<=c for t,c in zip(awards,claims))
    return awards,level

@lru_cache(maxsize=None)
def mechanism(profile):
    n=len(profile);r=len(profile[0])
    totals=tuple(sum(profile[i][a] for i in range(n)) for a in range(r))
    estate=min(totals)
    pools=[];levels=[]
    for a in range(r):
        awards,level=cea(tuple(profile[i][a] for i in range(n)),estate)
        pools.append(awards);levels.append(level)
    payments=tuple(sum(pools[a][i] for a in range(r)) for i in range(n))
    assert all(y>=0 for y in payments)
    assert sum(payments)==r*estate
    if estate==0:
        assert all(y==0 for y in payments)
    return dict(totals=totals,estate=estate,pools=tuple(pools),
                levels=tuple(levels),payments=payments)

def members(mask,n):
    return tuple(i for i in range(n) if mask&(1<<i))

def check_cell_formula(profile):
    n=len(profile);r=len(profile[0]);m=mechanism(profile)
    h=min(range(r),key=lambda a:m['totals'][a])
    formula=[profile[i][h] for i in range(n)]
    subsets={}
    for a in range(r):
        if a==h:
            continue
        saturated=tuple(i for i in range(n) if profile[i][a]<m['levels'][a])
        assert len(saturated)<n
        q=n-len(saturated)
        level=(m['totals'][h]-sum(profile[i][a] for i in saturated))/q
        assert level==m['levels'][a]
        assert level>=0
        assert all(profile[i][a]<=level for i in saturated)
        assert all(profile[i][a]>=level for i in range(n) if i not in saturated)
        for i in range(n):
            formula[i]+=profile[i][a] if i in saturated else level
        subsets[str(a)]=saturated
    assert tuple(formula)==m['payments']
    COUNTS['cell_formula_checks']+=1
    return dict(bottleneck=h,saturated_subsets=subsets,payments=tuple(formula))

def check_profile(profile):
    n=len(profile);r=len(profile[0]);m=mechanism(profile)
    COUNTS['profiles']+=1
    for mask in range(1,1<<n):
        C=members(mask,n)
        worth=min(sum(profile[i][a] for i in C) for a in range(r))
        assert sum(m['payments'][i] for i in C)>=worth
        COUNTS['coverage_comparisons']+=1
    check_cell_formula(profile)

def changed_mask(low,high):
    return sum(1<<i for i in range(len(low)) if low[i]!=high[i])

def check_transition(low,high,mask):
    n=len(low);r=len(low[0]);C=members(mask,n)
    assert all(high[i][a]>=low[i][a] for i in range(n) for a in range(r))
    assert all(low[i]==high[i] for i in range(n) if i not in C)
    before=mechanism(low);after=mechanism(high)
    D=tuple(sum(high[i][a]-low[i][a] for i in C) for a in range(r))
    gain=sum(after['payments'][i]-before['payments'][i] for i in C)
    assert gain>=min(D)
    assert after['estate']>=before['estate']
    for a in range(r):
        gain_a=sum(after['pools'][a][i]-before['pools'][a][i] for i in C)
        assert gain_a>=0
        if after['levels'][a]<before['levels'][a]:
            COUNTS['water_level_decreases']+=1
            assert all(after['pools'][a][i]<=before['pools'][a][i]
                       for i in range(n) if i not in C)
        elif after['levels'][a]>before['levels'][a]:
            COUNTS['water_level_increases']+=1
            assert all(after['pools'][a][i]>=before['pools'][a][i] for i in C)
    COUNTS['restoration_comparisons']+=1
    if any(low[i]==high[i] for i in C):
        COUNTS['comparisons_with_unchanged_protected_members']+=1
    if min(D)>0:
        COUNTS['positive_outside_worth_comparisons']+=1
    return gain,min(D)

def path_certificate(low,high,mask):
    n=len(low);r=len(low[0]);C=members(mask,n)
    d=tuple(tuple(high[i][a]-low[i][a] for a in range(r)) for i in range(n))
    T=mechanism(low)['totals']
    D=tuple(sum(d[i][a] for i in C) for a in range(r))
    points={Q(0),Q(1)}
    for a in range(r):
        for c in range(a):
            if D[a]!=D[c]:
                t=(T[c]-T[a])/(D[a]-D[c])
                if 0<t<1:
                    points.add(t)
    points=sorted(points);records=[]
    for u,v in zip(points,points[1:]):
        h=min(range(r),key=lambda a:T[a]+(u+v)/2*D[a])
        assert all(T[h]+t*D[h]<=T[a]+t*D[a] for a in range(r) for t in (u,v))
        left=tuple(tuple(low[i][a]+u*d[i][a] for a in range(r)) for i in range(n))
        right=tuple(tuple(low[i][a]+v*d[i][a] for a in range(r)) for i in range(n))
        ml=mechanism(left);mr=mechanism(right)
        gains=tuple(sum(mr['pools'][a][i]-ml['pools'][a][i] for i in C) for a in range(r))
        assert all(g>=0 for g in gains)
        assert gains[h]==(v-u)*D[h]
        assert sum(gains)>=(v-u)*min(D)
        records.append(dict(interval=(u,v),bottleneck=h,pool_coalition_gains=gains,
                            certified_lower=(v-u)*D[h],required_lower=(v-u)*min(D)))
        COUNTS['path_segments']+=1
    overall=sum(mechanism(high)['payments'][i]-mechanism(low)['payments'][i] for i in C)
    assert sum(sum(x['pool_coalition_gains']) for x in records)==overall
    assert sum(x['required_lower'] for x in records)==min(D)
    return dict(low=low,high=high,coalition=C,restoration_totals=D,
                outside_worth=min(D),payment_gain=overall,segments=records)

def exhaustive_binary():
    n=r=3
    profiles=[]
    for flat in product((Q(0),Q(1)),repeat=n*r):
        profile=tuple(tuple(flat[i*r+a] for a in range(r)) for i in range(n))
        check_profile(profile);profiles.append(profile)
    starts=COUNTS['restoration_comparisons']
    for statuses in product(((Q(0),Q(0)),(Q(0),Q(1)),(Q(1),Q(1))),repeat=n*r):
        low=tuple(tuple(statuses[i*r+a][0] for a in range(r)) for i in range(n))
        high=tuple(tuple(statuses[i*r+a][1] for a in range(r)) for i in range(n))
        changed=changed_mask(low,high)
        for mask in range(1,1<<n):
            if mask&changed==changed:
                check_transition(low,high,mask)
    comparisons=COUNTS['restoration_comparisons']-starts
    assert len(profiles)==512 and comparisons==42363
    return dict(owners=n,pools=r,box='all independent coordinates in [0,1]',
                profiles=len(profiles),ordered_endpoint_pairs=3**9,
                protected_coalition_comparisons=comparisons)

def rational_boxes():
    rng=random.Random(20261019)
    institutions=[];examples=[]
    for n in range(1,6):
        for r in range(1,5):
            upper=tuple(tuple(Q(rng.randrange(0,7),3) for a in range(r)) for i in range(n))
            count=0
            for trial in range(30):
                low=tuple(tuple(upper[i][a]*Q(rng.randrange(5),4) for a in range(r)) for i in range(n))
                chosen=rng.randrange(1,1<<n)
                high=tuple(tuple(low[i][a]+(upper[i][a]-low[i][a])*Q(rng.randrange(4),3)
                                 if chosen&(1<<i) else low[i][a]
                                 for a in range(r)) for i in range(n))
                assert all(0<=low[i][a]<=high[i][a]<=upper[i][a] for i in range(n) for a in range(r))
                check_profile(low);check_profile(high)
                changed=changed_mask(low,high)
                for mask in range(1,1<<n):
                    if mask&changed==changed:
                        check_transition(low,high,mask);count+=1
                cert=path_certificate(low,high,chosen)
                if len(examples)<5 and len(cert['segments'])>1 and cert['outside_worth']>0:
                    examples.append(cert)
            institutions.append(dict(owners=n,pools=r,fixed_endowments=upper,
                                     endpoint_pairs=30,protected_coalition_comparisons=count))
    return institutions,examples

def explicit_cases():
    # Three successive bottlenecks, a positive outside-production requirement,
    # and owner3 (zero-based index3) protected but unchanged.
    low=((Q(0),Q(0),Q(1,4)),(Q(0),Q(1,2),Q(0)),
         (Q(0),Q(0),Q(1,2)),(Q(0),Q(0),Q(1,4)))
    d=((Q(3),Q(1),Q(1)),(Q(2),Q(1),Q(0)),
       (Q(0),Q(0),Q(0)),(Q(0),Q(0),Q(0)))
    high=tuple(tuple(a+b for a,b in zip(row,delta)) for row,delta in zip(low,d))
    mask=(1<<0)|(1<<1)|(1<<3)
    check_transition(low,high,mask)
    switches=path_certificate(low,high,mask)
    assert {segment['bottleneck'] for segment in switches['segments']}=={0,1,2}
    assert switches['outside_worth']==1

    # Increasing estate can coexist with a falling water level in another pool.
    low2=((Q(0),Q(0)),(Q(10),Q(1)))
    high2=((Q(10),Q(1,2)),(Q(10),Q(1)))
    check_transition(low2,high2,1)
    assert mechanism(high2)['estate']>mechanism(low2)['estate']
    assert mechanism(high2)['levels'][0]<mechanism(low2)['levels'][0]
    falling=path_certificate(low2,high2,1)

    profiles=tuple(((Q(1,2),t),(Q(1,2),Q(2)-t)) for t in (Q(1,5),Q(1,2),Q(4,5)))
    payments=tuple(mechanism(p)['payments'][0] for p in profiles)
    assert payments==(Q(7,10),Q(1),Q(1))
    assert payments[1]!=(payments[0]+payments[2])/2
    return dict(three_bottleneck_path=switches,
                increased_estate_decreased_water_level=falling,
                ownership_cell_example=dict(profiles=profiles,owner0_payments=payments))

def encode(x):
    if isinstance(x,Q):
        return str(x)
    raise TypeError(type(x).__name__)

if __name__=='__main__':
    exhaustive=exhaustive_binary()
    institutions,examples=rational_boxes()
    explicit=explicit_cases()
    source=Path(__file__)
    result=dict(status='PASS',timestamp=datetime.now(timezone.utc).isoformat(),
                scope='Exact finite calibration; the companion theorem proves all-real guarantees.',
                counts=COUNTS,exhaustive_binary=exhaustive,rational_institutions=institutions,
                sampled_path_certificates=examples,explicit_cases=explicit,
                checker_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    source.with_suffix('.json').write_text(json.dumps(result,default=encode,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],counts=COUNTS,
                         exhaustive_binary=exhaustive,rational_fixed_institutions=len(institutions)),
                     indent=2))

