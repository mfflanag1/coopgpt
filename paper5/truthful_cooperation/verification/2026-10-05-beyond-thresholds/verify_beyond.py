"""Exact rational checks; finite certificates supplement the written proofs.

No optimizer, numerical tolerances, or Python assert statements are used.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
from math import comb
from pathlib import Path
import hashlib
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def profile(k, r, j, h):
    return tuple(tuple(Q(1) if l != j or i < h else Q(1, r)
                       for i in range(r)) for l in range(k))


def price_key(j, h, l, r):
    return ('p', -1 if h == r else j, h, l)


def reconstruct(k, r, kind, j, h, owner):
    """Recover each inequality from actual capacities and the named coalition."""
    c = profile(k, r, j, h)
    T = min(map(sum, c))
    require(all(0 < x <= T for pool in c for x in pool), 'capping domain')
    if kind == 'cover':
        require(h == 0, 'coverage must be at L_j')
        selections = [range(r) if l == j else (0,) for l in range(k)]
        totals = [sum(c[l][i] for i in selections[l]) for l in range(k)]
        return {price_key(j, h, l, r): totals[l] for l in range(k)}, min(totals)
    if kind == 'budget':
        # Divide the actual row B*T - sum_i c_i*p_pool >= 0 by T.
        row = {'B': Q(1)}
        row.update({price_key(j, h, l, r): -sum(c[l]) / T for l in range(k)})
        return row, Q(0)
    require(kind == 'mono', 'unknown row')
    require(0 <= h < r and owner == h, 'wrong changing owner')
    cp = profile(k, r, j, h + 1)
    changes = [(l, i) for l in range(k) for i in range(r) if c[l][i] != cp[l][i]]
    require(changes == [(j, owner)], 'not a one-owner deviation')
    require(cp[j][owner] > c[j][owner], 'wrong direction')
    return {price_key(j, h + 1, j, r): cp[j][owner],
            price_key(j, h, j, r): -c[j][owner]}, Q(0)


def certificate(k, r):
    rows = []
    def add(kind, j, h, owner, weight):
        row, rhs = reconstruct(k, r, kind, j, h, owner)
        rows.append(dict(kind=kind, j=j, h=h, owner=owner,
                         row=row, rhs=rhs, weight=Q(weight)))
    for j in range(k):
        add('cover', j, 0, None, r)
        add('budget', j, 0, None, 1)
        for h in range(r):
            add('mono', j, h, h, (r - 1) * r ** (h + 1))
    add('budget', 0, r, None, (r - 1) * r ** r)
    return rows


def verify_certificate(k, r, rows):
    total = defaultdict(Q)
    rhs = Q(0)
    for x in rows:
        row, b = reconstruct(k, r, x['kind'], x['j'], x['h'], x['owner'])
        require(x['row'] == row and x['rhs'] == b, 'row differs from game')
        require(x['weight'] >= 0, 'negative multiplier')
        for key, value in row.items():
            total[key] += x['weight'] * value
        rhs += x['weight'] * b
    residual = {key: value for key, value in total.items() if value}
    require(residual == {'B': k + (r - 1) * r ** r}, 'uncancelled coefficients')
    require(rhs == k * r, 'wrong right side')
    return str(rhs / residual['B'])


def mutation_checks():
    original = certificate(3, 3)
    count = 0
    for mutation in range(8):
        rows = deepcopy(original)
        expected = 'row differs from game'
        if mutation == 0:
            rows[0]['rhs'] += 1
        elif mutation == 1:
            key = next(iter(rows[0]['row']))
            rows[0]['row'][key] += 1
        elif mutation == 2:
            rows[0]['weight'] = Q(-1)
            expected = 'negative multiplier'
        elif mutation == 3:
            rows[2]['owner'] = 1
            expected = 'wrong changing owner'
        elif mutation == 4:
            rows[-1]['weight'] += 1
            expected = 'uncancelled coefficients'
        elif mutation == 5:
            rows.pop(2)
            expected = 'uncancelled coefficients'
        elif mutation == 6:
            rows[0]['j'] = 1
        else:
            # Substitute a different VALID budget row: only aggregate checking
            # should reject it, rather than row syntax or report validation.
            rows[1]['j'] = 1
            rows[1]['row'], rows[1]['rhs'] = reconstruct(3, 3, 'budget', 1, 0, None)
            expected = 'uncancelled coefficients'
        try:
            verify_certificate(3, 3, rows)
        except ValueError as error:
            require(str(error) == expected, 'mutation failed at unexpected guard')
            count += 1
        else:
            raise ValueError('corrupt certificate accepted')
    return count


def escape_payments(k, r, h):
    delta = Q(r - h, r)
    T = h + delta
    z = T / r
    return max(delta - z, Q(0)) / (r - h), 1 - z, z / (k - 1), T


def escape_checks():
    cases = covers = edges = 0
    largest_ratio = Q(0)
    for r in range(2, 21):
        for k in (2, 3, 8, 216):
            previous = None
            for h in range(r):
                a, b, c, T = escape_payments(k, r, h)
                require(all(isinstance(x, Q) for x in (a, b, c)), 'non-rational escape payment')
                require(min(a, b, c) >= 0, 'negative escape payment')
                paid = (r - h) * a + h * b + (k - 1) * r * c
                largest_ratio = max(largest_ratio, paid / T)
                require(paid <= 2 * T, 'escape budget')
                if previous is not None:
                    require(previous <= b, 'escape monotonicity')
                    edges += 1
                previous = a
                # n is the minimum number of selected owners in any other pool.
                # Higher counts only increase payment, so all coalitions reduce here.
                for small, big, n in product(range(r - h + 1), range(h + 1), range(r + 1)):
                    value = min(Q(small, r) + big, n)
                    payment = small * a + big * b + (k - 1) * n * c
                    require(payment >= value, 'escape coalition')
                    covers += 1
                # Marginals: special owners lose their full capacity on removal;
                # other unit owners lose max(0,T-(r-1)). Check the fair top-up.
                ma, mb = Q(1, r), Q(1)
                mc = max(T - (r - 1), Q(0))
                fair = (r - h) * max(a, ma / k) + h * max(b, mb / k)
                fair += (k - 1) * r * max(c, mc / k)
                require(fair <= 3 * T, 'fair escape budget')
                cases += 1
            require(previous <= Q(1, k), 'last link to H')
            edges += 1
    return dict(non_H_profile_types=cases, reduced_coalitions=covers, base_edge_types=edges,
                largest_base_factor=str(largest_ratio), r_range=[2, 20], k_values=[2, 3, 8, 216])


def value(c, selected):
    return min(sum(x for i, x in enumerate(pool) if (j, i) in selected)
               for j, pool in enumerate(c))


def labeled_escape_checks():
    """Independent brute-force game checks without the coalition-count reduction."""
    profiles_checked = coalitions_checked = edges_checked = 0
    for k, r in ((2, 2), (2, 3), (3, 2), (3, 3)):
        H = tuple(tuple(Q(1) for _ in range(r)) for _ in range(k))
        profiles = {H}
        for j in range(k):
            for high_mask in range(1 << r):
                profiles.add(tuple(tuple(Q(1) if l != j or high_mask >> i & 1 else Q(1, r)
                                         for i in range(r)) for l in range(k)))
        slots = [(j, i) for j in range(k) for i in range(r)]
        all_owners = set(slots)
        table = {}
        for c in profiles:
            T = value(c, all_owners)
            if c == H:
                payments = {i: Q(1, k) for i in slots}
            else:
                special = [j for j, pool in enumerate(c) if any(x != 1 for x in pool)]
                require(len(special) == 1, 'labeled family definition')
                j = special[0]
                h = sum(x == 1 for x in c[j])
                a, b, other, _ = escape_payments(k, r, h)
                payments = {owner: (other if owner[0] != j else
                                   b if c[owner[0]][owner[1]] == 1 else a)
                            for owner in slots}
            marginal = {i: T - value(c, all_owners - {i}) for i in slots}
            fair = {i: max(payments[i], marginal[i] / k) for i in slots}
            require(min(payments.values()) >= 0, 'labeled nonnegativity')
            require(sum(payments.values()) <= 2 * T, 'labeled base budget')
            require(sum(fair.values()) <= 3 * T, 'labeled fair budget')
            for mask in range(1 << (k * r)):
                S = {i for n, i in enumerate(slots) if mask >> n & 1}
                worth = value(c, S)
                require(sum(payments[i] for i in S) >= worth, 'labeled base coalition')
                require(sum(fair[i] for i in S) >= worth, 'labeled fair coalition')
                coalitions_checked += 1
            table[c] = payments, fair
            profiles_checked += 1
        for c in profiles:
            for cp in profiles:
                changed = [i for i in slots if c[i[0]][i[1]] != cp[i[0]][i[1]]]
                if len(changed) != 1:
                    continue
                i = changed[0]
                if cp[i[0]][i[1]] <= c[i[0]][i[1]]:
                    continue
                require(table[cp][0][i] >= table[c][0][i], 'labeled base monotonicity')
                require(table[cp][1][i] >= table[c][1][i], 'labeled fair monotonicity')
                edges_checked += 1
    return dict(labeled_profiles_including_H=profiles_checked,
                all_coalitions=coalitions_checked, all_base_and_fair_edges=edges_checked,
                instances=[[2, 2], [2, 3], [3, 2], [3, 3]])


def failed_constructions():
    # Exact integration of the pivotal-height rule, including every breakpoint.
    c = ((Q(1, 2), Q(1, 2)), (Q(1), Q(1, 4), Q(1, 4)))
    totals = list(map(sum, c))
    T = min(totals)
    heights = [sum(pool) - max(pool) for pool in c]
    payments = {}
    for j, pool in enumerate(c):
        for i, cap in enumerate(pool):
            start = totals[j] - cap
            cuts = sorted({start, T} | {h for h in heights if start < h < T})
            payment = Q(0)
            if start < T:
                for a, b in zip(cuts, cuts[1:]):
                    mid = (a + b) / 2
                    payment += (b - a) / sum(h <= mid for h in heights)
            payments[j, i] = payment
    S = {(0, 0), (1, 1), (1, 2)}
    worth, paid = value(c, S), sum(payments[i] for i in S)
    require((worth, paid) == (Q(1, 2), Q(1, 4)), 'height witness')
    # Refute the delegate's source-cost equality. Each of m unit coalitions
    # contains exporter e and one distinct owner per other pool: dual cost m.
    # Paying every owner of one unit pool one is a cover of weighted cost m.
    for m in range(2, 7):
        c = ((Q(1), Q(1)), tuple(Q(1) for _ in range(m)))
        weights = {(0, 0): Q(1), (0, 1): Q(m)}
        weights.update({(1, i): Q(1) for i in range(m)})
        loads = defaultdict(Q)
        dual = Q(0)
        for i in range(m):
            S = {(0, 1), (1, i)}
            dual += value(c, S)
            for owner in S:
                loads[owner] += 1
        require(all(loads[i] <= w for i, w in weights.items()), 'source dual infeasible')
        require(dual == m and min(2 + (m - 1), 1 + m) == m + 1,
                'source-cost counterexample')
        for mask in range(1 << (m + 2)):
            slots = list(weights)
            S = {x for n, x in enumerate(slots) if mask >> n & 1}
            payment = sum(1 for j, i in S if j == 1)
            require(payment >= value(c, S), 'source primal cover')
    return dict(height_coalition_value=str(worth), height_payment=str(paid),
                rejected_source_equalities=5)


def order_tail_checks():
    # Exact binomial tail used in the random-order theorem. The asymptotic and
    # exponential bound remain conventional proofs, not finite-test conclusions.
    for lam in range(1, 9):
        L, g, n = 2 * lam, 8 * lam, 32 * lam * lam
        tail = Q(comb(n // g, L), comb(n, L))
        require(tail >= Q(1, (16 * lam) ** (2 * lam)), 'order tail')
    return 8


def main():
    results = []
    for k, r in ((2, 2), (8, 2), (3, 3), (16, 4), (216, 3), (5, 8)):
        rows = certificate(k, r)
        results.append(dict(k=k, r=r, rows=len(rows), factor=verify_certificate(k, r, rows)))
    report = dict(status='PASS', source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  proportional_certificates=results, corruptions_rejected=mutation_checks(),
                  finite_family_escape=escape_checks(), labeled_escape=labeled_escape_checks(),
                  rejected_claims=failed_constructions(),
                  random_order_binomial_checks=order_tail_checks(),
                  scope='Finite exact checks; neither an unrestricted lower bound nor an all-profile construction.')
    Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
