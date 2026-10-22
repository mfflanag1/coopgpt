"""Standard-library rational checks for the contextual selection barriers."""
from fractions import Fraction as F
from itertools import permutations, combinations
import json


def pool_value(capacities, coalition):
    return min(sum(capacities[2*j+t] for t in range(2) if 2*j+t in coalition)
               for j in range(len(capacities)//2))


def coalitions(n):
    for mask in range(1 << n):
        yield {i for i in range(n) if mask >> i & 1}


stats = {'core_row_checks': 0, 'witness_checks': 0, 'shapley_cases': 0}
for k in range(2, 7):
    n = 2*k
    for j in range(k):
        cap = [F(4) if i % 2 == 0 else F(1) for i in range(n)]
        cap[2*j] = F(1)
        q = [F(1) if i//2 == j else F(0) for i in range(n)]
        for s in coalitions(n):
            assert sum(q[i] for i in s) >= pool_value(cap, s)
            stats['core_row_checks'] += 1
        big_lows = {2*l+1 for l in range(k) if l != j}
        assert pool_value(cap, set(range(n))-big_lows) == 2
        for owner in [2*j, 2*j+1]:
            assert pool_value(cap, {owner}|big_lows) == 1
            stats['witness_checks'] += 1
    for i, j in combinations(range(k), 2):
        cap = [F(4) if x % 2 == 0 else F(1) for x in range(n)]
        cap[2*i] = cap[2*j] = F(1)
        big_lows = {2*l+1 for l in range(k) if l not in (i, j)}
        assert pool_value(cap, set(range(n))-big_lows) == 2
        for a in (2*i, 2*i+1):
            for b in (2*j, 2*j+1):
                assert pool_value(cap, {a,b}|big_lows) == 1
                stats['witness_checks'] += 1
        for lam in (F(0), F(1,4), F(1,2), F(3,4), F(1)):
            q = [lam if x//2 == i else 1-lam if x//2 == j else F(0)
                 for x in range(n)]
            assert sum(q) == 2
            assert sum(x*x for x in q) == 1 + 4*(lam-F(1,2))**2
            for s in coalitions(n):
                assert sum(q[x] for x in s) >= pool_value(cap, s)
                stats['core_row_checks'] += 1
    assert F(2,1) + F(k-1,2) == F(k+3,2)
    for eps in (F(0), F(1,10), F(1,4), F(49,100)):
        assert 2-4*eps+F(k-1,2)*(1-2*eps) == (1-2*eps)*F(k+3,2)

# Actual three-owner Shapley scores from permutation marginals.
for eps in (F(0), F(1,10), F(1,4)):
    def value(s):
        return min((1+eps) if 0 in s else F(0), F((1 in s)+(2 in s)))
    phi = [F(0)]*3
    for order in permutations(range(3)):
        s = set()
        for i in order:
            old = value(s)
            s.add(i)
            phi[i] += (value(s)-old)/6
    assert phi == [(2+eps)/3, (1+2*eps)/6, (1+2*eps)/6]
    pair_density = 1/(phi[0]+phi[1])
    assert pair_density >= 1
    q = [pair_density*w for w in phi]
    assert q[0] == (4+2*eps)/(5+4*eps)
    for s in coalitions(3):
        assert sum(q[i] for i in s) >= value(s)
    stats['shapley_cases'] += 1
stats['status'] = 'PASS'
print(json.dumps(stats, indent=2))
