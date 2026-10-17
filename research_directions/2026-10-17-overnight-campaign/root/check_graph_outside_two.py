#!/usr/bin/env python3
"""Exact finite diagnostics for the utilization-price OUT theorem.

The all-real theorem is analytic. This exercises simultaneous mixed-owner
withdrawals, zero faces, graph interactions, and rational-profit copies.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import lcm
from pathlib import Path
import importlib.util, itertools, json, random

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('unit_solver', BASE/'composition/exact_huber_solver.py')
unit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unit)

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def engine(n, edges, weights):
    denominator = lcm(*(w.denominator for w in weights))
    integer = [int(w*denominator) for w in weights]
    width = max(integer, default=0)
    lifted = [(u*width+a, v*width+w-1-a)
              for (u,v),w in zip(edges,integer) for a in range(w)]
    @lru_cache(None)
    def evaluate(capacity):
        if not width:
            return (Q(0),)*n, Q(0)
        copies = [capacity[v] for v in range(n) for _ in range(width)]
        cert = unit.certificate(copies, lifted)
        copy_prices = [min(2*p,Q(1)) for p in cert['p']]
        prices = tuple(sum(copy_prices[v*width:(v+1)*width])/denominator for v in range(n))
        value = sum(cert['lambda'])/denominator
        require(sum(c*p for c,p in zip(capacity,prices)) == 2*value, 'exact factor2 accounting')
        return prices,value
    return evaluate

def aggregate(bundles, indices):
    return tuple(sum(bundles[i][v] for i in indices) for v in range(len(bundles[0])))

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def main():
    rng = random.Random(20261017)
    cases = [
      ('edge',2,[(0,1)],[Q(1)]),
      ('path4',4,[(0,1),(1,2),(2,3)],[Q(1)]*3),
      ('triangle',3,[(0,1),(1,2),(0,2)],[Q(1)]*3),
      ('cycle5',5,[(0,1),(1,2),(2,3),(3,4),(0,4)],[Q(1)]*5),
      ('K4',4,list(itertools.combinations(range(4),2)),[Q(1)]*6),
      ('weighted_path',4,[(0,1),(1,2),(2,3)],[Q(1),Q(3),Q(2)]),
      ('weighted_K4',4,list(itertools.combinations(range(4),2)),[Q(1),Q(2),Q(3),Q(1),Q(3),Q(2)]),
      ('rational_triangle',3,[(0,1),(1,2),(0,2)],[Q(1,2),Q(3,2),Q(1)]),
    ]
    counts = dict(profiles=0, coalition_coverage=0, outside_deviations=0, full_marginal_floors=0)
    for name,n,edges,weights in cases:
        evaluate = engine(n,edges,weights)
        for trial in range(32):
            owners = [tuple(Q(rng.randrange(5),2) for _ in range(n)) for _ in range(3)]
            if trial == 0:
                owners = [(Q(0),)*n for _ in range(3)]
            elif trial == 1:
                owners = [tuple(Q(v==i%n) for v in range(n)) for i in range(3)]
            total = aggregate(owners,range(3))
            prices,value = evaluate(total)
            payments = [dot(b,prices) for b in owners]
            for i in range(3):
                off = tuple(total[v]-owners[i][v] for v in range(n))
                require(payments[i] >= value-evaluate(off)[1], f'{name}: full marginal')
                counts['full_marginal_floors'] += 1
            for mask in range(1,8):
                members = [i for i in range(3) if mask>>i&1]
                holding = aggregate(owners,members)
                before = sum(payments[i] for i in members)
                require(before >= evaluate(holding)[1], f'{name}: coverage')
                counts['coalition_coverage'] += 1
                # Vary fractions independently within every actual member bundle.
                withdrawal = tuple(sum(owners[i][v]*Q(rng.randrange(3),2) for i in members) for v in range(n))
                if trial % 8 == 0:
                    withdrawal = holding
                reduced = tuple(total[v]-withdrawal[v] for v in range(n))
                retained = tuple(holding[v]-withdrawal[v] for v in range(n))
                after_prices,_ = evaluate(reduced)
                outside = evaluate(withdrawal)[1]
                require(before-dot(retained,after_prices) >= outside,
                        f'{name}: OUT failed on {owners}, {members}, {withdrawal}')
                counts['outside_deviations'] += 1
            counts['profiles'] += 1
    result = {'status':'PASS','arithmetic':'exact Fraction','counts':counts,
              'scope':'finite diagnostics only; all-real theorem is analytic'}
    (BASE/'root/GRAPH_OUTSIDE_TWO_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
