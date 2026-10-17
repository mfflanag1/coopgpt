#!/usr/bin/env python3
"""Independent exact KKT/LP certificate corroboration for Huber prices.

Uses a bipartite double cover solely to FIND fractional edge-flow certificates.
The checked certificate is on the original resource graph and original owners.
No extra strategic owner or coalition is added to the mechanism.
"""
from fractions import Fraction as Q
from collections import deque
import json
import random
import argparse
import importlib.util
from pathlib import Path


def oracle(capacities, edges):
    spec = importlib.util.spec_from_file_location('huber_oracle', Path(__file__).with_name('verify_huber_price.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.price(tuple(capacities), tuple(edges))


def require(test, message):
    if not test:
        raise RuntimeError(message)


def certificate(capacities, edges):
    p = oracle(capacities, edges)
    d = [c*min(2*x, Q(1)) for c, x in zip(capacities, p)]
    n = len(d)
    source, sink = 2*n, 2*n+1
    adjacency = [[] for _ in range(2*n+2)]
    residual = {}
    original = {}
    total = sum(d)
    def add(u, v, capacity):
        adjacency[u].append(v)
        adjacency[v].append(u)
        residual[u, v] = capacity
        residual[v, u] = Q(0)
        original[u, v] = capacity
    for v in range(n):
        add(source, v, d[v])
        add(n+v, sink, d[v])
    for u, v in edges:
        if p[u]+p[v] == 1:
            add(u, n+v, total)
            add(v, n+u, total)
    flow = Q(0)
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in adjacency[u]:
                if v not in parent and residual[u, v] > 0:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break
        path = []
        v = sink
        while v != source:
            u = parent[v]
            path.append((u, v))
            v = u
        change = min(residual[e] for e in path)
        for u, v in path:
            residual[u, v] -= change
            residual[v, u] += change
        flow += change
    require(flow == total, ('infeasible KKT edge degrees', capacities, edges, p, d, flow, total))
    lambdas = []
    for u, v in edges:
        forward = original.get((u, n+v), Q(0))-residual.get((u, n+v), Q(0))
        backward = original.get((v, n+u), Q(0))-residual.get((v, n+u), Q(0))
        lambdas.append((forward+backward)/2)
    cert = {'capacities': list(capacities), 'edges': list(edges), 'p': list(p), 'lambda': lambdas}
    verify(cert)
    return cert


def verify(cert):
    c = list(map(Q, cert['capacities']))
    p = list(map(Q, cert['p']))
    edges = [tuple(x) for x in cert['edges']]
    lam = list(map(Q, cert['lambda']))
    require(len(c) == len(p) and len(edges) == len(lam), 'certificate lengths')
    require(all(x >= 0 for x in c) and all(0 <= x <= 1 for x in p), 'domains')
    require(all(x >= 0 for x in lam), 'nonnegative flow')
    degree = [Q(0)]*len(c)
    for (u, v), x in zip(edges, lam):
        require(p[u]+p[v] >= 1, ('dual feasibility', u, v))
        require(x == 0 or p[u]+p[v] == 1, ('slack flow', u, v, x))
        degree[u] += x
        degree[v] += x
    require(degree == [a*min(2*b, Q(1)) for a, b in zip(c, p)], 'KKT stationarity')
    rounded = [Q(0) if x < Q(1, 2) else Q(1) if x > Q(1, 2) else Q(1, 2) for x in p]
    require(all(rounded[u]+rounded[v] >= 1 for u, v in edges), 'rounded dual feasibility')
    require(sum(lam) == sum(a*b for a, b in zip(c, rounded)), 'LP strong duality certificate')
    require(sum(a*b for a, b in zip(c, p)) <= Q(3, 2)*sum(lam), 'funding')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if args.verify:
        packet = json.loads(args.verify.read_text())
        for row in packet['certificates']:
            verify(row)
        print(json.dumps({'status': 'PASS', 'certificate_count': len(packet['certificates']),
                          'mode': 'standalone exact replay; optimizer not imported'}, indent=2))
        return
    rng = random.Random(173204)
    rows = []
    graph_rows = [
        (2, ((0, 1),)),
        (5, ((0, 1), (1, 2), (2, 3), (3, 4))),
        (7, ((0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6))),
        (5, ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4))),
        (4, ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))),
    ]
    for n, edges in graph_rows:
        for _ in range(100):
            c = [Q(rng.randrange(12), rng.choice((1, 2, 3))) for _ in range(n)]
            rows.append(certificate(c, edges))
    # Includes a non-bipartite strict fractional optimum: all triangle capacities1.
    rows.append(certificate([Q(1)]*3, ((0, 1), (0, 2), (1, 2))))
    print(json.dumps({'status': 'PASS', 'certificate_count': len(rows),
                      'scope': 'Exact finite KKT and primal/dual corroboration; not the universal proof',
                      'certificates': rows}, default=str, indent=2))


if __name__ == '__main__':
    main()
