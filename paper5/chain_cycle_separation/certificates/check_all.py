"""Replay frozen certificates; --smt adds independent raw-core LP queries."""
import argparse
from collections import deque
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import platform

import frozen_family
import independent_family

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def cover(m, weights, point, total):
    require(len(point) == 3*m and min(point) >= 0 and sum(point) == total,
            'invalid core totals')
    for i, j, k in product(range(m), repeat=3):
        require(point[i]+point[m+j]+point[2*m+k] >= weights(i, j, k),
                'uncovered control triple')


def chain_controls():
    x = [F(1, 3)]*3
    for i in range(3):
        y = [F(int(j == i)) for j in range(3)]
        cover(1, lambda i, j, k: 1, y, 1)
        require(sum(abs(a-b) for a, b in zip(x, y)) == F(4, 3),
                'simplex distance')
    cover(1, lambda i, j, k: 1, x, 1)
    # The zero diagonal team pins u1,v1,z1. The (u0,v0,z1)
    # cover and efficiency also pin z0, leaving the stated unit segment.
    weights = lambda i, j, k: int(i == 0 and j == 0)
    for t in (F(0), F(1, 2), F(1)):
        cover(2, weights, [t, 0, 1-t, 0, 0, 0], 1)
    return {'simplex': {'leximin': ['1/3']*3, 'ideals': ['1']*3,
                        'distance_to_vertex': '4/3'},
            'permanent_zero_control': {'core': '(t,0;1-t,0;0,0), 0<=t<=1',
                                      'leximin': ['1/2', '0', '1/2', '0', '0', '0'],
                                      'first_floor': '0',
                                      'first_stage_endpoint_violates_protection': True},
            'scope': 'Analytic controls explained in README; finite exact covers corroborate them.'}


