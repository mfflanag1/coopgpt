#!/usr/bin/env python3
"""Exact small-instance corroboration of the Huber-price candidate.

No floating point, SciPy, or mathematical extrapolation from bounded tests.
The optimizer is found by exhaustive tight-edge patterns, independently of
the payment derivative proof. Production is found by exhaustive half-integral
fractional vertex covers, not by the optimizer's KKT multipliers.
"""
from fractions import Fraction as Q
from itertools import product
from functools import lru_cache
import argparse
import json
import random
import time


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def h(x):
    return x*x if x <= Q(1, 2) else x-Q(1, 4)


@lru_cache(maxsize=None)
def active_patterns(n, edges):
    patterns = []
    for mask in range(1 << len(edges)):
        adjacency = [[] for _ in range(n)]
        for j, (u, v) in enumerate(edges):
            if (mask >> j) & 1:
                adjacency[u].append(v)
                adjacency[v].append(u)
        seen = set()
        components = []
        for start in range(n):
            if start in seen:
                continue
            colors = {start: 0}
            stack = [start]
            odd = False
            while stack:
                u = stack.pop()
                seen.add(u)
                for v in adjacency[u]:
                    if v not in colors:
                        colors[v] = 1-colors[u]
                        stack.append(v)
                    elif colors[v] == colors[u]:
                        odd = True
            if len(colors) == 1:
                components.append(('isolated', (start,), ()))
            elif odd:
                components.append(('half', tuple(sorted(colors)), ()))
            else:
                components.append(('pair', tuple(sorted(v for v in colors if colors[v] == 0)),
                                   tuple(sorted(v for v in colors if colors[v] == 1))))
        patterns.append(tuple(components))
    return tuple(dict.fromkeys(patterns))


@lru_cache(maxsize=200000)
def price(capacities, edges):
    n = len(capacities)
    positive = tuple(v for v in range(n) if capacities[v] > 0)
    if len(positive) != n:
        reindex = {v: j for j, v in enumerate(positive)}
        small_edges = tuple((reindex[u], reindex[v]) for u, v in edges
                            if u in reindex and v in reindex)
        small = price(tuple(capacities[v] for v in positive), small_edges)
        result = [Q(1)]*n
        for j, v in enumerate(positive):
            result[v] = small[j]
        return tuple(result)
    if not edges:
        return (Q(0),)*n
    best = None
    answers = set()
    for pattern in active_patterns(n, edges):
        p = [Q(0)]*n
        for kind, left, right in pattern:
            if kind == 'half':
                for v in left:
                    p[v] = Q(1, 2)
            elif kind == 'pair':
                a = sum(capacities[v] for v in left)
                b = sum(capacities[v] for v in right)
                t = Q(b, 2*a) if a >= b else 1-Q(a, 2*b)
                for v in left:
                    p[v] = t
                for v in right:
                    p[v] = 1-t
        if any(p[u]+p[v] < 1 for u, v in edges):
            continue
        objective = sum(c*h(x) for c, x in zip(capacities, p))
        if best is None or objective < best:
            best = objective
            answers = {tuple(p)}
        elif objective == best:
            answers.add(tuple(p))
    require(best is not None, ('no candidate', capacities, edges))
    require(len(answers) == 1, ('nonunique oracle', capacities, edges, answers))
    return answers.pop()


@lru_cache(maxsize=None)
def cover_vertices(n, edges):
    return tuple(x for x in product((Q(0), Q(1, 2), Q(1)), repeat=n)
                 if all(x[u]+x[v] >= 1 for u, v in edges))


@lru_cache(maxsize=200000)
def production(capacities, edges):
    return min(sum(c*x for c, x in zip(capacities, p))
               for p in cover_vertices(len(capacities), edges))


def pay(bundles, edges):
    c = tuple(sum(row[v] for row in bundles) for v in range(len(bundles[0])))
    p = price(c, edges)
    return tuple(sum(b*x for b, x in zip(row, p)) for row in bundles)


