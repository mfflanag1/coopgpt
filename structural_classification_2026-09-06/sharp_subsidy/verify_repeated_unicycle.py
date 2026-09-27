"""Exact coverage and fixed-obstruction certificates; no optimization imports."""
from itertools import product, combinations, permutations
from pathlib import Path
from copy import deepcopy
import json
from verify_cyclic_patterns import check

def coverage():
    representatives = set()
    count = 0
    for P in combinations(product(range(4), repeat=3), 2):
        if any(P[0][s] == P[1][s] for s in range(3)):
            continue
        if set(P[0]) | set(P[1]) != set(range(4)):
            continue
        if not set(P[0]) & set(P[1]):
            continue
        if all(len(set(t)) == 3 for t in P):
            continue
        count += 1
        representatives.add(min(tuple(sorted(tuple(p[t[s]] for s in ss) for t in P))
                                for p in permutations(range(4))
                                for ss in permutations(range(3))))
    return count, representatives

def verify(data):
    count, representatives = coverage()
    actual = [tuple(tuple(t) for t in r['certificate']['P']) for r in data['records']]
    if count != 216 or data['labeled_patterns'] != count:
        raise ValueError('coverage count')
    if len(actual) != len(set(actual)) or set(actual) != representatives:
        raise ValueError('incomplete or duplicated orbit coverage')
    for record in data['records']:
        if record['certificate']['m'] != 4:
            raise ValueError('size')
        result = check(record['certificate'], check_protected=False)
        if result['fixed_pattern_lower'] != '1/6' or result['fixed_pattern_upper'] != '1/6':
            raise ValueError('claimed exact optimum not certified')
    return {'status': 'PASS', 'labeled_patterns': count, 'orbits': len(actual),
            'exact_fixed_obstruction_optimum': '1/6',
            'scope': 'm=4, |P|=2, connected repeated-label unicyclic incidence multigraphs; not full subsidy'}

if __name__ == '__main__':
    data = json.loads(Path(__file__).with_name('REPEATED_UNICYCLE_AUDIT.json').read_text())
    result = verify(data)
    bad = deepcopy(data)
    bad['records'].pop()
    try:
        verify(bad)
    except ValueError:
        pass
    else:
        raise ValueError('missing orbit accepted')
    bad = deepcopy(data)
    bad['records'][0]['certificate']['inequality_multipliers'] = []
    bad['records'][0]['certificate']['equality_multipliers'] = [0] * 7
    try:
        verify(bad)
    except ValueError:
        pass
    else:
        raise ValueError('empty dual accepted')
    print(json.dumps(dict(result, negative_controls=2)))
