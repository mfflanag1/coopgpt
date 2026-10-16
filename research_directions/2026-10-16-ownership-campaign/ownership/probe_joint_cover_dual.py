#!/usr/bin/env python3
"""Exploratory symmetric LP; no theorem is inferred from floats."""
import argparse
import itertools
import json
import math
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog


def tree(b, height):
    levels = [0]
    adj = [[]]
    for d in range(height):
        for v in [v for v, z in enumerate(levels) if z == d]:
            for _ in range(b):
                u = len(adj)
                adj.append([v])
                adj[v].append(u)
                levels.append(d + 1)
    return adj, levels


def component_vectors(adj, levels, height, radius):
    """All connected radius <=r<=2 subtrees, quotient by level counts."""
    out = set()
    centers = [levels.index(d) for d in range(height + 1)]
    for v in centers:
        base = [0] * (2 * height + 1)
        base[height + levels[v]] = 1
        states = {tuple(base)}
        for u in adj[v]:
            branch = {(0,) * len(base)}
            grandchildren = [w for w in adj[u] if w != v] if radius == 2 else []
            for subset in itertools.product((0, 1), repeat=len(grandchildren)):
                z = [0] * len(base)
                z[max(levels[u], levels[v]) - 1] += 1
                z[height + levels[u]] += 1
                for keep, w in zip(subset, grandchildren):
                    if keep:
                        z[max(levels[u], levels[w]) - 1] += 1
                        z[height + levels[w]] += 1
                branch.add(tuple(z))
            states = {tuple(a + b for a, b in zip(s, t)) for s in states for t in branch}
        out.update(z for z in states if sum(z[:height]) > 0)
    return sorted(out)


def double_star_vectors(adj, levels, height):
    out = set()
    for d in range(1, height + 1):
        v = levels.index(d)
        u = next(q for q in adj[v] if levels[q] == d - 1)
        other_edges = [(u, w) for w in adj[u] if w != v] + [(v, w) for w in adj[v] if w != u]
        for bits in itertools.product((0, 1), repeat=len(other_edges)):
            z = [0] * (2 * height + 1)
            z[d - 1] = 1
            z[height + d - 1] = 1
            z[height + d] = 1
            for keep, (a, w) in zip(bits, other_edges):
                if keep:
                    z[max(levels[a], levels[w]) - 1] += 1
                    z[height + levels[w]] += 1
            out.add(tuple(z))
    return sorted(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--branching', type=int, default=3)
    p.add_argument('--height', type=int, default=4)
    p.add_argument('--star-cost', type=str, default='13/11')
    p.add_argument('--double-star-cost', type=str, default=None)
    p.add_argument('--depth-cost', type=str, default='7/4')
    args = p.parse_args()
    b, h = args.branching, args.height
    c1 = float(Fraction(args.star_cost))
    adj, levels = tree(b, h)
    rows = []
    for radius, cost in ((1, c1), (2, float(Fraction(args.depth_cost)))):
        for z in component_vectors(adj, levels, h, radius):
            rows.append(list(z[:h]) + [-cost * q for q in z[h:]])
    if args.double_star_cost:
        cost = float(Fraction(args.double_star_cost))
        for z in double_star_vectors(adj, levels, h):
            rows.append(list(z[:h]) + [-cost * q for q in z[h:]])
    obj = [-b ** d for d in range(1, h + 1)] + [0] * (h + 1)
    norm = [[0] * h + [b ** d for d in range(h + 1)]]
    result = linprog(obj, A_ub=np.array(rows), b_ub=np.zeros(len(rows)),
                     A_eq=np.array(norm), b_eq=[1], bounds=(0, None), method='highs')
    print(json.dumps({'exploration_only': True, 'branching': b, 'height': h,
                      'star_cost': args.star_cost, 'constraints': len(rows),
                      'double_star_cost': args.double_star_cost,
                      'depth_cost': args.depth_cost,
                      'success': result.success, 'objective': -result.fun if result.success else None,
                      'edge_weights': result.x[:h].tolist() if result.success else None,
                      'vertex_weights': result.x[h:].tolist() if result.success else None,
                      'rational_guesses': [str(Fraction(float(z)).limit_denominator(10**7))
                                           for z in result.x] if result.success else None}, indent=2))


if __name__ == '__main__':
    main()
