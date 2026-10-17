#!/usr/bin/env python3
"""Finite aggregate-resource-price architecture scout. Numeric LP, exact values.

All inequalities are necessary for a single aggregate-price function with two
fixed fully eligible actual owners. Different ownership-report distributions
may induce the same aggregate c; an aggregate-price rule must use the same p(c).
LP optima are NUMERICAL until a separate exact dual certificate is checked.
"""
from fractions import Fraction as Q
from itertools import product, combinations
from functools import lru_cache
from pathlib import Path
import argparse
import json
import time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def solve_square(matrix, rhs):
    n = len(rhs)
    rows = [[Q(x) for x in matrix[i]]+[Q(rhs[i])] for i in range(n)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k]), None)
        if pivot is None:
            return None
        rows[k], rows[pivot] = rows[pivot], rows[k]
        z = rows[k][k]
        rows[k] = [x/z for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                z = rows[i][k]
                rows[i] = [x-z*y for x, y in zip(rows[i], rows[k])]
    return tuple(row[-1] for row in rows)


@lru_cache(maxsize=None)
def dual_vertices(n, edges, weights):
    constraints = []
    rhs = []
    for v in range(n):
        row = [0]*n
        row[v] = 1
        constraints.append(row)
        rhs.append(Q(0))
    for (u, v), w in zip(edges, weights):
        row = [0]*n
        row[u] = row[v] = 1
        constraints.append(row)
        rhs.append(Q(w))
    answer = set()
    for active in combinations(range(len(rhs)), n):
        p = solve_square([constraints[j] for j in active], [rhs[j] for j in active])
        if p is not None and all(sum(a*x for a, x in zip(row, p)) >= b
                                 for row, b in zip(constraints, rhs)):
            answer.add(p)
    if not answer:
        raise RuntimeError('no production dual vertex')
    return tuple(sorted(answer))


def build(n, edges, weights, levels):
    profiles = tuple(product(levels, repeat=n))
    index = {c: j for j, c in enumerate(profiles)}
    vertices = dual_vertices(n, tuple(edges), tuple(weights))
    values = [min(sum(c*x for c, x in zip(cap, p)) for p in vertices) for cap in profiles]
    count = n*len(profiles)+1
    row_ids, col_ids, data, rhs, labels = [], [], [], [], []
    def add(row, bound, label):
        rownum = len(rhs)
        for col, coefficient in row.items():
            if coefficient:
                row_ids.append(rownum)
                col_ids.append(col)
                data.append(float(coefficient))
        rhs.append(float(bound))
        labels.append(label)
    for j, cap in enumerate(profiles):
        add({**{j*n+v: cap[v] for v in range(n)}, count-1: -values[j]}, 0, ('budget', j))
        for e, ((u, v), w) in enumerate(zip(edges, weights)):
            add({j*n+u: -1, j*n+v: -1}, -Q(w), ('cover', j, e))
        for k in range(n):
            lev = levels.index(cap[k])
            if lev+1 == len(levels):
                continue
            more = list(cap)
            more[k] = levels[lev+1]
            high = index[tuple(more)]
            delta = more[k]-cap[k]
            for mask in range(1 << n):
                row = {high*n+k: -delta}
                for v in range(n):
                    if mask >> v & 1:
                        row[j*n+v] = cap[v]
                        row[high*n+v] = row.get(high*n+v, Q(0))-cap[v]
                add(row, 0, ('monotone', j, high, k, mask))
    matrix = coo_matrix((data, (row_ids, col_ids)), shape=(len(rhs), count)).tocsr()
    return profiles, values, matrix, np.asarray(rhs), labels


def run(n, edges, weights, levels, output=None):
    start = time.time()
    profiles, values, matrix, rhs, labels = build(n, edges, weights, levels)
    objective = np.zeros(matrix.shape[1])
    objective[-1] = 1
    result = linprog(objective, A_ub=matrix, b_ub=rhs,
                     bounds=[(0, None)]*(matrix.shape[1]-1)+[(0, None)],
                     method='highs')
    answer = {'status': result.message, 'success': result.success, 'n': n, 'edges': edges,
              'weights': weights, 'levels': levels, 'profiles': len(profiles),
              'variables': matrix.shape[1], 'constraints': matrix.shape[0],
              'seconds': time.time()-start,
              'scope': 'numeric finite necessary-condition LP; not an exact or general lower certificate'}
    if result.success:
        answer.update({'objective': result.fun,
                       'max_primal_violation': float(np.max(matrix@result.x-rhs)),
                       'dual_nonzeros': int(np.count_nonzero(np.abs(result.ineqlin.marginals)>1e-8))})
        if output:
            payload = {**answer, 'profiles_data': profiles, 'values_data': values,
                       'prices': result.x[:-1].reshape((-1,n)).tolist(),
                       'dual_support': [(j, labels[j], float(x)) for j, x in enumerate(result.ineqlin.marginals)
                                        if abs(x)>1e-8]}
            Path(output).write_text(json.dumps(payload, default=str, indent=2))
    return answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph', choices=('path4', 'path5', 'cycle4', 'cycle5', 'k23'), default='path4')
    parser.add_argument('--weights', default='1,2,4')
    parser.add_argument('--levels', default='1,4,16,64')
    parser.add_argument('--output')
    args = parser.parse_args()
    graphs = {
        'path4': (4, ((0,1),(1,2),(2,3))),
        'path5': (5, ((0,1),(1,2),(2,3),(3,4))),
        'cycle4': (4, ((0,1),(1,2),(2,3),(0,3))),
        'cycle5': (5, ((0,1),(1,2),(2,3),(3,4),(0,4))),
        'k23': (5, ((0,2),(0,3),(0,4),(1,2),(1,3),(1,4))),
    }
    n, edges = graphs[args.graph]
    weights = tuple(map(Q, args.weights.split(',')))
    levels = tuple(map(Q, args.levels.split(',')))
    if len(weights) != len(edges) or min(levels) <= 0:
        raise RuntimeError('weight count must match edges; all profile capacities must be positive')
    print(json.dumps(run(n, edges, weights, levels, args.output), default=str, indent=2))


if __name__ == '__main__':
    main()
