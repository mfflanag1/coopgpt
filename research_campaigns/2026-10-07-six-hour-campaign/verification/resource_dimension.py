#!/usr/bin/env python3
"""Exact finite support for the resource-dimension fallback and refinements.

Standard library only; every check remains active under python -O. No files are
read or written. The exhaustive grid has three owners, two resource coordinates,
and every bundle entry in {0, 1, 2}. These finite checks do not prove universal or
asymptotic claims, and do not reverify the imported weighted-glove lower theorem.
"""
from fractions import Fraction as Q
from itertools import product
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def checked(counts, key, condition, context):
    require(condition, key + ': ' + context)
    counts[key] = counts.get(key, 0) + 1


def ratio(numerator, denominator):
    require(denominator >= 0, 'negative normalization denominator')
    if denominator == 0:
        require(numerator == 0, 'nonzero numerator at zero denominator')
        return Q(0)
    return Q(numerator) / Q(denominator)


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q(0))


def aggregate(profile):
    return tuple(sum(owner[e] for owner in profile) for e in range(len(profile[0])))


def value(technology, resources):
    name, forms = technology
    if forms is None:
        require(name == 'max', 'unknown non-min-linear technology')
        return Q(max(resources))
    return min(dot(w, resources) for w in forms)


def state(technology, profile):
    c = aggregate(profile)
    T = value(technology, c)
    rho = tuple(max(ratio(owner[e], c[e]) for e in range(len(c))) for owner in profile)
    result = dict(c=c, T=T, rho=rho, P=tuple(T * r for r in rho))
    forms = technology[1]
    if forms is not None:
        theta = tuple(max(ratio(dot(w, owner), dot(w, c)) for w in forms)
                      for owner in profile)
        marginal = tuple(T - value(technology, tuple(ce - be for ce, be in zip(c, owner)))
                         for owner in profile)
        optimum = min(forms, key=lambda w: dot(w, c))
        result.update(theta=theta, M=marginal, Q=tuple(T * t for t in theta),
                      core=tuple(dot(optimum, owner) for owner in profile))
    return result


def coalition_values(technology, profile):
    n = len(profile)
    d = len(profile[0])
    return tuple(value(technology, tuple(sum(profile[i][e] for i in range(n) if mask >> i & 1)
                                        for e in range(d))) for mask in range(1 << n))


def validate_payments(payments, profile, T, worths, counts, context):
    c = aggregate(profile)
    active = sum(ce > 0 for ce in c)
    for payment in payments:
        checked(counts, 'individual_nonnegativity', payment >= 0, context)
    checked(counts, 'dimension_budget', sum(payments) <= min(len(profile), active) * T, context)
    for mask, worth in enumerate(worths):
        paid = sum(payments[i] for i in range(len(profile)) if mask >> i & 1)
        checked(counts, 'coalition_coverage', paid >= worth, context + ', coalition=' + str(mask))


TECHNOLOGIES = (
    ('max', None),
    ('sum', ((1, 1),)),
    ('min', ((1, 0), (0, 1))),
    ('mixed_min', ((2, 1), (1, 3))),
)
PROFILES = tuple(tuple((flat[2 * i], flat[2 * i + 1]) for i in range(3))
                 for flat in product(range(3), repeat=6))


