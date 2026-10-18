#!/usr/bin/env python3
"""Independent exact checks of R=1 projective square-root lower certificate."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations
import hashlib
import json
from pathlib import Path


def require(test, message):
    if not test:
        raise RuntimeError(message)


def linmap(images, x):
    out = 0
    for j, image in enumerate(images):
        if x & (1 << j):
            out ^= image
    return out


def weighted_certificate(M, terminal_coverage=False):
    """Every row is oriented lhs>=rhs; all weights are nonnegative."""
    products = {M + 1: Q(1)}
    for m in range(M, 1, -1):
        products[m] = products[m + 1] * Q(2*m, 2*m-1)
    qprod = products.get(2, Q(1))
    scale = Q(M-1, M) if terminal_coverage else Q(1)
    rows = [{'kind': 'seed_coverage', 'weight': scale*Q(2, 3)*qprod,
             'terms': {'q1': Q(3)}, 'rhs': Q(1)}]
    for m in range(2, M + 1):
        weight = scale*products[m]
        rows.append({'kind': 'tcwm_transition', 'm': m, 'weight': weight,
                     'terms': {f'q{m}': Q(2*m-1), f'q{m-1}': -Q(2*m-2),
                               f'z{m-1}': -Q(1)}, 'rhs': Q(0)})
        rows.append({'kind': 'new_member_old_nonnegative', 'm': m, 'weight': weight,
                     'terms': {f'z{m-1}': Q(1)}, 'rhs': Q(0)})
    rows += [{'kind': 'final_budget', 'weight': Q(1),
              'terms': {'kappa': Q(1), f'q{M}': -Q(2*M), 'final_root': -Q(1)},
              'rhs': Q(0)}]
    if terminal_coverage:
        rows.append({'kind': 'final_triple_coverage', 'weight': Q(1),
                     'terms': {'final_root': Q(1), f'q{M}': Q(2)}, 'rhs': Q(1)})
    else:
        rows.append({'kind': 'final_root_nonnegative', 'weight': Q(1),
                     'terms': {'final_root': Q(1)}, 'rhs': Q(0)})
    coefficients = defaultdict(Q)
    rhs = Q(0)
    for row in rows:
        require(row['weight'] >= 0, 'negative certificate multiplier')
        for variable, value in row['terms'].items():
            coefficients[variable] += row['weight'] * value
        rhs += row['weight'] * row['rhs']
    require(coefficients['kappa'] == 1, 'budget coefficient not1')
    require(all(value == 0 for key, value in coefficients.items() if key != 'kappa'),
            'certificate failed to eliminate payment variables')
    target = Q(1) + scale*Q(2, 3)*qprod if terminal_coverage else Q(2, 3)*qprod
    require(rhs == target, 'certificate lower mismatch')
    require(len(rows) == 2*M+1, 'unexpected row count')
    return {'M': M, 'terminal_coverage': terminal_coverage,
            'row_count': len(rows), 'lower': str(rhs),
            'sum_coefficients': {key: str(value) for key, value in coefficients.items()},
            'rows': [{**row, 'weight': str(row['weight']), 'rhs': str(row['rhs']),
                      'terms': {key: str(value) for key, value in row['terms'].items()}}
                     for row in rows]}


def main():
    counts = Counter()
    families = []
    for M in range(1, 10):
        basis = [1 << j for j in range(M + 1)]
        v = 1
        highs = basis[1:]

        def profile(m):
            return [v] + highs + [x ^ v if j < m else 0 for j, x in enumerate(highs)]

        profiles = {m: profile(m) for m in range(1, M + 1)}
        for m, p in profiles.items():
            support = set(p) - {0}
            triples = {tuple(sorted((x, y, x ^ y)))
                       for x, y in combinations(support, 2) if x ^ y in support}
            expected = {tuple(sorted((1, highs[j], highs[j] ^ 1))) for j in range(m)}
            require(triples == expected, f'supported triples M={M}, m={m}')
            require(all(1 in edge for edge in triples), 'common reported cap missing')
            require(p[0] == 1 and len(triples) >= 1, 'production-one certificate')
            counts['profile_support_checks'] += 1
            counts['supported_triples'] += len(triples)

            generators = []
            for j in range(1, m + 1):
                images = basis.copy()
                images[j] ^= 1
                generators.append(images)
            for j in range(1, m):
                images = basis.copy()
                images[j], images[j + 1] = images[j + 1], images[j]
                generators.append(images)
            active_rows = {highs[j] for j in range(m)} | {highs[j] ^ 1 for j in range(m)}
            reached = {highs[0]}
            for images in generators:
                mapped = [linmap(images, x) for x in p]
                require(Counter(mapped) == Counter(p), 'whole profile not stabilized')
                require(linmap(images, 1) == 1, 'ladder moved root row')
                require(all(linmap(images, highs[j]) == highs[j] for j in range(m, M)),
                        'ladder moved inactive high report')
                require(len({linmap(images, x) for x in range(1 << (M + 1))})
                        == 1 << (M + 1), 'linear map not invertible')
                counts['ladder_generators'] += 1
            while True:
                enlarged = reached | {linmap(images, x) for images in generators for x in reached}
                if enlarged == reached:
                    break
                reached = enlarged
            require(reached == active_rows, 'active paired owners not transitive')
            counts['transitivity_checks'] += 1

        seed = profiles[1]
        seed_maps = []
        images = basis.copy()
        images[0], images[1] = images[1], images[0]
        seed_maps.append(images)
        images = basis.copy()
        images[0] ^= images[1]
        seed_maps.append(images)
        reached = {1}
        for images in seed_maps:
            require(Counter(linmap(images, x) for x in seed) == Counter(seed),
                    'seed does not preserve ALL owner reports')
            require(all(linmap(images, highs[j]) == highs[j] for j in range(1, M)),
                    'seed moved another high resource')
            require(len({linmap(images, x) for x in range(1 << (M + 1))})
                    == 1 << (M + 1), 'seed map not invertible')
            counts['seed_generators'] += 1
        while True:
            enlarged = reached | {linmap(images, x) for images in seed_maps for x in reached}
            if enlarged == reached:
                break
            reached = enlarged
        require(reached == {1, 2, 3}, 'seed owners not transitive')
        counts['seed_transitivity_checks'] += 1

        q = Q(1)
        for m in range(2, M + 1):
            before, after = profiles[m - 1], profiles[m]
            changed = [i for i in range(len(after)) if before[i] != after[i]]
            require(changed == [M + m], 'wrong fixed owner restored')
            coalition = list(range(1, m)) + list(range(M + 1, M + m)) + [M + m]
            require(len(coalition) == 2 * m - 1, 'coalition size')
            require(0 not in coalition and m not in coalition, 'forbidden extra coalition member')
            require(all(before[i] == after[i] for i in coalition if i != M + m),
                    'old coalition reports changed')
            require(all(after[i] in {highs[j] for j in range(m)} |
                        {highs[j] ^ 1 for j in range(m)} for i in coalition),
                    'coalition high payments outside symmetric orbit')
            require(before[M + m] == 0, 'restoring report not zero')
            q *= Q(2 * m, 2 * m - 1)
            counts['fixed_owner_transitions'] += 1
        lower = Q(2, 3) * q
        require(lower * lower >= Q(3 * M + 1, 9), 'sqrt lower bound')
        families.append({'M': M, 'owners': 2 * M + 1, 'protected_size': 2 * M - 1,
                         'Q': str(q), 'funding_lower': str(lower)})

    for M in range(1, 1001):
        require((2*M+2)**2 * (3*M+1) - (2*M+1)**2 * (3*M+4) == M,
                'lower induction polynomial')
        require((2*M+1)**2 * (M+1) - (2*M+2)**2 * M == M+1,
                'upper induction polynomial')
        counts['cleared_polynomial_checks'] += 2
    certificates = [weighted_certificate(M, terminal_coverage=use_terminal)
                    for use_terminal in (False, True) for M in range(1, 65)]
    counts['exact_weighted_certificates'] = len(certificates)
    counts['exact_weighted_rows'] = sum(certificate['row_count'] for certificate in certificates)
    out = {'status': 'PASS', 'counts': dict(counts), 'families': families,
           'statement': 'R=1, kappa >= (2/3) Q_M, s=2M-1, n=2M+1',
           'scope': 'finite support/stabilizer/transition checks; analytic proof supplies all-M and real-domain averaging',
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'full_certificate_M8': certificates[7],
           'terminal_coverage_certificate_M8': certificates[71]}
    target = Path(__file__).with_suffix('.json')
    target.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({key: value for key, value in out.items()
                      if key not in ('full_certificate_M8', 'terminal_coverage_certificate_M8')}, indent=2))


if __name__ == '__main__':
    main()
