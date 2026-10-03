"""Exact checks for five preregistered instances; no optimizer or dependencies.
Run with python3 -B -O verify_initial.py. JSON goes to stdout.
The general proofs and leximin optimality arguments are in companion notes.
"""
from fractions import Fraction as F
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys


def require(ok, why):
    if not ok:
        raise ValueError(why)


def pays(x, mask):
    return sum((v for i, v in enumerate(x) if mask >> i & 1), F(0))


def covered(x, values):
    return all(pays(x, m) >= v for m, v in enumerate(values))


def certify(values, witnesses, h, y, lower_mask, expected_subsidy):
    m = len(h)
    require(len(values) == 1 << m, 'All-coalition list incomplete')
    total = values[-1]
    for x in witnesses:
        require(len(x) == m and min(x) >= 0, 'Invalid core witness')
        require(sum(x) == total and covered(x, values), 'Core witness failed')
    for i in range(m):
        marginal_cap = total - values[((1 << m) - 1) ^ (1 << i)]
        require(h[i] == marginal_cap, 'Deletion cap differs from claimed ideal')
        require(max(x[i] for x in witnesses) == h[i], 'Ideal not attained')
    require(all(y[i] >= h[i] / 3 for i in range(m)), 'Floor failure')
    require(covered(y, values), 'Subsidized cover failed')
    outside_floors = sum((h[i] / 3 for i in range(m) if not (lower_mask >> i & 1)), F(0))
    lower = values[lower_mask] + outside_floors - total
    require(lower == sum(y) - total == expected_subsidy, 'Primal/lower bound mismatch')
    return {'players': m, 'coalitions': len(values), 'T': total,
            'H': list(map(str, h)), 'ideal_witnesses': [list(map(str, x)) for x in witnesses],
            'protected_allocation': list(map(str, y)), 'lower_coalition_mask': lower_mask,
            'subsidy': str(expected_subsidy), 'ratio': str(expected_subsidy / total)}


def flow_case(n):
    edges = []
    for i in range(n):
        edges.extend([('s', ('L', i)), (('L', i), ('R', i)), (('R', i), 't')])
    edges.extend([(('L', i), ('R', i + 1)) for i in range(n - 1)])
    m = len(edges)
    inner = [(side, i) for side in ('L', 'R') for i in range(n)]
    cut_masks = []
    for bits in range(1 << len(inner)):
        cut = {'s'} | {v for j, v in enumerate(inner) if bits >> j & 1}
        cut_masks.append(sum(1 << j for j, (u, v) in enumerate(edges) if u in cut and v not in cut))
    paths = [sum(1 << (3*i+j) for j in range(3)) for i in range(n)]
    paths += [(1 << (3*i)) | (1 << (3*n+i)) | (1 << (3*(i+1)+2)) for i in range(n-1)]
    # Confirm these are every actual source-sink path, independently of the formula.
    actual = []
    def walk(vertex, mask):
        if vertex == 't':
            actual.append(mask)
            return
        for j, (u, v) in enumerate(edges):
            if u == vertex:
                walk(v, mask | (1 << j))
    walk('s', 0)
    require(set(actual) == set(paths) and all(p.bit_count() == 3 for p in paths), 'Path list failed')
    packings = []
    for bits in range(1 << len(paths)):
        used = 0
        count = 0
        disjoint = True
        for j, path in enumerate(paths):
            if bits >> j & 1:
                if used & path:
                    disjoint = False
                    break
                used |= path
                count += 1
        if disjoint:
            packings.append((used, count))
    values = []
    for coalition in range(1 << m):
        cut_value = min((coalition & cut).bit_count() for cut in cut_masks)
        packing_value = max(count for used, count in packings if used & coalition == used)
        require(cut_value == packing_value, 'Independent max-flow/min-cut mismatch')
        values.append(cut_value)
    witnesses = []
    for role in (0, 2):
        witnesses.append([F(int(j < 3*n and j % 3 == role)) for j in range(m)])
    for i in range(n):
        chosen = {3*j for j in range(i)} | {3*i+1} | {3*j+2 for j in range(i+1, n)}
        witnesses.append([F(int(j in chosen)) for j in range(m)])
    h = [F(int(j < 3*n)) for j in range(m)]
    y = [v/3 for v in h]
    for i in range(n - 1):
        y[3*i] += F(1,3)
    lower = 0
    for path in paths[n:]:
        lower |= path
    result = certify(values, witnesses, h, y, lower, F(n-1, 3))
    bad = [v/3 for v in h]
    if n == 1:
        bad[0] = 0
    require(not covered(bad, values), 'Damaged protection certificate unexpectedly covers')
    result.update({'id': f'F0{n}', 'edges': [[str(u), str(v)] for u,v in edges],
                   'independent_path_packings': len(packings), 'cuts': len(cut_masks),
                   'negative_controls_rejected': 1})
    return result


def assignment_case(extra):
    weights = [[4, extra, 0], [0, 10, 0], [0, 5, 0]]
    values = []
    for coalition in range(64):
        def match(i, used):
            if i == 3:
                return 0
            best = match(i+1, used)
            if coalition >> i & 1:
                for j in range(3):
                    if coalition >> (j+3) & 1 and not (used >> j & 1):
                        best = max(best, weights[i][j] + match(i+1, used | (1 << j)))
            return best
        values.append(match(0,0))
    def allocation(p,q):
        return list(map(F,[p,q,0,4-p,10-q,0]))
    witnesses = [allocation(p,q) for p,q in [(0,0),(4,0),(4,5)]]
    h = list(map(F,[4,5,0,4,10,0]))
    for x in witnesses:
        require(sum(x) == values[-1] == 14 and covered(x, values), 'Assignment witness failure')
    for i in range(6):
        require(max(x[i] for x in witnesses) == h[i] == 14-values[63 ^ (1 << i)], 'Assignment ideal failure')
    lex = allocation(2,5 if extra == 0 else 3)
    require(covered(lex, values), 'Claimed leximin vector not in core')
    if extra:
        require(not covered(allocation(2,5), values), 'Coupling negative control not rejected')
    return {'id': 'A04' if extra == 0 else 'A05', 'matrix': weights,
            'coalitions': 64, 'T': 14, 'H': list(map(str,h)),
            'ideal_witnesses': [list(map(str,x)) for x in witnesses],
            'leximin': list(map(str,lex)), 'leximin_optimality': 'analytic certificate in GEOMETRY_BRIDGE.txt',
            'negative_controls_rejected': int(bool(extra))}


if __name__ == '__main__':
    results = [flow_case(n) for n in (1,2,3)] + [assignment_case(x) for x in (0,9)]
    print(json.dumps({'status': 'PASS', 'python': sys.version.split()[0],
                      'optimized': sys.flags.optimize, 'finite_instances': 5,
                      'all_coalition_counts': sum(r['coalitions'] for r in results),
                      'negative_controls_rejected': sum(r['negative_controls_rejected'] for r in results),
                      'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'scope': 'Five exact instances, all coalitions; no claim of universal theorem or novelty.',
                      'results': results}, indent=2))
