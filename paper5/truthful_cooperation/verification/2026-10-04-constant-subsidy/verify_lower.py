"""Exact orbit-projected dual checks from actual original-owner coalitions.
The conventional symmetrization argument justifies equal payments within roles.
No optimizer or numerical discovery code is imported.
"""
import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def profiles(k, m):
    require(type(k) is int and k >= 3 and type(m) is int and m >= 2, 'parameters')
    t = 2*m-2
    low = (1, 1)+(2,)*(m-2)
    high = (1,)+(2,)*(m-2)+(t,)
    return {'X': (low,)+(high,)*(k-1), 'Y': (low, low)+(high,)*(k-2)}


def role(label, capacities, pool, owner):
    m=len(capacities[pool]); t=2*m-2
    current=tuple(sorted(capacities[pool])); value=capacities[pool][owner]
    low=(1,1)+(2,)*(m-2); high=(1,)+(2,)*(m-2)+(t,)
    if current==low:
        require(value in (1,2), 'short orbit capacity')
        r='a' if value==1 else 'b'
    else:
        require(current==high, 'long orbit capacities')
        if value==1: r='u'
        elif value==t: r='w'
        else:
            require(value==2 and m>2, 'middle orbit capacity'); r='v'
    return r if label=='X' else r.upper()


def coalition(label, kind, k, m):
    masks = []
    for j in range(k):
        short = j < (1 if label == 'X' else 2)
        if kind == 1:
            chosen = [0]
        elif kind == 2:
            require(m > 2, 'second role exists')
            chosen = [0, 1] if short else [1]
        elif kind == 3:
            chosen = [0]+list(range(2, m)) if short else list(range(m-1))
        elif kind == 4:
            chosen = list(range(m)) if short else [m-1]
        else:
            raise ValueError('coalition kind')
        masks.append(chosen)
    return masks


def make_certificate(k, m):
    q, t = m-2, 2*m-2
    rows = []
    for label, weights in [('X', {1: 2, 2: 2*q, 3: 2*(t-1), 4: 2}),
                           ('Y', {1: k-1, 2: q*(k-1), 4: k-1})]:
        rows.append({'kind': 'budget', 'profile': label,
                     'weight': 2*t if label == 'X' else k-1})
        for kind, weight in weights.items():
            if weight:
                rows.append({'kind': 'cover', 'profile': label,
                             'coalition': coalition(label, kind, k, m),
                             'weight': weight})
    rows.append({'kind': 'monotone', 'low': 'Y', 'high': 'X',
                 'owner': [0, 0], 'new_capacity': t,
                 'weight': 2*(t-1)*(k-1)})
    return {'k': k, 'm': m, 'claimed_lower': str(F((k-1)*(t-1), t*(k-1+2*t))),
            'rows': rows}


def verify(cert):
    k, m = cert['k'], cert['m']
    ps = profiles(k, m)
    total, right = Counter(), F(0)
    require(cert['rows'], 'nonempty certificate')
    for row in cert['rows']:
        require(type(row['weight']) is int and row['weight'] > 0, 'positive exact weight')
        weight = F(row['weight'])
        terms, rhs = Counter(), 0
        if row['kind'] in ('budget', 'cover'):
            label = row['profile']; c = ps[label]
            if row['kind'] == 'budget':
                T = min(map(sum, c)); terms['beta'] = T; rhs = -T
                for j in range(k):
                    for i in range(m): terms[role(label, c, j, i)] -= 1
            else:
                sets = row['coalition']
                require(len(sets) == k, 'coalition pools')
                values = []
                for j, chosen in enumerate(sets):
                    require(len(chosen) == len(set(chosen)) and
                            all(type(i) is int and 0 <= i < m for i in chosen), 'valid coalition')
                    values.append(sum(c[j][i] for i in chosen))
                    for i in chosen: terms[role(label, c, j, i)] += 1
                rhs = min(values)
        elif row['kind'] == 'monotone':
            require(row['low'] == 'Y' and row['high'] == 'X', 'report direction')
            j, i = row['owner']
            require(type(j) is int and type(i) is int and 0 <= j < k and 0 <= i < m, 'valid report owner')
            low = ps['Y']; high = [list(p) for p in low]
            new = row['new_capacity']
            require(type(new) is int and new > low[j][i], 'strict increase')
            high[j][i] = new
            require(sorted(tuple(sorted(p)) for p in high) ==
                    sorted(tuple(sorted(p)) for p in ps['X']), 'one-owner profile match')
            before=role('Y', low, j, i); after=role('X', high, j, i)
            require(before=='A' and after=='w', 'changed owner roles')
            terms[after] = 1; terms[before] = -1
        else:
            raise ValueError('allowed row kind')
        for var, val in terms.items(): total[var] += weight*val
        right += weight*rhs
    require(total['beta'] > 0, 'positive beta coefficient')
    require(all(v == 0 for var, v in total.items() if var != 'beta'), 'payment cancellation')
    bound = right/total['beta']
    require(bound == F(cert['claimed_lower']), 'claimed bound')
    return {'k': k, 'owners_per_pool': m, 'bound': str(bound),
            'beta_coefficient': str(total['beta']), 'rhs': str(right),
            'rows': len(cert['rows']), 'floor_rows': 0}


