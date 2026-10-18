#!/usr/bin/env python3
"""Independent exact bounded-s projective tail checks; no optimization solver."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


def require(test, message):
    if not test:
        raise RuntimeError(message)


def recurrence(s, M):
    value = Q(1, 3)
    for m in range(2, M + 1):
        k = min(s-1, 2*m-2)
        value *= Q(k, k+1)
    return value


def closed_form(s, M):
    h = min(M, (s+1)//2)
    qprod = Q(1)
    for j in range(2, h+1):
        qprod *= Q(2*j, 2*j-1)
    return qprod / (3*h) * Q(s-1, s)**(M-h)


def certificate(s, M):
    rows = []
    needed = Q(2*(M-1))
    for m in range(M, 1, -1):
        k = min(s-1, 2*m-2)
        weight = needed / (k+1)
        rows += [{'kind': 'tcwm', 'm': m, 'old_count': k, 'weight': weight,
                  'terms': {f'q{m}': Q(k+1), f'q{m-1}': -Q(k), f'z{m-1}': -Q(1)},
                  'rhs': Q(0)},
                 {'kind': 'zero_owner_nonnegative', 'm': m, 'weight': weight,
                  'terms': {f'z{m-1}': Q(1)}, 'rhs': Q(0)}]
        needed = k*weight
    rows += [{'kind': 'seed_coverage', 'weight': needed/3,
              'terms': {'q1': Q(3)}, 'rhs': Q(1)},
             {'kind': 'final_budget', 'weight': Q(1),
              'terms': {'kappa': Q(1), 'root': -Q(1), f'q{M}': -Q(2*M)}, 'rhs': Q(0)},
             {'kind': 'final_coverage', 'weight': Q(1),
              'terms': {'root': Q(1), f'q{M}': Q(2)}, 'rhs': Q(1)}]
    coefficients = defaultdict(Q)
    rhs = Q(0)
    for row in rows:
        require(row['weight'] >= 0, 'negative weight')
        for key, value in row['terms'].items():
            coefficients[key] += row['weight']*value
        rhs += row['weight']*row['rhs']
    require(coefficients['kappa'] == 1, 'kappa coefficient')
    require(all(value == 0 for key, value in coefficients.items() if key != 'kappa'),
            'payment cancellation failed')
    require(rhs == 1+2*(M-1)*recurrence(s, M), 'wrong bound')
    require(len(rows) == 2*M+1, 'row count')
    return {'s': s, 'M': M, 'row_count': len(rows), 'lower': str(rhs),
            'aggregated_coefficients': {key: str(value) for key, value in coefficients.items()},
            'rows': [{**row, 'weight': str(row['weight']), 'rhs': str(row['rhs']),
                      'terms': {key: str(value) for key, value in row['terms'].items()}}
                     for row in rows]}


def main():
    counts = Counter()
    peaks = []
    for s in range(2, 65):
        scores = {}
        for M in range(1, 3*s+4):
            q = recurrence(s, M)
            require(q == closed_form(s, M), 'closed form mismatch')
            counts['closed_forms'] += 1
            scores[M] = 1+2*(M-1)*q
        peak = max(scores.values())
        maximizers = [M for M, value in scores.items() if value == peak]
        require(maximizers == [s, s+1], 'peak location')
        counts['finite_peak_checks'] += 1
        peaks.append({'s': s, 'peak_M': maximizers, 'lower': str(peak)})
        for M in sorted({1, (s+1)//2, (s+1)//2+1, s-1, s, s+1, s+2, 2*s}):
            cert = certificate(s, M)
            counts['exact_certificates'] += 1
            counts['certificate_rows'] += cert['row_count']

    for s in range(2, 17):
        M = 2*s
        root = 0
        high = {j: j for j in range(1, M+1)}
        low = {j: M+j for j in range(1, M+1)}
        for m in range(2, M+1):
            old = [owner for j in range(1, m) for owner in (high[j], low[j])]
            k = min(s-1, len(old))
            selected = old[:k]
            coalition = selected+[low[m]]
            require(len(coalition) == k+1 <= s, 'coalition too large')
            require(root not in coalition and high[m] not in coalition, 'wrong coalition members')
            require(len(set(coalition)) == len(coalition), 'duplicate owner')
            require(all(owner in old for owner in selected), 'not old active owner')
            counts['fixed_subset_coalitions'] += 1
            if k % 2:
                counts['partial_pair_coalitions'] += 1

    example = certificate(6, 6)
    require(recurrence(6, 6) == Q(25, 243), 's6 per-owner lower')
    require(Q(example['lower']) == Q(493, 243) > 2, 's6 exhibit')
    out = {'status': 'PASS', 'counts': dict(counts),
           's6_example': {'owners': 13, 'resources': 127, 'activities': 2667,
                          'per_private_owner_lower': '25/243', 'funding_lower': '493/243'},
           'full_s6_M6_certificate': example, 'peak_samples': peaks,
           'scope': 'exact scalar and actual-label subset checks; analytic symmetry and support theorem remain dependencies',
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(__file__).with_suffix('.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({key: value for key, value in out.items()
                      if key not in ('full_s6_M6_certificate', 'peak_samples')}, indent=2))


if __name__ == '__main__':
    main()
