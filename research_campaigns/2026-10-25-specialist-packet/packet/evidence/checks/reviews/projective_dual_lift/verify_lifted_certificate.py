#!/usr/bin/env python3
"""Replay the serialized positive certificate in original payment coordinates.

Checks original row validity and exact cancellation directly. It does not use
compressed q/z/eta identities or invoke a symmetrization theorem.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import gzip
import hashlib
import json

HERE=Path(__file__).resolve().parent


def main():
    data=json.loads((HERE/'PROFILE_TABLE.json').read_text())
    profiles=[tuple(p) for p in data['profiles']]
    triples=[tuple(a) for a in data['activities']]
    assert triples==sorted({triple for triple in combinations(range(1,8),3)
                            if triple[0]^triple[1]^triple[2]==0})
    assert len(profiles)==len(set(profiles))
    # A primal activity and a dual price on the common cap plus unused rows
    # prove grand production one at every serialized profile, without an LP solver.
    values={}
    for p_id,p in enumerate(profiles):
        assert len(p)==5 and all(0<=a<=7 for a in p)
        capacity=Counter(a for a in p if a)
        assert all(c==1 for c in capacity.values())
        supported=[a for a in triples if all(capacity[j]>=1 for j in a)]
        assert supported
        common=set(supported[0])
        for a in supported[1:]:
            common.intersection_update(a)
        assert common
        cap=min(common)
        price={j:int(j==cap or capacity[j]==0) for j in range(1,8)}
        assert all(sum(price[j] for j in a)>=1 for a in triples)
        assert sum(price[j]*capacity[j] for j in range(1,8))==1
        values[p_id]=1
    rows=gzip.decompress((HERE/'LIFTED_CERTIFICATE_ROWS.jsonl.gz').read_bytes()).splitlines()
    g=defaultdict(Q); before=defaultdict(Q)
    K=Q(0); rhs=Q(0)
    row_counts=Counter(); multiplicities=Counter(); distinct=set()
    saved_multiplicities=Counter(); multiplicity_histogram=defaultdict(Counter)
    for encoded in rows:
        row=json.loads(encoded)
        kind=row['kind']; weight=Q(*row['weight'])
        assert weight>0 and isinstance(row['multiplicity'],int) and row['multiplicity']>0
        assert weight==Q(row['multiplicity'],20160*(3 if kind=='seed_coverage' else 1))
        high_id=row['high_profile_id']; high=profiles[high_id]
        low_id=row['low_profile_id']
        C=tuple(row['coalition'])
        assert C==tuple(sorted(set(C))) and all(0<=i<5 for i in C)
        if kind=='budget':
            assert C==tuple(range(5)) and row['K_coefficient']==values[high_id] and row['rhs']==0
            expected=[[high_id,i,-1] for i in C]
        elif kind in ('seed_coverage','terminal_coverage'):
            assert row['K_coefficient']==0 and row['rhs']==1
            # Three unit capacities forming an activity give lower one;
            # price 1/3 on every row gives matching upper one for this coalition.
            assert len(C)==3 and tuple(sorted(high[i] for i in C)) in triples
            assert all(high[i] for i in C)
            expected=[[high_id,i,1] for i in C]
        elif kind=='tcwm':
            low=profiles[low_id]
            assert len(C)<=2 and row['K_coefficient']==row['rhs']==0
            changed={i for i in range(5) if low[i]!=high[i]}
            assert len(changed)==1 and changed<=set(C)
            assert all(low[i]==0 and high[i]!=0 for i in changed)
            assert all(low[i]==high[i] for i in range(5) if i not in changed)
            expected=[[high_id,i,1] for i in C]+[[low_id,i,-1] for i in C]
        elif kind=='restorer_nonnegative':
            assert len(C)==1 and high[C[0]]==0
            assert row['K_coefficient']==row['rhs']==0
            expected=[[high_id,C[0],1]]
        else:
            raise AssertionError(kind)
        assert row['terms']==expected
        key=(kind,low_id,high_id,C)
        assert key not in distinct
        distinct.add(key)
        saved_multiplicities[key]=row['multiplicity']
        multiplicity_histogram[kind][row['multiplicity']]+=1
        for p_id,i,c in expected:
            g[p_id,i]+=weight*c
            if kind!='restorer_nonnegative':
                before[p_id,i]+=weight*c
        K+=weight*row['K_coefficient']; rhs+=weight*row['rhs']
        row_counts[kind]+=1; multiplicities[kind]+=row['multiplicity']
    assert K==1 and rhs==Q(4,3) and all(v==0 for v in g.values())
    assert all(v<=0 for v in before.values())
    negative=[(p,i,v) for (p,i),v in before.items() if v<0]
    assert all(profiles[p][i]==0 for p,i,v in negative)
    assert all(count==20160 for count in multiplicities.values())
    # Reconstruct the claimed group size separately from the builder's method.
    action_data=json.loads((HERE/'ACTION_GROUPS.json').read_text())
    maps=[tuple(x) for x in action_data['resource_maps_on_0_through_7']]
    perms=[tuple(x) for x in action_data['owner_permutations_old_to_new']]
    assert len(maps)==len(set(maps))==168 and len(perms)==len(set(perms))==120
    for f in maps:
        assert sorted(f)==list(range(8)) and f[0]==0
        assert all(f[a^b]==(f[a]^f[b]) for a in range(8) for b in range(8))
    assert all(sorted(pi)==list(range(5)) for pi in perms)
    # Reconstruct every action's rows using inverse owner indexing, independently
    # of the builder's old-to-new assignment loop; retain all duplicate actions.
    ids={p:i for i,p in enumerate(profiles)}
    reconstructed=Counter()
    actions=0
    for f in maps:
        for pi in perms:
            inverse=[pi.index(i) for i in range(5)]
            low=tuple(f[action_data['base_low_profile'][inverse[i]]] for i in range(5))
            high=tuple(f[action_data['base_high_profile'][inverse[i]]] for i in range(5))
            branch=tuple(sorted(pi[i] for i in action_data['base_seed_and_terminal_coalition']))
            C=tuple(sorted(pi[i] for i in action_data['base_transition_coalition']))
            eta=(pi[action_data['base_zero_restorer']],)
            for key in (('budget',None,ids[high],tuple(range(5))),
                        ('terminal_coverage',None,ids[high],branch),
                        ('tcwm',ids[low],ids[high],C),
                        ('seed_coverage',None,ids[low],branch),
                        ('restorer_nonnegative',None,ids[low],eta)):
                reconstructed[key]+=1
            actions+=1
    assert actions==20160 and reconstructed==saved_multiplicities
    result={'status':'PASS','arithmetic':'fractions.Fraction',
            'verified_from':'serialized actual-variable inequalities, independently of quotient orbit identities',
            'profiles_with_exact_primal_dual_value_checked':len(profiles),
            'rows_checked':len(rows),'rows_by_kind':dict(row_counts),
            'raw_action_multiplicities_by_kind':dict(multiplicities),
            'group_orders':[len(maps),len(perms)],'group_actions':len(maps)*len(perms),
            'all_group_action_multiplicities_reconstructed':True,
            'multiplicity_histograms':{kind:dict(hist) for kind,hist in multiplicity_histogram.items()},
            'payment_coordinates_cancelled':len(g),'K_coefficient':str(K),'rhs':str(rhs),
            'negative_coordinates_before_nonnegative_rows':len(negative),
            'nonnegative_rows_are_not_zero_payment_assumptions':True,
            'input_hashes':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                           for name in ('PROFILE_TABLE.json','ACTION_GROUPS.json','LIFTED_CERTIFICATE_ROWS.jsonl.gz')}}
    (HERE/'VERIFICATION_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
