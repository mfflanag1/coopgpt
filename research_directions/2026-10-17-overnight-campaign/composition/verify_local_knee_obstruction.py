#!/usr/bin/env python3
from fractions import Fraction as Q
import json


def require(test, message):
    if not test:
        raise RuntimeError(message)


edges = ((0, 1), (1, 2))
w = (Q(5, 4), Q(3))
q = (Q(5, 8), Q(3, 2), Q(3, 2))
cases = [
    ((Q(5, 8), Q(15, 8), Q(1)), (Q(1, 4), Q(1), Q(2)), (Q(1, 4), Q(1))),
    ((Q(3, 4), Q(15, 8), Q(1)), (Q(45, 196), Q(50, 49), Q(97, 49)), (Q(27, 98), Q(1))),
]
payments = []
for c, p, lam in cases:
    degree = [Q(0)]*3
    for j, (u, v) in enumerate(edges):
        require(p[u]+p[v] == w[j], 'tight cover')
        degree[u] += lam[j]
        degree[v] += lam[j]
    require(degree == [c[v]*min(p[v]/q[v], Q(1)) for v in range(3)], 'exact stationarity')
    require(p[0] < q[0] and p[1] < q[1] and p[2] > q[2], 'quadratic/linear pieces')
    payments.append(c[0]*p[0]+c[2]*p[2])
require(payments[0]-payments[1] == Q(7, 1568), 'strict incentive failure')
print(json.dumps({'status': 'PASS', 'payments': payments, 'profitable_withholding_gain': payments[0]-payments[1],
                  'arithmetic': 'exact rationals', 'scope': 'two-profile counterexample to specified local-knee mechanism'},
                 default=str, indent=2))
