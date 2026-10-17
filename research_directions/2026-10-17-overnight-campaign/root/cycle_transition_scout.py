"""Bounded discovery of actual-owner transition certificates on resource cycles.

This script does not prove an all-profile upper bound. Optimizer output is a
candidate until reconstructed using rational arithmetic and an independent
production oracle. Zero caps in coalitions do not create new strategic owners.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse, gzip, json, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


@lru_cache(None)
def cycle_value(cap, weights):
    """Exact dual dynamic program, integer potentials on an even cycle."""
    d = len(cap)
    need(d % 2 == 0 and len(weights) == d, 'even cycle shape')
    w = max(weights)
    best = None
    for start in range(w + 1):
        prev = [None] * (w + 1)
        prev[start] = cap[0] * start
        for k in range(1, d):
            nxt = [None] * (w + 1)
            for b in range(w + 1):
                eligible = [prev[a] for a in range(w + 1)
                            if a + b >= weights[k - 1] and prev[a] is not None]
                if eligible:
                    nxt[b] = min(eligible) + cap[k] * b
            prev = nxt
        for end, cost in enumerate(prev):
            if cost is not None and end + start >= weights[-1]:
                best = cost if best is None else min(best, cost)
    need(best is not None, 'dual empty')
    return best


def solve(name, word, weights, levels=(1, 2), limit=180):
    began = time.monotonic()
    d, n = len(word), max(word) + 1
    need(set(word) == set(range(n)), 'owners not contiguous')
    states = list(product(levels, repeat=d))
    lookup = {p: j for j, p in enumerate(states)}
    count = len(states)
    factor_idx = count * n
    rows, cols, data, rhs, tags = [], [], [], [], []
    worth = []
    def add(coeff, b, tag):
        r = len(rhs)
        for j, a in coeff.items():
            if a:
                rows.append(r); cols.append(j); data.append(a)
        rhs.append(b); tags.append(tag)
    for k, p in enumerate(states):
        values = [cycle_value(tuple(p[j] if mask >> word[j] & 1 else 0
                                    for j in range(d)), tuple(weights))
                  for mask in range(1 << n)]
        worth.append(values)
        add({**{k*n+i: 1 for i in range(n)}, factor_idx: -values[-1]},
            0, ['budget', k])
        for mask, val in enumerate(values):
            if val:
                add({k*n+i: -1 for i in range(n) if mask >> i & 1},
                    -val, ['coalition', k, mask])
        for j in range(d):
            ix = levels.index(p[j])
            if ix + 1 < len(levels):
                high = p[:j] + (levels[ix+1],) + p[j+1:]
                h = lookup[high]; i = word[j]
                add({k*n+i: 1, h*n+i: -1}, 0, ['monotone', k, h, i])
    mat = coo_matrix((data, (rows, cols)), shape=(len(rhs), factor_idx+1)).tocsr()
    obj = np.zeros(factor_idx + 1); obj[-1] = 1
    ans = linprog(obj, A_ub=mat, b_ub=np.array(rhs), bounds=(0, None),
                  method='highs', options={'time_limit': limit})
    info = dict(name=name, word=word, weights=weights, levels=levels,
                n=n, d=d, profiles=count, rows=len(rhs), success=bool(ans.success),
                status=int(ans.status), message=ans.message,
                elapsed_seconds=time.monotonic()-began,
                scope='bounded exploratory LP, no continuous upper claim')
    if not ans.success:
        return info
    info['float_optimum'] = float(ans.fun)
    multipliers = [Q(float(-v)).limit_denominator(10**8) if v < -1e-8 else Q(0)
                   for v in ans.ineqlin.marginals]
    combo = {}; right = Q(0); cert = []
    for k, m in enumerate(multipliers):
        if not m:
            continue
        for ix in range(mat.indptr[k], mat.indptr[k+1]):
            j, a = int(mat.indices[ix]), int(mat.data[ix])
            combo[j] = combo.get(j, Q(0)) + m*a
        right += m*int(rhs[k]); cert.append({'weight': str(m), 'tag': tags[k]})
    valid = combo.get(factor_idx, 0) < 0 and all(a >= 0 for j,a in combo.items() if j != factor_idx)
    info['reconstructed_dual_valid'] = bool(valid)
    info['exact_dual_lower'] = str(right/combo[factor_idx]) if valid else None
    info['dual_support'] = len(cert)
    # Preserve useful or calibration certificates; do not retain huge null primals.
    if valid and (right/combo[factor_idx] > Q(9,8) or name.startswith('calibrate')):
        profiles = [[[p[j] if word[j] == i else 0 for j in range(d)]
                     for i in range(n)] for p in states]
        primal = [Q(float(v)).limit_denominator(10**8) for v in ans.x]
        payload = {**info, 'all_profiles': profiles, 'profile_encoding': 'actual_bundles',
                   'edges': [[j, (j+1)%d, weights[j]] for j in range(d)],
                   'C_index': factor_idx, 'exact_bound': info['exact_dual_lower'],
                   'certificate': cert, 'primal': list(map(str, primal))}
        with gzip.open(Path(__file__).with_name(name+'.json.gz'), 'wt') as f:
            json.dump(payload, f)
    return info


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=12)
    ap.add_argument('--limit', type=int, default=120)
    args = ap.parse_args()
    rng = np.random.default_rng(20261017)
    cases = [('calibrate_cycle4', [0,1,2,3], [1]*4)]
    patterns = [[0,1,2,3,4,0,1,2,3,4], [0,1,2,0,3,4,1,3,2,4],
                [0,1,0,2,3,1,4,2,4,3], [0,1,2,3,0,4,2,1,4,3]]
    for k in range(args.cases):
        word = patterns[k % len(patterns)]
        weights = [1]*len(word) if k < len(patterns) else list(map(int, rng.integers(1,4,len(word))))
        cases.append(('five_owner_'+str(k), word, weights))
    out = Path(__file__).with_name('cycle_transition_scout.jsonl')
    for name, word, weights in cases:
        info = solve(name, word, weights, limit=args.limit)
        line = json.dumps(info)
        with out.open('a') as f: f.write(line+'\n')
        print(line, flush=True)
