#!/usr/bin/env python3
"""Replay finite Model A LP certificates using exact rationals and stdlib only.

No solver, floating-point discovery result, or implementation of the proposed
mechanism is trusted. This verifier independently reconstructs coalition worth,
the complete finite Cartesian report domain, own-owner adjacent transitions,
every primal constraint, and the selected exact dual inequalities. A feasible
finite primal proves only a finite-domain upper; a valid dual is a lower bound
for every continuous-domain mechanism satisfying these restricted constraints.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json


def check(condition, message):
    if not condition:
        raise ValueError(message)


def worth(profile, mask, blocks):
    m = len(blocks)
    k = max(blocks) + 1
    grid = profile[0] if mask & (1 << k) else F()
    capacity = local_service = F()
    for j, a in enumerate(blocks):
        h = profile[1+j] if mask & (1 << (k+1+j)) else F()
        ell = profile[1+m+j] if mask & (1 << a) else F()
        capacity += h
        local_service += min(h, ell)
    return min(capacity, local_service + grid)


def verify(cert):
    blocks = tuple(cert['blocks'])
    check(blocks and all(isinstance(a, int) for a in blocks), 'Invalid blocks')
    check(set(blocks) == set(range(max(blocks)+1)), 'Empty or missing block')
    levels = tuple(map(F, cert['levels']))
    check(levels and levels == tuple(sorted(set(levels))) and levels[0] >= 0,
          'Invalid capacity grid')
    theta = F(cert['theta'])
    check(0 <= theta <= 1, 'Invalid floor weight')
    normalizer = cert['normalizer']
    check(normalizer in ('production', 'static'), 'Unknown normalizer')
    m, k = len(blocks), max(blocks)+1
    n, d = m+k+1, 2*m+1
    full = (1 << n)-1
    profiles = tuple(product(levels, repeat=d))
    check(tuple(tuple(map(F, b)) for b in cert['all_profiles']) == profiles,
          'Profiles are not exactly the declared full Cartesian domain')
    count = len(profiles)
    check((cert['profiles'], cert['owners'], cert['dimension']) == (count, n, d),
          'Dimension metadata mismatch')
    owner = (k,) + tuple(range(k+1, n)) + blocks
    lookup = {b: q for q, b in enumerate(profiles)}
    total = [worth(b, full, blocks) for b in profiles]
    floors = [[theta*(total[q]-worth(b, full ^ (1 << a), blocks))
               for a in range(k)] for q, b in enumerate(profiles)]
    static = list(map(F, cert['static_funding']))
    check(len(static) == count and len(cert['static_certificates']) == count,
          'Static data dimension mismatch')

    # Every static value is proved both primal and dual, independently of its
    # use as a possible budget normalizer in the report-transition program.
    for q, b in enumerate(profiles):
        item = cert['static_certificates'][q]
        x = list(map(F, item['primal']))
        check(len(x) == n and all(v >= 0 for v in x), 'Invalid static primal')
        check(sum(x) == static[q], 'Wrong static primal objective')
        for mask in range(1 << n):
            check(sum(x[i] for i in range(n) if mask & (1 << i)) >=
                  worth(b, mask, blocks), 'Static coalition failure')
        check(all(x[a] >= floors[q][a] for a in range(k)), 'Static floor failure')
        coefficients, rhs = [F()]*n, F()
        for entry in item['dual']:
            w, tag = F(entry['weight']), entry['tag']
            check(w > 0, 'Static dual requires positive weights')
            if tag[0] == 'coalition':
                check(len(tag) == 2 and isinstance(tag[1], int) and
                      0 < tag[1] <= full, 'Invalid static coalition tag')
                mask = tag[1]
                for i in range(n):
                    if mask & (1 << i):
                        coefficients[i] -= w
                rhs -= w*worth(b, mask, blocks)
            elif tag[0] == 'floor':
                check(len(tag) == 2 and isinstance(tag[1], int) and
                      0 <= tag[1] < k, 'Invalid static floor tag')
                a = tag[1]
                coefficients[a] -= w
                rhs -= w*floors[q][a]
            else:
                raise ValueError('Unknown static dual row')
        check(all(v >= -1 for v in coefficients), 'Invalid static dual columns')
        check(-rhs == static[q], 'Static exact primal-dual gap')

    factor_index = count*n
    x = list(map(F, cert['primal']))
    check(len(x) == factor_index+1 and all(v >= 0 for v in x),
          'Invalid global primal')
    beta = x[factor_index]
    check(beta == F(cert['exact_optimum']), 'Wrong reported factor')
    denominators = total if normalizer == 'production' else static
    rows = {'budget': 0, 'coalition': 0, 'floor': 0, 'monotone': 0}
    all_coalitions = 0
    for q, b in enumerate(profiles):
        y = x[q*n:(q+1)*n]
        check(sum(y) <= beta*denominators[q], 'Global budget failure')
        rows['budget'] += 1
        for mask in range(1 << n):
            value = worth(b, mask, blocks)
            check(sum(y[i] for i in range(n) if mask & (1 << i)) >= value,
                  'Global coalition failure')
            all_coalitions += 1
            rows['coalition'] += int(value > 0)
        for a in range(k):
            check(y[a] >= floors[q][a], 'Global floor failure')
            rows['floor'] += int(floors[q][a] > 0)
        for coordinate in range(d):
            pos = levels.index(b[coordinate])
            if pos+1 == len(levels):
                continue
            high = list(b)
            high[coordinate] = levels[pos+1]
            high_q, i = lookup[tuple(high)], owner[coordinate]
            check(y[i] <= x[high_q*n+i], 'Global own-report monotonicity failure')
            rows['monotone'] += 1
    check(rows == cert['row_counts'], 'Row metadata mismatch')

    # A positive combination of <= rows yields a valid lower bound if every
    # payment coefficient is nonnegative and the factor coefficient is negative.
    coefficients, rhs = {}, F()
    def add(index, coefficient):
        coefficients[index] = coefficients.get(index, F())+coefficient
    for entry in cert['dual_certificate']:
        w, tag = F(entry['weight']), entry['tag']
        check(w > 0, 'Global dual requires positive weights')
        check(len(tag) >= 2 and isinstance(tag[1], int) and 0 <= tag[1] < count,
              'Invalid dual profile index')
        kind, q = tag[:2]
        if kind == 'budget':
            check(len(tag) == 2, 'Invalid budget tag')
            for i in range(n):
                add(q*n+i, w)
            add(factor_index, -w*denominators[q])
        elif kind == 'coalition':
            check(len(tag) == 3 and isinstance(tag[2], int) and
                  0 < tag[2] <= full, 'Invalid coalition tag')
            mask = tag[2]
            for i in range(n):
                if mask & (1 << i):
                    add(q*n+i, -w)
            rhs -= w*worth(profiles[q], mask, blocks)
        elif kind == 'floor':
            check(len(tag) == 3 and isinstance(tag[2], int) and
                  0 <= tag[2] < k, 'Invalid floor tag')
            a = tag[2]
            add(q*n+a, -w)
            rhs -= w*floors[q][a]
        elif kind == 'monotone':
            check(len(tag) == 4 and isinstance(tag[2], int) and
                  0 <= tag[2] < count and isinstance(tag[3], int) and
                  0 <= tag[3] < n, 'Invalid monotone tag')
            high, i = tag[2:]
            changed = [j for j in range(d) if profiles[q][j] != profiles[high][j]]
            check(len(changed) == 1, 'Dual transition changes multiple coordinates')
            j = changed[0]
            check(owner[j] == i and levels.index(profiles[high][j]) ==
                  levels.index(profiles[q][j])+1, 'Dual transition is not an adjacent own report')
            add(q*n+i, w)
            add(high*n+i, -w)
        else:
            raise ValueError('Unknown global dual row')
    c = coefficients.get(factor_index, F())
    check(c < 0, 'No negative dual factor coefficient')
    check(all(v >= 0 for i, v in coefficients.items() if i != factor_index),
          'Negative dual payment coefficient')
    lower = rhs/c
    check(lower == beta == F(cert['exact_dual_lower']), 'Global exact primal-dual gap')
    check(c == F(cert['dual_budget_coefficient']) and rhs == F(cert['dual_rhs']),
          'Dual summary metadata mismatch')
    check(len(cert['dual_certificate']) == cert['dual_support'], 'Dual support mismatch')
    static_max = max((s/t for s, t in zip(static, total) if t), default=F())
    check(static_max == F(cert['static_max_factor']), 'Static maximum mismatch')
    return {'status': 'PASS', 'profiles': count, 'owners': n, 'dimension': d,
            'theta': str(theta), 'blocks': list(blocks), 'normalizer': normalizer,
            'exact_optimum': str(beta), 'static_max_factor': str(static_max),
            'all_coalitions_checked': all_coalitions,
            'all_floors_checked': count*k, 'adjacent_own_reports': rows['monotone'],
            'static_primal_dual_pairs': count, 'dual_support': len(cert['dual_certificate']),
            'dual_payment_coefficients_all_zero': all(
                v == 0 for i, v in coefficients.items() if i != factor_index)}


def negative_controls(cert):
    bad = copy.deepcopy(cert)
    bad['primal'][-1] = '0'
    bad['exact_optimum'] = '0'
    try:
        verify(bad)
    except ValueError:
        pass
    else:
        raise ValueError('Negative control failed: zero funding factor accepted')
    bad = copy.deepcopy(cert)
    for entry in bad['dual_certificate']:
        if entry['tag'][0] == 'budget':
            entry['weight'] = str(F(entry['weight'])/2)
            break
    else:
        raise ValueError('No budget row for negative control')
    try:
        verify(bad)
    except ValueError:
        pass
    else:
        raise ValueError('Negative control failed: changed dual weight accepted')
    return 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', type=Path, nargs='+')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    reports = []
    for path in args.files:
        with gzip.open(path, 'rt') if path.suffix == '.gz' else path.open() as handle:
            cert = json.load(handle)
        report = verify(cert)
        report['file'] = path.name
        report['certificate_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        if args.negative_controls:
            report['negative_controls_rejected'] = negative_controls(cert)
        reports.append(report)
    result = {'status': 'PASS', 'certificates': reports,
              'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'Exact finite-domain optima and restricted-profile lower bounds only.'}
    encoded = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end='')
