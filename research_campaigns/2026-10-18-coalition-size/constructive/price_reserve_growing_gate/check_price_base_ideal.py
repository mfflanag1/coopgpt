#!/usr/bin/env python3
"""Exact replay of the new price-base assignment, not a new search.

Adapted transparently from the retained check_unit_worth_rule.py. Reads its
already audited PG(3,2) geometry/value data without changing those sources.
The universal argument is in UNIT_WORTH_PRICE_BASE_FRONTIER.txt; this bounded
replay does not establish that argument or an all-real mechanism.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import comb
from pathlib import Path
import json
import numpy as np

CAMP = Path(__file__).resolve().parents[2]
SOURCE = CAMP / 'lower' / 'branching_pilot'
meta = json.loads((SOURCE / 'quotient.json').read_text())
arr = np.load(SOURCE / 'quotient.npz')
profile_orbit = arr['profile']
edges = [tuple(e) for e in meta['edges']]
values = [F(meta['oracles'][str(mask)]['value']) for mask in meta['profile_reps']]
ideal = [mask for mask in range(32768) if values[int(profile_orbit[mask])] <= 1]
reps = [mask for mask in meta['profile_reps'] if values[int(profile_orbit[mask])] <= 1]

def value(mask):
    return values[int(profile_orbit[mask])]

@lru_cache(None)
def geometry(mask):
    supported = [e for e in edges if all(mask & (1 << i) for i in e)]
    if not supported:
        return 0, None, ()
    common = set(supported[0])
    for e in supported[1:]:
        common.intersection_update(e)
    assert common
    if len(supported) > 1:
        assert len(common) == 1
    cap = min(common)
    private = tuple(v for e in supported for v in e if v != cap)
    assert len(private) == len(set(private)) == 2 * len(supported)
    return len(supported), cap, private

@lru_cache(None)
def q(s, m):
    out = F(1, 3)
    for j in range(2, m + 1):
        a = min(s - 1, 2 * j - 2)
        out *= F(a, a + 1)
    return out

@lru_cache(None)
def pay(mask, s):
    m, cap, private = geometry(mask)
    out = [F(0)] * 15
    if m:
        out[cap] = F(1, 3) if m == 1 else F(1)
        for v in private:
            out[v] = q(s, m)
    return tuple(out)

def price(mask):
    m, cap, private = geometry(mask)
    out = [F(0) if mask & (1 << i) else F(1) for i in range(15)]
    if m == 1:
        for i in (cap,) + private:
            out[i] = F(1, 3)
    elif m > 1:
        out[cap] = F(1)
    return out

formula_checks = 0
for s in range(1, 101):
    if s == 1:
        assert all(q(s, m) == 0 for m in range(2, 20))
        formula_checks += 18
        continue
    h = (s + 1) // 2
    Q_h = F(4 ** h, 2 * comb(2 * h, h))
    assert q(s, h) == Q_h / (3 * h)
    A = 1 + 2 * s * q(s, s)
    B = 1 + 2 * (s - 1) * q(s, s)
    assert A == 1 + F(s, s - 1) * (B - 1)
    assert A - B == 2 * q(s, s)
    candidates = {m: m * q(s, m) for m in range(1, 2 * s + 3)}
    assert [m for m, x in candidates.items() if x == max(candidates.values())] == [s - 1, s]
    old = {m: (m - 1) * q(s, m) for m in range(1, 2 * s + 3)}
    assert [m for m, x in old.items() if x == max(old.values())] == [s, s + 1]
    assert max([F(1)] + [1 + 2 * m * q(s, m) for m in range(2, 2 * s + 3)]) == A
    formula_checks += 6

coverage = endpoints = price_feasibility = price_efficiency = price_domination = 0
positive_low = zero_low = zero_to_positive = 0
bounds = []
for s in range(1, 16):
    bound = F(1) if s == 1 else 1 + 2 * s * q(s, s)
    bounds.append({'s': s, 'A_s': str(bound)})
    for T in reps:
        high = pay(T, s)
        p = price(T)
        assert all(v >= 0 for v in high)
        assert sum(high) <= bound * value(T)
        for e in edges:
            assert sum(p[i] for i in e) >= 1
            price_feasibility += 1
        assert sum(p[i] for i in range(15) if T & (1 << i)) == value(T)
        price_efficiency += 1
        for i in range(15):
            assert high[i] >= p[i] * bool(T & (1 << i))
            price_domination += 1
        S = T
        while True:
            # Inactive actual owners remain: adding them to a coalition adds
            # zero to this explicit upper, and cannot alter production.
            assert sum(high[i] for i in range(15) if S & (1 << i)) >= value(S)
            coverage += 1
            D = T ^ S
            if D.bit_count() <= s:
                lowpay = pay(S, s)
                delta = [high[i] - lowpay[i] for i in range(15)]
                gain = sum(delta[i] for i in range(15) if D & (1 << i))
                # Exact minimum over EVERY protected C containing D, including
                # unchanged active, isolated, and inactive actual owners.
                losses = sorted([max(F(0), -delta[i]) for i in range(15)
                                 if not D & (1 << i)], reverse=True)
                assert gain - sum(losses[:s - D.bit_count()]) >= value(D)
                endpoints += 1
                if D:
                    if value(S) == 1:
                        assert value(D) == 0
                        positive_low += 1
                    else:
                        zero_low += 1
                        zero_to_positive += int(value(T) == 1)
            if S == 0:
                break
            S = (S - 1) & T

print(json.dumps({
    'status': 'PASS',
    'scope': 'Bounded exact replay supporting the symbolic restricted-ideal theorem only.',
    'dependencies': ['lower/branching_pilot/quotient.json', 'lower/branching_pilot/quotient.npz'],
    'all_actual_ideal_profiles': len(ideal),
    'all_actual_endpoint_pairs_represented': sum(2 ** m.bit_count() for m in ideal),
    'final_profile_orbits': len(reps),
    'coalition_coverage_checks': coverage,
    'all_coalition_full_OUT_endpoint_checks': endpoints,
    'positive_low_nontrivial_endpoint_checks': positive_low,
    'zero_low_nontrivial_endpoint_checks': zero_low,
    'zero_to_positive_nontrivial_endpoint_checks': zero_to_positive,
    'dual_feasibility_edge_checks': price_feasibility,
    'dual_efficiency_checks': price_efficiency,
    'actual_owner_price_domination_checks': price_domination,
    'recurrence_and_funding_identity_checks_s_1_to_100': formula_checks,
    'bounds': bounds,
}, indent=2))
