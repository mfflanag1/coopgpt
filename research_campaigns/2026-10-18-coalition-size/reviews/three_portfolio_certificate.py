#!/usr/bin/env python3
"""Exact independent 36-row certificate for the fixed three-owner min2 domain.

Run with --output PATH to persist JSON. Uses no LP solver or symmetry premise.
"""
from collections import defaultdict
from fractions import Fraction as Q
from itertools import permutations
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    low = sorted(set(permutations(('L', 'R', '0'))))
    high = sorted(set(permutations(('L', 'L', 'R'))) |
                  set(permutations(('R', 'R', 'L'))))
    coefficients = defaultdict(Q)
    rhs = Q(0)
    rows = []

    def add(kind, weight, terms, bound):
        nonlocal rhs
        terms = {key: Q(value) for key, value in terms.items()}
        for key, value in terms.items():
            coefficients[key] += weight * value
        rhs += weight * bound
        rows.append({'kind': kind, 'weight': str(weight), 'rhs': str(bound),
                     'terms': [{'profile': list(p), 'owner': i, 'coefficient': str(v)}
                               for (p, i), v in sorted(terms.items())]})

    for p in high:
        for i in range(3):
            for j in range(i + 1, 3):
                if p[i] != p[j]:
                    add('high_unlike_pair_coverage', Q(1, 2),
                        {(p, i): 1, (p, j): 1}, Q(1))
    for p in low:
        zero = p.index('0')
        for incumbent in range(3):
            if incumbent == zero:
                continue
            h = list(p)
            h[zero] = p[incumbent]
            h = tuple(h)
            assert h in high
            add('pair_tcwm_restore_zero_to_incumbent_type', Q(1, 4),
                {(h, incumbent): 1, (h, zero): 1,
                 (p, incumbent): -1, (p, zero): -1}, Q(0))
        add('low_grand_coverage', Q(1, 4), {(p, i): 1 for i in range(3)}, Q(1))
        add('low_zero_owner_nonnegative', Q(1, 4), {(p, zero): 1}, Q(0))

    assert len(rows) == 36
    assert all(coefficients[p, i] == 0 for p in low for i in range(3))
    assert all(coefficients[p, i] == 1 for p in high for i in range(3))
    assert rhs == Q(15, 2)
    counts = {kind: sum(r['kind'] == kind for r in rows)
              for kind in sorted({r['kind'] for r in rows})}
    result = {'status': 'PASS', 'row_count': len(rows), 'row_counts': counts,
              'low_profile_count': len(low), 'high_profile_count': len(high),
              'zero_low_coefficients': 18, 'unit_high_coefficients': 18,
              'aggregated_rhs': str(rhs), 'uniform_lower': str(rhs / len(high)),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'rows': rows}
    rendered = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
