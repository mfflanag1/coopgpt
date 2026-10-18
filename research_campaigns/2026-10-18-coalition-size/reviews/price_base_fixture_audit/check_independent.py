#!/usr/bin/env python3
"""Independent exact verifier: enumerate model first, then validate witnesses.

No author Python module is imported. The twelve profiles are constructed from
their stated definition, rather than inferred from the submitted certificate.
All rows in both submitted dual certificates must be literal legal model rows.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
AUTHOR = CAMP / 'reviews/next_frontier_synthesis/check_price_base_fixture.json'
SEALED = CAMP / 'reviews/three_portfolio_certificate.json'
OWNERS = range(3)
B = {'0': (0, 0, 0), 'L': (1, 0, 1), 'R': (0, 1, 1)}
LOWS = set(permutations('0LR'))
HIGHS = set(permutations('LLR')) | set(permutations('LRR'))
PROFILES = sorted(LOWS | HIGHS)
COALITIONS = [c for k in (1, 2, 3) for c in combinations(OWNERS, k)]
PROTECTED = [c for c in COALITIONS if len(c) <= 2]


def key(p, i, kind='y'):
    return f'{kind}:{"".join(p)}:{i}'


def endowment(p, c):
    return tuple(sum(B[p[i]][a] for i in c) for a in range(3))


def worth(p, c):
    return min(endowment(p, c))


def row(coeff, rhs=0, equality=False):
    return (bool(equality), F(rhs), tuple(sorted((k, F(v)) for k, v in coeff.items() if v)))


def evaluate(r, assignment):
    eq, rhs, coeff = r
    lhs = sum(v * assignment[k] for k, v in coeff)
    assert lhs == rhs if eq else lhs >= rhs, (r, lhs, rhs)


def add_terms(*items):
    out = defaultdict(F)
    for coeff in items:
        for k, v in coeff.items():
            out[k] += v
    return dict(out)


def legal(l, h, c):
    for i in OWNERS:
        for a in range(3):
            if i not in c and B[l[i]][a] != B[h[i]][a]:
                return False
            if i in c and B[l[i]][a] > B[h[i]][a]:
                return False
    return True


def main():
    author = json.loads(AUTHOR.read_text())
    sealed = json.loads(SEALED.read_text())
    sealed_profiles = {tuple(t['profile']) for r in sealed['rows'] for t in r['terms']}
    assert sealed_profiles == set(PROFILES) == {tuple(p) for p in author['profiles']}
    assert all(worth(p, OWNERS) == 1 for p in PROFILES)
    assert author['source_sha256'] == hashlib.sha256(SEALED.read_bytes()).hexdigest()

    base = []
    priced = []
    counts = Counter()
    for p in PROFILES:
        for i in OWNERS:
            base.append(row({key(p, i): 1})); counts['payment_nonnegative'] += 1
        for c in COALITIONS:
            base.append(row({key(p, i): 1 for i in c}, worth(p, c)))
            counts['coverage'] += 1
        base.append(row({'K': worth(p, OWNERS), **{key(p, i): -1 for i in OWNERS}}))
        counts['budget'] += 1
        for a in range(3):
            priced.append(row({key(p, a, 'p'): 1})); counts['price_nonnegative'] += 1
        priced.append(row({key(p, a, 'p'): 1 for a in range(3)}, 1))
        counts['price_feasibility'] += 1
        priced.append(row({key(p, a, 'p'): endowment(p, OWNERS)[a] for a in range(3)},
                          worth(p, OWNERS), equality=True))
        counts['price_efficiency'] += 1
        for i in OWNERS:
            priced.append(row({key(p, i): 1,
                               **{key(p, a, 'p'): -B[p[i]][a] for a in range(3)}}))
            counts['price_domination'] += 1

    transitions = []
    for l in PROFILES:
        for h in PROFILES:
            for c in PROTECTED:
                if not legal(l, h, c):
                    continue
                coeff = add_terms({key(h, i): 1 for i in c}, {key(l, i): -1 for i in c})
                delta = tuple(sum(B[h[i]][a] - B[l[i]][a] for i in c) for a in range(3))
                assert min(delta) == 0
                base.append(row(coeff)); transitions.append((l, h, c))
                counts['comparison'] += 1
                if l != h:
                    counts['proper_comparison'] += 1
                    counts[f'proper_size_{len(c)}'] += 1
                    if any(l[i] == h[i] for i in c):
                        counts['proper_with_passive_owner'] += 1
    assert counts['coverage'] == 84 and counts['comparison'] == 108
    assert counts['proper_comparison'] == 36 and counts['proper_with_passive_owner'] == 24
    assert counts['proper_size_1'] == 12 and counts['proper_size_2'] == 24
    assert len({(l, h) for l, h, c in transitions if l != h}) == 12

    results = {}
    for model, optimum in [('unrestricted', F(5, 4)), ('price_base', F(3, 2))]:
        assignment = {'K': optimum}
        for p in PROFILES:
            actual_pay = list(map(F, author['primal_payments'][model][''.join(p)]))
            if p in LOWS:
                expected = [F(0) if t == '0' else F(1, 2) for t in p]
            else:
                expected = [F(1, 4) if p.count(t) == 2 else
                            F(3, 4) if model == 'unrestricted' else F(1) for t in p]
            assert actual_pay == expected
            assignment.update({key(p, i): actual_pay[i] for i in OWNERS})
            if model == 'price_base':
                price = list(map(F, author['restricted_primal_prices'][''.join(p)]))
                assignment.update({key(p, a, 'p'): price[a] for a in range(3)})
        rows = base + (priced if model == 'price_base' else [])
        allowed = set(rows)
        for r in rows:
            evaluate(r, assignment)

        total = defaultdict(F)
        rhs = F(0)
        for submitted in author['dual_certificates'][model]:
            r = row(submitted['coeff'], submitted['rhs'], submitted['equality'])
            assert r in allowed, ('not a literal legal model row', submitted)
            weight = F(submitted['weight'])
            assert r[0] or weight >= 0
            rhs += weight*r[1]
            for k, v in r[2]:
                total[k] += weight*v
        assert {k: v for k, v in total.items() if v} == {'K': F(6)}
        assert rhs == 6*optimum
        results[model] = {'optimum': str(optimum), 'all_model_rows_checked': len(rows),
                          'certificate_rows': len(author['dual_certificates'][model]),
                          'dual_total': {'K': '6', 'rhs': str(rhs)},
                          'literal_row_membership': True}

    # Independently reconstruct the new lower proof by profile combinatorics.
    # First cancel all low-profile coordinates, retaining one copy of each
    # high-profile majority pair and right-hand side 3.
    partial = defaultdict(F)
    rhs = F(0)
    selected = []
    for l in sorted(LOWS):
        z = l.index('0')
        for incumbent in OWNERS:
            if incumbent == z:
                continue
            h = list(l); h[z] = l[incumbent]; h = tuple(h)
            c = tuple(sorted((z, incumbent)))
            assert (l, h, c) in transitions
            selected.append((l, h, c))
            for i in c:
                partial[key(h, i)] += F(1, 2)
                partial[key(l, i)] -= F(1, 2)
        for i in OWNERS:
            partial[key(l, i)] += F(1) if i == z else F(1, 2)
        rhs += F(1, 2)
    expected_partial = {key(p, i): F(1) for p in HIGHS for i in OWNERS if p.count(p[i]) == 2}
    assert {k: v for k, v in partial.items() if v} == expected_partial
    assert rhs == 3 and len(selected) == 12
    for p in HIGHS:
        minority = next(i for i in OWNERS if p.count(p[i]) == 1)
        # D + 2G - E + 2*p_3, with the equality E freely signed.
        coeff = {key(p, minority): F(1)}
        for a in range(3):
            coeff[key(p, a, 'p')] = -B[p[minority]][a] + 2 - endowment(p, OWNERS)[a] + 2*(a == 2)
        assert {k: v for k, v in coeff.items() if v} == {key(p, minority): F(1)}
    results['independent_reconstruction'] = {
        'same_type_pair_rows': 12, 'low_payment_coordinates_canceled': 18,
        'high_majority_coordinates_remaining': 12, 'rhs': '3',
        'minority_price_eliminations': 6,
        'final_inequality': '6K >= 9'}

    # Validate every original sealed row against the independently generated
    # unconstrained model, including RHS and coefficient shape of transitions.
    for sealed_row in sealed['rows']:
        coeff = defaultdict(F)
        for t in sealed_row['terms']:
            coeff[key(tuple(t['profile']), t['owner'])] += F(t['coefficient'])
        assert row(coeff, sealed_row['rhs']) in set(base)
        assert F(sealed_row['weight']) >= 0
    results['sealed_source_literal_rows_checked'] = len(sealed['rows'])

    output = {'status': 'PASS', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Exact finite 12-profile min3 restriction only; no all-real primal extension or growing claim.',
              'arithmetic': 'Python Fraction; no optimizer; no author code imported',
              'profiles': [''.join(p) for p in PROFILES], 'counts': dict(counts),
              'results': results,
              'source_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (AUTHOR, SEALED, Path(__file__))}}
    Path(__file__).with_suffix('.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'counts': dict(counts), 'results': results}, indent=2))


if __name__ == '__main__':
    main()
