"""Exact finite checks of the envelope proof; not a proof by enumeration.

Standard library only. No Monte Carlo estimates and no numerical optimization
of a continuous envelope. Graph cuts are cross-checked against path blockers;
flow/cap identities use rational augmenting paths; the central domination is
checked after exact integration of the focal uniform variable.
"""
from collections import deque
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb, factorial, prod
import argparse
import json
import random


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def minimal(sets):
    sets = set(sets)
    return sorted(s for s in sets if not any(t != s and t & s == t for t in sets))


def paths(n, edges):
    out = [[] for _ in range(n)]
    for e, (a, b) in enumerate(edges):
        out[a].append((e, b))
    def walk(a, prefix):
        if a == n - 1:
            yield tuple(prefix)
        else:
            for e, b in out[a]:
                yield from walk(b, prefix + [e])
    return list(walk(0, []))


def cutsets(n, edges):
    cs = []
    for mask in range(1 << n):
        if mask & 1 and not mask >> (n - 1) & 1:
            cs.append(sum(1 << i for i, (a, b) in enumerate(edges)
                          if mask >> a & 1 and not mask >> b & 1))
    return minimal(cs)


def path_blockers(ps):
    blockers = [0]
    for p in ps:
        pm = sum(1 << e for e in p)
        blockers = minimal([b if b & pm else b | (1 << e)
                            for b in blockers for e in p])
    return blockers


def maxflow(n, edges, c, s=0, t=None):
    if t is None:
        t = n - 1
    require(s != t, 'maxflow terminals must differ')
    residual = [[Q(0) for _ in range(n)] for _ in range(n)]
    for (a, b), x in zip(edges, c):
        residual[a][b] += x
    value = Q(0)
    while True:
        parent = [-1] * n
        parent[s] = s
        todo = deque([s])
        while todo and parent[t] < 0:
            a = todo.popleft()
            for b, x in enumerate(residual[a]):
                if x > 0 and parent[b] < 0:
                    parent[b] = a
                    todo.append(b)
        if parent[t] < 0:
            return value
        b = t
        amount = None
        while b != s:
            a = parent[b]
            amount = residual[a][b] if amount is None else min(amount, residual[a][b])
            b = a
        b = t
        while b != s:
            a = parent[b]
            residual[a][b] -= amount
            residual[b][a] += amount
            b = a
        value += amount


def effective(n, edges, c):
    ds = []
    for e, (a, b) in enumerate(edges):
        bounds = [c[e]]
        if a != 0:
            bounds.append(maxflow(n, edges, c, 0, a))
        if b != n - 1:
            bounds.append(maxflow(n, edges, c, b, n - 1))
        ds.append(min(bounds))
    return ds


def weighted_sum(c, mask):
    return sum((x for e, x in enumerate(c) if mask >> e & 1), Q(0))


def uniform_cdf(weights, b, stoploss=False):
    ws = [x for x in weights if x]
    if not ws:
        return max(b, Q(0)) if stoploss else Q(b >= 0)
    n = len(ws)
    power = n + int(stoploss)
    value = Q(0)
    for bits in product((0, 1), repeat=n):
        shift = sum((x for x, bit in zip(ws, bits) if bit), Q(0))
        value += (-1) ** sum(bits) * max(Q(0), b - shift) ** power
    return value / (factorial(power) * prod(ws))


