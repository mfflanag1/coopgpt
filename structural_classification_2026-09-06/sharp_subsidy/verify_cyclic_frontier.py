"""Exact fixed-support bounds and independently checked full-core subsidy certificates.

No numerical solver or discovery layout is imported. A fixed-P upper bound is
never used as an upper bound on the market's other subsidy obstructions.
"""
from pathlib import Path
from itertools import product
from fractions import Fraction as Q
from copy import deepcopy
import json
from verify_cyclic_patterns import check


def require(condition, message):
    if not condition:
        raise ValueError(message)


def geometry(m, matching):
    require(type(m) is int and m > 0, 'size')
    require(all(len(t) == 3 and all(type(j) is int and 0 <= j < m for j in t) for t in matching), 'matching indices')
    require(all(len({t[s] for t in matching}) == len(matching) for s in range(3)), 'matching overlaps')
    edges = set()
    for a, b, c in list(matching) + [(j,j,j) for j in range(m)]:
        edges.update([(0,a,b),(1,a,c),(2,b,c)])
    edges = sorted(edges)
    lookup = {edge:i for i,edge in enumerate(edges)}
    teams = []
    for a,b,c in product(range(m), repeat=3):
        pair_ids = [lookup[e] for e in ((0,a,b),(1,a,c),(2,b,c)) if e in lookup]
        if pair_ids:
            teams.append(((a,m+b,2*m+c), pair_ids))
    return edges, lookup, teams


def sparse_rows(raw, count):
    seen = set()
    for row, value in raw:
        require(type(row) is int and 0 <= row < count and row not in seen, 'dual row index')
        seen.add(row)
        value = Q(value)
        require(value >= 0, 'negative dual multiplier')
        yield row, value


def full_market(data, pattern):
    m = data['m']; n = 3*m
    require(m == pattern['m'] and data['P'] == pattern['P'], 'full certificate market mismatch')
    edges, lookup, teams = geometry(m, data['P'])
    weights = list(map(Q, data['weights']))
    require(len(weights) == len(edges) and min(weights) >= 0, 'pair weights')
    require(weights == [Q(z,pattern['primal_scale']) for z in pattern['primal_integers'][:len(edges)]], 'weights differ from fixed-support primal')
    require(sum(weights[lookup[(s,j,j)]] for s in range(3) for j in range(m)) == 1, 'diagonal worth')
    values = [sum(weights[e] for e in ids) for _,ids in teams]
    ideals = list(map(Q, data['H']))
    require(len(ideals) == n and min(ideals) >= 0, 'ideal format')
    require(len(data['core_witnesses']) == n and len(data['ideal_upper_duals']) == n, 'ideal inventory')
    for i,(raw,dual) in enumerate(zip(data['core_witnesses'], data['ideal_upper_duals'])):
        x = list(map(Q,raw))
        require(len(x) == n and min(x) >= 0 and sum(x) == 1 and x[i] == ideals[i], 'core witness endpoint')
        require(all(sum(x[j] for j in team) >= v for (team,_),v in zip(teams,values)), 'core team coverage')
        nu = Q(dual['nu']); coefficient = [nu]*n; bound = nu
        for row, value in sparse_rows(dual['lambda'],len(teams)):
            bound -= value*values[row]
            for j in teams[row][0]:
                coefficient[j] -= value
        require(all(c >= int(j == i) for j,c in enumerate(coefficient)), 'ideal upper dual coefficient')
        require(bound == ideals[i], 'ideal upper objective')
    # Zero-worth omitted triples are covered by nonnegative coordinates. Each
    # coalition's disjoint-team production is covered by summing these bounds.
    y = list(map(Q,data['protected_y']))
    require(len(y) == n and all(y[i] >= ideals[i]/3 for i in range(n)), 'protected ideal floors')
    require(all(sum(y[j] for j in team) >= v for (team,_),v in zip(teams,values)), 'protected team coverage')
    mu = list(map(Q,data['subsidy_dual']['mu']))
    require(len(mu) == n and min(mu) >= 0, 'subsidy floor dual')
    capacity = mu[:]; bound = sum(a*h/3 for a,h in zip(mu,ideals))
    for row,value in sparse_rows(data['subsidy_dual']['lambda'],len(teams)):
        bound += value*values[row]
        for j in teams[row][0]:
            capacity[j] += value
    require(max(capacity) <= 1, 'subsidy dual capacity')
    require(bound == sum(y), 'subsidy primal dual gap')
    require(sum(y)-1 == Q(data['subsidy']) >= 0, 'subsidy value')
    return {'exact_witness_market_subsidy':str(sum(y)-1), 'exact_ideal_count':n, 'core_team_checks':n*len(teams)}


