"""Rejects an adaptive cycle-pair zero reduction using complete finite edge coverage."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import json
from verify_cyclic_patterns import check
from verify_cycle_boundary import upper

def verify(data):
    P = [[0,1,3],[2,4,1],[5,2,0]]
    c = data['unrestricted']
    if c['m'] != 6 or c['P'] != P:
        raise ValueError('unrestricted scope')
    baseline = check(c, check_protected=False)
    if baseline['fixed_pattern_lower'] != '2/9' or baseline['fixed_pattern_upper'] != '2/9':
        raise ValueError('unrestricted optimum')
    # Only labels 0,1,2 have incidence degree two; labels 3,4,5 are leaves.
    # Thus the unique cycle traverses all three P-nodes and labels 0,1,2.
    degree = [sum(t.count(j) for t in P) for j in range(6)]
    if degree != [2,2,2,1,1,1]:
        raise ValueError('incidence topology')
    required = {(0,0,1), (1,2,1), (2,2,0)}
    seen = set()
    for d in data['restrictions']:
        edge = tuple(d['zero_pair'])
        if d['m'] != 6 or d['P'] != P or edge not in required or edge in seen:
            raise ValueError('restricted scope/duplicate edge')
        seen.add(edge)
        if upper(d) != F(58,267):
            raise ValueError('restricted upper')
    if seen != required:
        raise ValueError('missing cycle-pair case')
    return {'status':'PASS','unrestricted_optimum':'2/9','all_cycle_pair_restriction_upper':'58/267',
            'minimum_loss':'4/801','cycle_pairs_checked':3,
            'scope':'adaptive zero-pair reduction on this fixed support fails; global subsidy unresolved'}

if __name__ == '__main__':
    d = json.loads(Path(__file__).with_name('ADAPTIVE_BOUNDARY_COUNTEREXAMPLE.json').read_text())
    result = verify(d)
    for mode in ('missing','empty'):
        bad = deepcopy(d)
        if mode == 'missing':
            bad['restrictions'].pop()
        else:
            r = bad['restrictions'][0]
            r['ineq'] = ['0'] * len(r['ineq'])
            r['eq'] = ['0'] * len(r['eq'])
        try:
            verify(bad)
        except ValueError:
            continue
        raise ValueError('negative control accepted: '+mode)
    print(json.dumps(dict(result,negative_controls=2)))
