#!/usr/bin/env python3
"""Construct exact compressed tail certificates and the complete GL(3,2)xS5 lift.

Standard library only. No mechanism formula, floating point, LP solver,
zero-payment assumption, external data, or edits outside this directory.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import permutations, product
from math import prod
from pathlib import Path
import gzip
import hashlib
import json

HERE=Path(__file__).resolve().parent


def fraction(q):
    q=Q(q)
    return [q.numerator,q.denominator]


def compressed(k,M,s,save=False):
    a={m:min(s-1,k*(m-1)) for m in range(2,M+1)}
    P=prod((Q(a[m],a[m]+1) for m in a),start=Q(1))
    w={m:Q(k*(M-1),a[m]+1)*prod(
        (Q(a[j],a[j]+1) for j in range(m+1,M+1)),start=Q(1)) for m in a}
    seed=Q(k*(M-1),k+1)*P
    # Independently derive the coefficients by backwards elimination.
    residual=Q(k*(M-1))
    for m in range(M,1,-1):
        assert w[m]==residual/(a[m]+1)
        residual=w[m]*a[m]
    assert seed==residual/(k+1)
    rows=[('budget',Q(1),{'K':Q(1),'z':Q(-1),f'q{M}':Q(-k*M),'other':Q(-1)},Q(0)),
          ('terminal_coverage',Q(1),{'z':Q(1),f'q{M}':Q(k)},Q(1))]
    if seed:
        rows.append(('seed_coverage',seed,{'q1':Q(k+1)},Q(1)))
    for m in a:
        rows.append((f'tcwm_{m}',w[m],{f'q{m}':Q(a[m]+1),f'q{m-1}':Q(-a[m]),f'eta{m}':Q(-1)},Q(0)))
        rows.append((f'restorer_nonnegative_{m}',w[m],{f'eta{m}':Q(1)},Q(0)))
    rows.append(('other_nonnegative',Q(1),{'other':Q(1)},Q(0)))
    coeff=defaultdict(Q)
    rhs=Q(0)
    for name,weight,terms,value in rows:
        assert weight>0
        for var,c in terms.items():
            coeff[var]+=weight*c
        rhs+=weight*value
    assert coeff['K']==1 and all(v==0 for key,v in coeff.items() if key!='K')
    B=1+Q(k*(M-1),k+1)*P
    assert rhs==B
    result={'k':k,'M':M,'s':s,'a':a,'P':fraction(P),'B':fraction(B),
            'seed_weight':fraction(seed),'transition_weights':{m:fraction(v) for m,v in w.items()}}
    if save:
        result['rows']=[{'kind':name,'weight':fraction(weight),
                         'terms':{key:fraction(c) for key,c in terms.items()},'rhs':fraction(value)}
                        for name,weight,terms,value in rows]
        result['aggregate_coefficients']={key:fraction(c) for key,c in sorted(coeff.items())}
    return result


def gl3():
    maps=[]
    for a,b,c in product(range(1,8),repeat=3):
        if b==a or c in (a,b,a^b):
            continue
        image=[]
        for row in range(8):
            out=0
            for bit,v in enumerate((a,b,c)):
                if row&(1<<bit):
                    out^=v
            image.append(out)
        assert sorted(image)==list(range(8))
        maps.append(tuple(image))
    assert len(maps)==len(set(maps))==168
    return sorted(maps)


def transformed(profile,resource_map,owner_map):
    result=[None]*5
    for i,row in enumerate(profile):
        result[owner_map[i]]=resource_map[row]
    return tuple(result)


def artifact(path,data):
    raw=(json.dumps(data,indent=2,sort_keys=True)+'\n').encode()
    path.write_bytes(raw)
    return {'file':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def main():
    checks=0
    for k in range(2,9):
        for M in range(1,25):
            for s in range(2,17):
                compressed(k,M,s)
                checks+=1
    samples=[compressed(2,2,2,True),compressed(2,6,6,True),compressed(3,2,2,True),compressed(4,1,2,True)]
    assert samples[0]['B']==[4,3] and samples[1]['B']==[493,243]
    artifacts=[artifact(HERE/'COMPRESSED_CERTIFICATES.json',{'status':'PASS',
                  'parameter_cases_checked':checks,'samples':samples})]
    maps=gl3()
    owner_maps=list(permutations(range(5)))
    assert len(owner_maps)==len(set(owner_maps))==120
    triples=sorted({tuple(sorted((a,b,a^b))) for a in range(1,8) for b in range(a+1,8)})
    assert len(triples)==7
    for g in maps:
        assert {tuple(sorted(g[a] for a in triple)) for triple in triples}==set(triples)
    C1=(1,2,3,4,0)
    C2=(1,2,3,4,5)
    seed_owners=(0,1,2)
    protected=(1,4)
    multiplicities=Counter()
    profiles=set()
    raw_counts=Counter()
    actions=0
    for g in maps:
        for pi in owner_maps:
            low=transformed(C1,g,pi)
            high=transformed(C2,g,pi)
            profiles.update((low,high))
            C=tuple(sorted(pi[i] for i in protected))
            branch=tuple(sorted(pi[i] for i in seed_owners))
            eta=(pi[4],)
            assert len(C)==2 and pi[4] in C and low[pi[4]]==0
            assert high[pi[4]]==g[5] and high[pi[1]]==low[pi[1]]
            assert all(low[i]==high[i] for i in range(5) if i!=pi[4])
            for kind,l,h,coalition in (
                ('budget',(),high,(0,1,2,3,4)),
                ('terminal_coverage',(),high,branch),
                ('tcwm',low,high,C),
                ('seed_coverage',(),low,branch),
                ('restorer_nonnegative',(),low,eta),
            ):
                multiplicities[kind,l,h,coalition]+=1
                raw_counts[kind]+=1
            actions+=1
    assert actions==168*120==20160
    assert sum(raw_counts.values())==5*actions
    profiles=sorted(profiles)
    ids={p:i for i,p in enumerate(profiles)}
    artifacts.append(artifact(HERE/'PROFILE_TABLE.json',{
        'owner_labels':['p','h1','l1','h2','l2'],
        'resource_rows':[1,2,3,4,5,6,7],
        'resource_encoding':'nonzero 3-bit vectors; v=1,e1=2,e2=4',
        'report_encoding':'0 is the zero vector; a nonzero integer is one unit in that resource row',
        'domain':'each fixed actual owner has the complete real cube [0,1]^7',
        'activities':triples,'profiles':profiles}))
    artifacts.append(artifact(HERE/'ACTION_GROUPS.json',{
        'resource_maps_on_0_through_7':maps,'owner_permutations_old_to_new':owner_maps,
        'cartesian_product_actions_enumerated':actions,
        'base_low_profile':C1,'base_high_profile':C2,
        'base_seed_and_terminal_coalition':seed_owners,
        'base_transition_coalition':protected,'base_zero_restorer':4}))
    coeff_before=defaultdict(Q)
    coeff_after=defaultdict(Q)
    K=Q(0); rhs=Q(0)
    kind_counts=Counter()
    lines=[]
    for (kind,low,high,C),count in sorted(multiplicities.items()):
        base=Q(1,3) if kind=='seed_coverage' else Q(1)
        weight=base*count/actions
        row={'kind':kind,'multiplicity':count,'weight':fraction(weight),
             'low_profile_id':ids[low] if low else None,'high_profile_id':ids[high],
             'coalition':C,'K_coefficient':0,'rhs':0,'terms':[]}
        if kind=='budget':
            row['K_coefficient']=1
            row['terms']=[[ids[high],i,-1] for i in C]
        elif kind=='tcwm':
            row['terms']=[[ids[high],i,1] for i in C]+[[ids[low],i,-1] for i in C]
        else:
            row['terms']=[[ids[high],i,1] for i in C]
            if kind in ('seed_coverage','terminal_coverage'):
                row['rhs']=1
        for p,i,c in row['terms']:
            coeff_after[p,i]+=weight*c
            if kind!='restorer_nonnegative':
                coeff_before[p,i]+=weight*c
        K+=weight*row['K_coefficient']; rhs+=weight*row['rhs']
        kind_counts[kind]+=1
        lines.append(json.dumps(row,separators=(',',':'),sort_keys=True))
    assert K==1 and rhs==Q(4,3)
    assert all(c==0 for c in coeff_after.values())
    assert all(c<=0 for c in coeff_before.values())
    negative=[(p,i,c) for (p,i),c in coeff_before.items() if c<0]
    assert all(profiles[p][i]==0 for p,i,c in negative)
    payload=('\n'.join(lines)+'\n').encode()
    packed=gzip.compress(payload,compresslevel=9,mtime=0)
    rowfile=HERE/'LIFTED_CERTIFICATE_ROWS.jsonl.gz'
    rowfile.write_bytes(packed)
    artifacts.append({'file':rowfile.name,'bytes':len(packed),'uncompressed_bytes':len(payload),
                      'sha256':hashlib.sha256(packed).hexdigest(),
                      'uncompressed_sha256':hashlib.sha256(payload).hexdigest()})
    summary={'status':'PASS','scope':'complete actual-variable finite lift for k=M=s=2; general tail scalar algebra separately checked',
        'compressed_parameter_cases':checks,'GL_order':len(maps),'owner_group_order':len(owner_maps),
        'group_actions_enumerated':actions,'raw_inequality_instances':sum(raw_counts.values()),
        'raw_instances_by_kind':dict(raw_counts),'distinct_weighted_rows':len(multiplicities),
        'distinct_rows_by_kind':dict(kind_counts),'distinct_profiles':len(profiles),
        'low_orbit_profiles':sum(0 in p for p in profiles),'high_orbit_profiles':sum(0 not in p for p in profiles),
        'touched_payment_coordinates':len(coeff_after),'all_payment_coefficients_after_nonnegativity_zero':True,
        'negative_coordinates_before_nonnegativity':len(negative),
        'negative_coefficient_values_before_nonnegativity':sorted({str(c) for p,i,c in negative}),
        'all_negative_coordinates_are_current_zero_report_owners':True,
        'K_coefficient':str(K),'rhs':str(rhs),'artifacts':artifacts,
        'duplicate_policy':'Every one of the 20160 actions contributes uniformly. Equal rows retain summed multiplicity.',
        'no_dummy_zero_assumption':True}
    artifact(HERE/'BUILD_RESULT.json',summary)
    print(json.dumps(summary,sort_keys=True))


if __name__=='__main__':
    main()
