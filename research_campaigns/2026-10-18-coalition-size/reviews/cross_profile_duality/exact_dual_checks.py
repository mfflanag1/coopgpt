#!/usr/bin/env python3
"""Exact contract/dual calibration and a deliberately invalid uncoupled-flow test."""
from collections import defaultdict
from fractions import Fraction as Q
from itertools import product, combinations
from pathlib import Path
import hashlib
import json


def require(test, message):
    if not test:
        raise RuntimeError(message)


def sum_bundles(bundles, dimension):
    return tuple(sum(b[v] for b in bundles) for v in range(dimension))


def mixed_owner_check():
    bundles = list(product((0, 1), repeat=3))
    profiles = list(product(bundles, repeat=2))
    value = lambda b: min(b)
    payments = {}
    coverage = budgets = transitions = mixed_restorations = unchanged_member = 0
    for p in profiles:
        total = value(sum_bundles(p, 3))
        payments[p] = (Q(total+value(p[0])-value(p[1]), 2),
                       Q(total+value(p[1])-value(p[0]), 2))
        require(all(y >= 0 for y in payments[p]), 'negative two-owner core payment')
        require(sum(payments[p]) == total, 'two-owner inefficiency')
        budgets += 1
        for C in ((0,), (1,), (0, 1)):
            require(sum(payments[p][i] for i in C) >= value(sum_bundles([p[i] for i in C], 3)),
                    'mixed owner coverage')
            coverage += 1
    for high in profiles:
        for low in profiles:
            for C in ((0,), (1,), (0, 1)):
                if any(high[i] != low[i] for i in range(2) if i not in C):
                    continue
                if any(high[i][v] < low[i][v] for i in C for v in range(3)):
                    continue
                delta = [tuple(high[i][v]-low[i][v] for v in range(3)) for i in C]
                outside = value(sum_bundles(delta, 3))
                loss = sum(payments[high][i]-payments[low][i] for i in C)
                require(loss >= outside, 'mixed-owner full OUT')
                transitions += 1
                mixed_restorations += any(sum(d) >= 2 for d in delta)
                unchanged_member += len(C) == 2 and any(high[i] == low[i] for i in C) and high != low
    return {'profiles': len(profiles), 'coverage_rows': coverage, 'budgets': budgets,
            'admissible_full_out_rows': transitions, 'mixed_coordinate_restoration_rows': mixed_restorations,
            'rows_with_unchanged_protected_member': unchanged_member}


def portfolio_certificate():
    source = Path(__file__).resolve().parents[1] / 'three_portfolio_certificate.json'
    data = json.loads(source.read_text())
    bundles = {'L': (1, 0), 'R': (0, 1), '0': (0, 0)}
    worth = lambda p, C: min(sum_bundles([bundles[p[i]] for i in C], 2))
    g = defaultdict(Q)
    numerator = Q(0)
    cover_resources = [Q(0), Q(0)]
    restoration_resources = [Q(0), Q(0)]
    coverage_count = transition_count = 0
    high_profiles = set()
    for row in data['rows']:
        if row['kind'] == 'low_zero_owner_nonnegative':
            continue
        weight = Q(row['weight'])
        terms = [(tuple(t['profile']), t['owner'], Q(t['coefficient'])) for t in row['terms']]
        for p, i, coeff in terms:
            g[p, i] += weight*coeff
        if row['kind'] in ('high_unlike_pair_coverage', 'low_grand_coverage'):
            p = terms[0][0]
            require(all(x[0] == p and x[2] == 1 for x in terms), 'coverage shape')
            C = [x[1] for x in terms]
            require(worth(p, C) == Q(row['rhs']), 'coverage RHS')
            numerator += weight*worth(p, C)
            for v in range(2):
                cover_resources[v] += weight*sum(bundles[p[i]][v] for i in C)
            coverage_count += 1
        else:
            require(row['kind'] == 'pair_tcwm_restore_zero_to_incumbent_type', 'unknown row')
            positive = [(p, i) for p, i, coeff in terms if coeff == 1]
            negative = [(p, i) for p, i, coeff in terms if coeff == -1]
            high, low = positive[0][0], negative[0][0]
            C = {i for p, i in positive}
            require(len(C) == 2 and C == {i for p, i in negative}, 'coalition multiplier coupling')
            require(all(p == high for p, i in positive) and all(p == low for p, i in negative), 'endpoint shape')
            require(all(high[i] == low[i] for i in range(3) if i not in C), 'changed outside coalition')
            require(all(bundles[high[i]][v] >= bundles[low[i]][v] for i in C for v in range(2)),
                    'not a binding restoration')
            high_profiles.add(high)
            for v in range(2):
                restoration_resources[v] += weight*sum(bundles[high[i]][v]-bundles[low[i]][v] for i in C)
            transition_count += 1
    nu = {p: Q(1) for p in high_profiles}
    profiles = {p for p, i in g} | set(nu)
    slack = {(p, i): nu.get(p, 0)-g[p, i] for p in profiles for i in range(3)}
    require(all(v >= 0 for v in slack.values()), 'dual node imbalance')
    denominator = sum(weight*worth(p, range(3)) for p, weight in nu.items())
    budget_resources = [sum(weight*sum(bundles[p[i]][v] for i in range(3)) for p, weight in nu.items())
                        for v in range(2)]
    slack_resources = [sum(value*bundles[p[i]][v] for (p, i), value in slack.items()) for v in range(2)]
    require(all(budget_resources[v]-restoration_resources[v] == cover_resources[v]+slack_resources[v]
                for v in range(2)), 'resource-conservation identity')
    require(numerator == Q(15, 2) and denominator == 6 and numerator/denominator == Q(5, 4),
            'incorrect unrestricted certificate')
    return {'coverage_rows': coverage_count, 'coupled_transition_rows': transition_count,
            'budget_rows': len(nu), 'numerator': str(numerator), 'denominator': str(denominator),
            'lower': str(numerator/denominator), 'positive_node_slacks': sum(value > 0 for value in slack.values()),
            'budget_resources': list(map(str, budget_resources)),
            'restoration_resources': list(map(str, restoration_resources)),
            'net_resources': [str(budget_resources[v]-restoration_resources[v]) for v in range(2)],
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}