def run():
    rng = random.Random(6100626)
    counts = dict(graphs=0, profiles=0, cuts=0, coalition_values=0,
                  incomparable_cap_pairs=0, own_cap_pairs=0,
                  conditional_domination=0, uniform_identities=0,
                  comparable_cap_changes=0, path_relaxation_cases=0)
    examples = []
    for n in range(2, 6):
        possible = list(combinations(range(n), 2))
        for mask in range(1, 1 << len(possible)):
            edges = [e for i, e in enumerate(possible) if mask >> i & 1]
            ps = paths(n, edges)
            if ps and set().union(*map(set, ps)) == set(range(len(edges))):
                examples.append((n, edges, ps))
    # A parallel-owner bridge and larger overlapping DAGs supplement enumeration.
    special = [(4, [(0, 1), (0, 2), (1, 3), (1, 3), (2, 3), (1, 2)])]
    for _ in range(24):
        n = 6
        edges = [(a, b) for a, b in combinations(range(n), 2)
                 if b == a + 1 or rng.randrange(3) == 0]
        special.append((n, edges))
    examples += [(n, es, paths(n, es)) for n, es in special]

    for n, edges, ps in examples:
        m = len(edges)
        cs = cutsets(n, edges)
        require(cs == path_blockers(ps), 'vertex cuts versus path blockers')
        L = max(map(len, ps))
        K = len(cs)
        require(L <= K, 'longest path versus cut count')
        before = {(e, h) for p in ps for j, e in enumerate(p) for h in p[j + 1:]}
        partitions = {}
        H = 0
        for C in cs:
            es = [e for e in range(m) if C >> e & 1]
            # Topological edge order (all examples have increasing vertex IDs).
            rank = {}
            for e in sorted(es, key=lambda j: edges[j][0]):
                rank[e] = 1 + max([rank[h] for h in rank if (h, e) in before] or [0])
            height = max(rank.values())
            require(height == max(sum(C >> e & 1 for e in p) for p in ps),
                    'cut order height versus path intersection')
            groups = [[e for e in es if rank[e] == r] for r in range(1, height + 1)]
            for A in groups:
                require(all((e, h) not in before and (h, e) not in before
                            for e, h in combinations(A, 2)), 'not an antichain')
            partitions[C] = {e: A for A in groups for e in A}
            H += height
        require(H <= K * L <= K * K, 'structural bound')
        counts['graphs'] += 1
        counts['cuts'] += K
        profiles = [[Q(0)] * m, [Q(1)] * m,
                    [Q(rng.randrange(9), 4) for _ in edges]]
        for c in profiles:
            d = effective(n, edges, c)
            T = maxflow(n, edges, c)
            require(T == min(weighted_sum(c, C) for C in cs), 'maxflow/mincut')
            require(maxflow(n, edges, d) == T, 'normalization grand value')
            require(all(0 <= x <= T for x in d), 'effective bound')
            # Exhaustive coalitions for smaller cases, deterministic sampled larger cases.
            masks = range(1 << m) if m <= 6 else sorted({0, (1 << m) - 1} |
                      {rng.randrange(1 << m) for _ in range(16)})
            for S in masks:
                vc = maxflow(n, edges, [x if S >> i & 1 else Q(0) for i, x in enumerate(c)])
                vd = maxflow(n, edges, [x if S >> i & 1 else Q(0) for i, x in enumerate(d)])
                require(vc == vd == min(weighted_sum(d, C & S) for C in cs),
                        'coalition cap preservation and cut coverage')
                counts['coalition_values'] += 1
            for e in range(m):
                for fraction in (Q(0), Q(1, 3), Q(1)):
                    t = fraction * c[e]
                    ct = c.copy()
                    ct[e] = t
                    dt = effective(n, edges, ct)
                    require(dt[e] == min(t, d[e]), 'own cap truncation')
                    require(all(min(t, old) <= new <= old for old, new in zip(d, dt)),
                            'universal truncation sandwich')
                    counts['own_cap_pairs'] += 1
                    for h in range(m):
                        if h != e and (e, h) not in before and (h, e) not in before:
                            require(dt[h] == d[h], 'incomparable cap changed')
                            counts['incomparable_cap_pairs'] += 1
                        elif h != e and dt[h] != d[h]:
                            counts['comparable_cap_changes'] += 1
                    require(min(weighted_sum(dt, C) for C in cs) <= T, 'grand flow monotonicity')
                    for U in ([Q(0)] * m, [Q(1)] * m,
                              [Q(rng.randrange(5), 4) for _ in edges]):
                        scores = [x * u for x, u in zip(dt, U)]
                        containing = [C for C in cs if C >> e & 1]
                        CA = min(containing, key=lambda C: (weighted_sum(scores, C & ~(1 << e)), C))
                        a = weighted_sum(scores, CA & ~(1 << e))
                        excluding = [weighted_sum(scores, C) for C in cs if not C >> e & 1]
                        q = min(dt[e], max(Q(0), min(excluding) - a)) if excluding else dt[e]
                        A = partitions[CA][e]
                        residual = max(Q(0), T - sum((d[h] * U[h] for h in A if h != e), Q(0)))
                        require(q <= min(d[e], residual), 'common-profile domination (6)')
                        counts['conditional_domination'] += 1
            counts['profiles'] += 1

    for n in range(1, 6):
        samples = list(product((Q(0), Q(1, 4), Q(1)), repeat=n)) if n <= 3 else [
            tuple(Q(rng.randrange(9), 4) for _ in range(n)) for _ in range(80)]
        for ws in samples:
            for b in (Q(0), Q(1, 3), Q(1), Q(2), Q(5)):
                common = sum(ws) * uniform_cdf(ws, b)
                integrated = Q(0)
                for i, w in enumerate(ws):
                    others = ws[:i] + ws[i + 1:]
                    integrated += uniform_cdf(others, b, True) - uniform_cdf(others, b - w, True)
                require(integrated == common, 'focal integration/common-event identity')
                require(common <= 2 * b, 'uniform-sum bound')
                if sum(ws) > 2 * b:
                    require(common <= b, 'convex CDF chord bound')
                counts['uniform_identities'] += 1

    # Exact obstruction to improving the standalone group lemma to constant 1.
    group_witness = 9 * Q(1, 5) * uniform_cdf((Q(1, 5),) * 9, Q(1))
    require(group_witness == Q(51907, 40320) and group_witness > 1,
            'expected constant-one group counterexample missing')
    require(counts['comparable_cap_changes'] > 0,
            'negative control: falsely universal cap independence not detected')
    for K in range(1, 33):
        integral = sum((Q((-1) ** j * comb(K - 1, j), j + 1)
                        for j in range(K)), Q(0))
        for t in (Q(0), Q(1, 3), Q(1)):
            require(t * integral == t / K, 'series path exact payment')
        true_total = K * integral
        relaxed_total = K * uniform_cdf((Q(1),), Q(1))
        require(true_total == 1 and relaxed_total / true_total == K,
                'path proof-relaxation gap')
        counts['path_relaxation_cases'] += 1
    # Previously certified bridge envelope repair is algebraic: low report belongs
    # to the high report's supremum interval. Recheck positive exact certificate.
    bridge_delta = Q(553, 136800000) - 1 / (Q(factorial(10)) * Q(9, 10) ** 10)
    require(bridge_delta == Q(97726081746439, 30050502681578400000) and bridge_delta > 0,
            'prior bridge certificate calibration')
    return {'status': 'PASS', 'checks': counts,
            'group_constant_one_obstruction': str(group_witness),
            'prior_bridge_envelope_repair_lower_bound': str(bridge_delta),
            'scope': 'Finite exact support only; no numerical envelope supremum or sharp-bound claim.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    args = parser.parse_args()
    result = run()
    content = json.dumps(result, indent=2) + '\n'
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(content)
    print(content, end='')
