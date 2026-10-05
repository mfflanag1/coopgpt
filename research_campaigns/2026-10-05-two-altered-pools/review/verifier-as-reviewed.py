"""Exact finite verification of the two-altered-pool assignment.

The labeled test computes actual coalition values and report edges, independent
of the proof's coalition reduction. No solver and no tolerance are used.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from math import lcm
from pathlib import Path
import hashlib
import json


def check(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def coefficients(r, h):
    check(2 <= r and 0 <= h < r, 'coefficient domain')
    T = Q(r + (r - 1) * h, r)
    delta = Q(r - h, r)
    z = T / r
    return max(delta - z, Q(0)) / (r - h), 1 - z, z, T


@lru_cache(None)
def ahead_weight(r, h, g):
    check(0 <= g < h < r, 'weight domain')
    e = Q(1, 2)
    for s in range(g, h):
        a = coefficients(r, s)[0]
        b = coefficients(r, s + 1)[1]
        check(b > 0, 'vanishing ratio denominator')
        e *= a / b
    return e


def components(k, r, counts):
    active = [j for j, h in enumerate(counts) if h < r]
    check(len(active) <= 2, 'outside two-pool domain')
    if not active:
        return []
    if len(active) == 1:
        return [(active[0], Q(1))]
    j, l = active
    h, g = counts[j], counts[l]
    if h == g:
        return [(j, Q(1, 2)), (l, Q(1, 2))]
    if h < g:
        j, l, h, g = l, j, g, h
    e = ahead_weight(r, h, g)
    return [(j, e), (l, 1 - e)]


def payments(profile):
    """Profile capacities are integers 1,r, representing actual reports 1/r,1."""
    k, r = len(profile), len(profile[0])
    check(k >= 2 and all(len(pool) == r for pool in profile), 'ownership')
    check(all(cap in (1, r) for pool in profile for cap in pool), 'report alphabet')
    counts = tuple(sum(cap == r for cap in pool) for pool in profile)
    mixture = components(k, r, counts)
    if not mixture:
        return tuple(Q(1, k) for _ in range(k * r))
    result = []
    for j, pool in enumerate(profile):
        for cap in pool:
            y = Q(0)
            for active, weight in mixture:
                a, b, z, _ = coefficients(r, counts[active])
                y += weight * (z / (k - 1) if active != j else b if cap == r else a)
            result.append(y)
    return tuple(result)


def all_profiles(k, r):
    H = tuple(tuple(r for _ in range(r)) for _ in range(k))
    found = {H}
    local = [tuple(r if mask >> i & 1 else 1 for i in range(r))
             for mask in range((1 << r) - 1)]
    for q in (1, 2):
        for active in combinations(range(k), q):
            for pools in product(local, repeat=q):
                c = list(H)
                for j, pool in zip(active, pools):
                    c[j] = pool
                found.add(tuple(c))
    expected = 1 + k * ((1 << r) - 1) + k * (k - 1) // 2 * ((1 << r) - 1) ** 2
    check(len(found) == expected, 'labeled profile partition')
    return found


def subset_values(values):
    sums = [0] * (1 << len(values))
    for mask in range(1, len(sums)):
        low = mask & -mask
        sums[mask] = sums[mask ^ low] + values[low.bit_length() - 1]
    return sums


def full_labeled(k, r):
    profiles = all_profiles(k, r)
    stored = {}
    coalitions = edges = 0
    largest_base = largest_fair = Q(0)
    witnesses = []
    for c in sorted(profiles):
        pay = payments(c)
        check(all(isinstance(x, Q) for x in pay), 'non-rational payment')
        totals = list(map(sum, c))
        Tscaled = min(totals)
        marginal = []
        for j in range(k):
            for i in range(r):
                removed = totals.copy()
                removed[j] -= c[j][i]
                marginal.append(Q(Tscaled - min(removed), r))
        fair = tuple(max(y, m / k) for y, m in zip(pay, marginal))
        check(min(pay) >= 0, 'negative labeled payment')
        T = Q(Tscaled, r)
        check(sum(pay) <= 2 * T, 'labeled base budget')
        check(sum(fair) <= 3 * T, 'labeled fair budget')
        largest_base = max(largest_base, sum(pay) / T)
        largest_fair = max(largest_fair, sum(fair) / T)
        # Scale every rational inequality to exact integer arithmetic. Capacities
        # remain in units 1/r; the denominator is divisible by r.
        D = lcm(r, *(x.denominator for x in pay), *(x.denominator for x in fair))
        pay_sums = subset_values([int(x * D) for x in pay])
        fair_sums = subset_values([int(x * D) for x in fair])
        local_capacity = [subset_values(pool) for pool in c]
        mask_pool = (1 << r) - 1
        for mask in range(1 << (k * r)):
            value_scaled = min(local_capacity[j][(mask >> (j * r)) & mask_pool]
                               for j in range(k))
            worth = value_scaled * (D // r)
            check(pay_sums[mask] >= worth, 'labeled coalition coverage')
            check(fair_sums[mask] >= worth, 'labeled fair coalition coverage')
            coalitions += 1
        stored[c] = pay, fair
        if len(witnesses) < 3:
            witnesses.append(dict(capacities_scaled=c, base=list(map(str, pay))))
    for c, (pay, fair) in stored.items():
        for j in range(k):
            for i in range(r):
                if c[j][i] == r:
                    continue
                cp = [list(pool) for pool in c]
                cp[j][i] = r
                cp = tuple(map(tuple, cp))
                check(cp in stored, 'family not closed under increases')
                yp, fp = stored[cp]
                check(yp[j * r + i] >= pay[j * r + i], 'labeled own monotonicity')
                check(fp[j * r + i] >= fair[j * r + i], 'labeled fair monotonicity')
                edges += 1
    return dict(k=k, r=r, labeled_profiles=len(profiles), all_coalitions=coalitions,
                directed_base_and_fair_edges=edges, max_base_factor=str(largest_base),
                max_fair_factor=str(largest_fair), sample_payments=witnesses)


def old_boundary_checks():
    count = 0
    for k, r in ((2, 2), (3, 3), (8, 7), (216, 12)):
        H = tuple(tuple(r for _ in range(r)) for _ in range(k))
        check(payments(H) == (Q(1, k),) * (k * r), 'H boundary changed')
        for h in range(r):
            a, b, z, _ = coefficients(r, h)
            c = list(H)
            c[0] = tuple(r if i < h else 1 for i in range(r))
            expected = tuple([b] * h + [a] * (r - h) + [z / (k - 1)] * ((k - 1) * r))
            check(payments(tuple(c)) == expected, 'one-pool boundary changed')
            count += 1
    return count


def reduced_parameters():
    """Wide exact parameter checks of algebra and all owner-role edges."""
    pair_cases = edge_cases = ratio_cases = 0
    largest = Q(0)
    for r in range(2, 41):
        costs = []
        for h in range(r):
            a, b, z, T = coefficients(r, h)
            F = (r - h) * a + h * b + r * z
            costs.append(F)
            check(2 * T - F >= Q(1, r), 'slack bound')
            if h < r - 1:
                direct = a / coefficients(r, h + 1)[1]
                identity = Q(1, r - 1) * max(1 - Q(h * h, (r - h) * (r - h - 1)), 0)
                check(direct == identity and direct <= Q(1, r - 1), 'ratio identity')
                ratio_cases += 1
        for h in range(r):
            for g in range(h + 1):
                T = coefficients(r, g)[3]
                e = Q(1, 2) if h == g else ahead_weight(r, h, g)
                cost = e * costs[h] + (1 - e) * costs[g]
                check(cost <= 2 * T, 'two-pool exact budget')
                check(costs[h] - costs[g] <= 2 * (h - g), 'cost increment')
                largest = max(largest, cost / T)
                pair_cases += 1
        # Two-role profiles at four k values; coverage is checked independently
        # by full_labeled, not inferred here from budget or monotonicity.
        for k in (2, 3, 8, 216):
            for h in range(r):
                for g in range(r):
                    active = components(k, r, (h, g) + (r,) * (k - 2))
                    current = sum(w * (coefficients(r, h)[0] if j == 0 else
                                       coefficients(r, g)[2] / (k - 1)) for j, w in active)
                    if h + 1 == r:
                        target = coefficients(r, g)[2] / (k - 1)
                    else:
                        updated = components(k, r, (h + 1, g) + (r,) * (k - 2))
                        target = sum(w * (coefficients(r, h + 1)[1] if j == 0 else
                                          coefficients(r, g)[2] / (k - 1)) for j, w in updated)
                    check(target >= current, 'reduced own monotonicity')
                    edge_cases += 1
    return dict(r_range=[2, 40], pair_budget_cases=pair_cases,
                own_edge_role_cases=edge_cases, ratio_identities=ratio_cases,
                largest_two_pool_factor=str(largest))


def rejected_minimum_selector():
    # Direct witness from the independent delegate: a minimum-pool selector
    # switches identity after the selected owner's report rises.
    k, r = 4, 2
    before = ((1, 1), (1, 1), (2, 2), (2, 2))
    after = ((2, 1), (1, 1), (2, 2), (2, 2))
    check(min(map(sum, before)) == min(map(sum, after)) == 2, 'witness value')
    old_payment = coefficients(r, 0)[0]
    new_payment = coefficients(r, 0)[2] / (k - 1)
    check(old_payment == Q(1, 4) and new_payment == Q(1, 6), 'selector witness')
    check(new_payment < old_payment, 'failed selector unexpectedly monotone')
    # The final formula repairs precisely that same edge.
    repaired_old, repaired_new = payments(before)[0], payments(after)[0]
    check(repaired_new >= repaired_old, 'selector failure not repaired')
    return dict(k=k, r=r, rejected_before=str(old_payment), rejected_after=str(new_payment),
                final_before=str(repaired_old), final_after=str(repaired_new))


def main():
    labeled = [full_labeled(k, r) for k, r in ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (3, 4))]
    report = dict(status='PASS', source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Complete finite labeled tests plus parameter checks; universal quantifiers rely on the written proof.',
                  labeled=labeled, boundary_profile_types=old_boundary_checks(),
                  wide_parameter_checks=reduced_parameters(),
                  rejected_minimum_selector=rejected_minimum_selector())
    Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
    compact = {key: value for key, value in report.items() if key != 'labeled'}
    compact['labeled_totals'] = {name: sum(x[name] for x in labeled) for name in
                               ('labeled_profiles', 'all_coalitions', 'directed_base_and_fair_edges')}
    print(json.dumps(compact, indent=2))


if __name__ == '__main__':
    main()