def invalid_uncoupled_flow(N=8):
    fake = defaultdict(Q)
    actual = defaultdict(Q)
    nu = {}
    count = 0
    for short in range(N):
        for long_type, short_type in (('A', 'B'), ('B', 'A')):
            p = tuple(short_type if i == short else long_type for i in range(N))
            nu[p] = Q(1)
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            low = tuple('A' if k == i else 'B' if k == j else '0' for k in range(N))
            for k in (i, j):
                fake[low, k] += 1
                actual[low, k] += 1
            for payload, restore_type in ((i, 'A'), (j, 'B')):
                before = low
                for restoring in range(N):
                    if restoring in (i, j):
                        continue
                    after = list(before)
                    after[restoring] = restore_type
                    after = tuple(after)
                    fake[after, payload] += 1
                    fake[before, payload] -= 1
                    for member in (payload, restoring):
                        actual[after, member] += 1
                        actual[before, member] -= 1
                    before = after
                    count += 1
    require(all(value <= nu.get(p, 0) for (p, i), value in fake.items()), 'fake relaxed certificate miscomputed')
    violations = [(p, i, value-nu.get(p, 0)) for (p, i), value in actual.items() if value > nu.get(p, 0)]
    require(len(violations) > 0, 'uncoupling unexpectedly preserved actual dual feasibility')
    return {'WARNING': 'This is deliberately NOT a valid contract certificate.',
            'owners': N, 'false_relaxation_lower': str(Q(N-1, 2)),
            'false_owner_only_transition_rows': count, 'budget_profiles': len(nu),
            'actual_coupled_balance_violations': len(violations),
            'interpretation': 'Removing the restoring-owner terms from protected pair rows invents an unbounded lower even for min2.'}


def projective_resource_calibration():
    source = Path(__file__).resolve().parents[1] / 'projective_bounded_tail_audit_check.json'
    data = json.loads(source.read_text())
    cert = data['full_s6_M6_certificate']
    lower = Q(cert['lower'])
    mu = sum(Q(row['weight']) for row in cert['rows'] if row['kind'] == 'tcwm')
    # Under the full finite symmetry average, each restoration is one resource
    # unit, budget mass is1, and all nonnegative slack rows have zero reports.
    require(Q(13)-mu == 3*lower, 'projective net-resource identity')
    per_row = (Q(13)-mu)/127
    require(127*per_row/3 == lower, 'uniform projective production')
    return {'scope': 'compressed exact certificate plus analytically justified finite group average; group not enumerated',
            'budget_mass': '1', 'budget_total_resource': '13', 'restoration_total_resource': str(mu),
            'net_resource_per_row': str(per_row), 'F_net_resources': str(lower),
            'dual_objective': str(lower), 'resource_bound_is_tight': True,
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}


def truncated_coverage_counterexample(M=4):
    n = 1+2*M
    worth = lambda S: sum({0, 1+2*j, 2+2*j} <= set(S) for j in range(M))
    checked = 0
    for size in range(1, 4):
        for S in combinations(range(n), size):
            require(int(0 in S) >= worth(S), 'small coverage counterexample wrong')
            checked += 1
    require(worth(range(n)) == M > 1, 'grand value')
    return {'arity': 3, 'owners': n, 'resource_rows': 3*M, 'activities': M,
            'all_size_at_most3_coverage_rows_checked': checked,
            'candidate_total_payment': 1, 'grand_coalition_value': M,
            'scope': 'static counterexample to dropping large-coalition coverage rows, not a proposed global mechanism'}


def main():
    output = {'status': 'PASS', 'mixed_owner_min3': mixed_owner_check(),
              'actual_min2_farkas_certificate': portfolio_certificate(),
              'invalid_relaxation_diagnostic': invalid_uncoupled_flow(),
              'projective_resource_calibration': projective_resource_calibration(),
              'truncated_coverage_counterexample': truncated_coverage_counterexample(),
              'net_resource_bound_counterexample': {'technology': 'min(A,B)',
                  'profiles': [[1000, 1], [1, 1000]], 'one_owner': True,
                  'lambda_grand_each': 1, 'nu_each': 1, 'mu': 0,
                  'actual_dual_ratio': '1', 'net_resource_bound_ratio': '1001/2'},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(__file__).with_suffix('.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
