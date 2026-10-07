#!/usr/bin/env python3
"""Exact finite support for the cut-height theorem, not a proof of all DAGs."""
from itertools import combinations
from collections import Counter
import json
import random

def reachable(n, edges, deleted):
    r = [False] * n
    r[0] = True
    for i, (a, b) in enumerate(edges):
        if not deleted >> i & 1:
            r[b] |= r[a]
    return r

def cuts(n, edges):
    found = set()
    for inner in range(1 << (n - 2)):
        side = 1 | (inner << 1)
        cm = sum(1 << i for i, (a, b) in enumerate(edges)
                 if side >> a & 1 and not side >> b & 1)
        rr = reachable(n, edges, cm)
        qq = [False] * n
        qq[-1] = True
        for i, (a, b) in reversed(list(enumerate(edges))):
            if not cm >> i & 1:
                qq[a] |= qq[b]
        if all(rr[a] and qq[b] for i, (a, b) in enumerate(edges) if cm >> i & 1):
            found.add(cm)
    return found

def cuts_by_edge_subsets(n, edges):
    """Independent blocker enumeration for small graphs; no private-path test."""
    found = set()
    for cm in range(1 << len(edges)):
        if reachable(n, edges, cm)[-1]:
            continue
        if all(reachable(n, edges, cm ^ (1 << i))[-1]
               for i in range(len(edges)) if cm >> i & 1):
            found.add(cm)
    return found

def path_maximizing_cut(n, edges, cm):
    dist = [-10**9] * n
    dist[0] = 0
    pred = [None] * n
    for i, (a, b) in enumerate(edges):
        nd = dist[a] + (cm >> i & 1)
        if nd > dist[b]:
            dist[b] = nd
            pred[b] = (a, i)
    result = []
    v = n - 1
    while v:
        v, e = pred[v]
        result.append(e)
    return list(reversed(result))

def run():
    rows = []
    for r in range(1, 10):
        n = 2 * r
        es = [(a, b) for a in range(n) for b in range(a+1, min(a+3, n))]
        cs = cuts(n, es)
        hist = Counter(sum(C >> e & 1 for e in path_maximizing_cut(n, es, C)) for C in cs)
        H = sum(h * number for h, number in hist.items())
        assert len(cs) == r*r and H == r*(r+1)*(2*r+1)//6
        assert hist == {h: 2*r-2*h+1 for h in range(1, r+1)}
        rows.append({'r': r, 'K': len(cs), 'H': H, 'height_histogram': dict(sorted(hist.items()))})
    rng = random.Random(20261007)
    count = intervals = independent = 0
    for trial in range(300):
        n = rng.randrange(2, 11)
        es = [(a,b) for a,b in combinations(range(n),2) if b == a+1 or rng.random() < .3]
        if trial % 11 == 0:
            es = sorted(es + [rng.choice(es)])
        cs = cuts(n, es)
        if len(es) <= 10:
            assert cs == cuts_by_edge_subsets(n, es)
            independent += 1
        K = len(cs)
        for C in cs:
            rr = reachable(n, es, C)
            P = path_maximizing_cut(n, es, C)
            chain = [e for e in P if C >> e & 1]
            r = len(chain)
            assert 2*K >= r*(r+1)
            # Further refinement counts singleton witnesses for P\C.
            assert K >= len(P) + r*(r-1)//2
            assert len(P) >= 2*r-1
            witnesses = set()
            pm = sum(1 << e for e in P)
            for a in range(r):
                for b in range(a,r):
                    x = es[chain[a]][0]
                    y = es[chain[b]][1]
                    side = [v <= x or (rr[v] and v < y) for v in range(n)]
                    B = sum(1 << e for e,(u,v) in enumerate(es) if side[u] and not side[v])
                    intended = sum(1 << e for e in chain[a:b+1])
                    assert B & pm == intended
                    ds = [D for D in cs if D & B == D]
                    assert ds and all(D & pm == intended for D in ds)
                    witnesses.add(ds[0])
                    intervals += 1
            assert len(witnesses) == r*(r+1)//2
            count += 1
    return {'status': 'PASS', 'family': rows, 'random_graphs': 300,
            'cuts_checked': count, 'intervals_checked': intervals,
            'independent_edge_subset_crosschecks': independent,
            'scope': 'Exact finite checks supplement the written universal proof.'}

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