def check_profile(bundles, edges, full_coalitions=True):
    n = len(bundles)
    d = len(bundles[0])
    c = tuple(sum(row[v] for row in bundles) for v in range(d))
    p = price(c, edges)
    y = pay(bundles, edges)
    value = production(c, edges)
    require(all(x >= 0 for x in y), ('negative payment', bundles, edges, y))
    require(sum(y) <= Q(3, 2)*value, ('funding', bundles, edges, p, y, value))
    if full_coalitions:
        for mask in range(1 << n):
            coalition = tuple(sum(bundles[i][v] for i in range(n) if mask >> i & 1)
                              for v in range(d))
            require(sum(y[i] for i in range(n) if mask >> i & 1) >= production(coalition, edges),
                    ('coalition', mask, bundles, edges, p, y))
    return value, sum(y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--random', type=int, default=1200)
    parser.add_argument('--seed', type=int, default=20261017)
    args = parser.parse_args()
    started = time.time()
    rng = random.Random(args.seed)
    graphs = [
        ('edge', 2, ((0, 1),)),
        ('path4', 4, ((0, 1), (1, 2), (2, 3))),
        ('star4', 4, ((0, 1), (0, 2), (0, 3))),
        ('path6', 6, tuple((i, i+1) for i in range(5))),
        ('binary7', 7, ((0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6))),
        ('triangle', 3, ((0, 1), (0, 2), (1, 2))),
        ('cycle5', 5, ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4))),
        ('complete4', 4, ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))),
    ]
    checked = transitions = 0
    worst = (Q(0), None)
    # Exhaustive mixed-owner binary bundles on the first three graphs.
    exhaustive = []
    for name, d, edges in graphs[:3]:
        count = changes = 0
        for bits in product((0, 1), repeat=2*d):
            bundles = [bits[:d], bits[d:]]
            value, total = check_profile(bundles, edges)
            y = pay(bundles, edges)
            for i in range(2):
                for v in range(d):
                    if bundles[i][v] == 0:
                        more = [list(row) for row in bundles]
                        more[i][v] = 1
                        require(pay(more, edges)[i] >= y[i], ('binary incentive', bundles, more, edges))
                        changes += 1
            count += 1
        checked += count
        transitions += changes
        exhaustive.append({'graph': name, 'profiles': count, 'coordinate_transitions': changes})
    random_counts = {name: 0 for name, _, _ in graphs}
    for trial in range(args.random):
        name, d, edges = graphs[trial % len(graphs)]
        owners = rng.randrange(2, 6)
        bundles = [[Q(rng.randrange(0, 10), rng.choice((1, 1, 2, 3))) for _ in range(d)]
                   for _ in range(owners)]
        value, total = check_profile(bundles, edges)
        y = pay(bundles, edges)
        if value and total/value > worst[0]:
            worst = (total/value, {'graph': name, 'bundles': bundles, 'payments': y, 'F': value})
        for _ in range(3):
            i = rng.randrange(owners)
            more = [row[:] for row in bundles]
            for v in range(d):
                if rng.randrange(2):
                    more[i][v] += Q(rng.randrange(0, 10), rng.choice((1, 2, 3)))
            require(pay(more, edges)[i] >= y[i], ('mixed whole-bundle incentive', bundles, more, edges, y))
            transitions += 1
        checked += 1
        random_counts[name] += 1
    # Explicit endpoint of the rule-specific funding supremum.
    edge = ((0, 1),)
    for m in (1, 2, 10, 100, 10000):
        bundles = [(Q(m), Q(0)), (Q(0), Q(1))]
        _, total = check_profile(bundles, edge)
        require(total == Q(3, 2)-Q(1, 2*m), ('sharpness', m, total))
    result = {
        'status': 'PASS', 'arithmetic': 'exact fractions throughout',
        'scope': 'finite corroboration only; general proof is separate',
        'profiles': checked, 'incentive_transitions': transitions,
        'exhaustive_binary': exhaustive, 'random_seed': args.seed,
        'random_by_graph': random_counts, 'worst_sample': worst,
        'seconds': round(time.time()-started, 3)
    }
    print(json.dumps(result, default=str, indent=2))


if __name__ == '__main__':
    main()
