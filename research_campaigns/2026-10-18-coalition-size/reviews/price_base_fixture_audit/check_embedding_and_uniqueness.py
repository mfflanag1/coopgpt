#!/usr/bin/env python3
"""Exact domain-equivalence and efficient-price checks; no new search."""
from datetime import datetime, timezone
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
U = {'0': (0, 0), 'L': (1, 0), 'R': (0, 1), 'D': (1, 1)}
OWN = range(3)
COALS = [c for k in (1, 2, 3) for c in combinations(OWN, k)]
PROTECT = [c for c in COALS if len(c) <= 2]
PROFILES = list(product(U, repeat=3))


def add(vectors):
    vectors = list(vectors)
    return tuple(sum(x[a] for x in vectors) for a in range(2))


def reserve(ab):
    a, b = map(Q, ab)
    t, x = (a+b)/2, (a-b)/2
    assert t >= abs(x)
    return t-abs(x)


def embed(ab):
    a, b = ab
    return a, b, a+b


def main():
    totals_checked = 0
    legal = 0
    positive_outside = 0
    for p in PROFILES:
        for i in OWN:
            a, b = U[p[i]]
            assert (1-a, 1-b) in U.values()  # owner's withdrawn complement
        for c in COALS:
            ab = add(U[p[i]] for i in c)
            assert reserve(ab) == min(ab) == min(embed(ab))
            totals_checked += 1
    for l in PROFILES:
        for h in PROFILES:
            for c in PROTECT:
                if any(l[i] != h[i] for i in OWN if i not in c):
                    continue
                if any(U[l[i]][a] > U[h[i]][a] for i in c for a in range(2)):
                    continue
                delta = add((U[h[i]][0]-U[l[i]][0], U[h[i]][1]-U[l[i]][1]) for i in c)
                assert reserve(delta) == min(delta) == min(embed(delta))
                legal += 1
                positive_outside += min(delta) > 0
    fixture = [p for p in PROFILES if 'D' not in p and 'L' in p and 'R' in p]
    assert len(fixture) == 12
    assert all(all(0 <= v <= 1 for v in embed(U[t])) for p in fixture for t in p)
    assert embed(U['D']) == (1, 1, 2)  # whole-domain linear lift uses a larger third cap

    high_evidence = []
    for p in fixture:
        if '0' in p:
            continue
        B = embed(add(U[t] for t in p))
        excess = tuple(x-1 for x in B)
        unique_index = 1 if p.count('L') == 2 else 0
        positive_indices = [a for a, x in enumerate(excess) if x > 0]
        assert len(positive_indices) == 2 and unique_index not in positive_indices
        price = tuple(int(a == unique_index) for a in range(3))
        assert sum(price) == 1 and sum(price[a]*B[a] for a in range(3)) == 1
        minority = next(i for i in OWN if p.count(p[i]) == 1)
        assert sum(price[a]*embed(U[p[minority]])[a] for a in range(3)) == 1
        high_evidence.append({'profile': ''.join(p), 'B': B, 'excess_B_minus_one': excess,
                              'unique_price': price,
                              'argument': 'p>=0, p.B=1, sum(p)>=1 imply p.(B-1)<=0; its two positive coefficients force those coordinates zero, and efficiency fixes the remaining coordinate to one.'})
    assert len(high_evidence) == 6
    out = {'status': 'PASS', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
           'scope': 'Equivalent worths and legal report comparisons, not a payment mechanism on all64 profiles.',
           'application_profiles': 64, 'coalition_worth_equalities': totals_checked,
           'legal_size_at_most_two_comparisons': legal,
           'comparisons_with_positive_outside_worth': positive_outside,
           'unit_cube_min3_fixture_profiles': len(fixture),
           'high_price_uniqueness': high_evidence,
           'whole64_linear_min3_owner_cap': [1, 1, 2],
           'fixture_min3_owner_cap': [1, 1, 1]}
    Path(__file__).with_suffix('.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k != 'high_price_uniqueness'}, indent=2))


if __name__ == '__main__':
    main()
