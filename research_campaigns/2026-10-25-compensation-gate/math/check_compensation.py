#!/usr/bin/env python3
"""Exact finite replay of the symbolic proof; this is not a continuum search."""
from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path


def price_charges(a, b):
    if a < b:
        return (a, Q(0))
    if b < a:
        return (Q(0), b)
    return (a / 2, b / 2)  # tie choice irrelevant to the off-diagonal witness


def value(profile):
    return min(map(sum, zip(*profile)))


def subsets(n, max_size=None):
    return [C for k in range(1, (max_size or n) + 1)
            for C in combinations(range(n), k)]


def check_profiles(profiles, pay, max_size, factor):
    n = len(profiles[0])
    d = len(profiles[0][0])
    coverage = comparisons = 0
    for b, y in zip(profiles, pay):
        assert all(z >= 0 for z in y)
        assert sum(y) <= factor * value(b)
        for C in subsets(n):
            assert sum(y[i] for i in C) >= value([b[i] for i in C])
            coverage += 1
    for il, l in enumerate(profiles):
        for ih, h in enumerate(profiles):
            if il == ih or not all(l[i][a] <= h[i][a]
                                  for i in range(n) for a in range(d)):
                continue
            changed = {i for i in range(n) if l[i] != h[i]}
            delta = tuple(sum(h[i][a] - l[i][a] for i in range(n))
                          for a in range(d))
            for C in subsets(n, max_size):
                if changed <= set(C):
                    assert sum(pay[ih][i] - pay[il][i] for i in C) >= min(delta)
                    comparisons += 1
    return dict(coverage=coverage, fullOUT_comparisons=comparisons)


def staircase(L):
    delta = Q(1, L + 2)
    q = []
    for k in range(L + 1):
        if k % 2 == 0:
            q.append((1 + k * delta, 1 + (k + 1) * delta))
        else:
            q.append((1 + (k + 1) * delta, 1 + k * delta))
    reserve = [Q(0), Q(0)]
    irreversible = []
    releases = Q(0)
    previous_recycling = None
    for k, (a, b) in enumerate(q):
        assert 0 < a < 2 and 0 < b < 2 and a != b
        F = min(a, b)
        assert F == 1 + k * delta
        u = price_charges(a, b)
        assert sum(u) == F
        if k:
            old = q[k - 1]
            changer = 0 if k % 2 else 1
            passive = 1 - changer
            assert (a, b)[passive] == old[passive]
            assert (a, b)[changer] - old[changer] == 2 * delta
            old_u = price_charges(*old)
            assert old_u[changer] == min(old) and u[changer] == 0
            reserve[changer] += old_u[changer]
        W_k = k + delta * k * (k - 1) / 2
        assert sum(reserve) == W_k
        irreversible.append(tuple(u[i] + reserve[i] for i in range(2)))
        recycling = tuple(F - z for z in u)
        assert all(x >= 0 for x in recycling) and sum(recycling) == F
        if k:
            releases += sum(max(Q(0), previous_recycling[i] - recycling[i])
                            for i in range(2))
        previous_recycling = recycling
    W = sum(min(q[k - 1]) for k in range(1, L + 1))
    F_L = min(q[-1])
    K = 1 + W / F_L
    assert W == Q(3 * L * (L + 1), 2 * (L + 2))
    assert K == 1 + Q(3 * L, 4)
    assert releases == W
    assert releases >= max(Q(0), W - F_L)  # quantitative theorem at K=2
    profiles = [((a, Q(0)), (Q(0), b)) for a, b in q]
    checks = check_profiles(profiles, irreversible, 2, K)
    for k in range(1, L + 1):
        assert sum(irreversible[k]) / min(q[k]) > sum(irreversible[k-1]) / min(q[k-1])
    assert sum(irreversible[-1]) / F_L == K
    return dict(L=L, delta=str(delta), W=str(W), final_value=str(F_L),
                exact_restricted_factor=str(K), factor_two_releases=str(releases), **checks)


def cea(claims, estate):
    """Independent exact water-filling, including zero claims and exhausted estate."""
    assert 0 <= estate <= sum(claims)
    remaining = estate
    active = set(range(len(claims)))
    awards = [Q(0)] * len(claims)
    while active:
        level = remaining / len(active)
        saturated = {i for i in active if claims[i] <= level}
        if not saturated:
            for i in active:
                awards[i] = level
            break
        for i in saturated:
            awards[i] = claims[i]
            remaining -= claims[i]
        active -= saturated
    assert sum(awards) == estate
    assert all(0 <= a <= c for a, c in zip(awards, claims))
    return awards


def crossing_calibration():
    A, B, C, D = map(lambda x: tuple(map(Q, x)), [(1,0,2), (0,2,0), (2,0,1), (1,2,2)])
    z = (Q(0),) * 3
    profiles = [(A,z,z,D), (A,z,C,D), (A,B,z,D)]
    pay = []
    for b in profiles:
        E = value(b)
        pools = [cea(tuple(b[i][a] for i in range(4)), E) for a in range(3)]
        pay.append(tuple(sum(pool[i] for pool in pools) for i in range(4)))
    expected = [(Q(2),Q(0),Q(0),Q(4)),
                (Q(4,3),Q(0),Q(4,3),Q(10,3)),
                (Q(2),Q(1),Q(0),Q(3))]
    assert pay == expected
    checks = check_profiles(profiles, pay, 2, Q(3))
    assert checks == dict(coverage=45, fullOUT_comparisons=8)
    return dict(status='prior positive calibration only', payments=[[str(x) for x in y] for y in pay], **checks)


def full_box_calibration():
    grid = list(map(Q, ['0','1/4','1/2','1','3/2','2']))
    profiles = [((a,Q(0)),(Q(0),b)) for a,b in product(grid, repeat=2)]
    dictator = [(value(b),Q(0)) for b in profiles]
    recycling = [(value(b),value(b)) for b in profiles]
    for p, y in zip(profiles, recycling):
        assert all(yi >= ui for yi, ui in zip(y, price_charges(p[0][0],p[1][1])))
    return dict(profiles=len(profiles),
                factor_one=check_profiles(profiles,dictator,2,Q(1)),
                factor_two=check_profiles(profiles,recycling,2,Q(2)),
                scope='finite checks supplementary to full-box symbolic proofs')


if __name__ == '__main__':
    result = dict(status='PASS', arithmetic='fractions.Fraction; standard library only',
                  staircase=[staircase(L) for L in [1,2,3,4,8,16,32,64,128]],
                  calibration=full_box_calibration(), crossing=crossing_calibration(),
                  frontier_changed=False, novelty_confirmed=False)
    text = json.dumps(result, indent=2) + '\n'
    Path(__file__).with_name('EXACT_CHECK.json').write_text(text)
    print(text)