def topology(data):
    m=data['m']; p=data['P']; neighbors=[set() for _ in range(m+len(p))]
    used_sectors=[set() for _ in range(m)]
    for k,t in enumerate(p):
        require(len(set(t)) == 3, 'frontier has repeated-label team')
        for s,j in enumerate(t):
            neighbors[j].add(m+k); neighbors[m+k].add(j); used_sectors[j].add(s)
    visited={0}; pending=[0]
    while pending:
        for j in neighbors[pending.pop()] - visited:
            visited.add(j); pending.append(j)
    require(len(visited) == len(neighbors), 'disconnected incidence support')
    counts=[sum(len(neighbors[j]) == d for j in range(m)) for d in (1,2,3)]
    leaves=[sum(len(neighbors[j]) == 1 and s in used_sectors[j] for j in range(m)) for s in range(3)]
    rank=3*len(p)-len(neighbors)+1
    return {'degree_counts':counts, 'sector_leaf_counts':leaves, 'cycle_rank':rank}


def run():
    root=Path(__file__).parent
    records=json.loads((root/'CYCLIC_FRONTIER_CERTIFICATES.json').read_text())
    expected=[f'CYCLIC_FRONTIER_{r}_{c}_{seed}' for r in (6,8,10) for c in (1,2) for seed in range(4)]
    expected += [f'CYCLIC_FRONTIER_{r}_1_{seed}' for r in (2,3,4) for seed in range(3)]
    expected += ['CYCLIC_FRONTIER_COUNT_TWIN']
    require([rec['name'] for rec in records] == expected, 'frontier inventory')
    results=[]; full_count=0
    for rec in records:
        d=rec['pattern']; actual=rec.get('full_market')
        result=check(d,check_protected=actual is None)
        if actual is not None:
            result.update(full_market(actual,d));full_count+=1
            result['scope']='fixed-P all-weight bound and independently checked full witness-market subsidy'
        result.update(topology(d));result['name']=rec['name']
        if result['cycle_rank'] == 1:
            optimum=Q(len(d['P'])-1,3*len(d['P']))
            require(Q(result['fixed_pattern_lower']) == Q(result['fixed_pattern_upper']) == optimum, 'unicyclic exact optimum')
        results.append(result)
    by_name={r['name']:r for r in results}
    a=by_name['CYCLIC_FRONTIER_8_2_0'];b=by_name['CYCLIC_FRONTIER_COUNT_TWIN']
    require(a['degree_counts'] == b['degree_counts'] == [7,7,1], 'count twins degrees')
    require(a['sector_leaf_counts'] == b['sector_leaf_counts'] == [3,3,1], 'count twins sectors')
    require(a['fixed_pattern_lower'] == a['fixed_pattern_upper'] == '3/11', 'first twin optimum')
    require(b['fixed_pattern_lower'] == b['fixed_pattern_upper'] == '4/15', 'second twin optimum')
    special=next(rec for rec in records if rec['name'] == 'CYCLIC_FRONTIER_10_2_3')
    actual=special['full_market'];m=actual['m'];weights=list(map(Q,actual['weights']));ideals=list(map(Q,actual['H']))
    _,lookup,_=geometry(m,actual['P'])
    def obstruction(p):
        used={s*m+j for t in p for s,j in enumerate(t)}
        worth=sum(weights[lookup[e]] for a,b,c in p for e in ((0,a,b),(1,a,c),(2,b,c)))
        return worth+sum(ideals[i]/3 for i in range(3*m) if i not in used)-1
    smaller=[t for t in actual['P'] if t != [12,9,11]]
    require(len(smaller) == len(actual['P'])-1, 'deleted-team inventory')
    require(obstruction(actual['P']) == Q(16,57), 'full-ideal original obstruction')
    require(obstruction(smaller) == Q(869,3078), 'stronger submatching obstruction')
    require(full_count == 6, 'full ideal inventory')
    require(sum(r['cycle_rank'] == 1 for r in results) == 21, 'unicyclic inventory')
    sample=next(rec for rec in records if 'full_market' in rec)
    bad=deepcopy(sample['full_market']);bad['ideal_upper_duals'][0]['nu']='0'
    try:full_market(bad,sample['pattern'])
    except ValueError:pass
    else:raise ValueError('damaged ideal upper dual accepted')
    bad=deepcopy(sample['full_market']);bad['subsidy_dual']['mu'][0]='2'
    try:full_market(bad,sample['pattern'])
    except ValueError:pass
    else:raise ValueError('damaged subsidy dual accepted')
    bad=deepcopy(sample['pattern']);bad['inequality_multipliers']=[];bad['equality_multipliers']=[0]*len(bad['equality_multipliers'])
    try:check(bad,check_protected=False)
    except ValueError:pass
    else:raise ValueError('empty fixed-pattern dual accepted')
    print(json.dumps({'status':'PASS','cases':results,'negative_controls':3,'full_ideal_market_count':full_count,'scope':'named fixed-P all-weight bounds and exact full subsidies of their witness markets; not exhaustive supports'}))

if __name__=='__main__':run()