def chain_smt_case(P, Q):
    import z3
    m = len(P)
    permP = max(permutations(range(m)), key=lambda r: sum(P[r[j]][j] for j in range(m)))
    permQ = max(permutations(range(m)), key=lambda r: sum(Q[j][r[j]] for j in range(m)))
    P = [[P[permP[i]][j] for j in range(m)] for i in range(m)]
    Q = [[Q[j][permQ[k]] for k in range(m)] for j in range(m)]
    s = [P[j][j]+Q[j][j] for j in range(m)]
    T = sum(s)
    p = [z3.Real('p'+str(i)) for i in range(3*m)]
    raw = [v >= 0 for v in p]+[z3.Sum(p) == T]
    raw += [p[i]+p[m+j]+p[2*m+k] >= P[i][j]+Q[j][k]
            for i, j, k in product(range(m), repeat=3)]

    def rational(v):
        if z3.is_int_value(v):
            return F(v.as_long())
        require(z3.is_rational_value(v), 'non-rational or infinite LP optimum')
        return F(v.numerator_as_long(), v.denominator_as_long())

    def zq(v):
        return z3.Q(v.numerator, v.denominator)

    def maximize(expr, constraints):
        opt = z3.Optimize()
        opt.set(timeout=30000)
        opt.add(constraints)
        handle = opt.maximize(expr)
        require(opt.check() == z3.sat, 'raw-core optimization failed')
        return rational(opt.lower(handle))

    face, left, fixed, levels = list(raw), set(range(3*m)), {}, []
    while left:
        t = z3.Real('floor_'+str(len(levels)))
        level = maximize(t, face+[p[i] >= t for i in left])
        face += [p[i] >= zq(level) for i in left]
        forced = []
        for i in sorted(left):
            solver = z3.Solver()
            solver.set(timeout=30000)
            solver.add(face+[p[i] > zq(level)])
            result = solver.check()
            require(result in (z3.sat, z3.unsat), 'unknown first-face query')
            if result == z3.unsat:
                forced.append(i)
        require(forced, 'leximin stage fixed no coordinate')
        for i in forced:
            fixed[i] = level
            face.append(p[i] == zq(level))
            left.remove(i)
        levels.append({'level': str(level), 'forced': forced})
    x = [fixed[i] for i in range(3*m)]
    H = [maximize(p[i], raw) for i in range(3*m)]
    require(all(h <= 3*v for h, v in zip(H, x)), 'chain protection failed')
    cover(m, lambda i, j, k: P[i][j]+Q[j][k], x, T)

    # All node/arc labels are explicit; no optimization is used for cycles.
    anchor = 2*m
    potential = x[:m]+[-v for v in x[2*m:]]+[F(0)]
    arcs = []
    for j in range(m):
        arcs.extend([(j, anchor, 0, j), (anchor, m+j, 0, 2*m+j),
                     (m+j, j, s[j], m+j)])
    for i, j in product(range(m), repeat=2):
        if i != j:
            arcs.append((i, j, P[j][j]-P[i][j], None))
            arcs.append((m+j, m+i, Q[j][j]-Q[j][i], None))
    slacks = [F(c)+potential[a]-potential[b] for a, b, c, _ in arcs]
    require(min(slacks) >= 0, 'potential representation infeasible')
    certificates = []
    for target, (tail, head, _, player) in enumerate(arcs):
        if player is None:
            continue
        eligible = [j for j, (_, _, _, f) in enumerate(arcs)
                    if (f is None and slacks[j] == 0) or
                       (f is not None and x[f] <= x[player])]
        todo, parent = deque([head]), {head: None}
        while todo and tail not in parent:
            a = todo.popleft()
            for j in eligible:
                aa, b, _, _ = arcs[j]
                if aa == a and b not in parent:
                    parent[b] = (a, j)
                    todo.append(b)
        require(tail in parent, 'missing head-to-tail certificate')
        backward, node = [], tail
        while node != head:
            prev, edge = parent[node]
            backward.append(edge)
            node = prev
        cycle = [target]+list(reversed(backward))
        require(all(arcs[a][1] == arcs[b][0]
                    for a, b in zip(cycle, cycle[1:]+cycle[:1])),
                'cycle arcs do not join')
        payoff_ids = [arcs[j][3] for j in cycle if arcs[j][3] is not None]
        require(len(payoff_ids) == 3 and len(set(payoff_ids)) == 3,
                'certificate does not have three payoff arcs')
        constant = sum(arcs[j][2] for j in cycle)
        require(F(constant) == sum(x[i] for i in payoff_ids) <= 3*x[player],
                'cycle telescope mismatch')
        certificates.append({'player': player, 'arc_ids': cycle,
                             'payoff_ids': payoff_ids, 'constant': constant})
    return {'P_after_relabeling': P, 'Q_after_relabeling': Q, 'T': T,
            'leximin': list(map(str, x)), 'ideals': list(map(str, H)),
            'levels': levels, 'arcs': arcs, 'cycle_certificates': certificates}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smt', action='store_true')
    args = parser.parse_args()
    (ROOT/'RESULTS.json').write_text(json.dumps({'status': 'RUNNING',
                                               'smt_requested': args.smt})+'\n')
    provenance = json.loads((ROOT/'SOURCE_PROVENANCE.json').read_text())
    hashes = {r['destination']: r['source_sha256'] for r in provenance
              if r['adaptation'] == 'none'}
    frozen = []
    for q in range(1, 5):
        name = f'frozen/depth_{q}.json'
        raw = (ROOT/name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == hashes[name], 'frozen input hash mismatch')
        frozen.append(frozen_family.verify(json.loads(raw)))
    independent = [independent_family.check(q) for q in range(1, 5)]
    nchecks = sum(row['all_triple_checks'] for row in frozen)
    require(nchecks == 7208, 'frozen coverage mismatch')
    require(sum(p['checked_triples'] for r in independent for p in r['covers'].values())
            == 7208, 'independent coverage mismatch')
    result = {'status': 'PASS', 'python': platform.python_version(),
              'frozen': frozen, 'independent': independent,
              'chain_controls': chain_controls(), 'smt_requested': args.smt,
              'scope': 'Finite exact certificates. The all-parameter theorem is the manuscript proof.'}
    if args.smt:
        result['cyclic_smt'] = independent_family.smt_check(4)
        inputs = [([[1, 0], [0, 0]], [[0, 0], [0, 0]]),
                  ([[2, 1], [1, 2]], [[2, 0], [1, 3]]),
                  ([[3, 1, 0], [1, 2, 1], [0, 1, 4]],
                   [[2, 1, 0], [0, 3, 1], [1, 0, 2]])]
        result['chain_smt'] = [chain_smt_case(P, Q) for P, Q in inputs]
    out = ROOT/'RESULTS.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': 'PASS', 'frozen_triple_checks': nchecks,
                      'independent_triple_checks': 7208, 'smt': args.smt,
                      'chain_smt_cases': len(result.get('chain_smt', []))}))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        (ROOT/'RESULTS.json').write_text(json.dumps({'status': 'FAIL',
                                                   'error': str(exc)})+'\n')
        raise
