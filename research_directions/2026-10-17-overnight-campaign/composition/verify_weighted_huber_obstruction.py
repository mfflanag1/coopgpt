#!/usr/bin/env python3
"""Exact certificates for the global-scale Huber weighted-path obstruction."""
from fractions import Fraction as Q
import json


def require(test, message):
    if not test:
        raise RuntimeError(message)


def check(m):
    edges = ((0, 1), (1, 2), (2, 3))
    w = (Q(1, 4), Q(1, 4), Q(1))
    c = (Q(m), Q(1), Q(1, m), Q(1, m))
    p = (Q(1, 4*(m+1)), Q(m, 4*(m+1)), Q(1, 2), Q(1, 2))
    lam = (Q(m, 2*(m+1)), Q(0), Q(1, m))
    degree = [Q(0)]*4
    for j, (u, v) in enumerate(edges):
        require(p[u]+p[v] >= w[j], ('Huber dual infeasible', m, j))
        require(lam[j] == 0 or p[u]+p[v] == w[j], ('KKT edge slackness', m, j))
        degree[u] += lam[j]
        degree[v] += lam[j]
    require(degree == [c[v]*min(2*p[v], Q(1)) for v in range(4)], ('KKT stationarity', m))
    require(all(0 < x < 1 for x in p), ('interior', m))
    primal = (Q(1), Q(0), Q(1, m))
    dual = (Q(0), Q(1, 4), Q(0), Q(1))
    usage = [Q(0)]*4
    for j, (u, v) in enumerate(edges):
        usage[u] += primal[j]
        usage[v] += primal[j]
        require(dual[u]+dual[v] >= w[j], ('production dual', m, j))
    require(all(x <= cap for x, cap in zip(usage, c)), ('primal feasibility', m))
    value = sum(x*a for x, a in zip(primal, w))
    require(value == sum(x*a for x, a in zip(dual, c)) == Q(1, 4)+Q(1, m), ('strong duality', m))
    payment = sum(x*a for x, a in zip(p, c))
    require(payment == Q(m, 2*(m+1))+Q(1, m), ('payment expression', m))
    ratio = payment/value
    require(ratio < 2, ('ratio', m))
    # Exact gap formula makes the limit2 transparent without numeric extrapolation.
    require(2-ratio == Q(2*(3*m+2), (m+1)*(m+4)), ('exact gap', m))
    return {'m': m, 'capacities': c, 'prices': p, 'KKT_lambda': lam,
            'primal': primal, 'dual': dual, 'F': value, 'payment': payment,
            'ratio': ratio, 'gap_from_two': 2-ratio}


if __name__ == '__main__':
    rows = [check(m) for m in (1, 2, 3, 10, 100, 1000, 1000000)]
    print(json.dumps({'status': 'PASS', 'arithmetic': 'exact rational',
                      'scope': 'Explicit general formulas independently checked at listed m; analytic limit in note',
                      'checks': rows}, default=str, indent=2))