def grid_checks():
    counts = dict(profiles=len(PROFILES), technology_profiles=0, rule_profiles=0,
                  zero_aggregate_profiles=0, profiles_with_zero_aggregate_coordinate=0,
                  zero_value_technology_profiles=0, unilateral_coordinate_transitions=0)
    per_rule = {rule: {} for rule in ('P', 'M', 'Q')}
    refinement = {}
    boundaries = {}
    for profile in PROFILES:
        c = aggregate(profile)
        counts['zero_aggregate_profiles'] += int(not any(c))
        counts['profiles_with_zero_aggregate_coordinate'] += int(any(ce == 0 for ce in c))
    for technology in TECHNOLOGIES:
        cache = {profile: state(technology, profile) for profile in PROFILES}
        for profile in PROFILES:
            current = cache[profile]
            c, T, rho = current['c'], current['T'], current['rho']
            context = technology[0] + ' ' + str(profile)
            worths = coalition_values(technology, profile)
            counts['technology_profiles'] += 1
            checked(boundaries, 'empty_coalition_value', worths[0] == 0, context)
            for e, ce in enumerate(c):
                if ce == 0:
                    checked(boundaries, 'zero_coordinate_normalization',
                            all(owner[e] == 0 and ratio(owner[e], ce) == 0 for owner in profile), context)
            if not any(c):
                checked(boundaries, 'zero_aggregate_shares', rho == (Q(0),) * 3, context)
            active = sum(ce > 0 for ce in c)
            checked(refinement, 'share_dimension_bound', sum(rho) <= min(3, active), context)
            for mask in range(8):
                share = sum(rho[i] for i in range(3) if mask >> i & 1)
                for e in range(2):
                    actual = sum(profile[i][e] for i in range(3) if mask >> i & 1)
                    checked(refinement, 'coalition_resource_domination', actual <= share * c[e], context)
            rules = ('P',) if technology[1] is None else ('P', 'M', 'Q')
            for rule in rules:
                validate_payments(current[rule], profile, T, worths, per_rule[rule], context)
                counts['rule_profiles'] += 1
            if T == 0:
                counts['zero_value_technology_profiles'] += 1
                checked(boundaries, 'zero_value_coalitions', all(worth == 0 for worth in worths), context)
                for rule in rules:
                    checked(boundaries, 'zero_value_payments', all(p == 0 for p in current[rule]), context)
            if technology[1] is not None:
                checked(refinement, 'core_efficiency', sum(current['core']) == T, context)
                for mask, worth in enumerate(worths):
                    checked(refinement, 'optimal_form_core_coverage',
                            sum(current['core'][i] for i in range(3) if mask >> i & 1) >= worth, context)
                for i in range(3):
                    checked(refinement, 'marginal_dominates_core', current['M'][i] >= current['core'][i], context)
                    checked(refinement, 'marginal_below_fallback', current['M'][i] <= current['P'][i], context)
                    checked(refinement, 'dual_share_below_coordinate_share', current['theta'][i] <= rho[i], context)
                    checked(refinement, 'dual_payment_below_fallback', current['Q'][i] <= current['P'][i], context)
                if technology[0] == 'sum':
                    checked(refinement, 'single_form_efficiency', sum(current['Q']) == T, context)
            for i in range(3):
                for e in range(2):
                    for increase in range(profile[i][e] + 1, 3):
                        changed = list(profile)
                        own = list(profile[i])
                        own[e] = increase
                        changed[i] = tuple(own)
                        later = cache[tuple(changed)]
                        counts['unilateral_coordinate_transitions'] += 1
                        transition = context + ', owner=' + str(i) + ', coordinate=' + str(e)
                        for rule in rules:
                            checked(per_rule[rule], 'own_coordinate_monotonicity',
                                    current[rule][i] <= later[rule][i], transition)
                            if profile[i][e] == 0:
                                checked(boundaries, 'own_monotonicity_from_zero',
                                        current[rule][i] <= later[rule][i], transition + ', rule=' + rule)
    require(counts['profiles'] == 729 and counts['technology_profiles'] == 4 * 729,
            'exhaustive profile grid is incomplete')
    require(counts['unilateral_coordinate_transitions'] == 4 * 6 * 3 * 3**5,
            'not every strictly increasing coordinate pair was checked')
    return dict(counts=counts, payment_rules=per_rule, refinements=refinement, zero_boundaries=boundaries)


def cone_checks():
    # Includes one-generator efficiency and two distinct two-generator cones.
    cases = (
        (((1, 1),), ((1,), (2,), (3,))),
        (((2, 1), (1, 3)), ((1, 0), (0, 1), (1, 1), (2, 1))),
        (((1, 0), (0, 1)), ((2, 1), (1, 3))),
    )
    counts = {}
    for generators, coefficients in cases:
        forms = tuple(tuple(sum(coef[j] * generators[j][e] for j in range(len(generators)))
                            for e in range(2)) for coef in coefficients)
        technology = ('cone_min', forms)
        for profile in PROFILES:
            current = state(technology, profile)
            c = current['c']
            projected = tuple(max(ratio(dot(a, owner), dot(a, c)) for a in generators)
                              for owner in profile)
            context = str((generators, coefficients, profile))
            for i in range(3):
                checked(counts, 'dual_share_below_generator_share', current['theta'][i] <= projected[i], context)
                checked(counts, 'generator_share_below_coordinate_share', projected[i] <= current['rho'][i], context)
            checked(counts, 'generator_count_share_bound', sum(projected) <= len(generators), context)
            checked(counts, 'generator_count_payment_bound',
                    sum(current['Q']) <= len(generators) * current['T'], context)
    return dict(cones=len(cases), profiles_per_cone=len(PROFILES), checks=counts)


