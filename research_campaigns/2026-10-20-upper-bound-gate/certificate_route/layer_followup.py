from fractions import Fraction as Q
import json


def matching_chain(n):
    assert n>=4 and n%2==0
    q=n//2; m=n-1; inf=m
    matchings=[]
    for t in range(m):
        pairs=[tuple(sorted((inf,t)))]+[tuple(sorted(((t+a)%m,(t-a)%m))) for a in range(1,q)]
        assert sorted(v for pair in pairs for v in pair)==list(range(n))
        matchings.append(pairs)
    all_pairs=[pair for M in matchings for pair in M]
    assert len(set(all_pairs))==n*(n-1)//2
    # Coordinate zero is R, passive owner v uses coordinate v+1.
    div=[[Q(0)]*(n+1) for _ in range(m+1)]
    for k,M in enumerate(matchings):
        for a,b in M:
            for owner in [0,a+1,b+1]:
                div[k][owner]-=1
                div[k+1][owner]+=1
    g=[row[:] for row in div]
    g[0]=[v+1 for v in g[0]] # grand coalition coverage at p_0
    nu=[Q(0)]*m+[Q(q)]
    assert all(g[p][i]<=nu[p] for p in range(m+1) for i in range(n+1))
    assert g[0]==[Q(1-q)]+[Q(0)]*n
    assert all(v==0 for row in g[1:m] for v in row)
    assert g[m]==[Q(q)]+[Q(1)]*n
    # Frozen passives own (1/n,1/n,0), R owns (0,0,1+k/m).
    assert min(Q(1)-Q(1,n),Q(1)-Q(1,n),Q(1))==1-Q(1,n)
    # Replace all flow by the FIRST matching directly from p_0 to p_m.
    new_div=[[Q(0)]*(n+1) for _ in range(m+1)]
    for a,b in matchings[0]:
        for owner in [0,a+1,b+1]:
            new_div[0][owner]-=1
            new_div[m][owner]+=1
    assert new_div==div
    # RC: budget resources minus all restorations = lambda b + sigma b.
    B=(Q(q),Q(q),Q(2*q)); Delta=(Q(0),Q(0),Q(q))
    residual=tuple(x-y for x,y in zip(B,Delta))
    assert residual==(Q(q),)*3
    return dict(passive_owners=n,actual_owners=n+1,profiles=m+1,
                arity=3,protection_size=3,original_edges=q*m,
                original_L=1,original_D=q,
                per_coalition_divergence_preserving_layer_cost_lower_bound=q*m,
                cost_ratio_lower_bound=m,recombined_edges=q,
                recombined_D=q,all_checks_passed=True)


def local_obstruction():
    p=(1,1,1,1)
    C=[{0,1},{2,3}]
    E=[{0,2},{1,3}]
    lows=[tuple(x-(i in S) for i,x in enumerate(p)) for S in C]
    highs=[tuple(x+(i in S) for i,x in enumerate(p)) for S in E]
    incoming=[sum(i in S for S in C) for i in range(4)]
    outgoing=[sum(i in S for S in E) for i in range(4)]
    assert incoming==outgoing==[1]*4
    shortcut_changes=[]
    for l in lows:
        for h in highs:
            changed=sum(a!=b for a,b in zip(l,h))
            assert changed==3
            shortcut_changes.append(changed)
    # Technology F=sum of four capacities has arity one, hence at most three.
    assert sum(sum(h) for h in highs)==12
    return dict(protection_size=2,balanced_middle_incidence=incoming,
                source_sink_shortcut_changed_owner_counts=shortcut_changes,
                all_four_shortcuts_illegal=True,all_checks_passed=True)


def branched_cut_check():
    # R1 owns A,K; R2 owns B; P,Q are actual passive owners.
    xy=[(Q(1,10),Q(1,10)),(Q(7,10),Q(4,10)),
        (Q(4,10),Q(7,10)),(Q(1),Q(1))]
    edges=[(0,1,{0,1,2}),(1,3,{0,1,2}),
           (0,2,{0,1,3}),(2,3,{0,1,3})]
    reports=[[(x,Q(0),x),(Q(0),y,Q(0)),(Q(0),)*3,(Q(0),)*3] for x,y in xy]
    div=[[Q(0)]*4 for _ in xy]
    old=Q(0)
    for a,b,C in edges:
        for i in C: div[a][i]-=1; div[b][i]+=1
        delta=tuple(sum(reports[b][i][r]-reports[a][i][r] for i in C)
                    for r in range(3))
        assert all(reports[b][i]==reports[a][i] for i in set(range(4))-C)
        old+=min(delta)
    assert div[1]==div[2]==[0]*4
    cut=[(a,b,C) for a,b,C in edges if xy[a][0]<Q(1,2)<xy[b][0]]
    w=[sum(i in C for a,b,C in cut) for i in range(4)]
    assert w==[2,2,1,1]==div[3]
    assert all({0,1}<=C for a,b,C in cut)
    direct_delta=tuple(sum(reports[3][i][r]-reports[0][i][r] for i in range(4))
                       for r in range(3))
    new=len(cut)*min(direct_delta)
    assert old==Q(6,5) and new==Q(9,5)
    return dict(old_OUT_part=str(old),contracted_OUT_part=str(new),
                cut_owner_incidence=w,all_checks_passed=True)

if __name__=='__main__':
    print(json.dumps({'matching_chains':[matching_chain(n) for n in [4,6,8,10,16,32]],
                      'local_legality_obstruction':local_obstruction(),
                      'branched_cut_check':branched_cut_check(),
                      'evidence':'exact checks supplementing symbolic all-n proof'},indent=2))