def main():
    cases = [(k,m) for k in [3,4,8,16,18,32,64,128] for m in [2,3,4,5,8,16]]
    cases += [(8*n*n+1,n+1) for n in [1,2,3,5,10]]
    results = [verify(make_certificate(k,m)) for k,m in cases]
    require(F(next(r['bound'] for r in results if r['k']==18 and r['owners_per_pool']==3)) > F(1,2), 'above half')
    diagonals = []
    for n in [1,2,3,5,10,100,1000,10000]:
        k,m,t = 8*n*n+1,n+1,2*n
        b = F((k-1)*(t-1),t*(k-1+2*t))
        require(b == F(2*n-1,2*n+1), 'diagonal identity')
        diagonals.append({'n':n,'k':k,'m':m,'bound':str(b),
                          'scope':'algebraic identity; large profiles not instantiated'})
    rejected = []
    original = make_certificate(8,4)
    mutations = []
    c=copy.deepcopy(original);c['rows'][0]['weight']=-1;mutations.append(('negative multiplier',c,'positive exact weight'))
    c=copy.deepcopy(original);c['rows'][0]['weight']=1.0;mutations.append(('float multiplier',c,'positive exact weight'))
    c=copy.deepcopy(original);c['claimed_lower']='1';mutations.append(('wrong claim',c,'claimed bound'))
    c=copy.deepcopy(original);c['rows'][1]['coalition'][0]=[4];mutations.append(('invalid owner',c,'valid coalition'))
    c=copy.deepcopy(original);c['rows'][1]['coalition'][0]=[0,0];mutations.append(('duplicate owner',c,'valid coalition'))
    c=copy.deepcopy(original);c['rows'].pop(0);mutations.append(('missing budget',c,'payment cancellation'))
    c=copy.deepcopy(original);c['rows'][-1]['low']='X';mutations.append(('reversed report',c,'report direction'))
    c=copy.deepcopy(original);c['rows'][-1]['new_capacity']=1;mutations.append(('equal reports',c,'strict increase'))
    c=copy.deepcopy(original);c['rows'][-1]['new_capacity']=5;mutations.append(('wrong high profile',c,'one-owner profile match'))
    c=copy.deepcopy(original);c['rows'][0]['kind']='floor';mutations.append(('hidden fairness row',c,'allowed row kind'))
    c=copy.deepcopy(original);c['rows'][1]['coalition'][0]=[];mutations.append(('lost coalition value',c,'payment cancellation'))
    c=copy.deepcopy(original);c['rows'][2]['coalition'][1].append(2);c['rows'][2]['coalition'][2]=[];mutations.append(('same coefficients lower worth',c,'claimed bound'))
    c=copy.deepcopy(original);c['rows'][-1]['owner']=[0,2];mutations.append(('report by short 2-owner',c,'one-owner profile match'))
    c=copy.deepcopy(original);c['rows'][-1]['owner']=[2,0];mutations.append(('report by long unit owner',c,'one-owner profile match'))
    c=make_certificate(8,2);c['claimed_lower']='1';mutations.append(('m2 wrong claim',c,'claimed bound'))
    c=make_certificate(8,2);c['rows'][-1]['owner']=[2,0];mutations.append(('m2 wrong report owner',c,'one-owner profile match'))
    for name, cert, expected in mutations:
        try: verify(cert)
        except ValueError as err:
            require(str(err)==expected, 'unexpected rejection: '+name+': '+str(err))
            rejected.append({'mutation':name,'reason':str(err)})
        else: raise ValueError('accepted corruption: '+name)
    result={'status':'PASS','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'certified_profiles_pairs':len(results),'certificates':results,
            'diagonal_identities':diagonals,'mutations_rejected':rejected,
            'limitations':['Conventional symmetrization and all-parameter proof are in LOWER_BOUND.txt.',
                           'Checks reconstruct named original-owner coalitions, not all coalitions.',
                           'Large diagonal identities certify arithmetic, not materialized profiles.']}
    Path(__file__).with_name('EXACT_LOWER.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',len(results),'exact duals;',len(rejected),'corruptions rejected')


if __name__=='__main__': main()
