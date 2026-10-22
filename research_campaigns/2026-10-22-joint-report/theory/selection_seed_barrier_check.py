"""Exact incidence, averaging, and finite-threshold checks, stdlib only."""
from fractions import Fraction as F
from itertools import combinations, product
import json


def value(cap, m, coalition):
    return min(sum(cap[i] for i in range(j*m, (j+1)*m) if i in coalition)
               for j in range(len(cap)//m))


def all_coalitions(n):
    for mask in range(1 << n):
        yield {i for i in range(n) if mask >> i & 1}


stats = {'coalition_checks': 0, 'average_checks': 0, 'scalar_checks': 0}
for m in range(2, 5):
    for k in range(2, 4):
        n = k*m
        for small in list(combinations(range(k), 1)) + list(combinations(range(k), 2)):
            cap = [m if i % m == 0 and i//m not in small else 1 for i in range(n)]
            big = [j for j in range(k) if j not in small]
            low_sets = [set(range(j*m+1, (j+1)*m)) for j in big]
            big_lows = set().union(*low_sets) if low_sets else set()
            assert value(cap, m, set(range(n))-big_lows) == m
            q = list(range(1, n+1))
            anchors_list = ([{small[0]*m+t} for t in range(m)] if len(small) == 1
                            else [{small[0]*m, small[1]*m}])
            for anchors in anchors_list:
                total = 0
                count = 0
                for picks in product(*low_sets):
                    coalition = anchors | set(picks)
                    assert value(cap, m, coalition) == 1
                    total += sum(q[i] for i in coalition)
                    count += 1
                assert F(total,count) == sum(q[i] for i in anchors) + F(sum(q[i] for i in big_lows),m-1)
                stats['average_checks'] += 1
            if len(small) == 1:
                allocation = [1 if i//m == small[0] else 0 for i in range(n)]
                assert sum(allocation) == m
            elif big:
                ell = big[0]
                allocation = [m if i == ell*m else 1 if i//m == ell else 0 for i in range(n)]
                assert sum(allocation) == 2*m-1
                assert allocation[small[0]*m] == allocation[small[1]*m] == 0
            else:
                continue
            for coalition in all_coalitions(n):
                assert sum(allocation[i] for i in coalition) >= value(cap,m,coalition)
                stats['coalition_checks'] += 1
for B in (F(1),F(5,4),F(3,2),F(7,4),F(19,10),F(199,100)):
    m = int(1/(2-B))+1
    while m <= 1/(2-B) or m < 2:
        m += 1
    eps = B-1
    gamma = 1-eps*F(m,m-1)
    assert gamma > 0
    for k in (2,3,10,100):
        cost = m*gamma + F(k-1,2)*gamma
        assert cost/m == gamma*(1+F(k-1,2*m))
        stats['scalar_checks'] += 1
stats['status'] = 'PASS'
print(json.dumps(stats, indent=2))