def dimension_witnesses():
    rows = []
    counts = {}
    for d in range(1, 21):
        basis = tuple(tuple(int(i == e) for e in range(d)) for i in range(d))
        maximum = ('max', None)
        initial = state(maximum, basis)
        checked(counts, 'unit_basis_grand_value', initial['T'] == 1, str(d))
        checked(counts, 'unit_basis_singleton_requirements',
                all(value(maximum, owner) == 1 for owner in basis), str(d))
        checked(counts, 'unit_basis_fallback_cost', sum(initial['P']) == d, str(d))
        epsilon = Q(1, d * d)
        positive = tuple(tuple(Q(1) if i == e else epsilon for e in range(d)) for i in range(d))
        perturbed = state(maximum, positive)
        T = 1 + (d - 1) * epsilon
        checked(counts, 'strictly_positive_reports', all(x > 0 for owner in positive for x in owner), str(d))
        checked(counts, 'positive_grand_value', perturbed['T'] == T, str(d))
        checked(counts, 'positive_singleton_requirements',
                all(value(maximum, owner) == 1 for owner in positive), str(d))
        checked(counts, 'positive_fallback_cost', sum(perturbed['P']) == d, str(d))
        checked(counts, 'positive_required_factor', Q(d) / T >= d - 1, str(d))
        linear = state(('linear', ((1,) * d,)), basis)
        checked(counts, 'linear_fallback_method_cost', sum(linear['P']) == d * linear['T'], str(d))
        checked(counts, 'linear_dual_share_efficiency', sum(linear['Q']) == linear['T'] == d, str(d))
        leontief = state(('leontief', basis), basis)
        checked(counts, 'leontief_marginal_method_cost', sum(leontief['M']) == d * leontief['T'] == d, str(d))
        rows.append(dict(d=d, epsilon=str(epsilon), nonconcave_required_factor=str(Q(d) / T)))
    return dict(dimensions=len(rows), checks=counts, rows=rows)


def reject_mutation(name, expected_label, operation, witness):
    try:
        operation()
    except AssertionError as exc:
        require(str(exc).startswith(expected_label + ':'),
                'Mutation failed for an unintended reason: ' + name + ': ' + str(exc))
        return dict(name=name, status='REJECTED', violated_check=expected_label, witness=witness)
    raise AssertionError('Substantive mutation was accepted: ' + name)


def mutation_controls():
    results = []
    profile = ((2, 0), (0, 2), (0, 0))
    technology = TECHNOLOGIES[1]
    current = state(technology, profile)
    worths = coalition_values(technology, profile)
    validate_payments(current['P'], profile, current['T'], worths, {}, 'positive control')
    results.append(reject_mutation('omit_T_multiplier', 'coalition_coverage',
        lambda: validate_payments(current['rho'], profile, current['T'], worths, {}, 'mutation'),
        dict(profile=profile, technology='sum', mutated_payments=list(map(str, current['rho'])))))

    profile = ((1, 1), (1, 1), (1, 1))
    technology = TECHNOLOGIES[0]
    current = state(technology, profile)
    worths = coalition_values(technology, profile)
    bad = tuple(current['T'] * max(ratio(x, x) for x in owner) for owner in profile)
    validate_payments(current['P'], profile, current['T'], worths, {}, 'positive control')
    results.append(reject_mutation('normalize_by_own_bundle_only', 'dimension_budget',
        lambda: validate_payments(bad, profile, current['T'], worths, {}, 'mutation'),
        dict(profile=profile, technology='max', mutated_payments=list(map(str, bad)))))

    profile = ((1, 0), (0, 1), (0, 0))
    technology = TECHNOLOGIES[2]
    current = state(technology, profile)
    worths = coalition_values(technology, profile)
    bad = tuple(current['T'] * min(ratio(dot(w, owner), dot(w, current['c']))
                                   for w in technology[1]) for owner in profile)
    validate_payments(current['Q'], profile, current['T'], worths, {}, 'positive control')
    results.append(reject_mutation('minimum_instead_of_maximum_dual_share', 'coalition_coverage',
        lambda: validate_payments(bad, profile, current['T'], worths, {}, 'mutation'),
        dict(profile=profile, technology='min', mutated_payments=list(map(str, bad)))))

    low = ((1, 0), (0, 1), (0, 0))
    high = ((2, 0), (0, 1), (0, 0))
    before, after = state(technology, low), state(technology, high)
    require(before['Q'][0] <= after['Q'][0], 'dual-share monotonicity positive control failed')
    for profile, current in ((low, before), (high, after)):
        validate_payments(current['core'], profile, current['T'],
                          coalition_values(technology, profile), {}, 'selected-core positive control')
    results.append(reject_mutation('use_selected_optimal_core_instead_of_dual_share',
        'own_coordinate_monotonicity',
        lambda: checked({}, 'own_coordinate_monotonicity', before['core'][0] <= after['core'][0], 'mutation'),
        dict(low_profile=low, high_profile=high, technology='min', owner=0,
             selected_core_before=str(before['core'][0]), selected_core_after=str(after['core'][0]))))
    require(len(results) >= 3, 'missing substantive mutation controls')
    return results


def run():
    grid = grid_checks()
    comparisons = sum(row['coalition_coverage'] + row['own_coordinate_monotonicity']
                      for row in grid['payment_rules'].values())
    return dict(status='PASS', arithmetic='fractions.Fraction; no floating-point comparisons',
                grid=grid, grid_coalition_and_incentive_comparisons=comparisons,
                nonnegative_cone_refinement=cone_checks(), dimension_witnesses=dimension_witnesses(),
                mutation_controls=mutation_controls(),
                scope='Exact finite support only. No universal/asymptotic proof claim and no replay of the imported weighted-glove lower theorem.',
                count_note='Recomputed counts include empty coalitions, every 0-to-2 jump, and separate P/M/Q inequalities; they do not reproduce the historical 87,480 count.')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
