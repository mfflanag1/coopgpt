#!/usr/bin/env python3
"""Exact all-coalition replay of the four-owner marginal-weight failure."""
from fractions import Fraction as F
from itertools import combinations
import json


def solve(cap, weights):
    rows = [set(s) for k in range(1, 5) for s in combinations(range(4), k)]
    def value(s):
        return min(sum(cap[i] for i in s if i < 2),
                   sum(cap[i] for i in s if i >= 2))
    x = [F(0)]*4
    free = set(range(4))
    trace = []
    while free:
        candidates = [((value(s)-sum(x[i] for i in s)) /
                       sum(weights[i] for i in s & free), s)
                      for s in rows if s & free]
        level = max(F(0), max(t for t, _ in candidates))
        if level == 0:
            break
        pin = set().union(*(s & free for t, s in candidates if t == level))
        trace.append({'level':str(level),'owners':[i+1 for i in sorted(pin)]})
        for i in pin:
            x[i] = level*weights[i]
        free -= pin
    assert all(sum(x[i] for i in s) >= value(s) for s in rows)
    return x, trace


records=[]
for cap, expected in [
    ((1,1,1,1), [F(1,2)]*4),
    ((4,1,1,1), [F(1,3),F(1,6),F(5,6),F(5,6)]),
]:
    T=min(sum(cap[:2]),sum(cap[2:]))
    weights=[]
    for i in range(4):
        remaining=list(cap)
        remaining[i]=0
        weights.append(F(T-min(sum(remaining[:2]),sum(remaining[2:])))+F(1,4))
    x,trace=solve(cap,weights)
    assert x==expected
    records.append({'profile':cap,'weights':list(map(str,weights)),
                    'payments':list(map(str,x)),'freezing':trace})
assert F(records[1]['payments'][0]) < F(records[0]['payments'][0])
print(json.dumps({'status':'PASS','all_coalitions_checked':15,'profiles':records},indent=2))
