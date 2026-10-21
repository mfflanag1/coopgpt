#!/usr/bin/env python3
"""Exact algebra checks for heterogeneous union/veto funding certificates."""
from fractions import Fraction as F
import json


def certificate(rho, payments, masses, c, t):
    n = len(payments)
    assert len(masses) == n and c > 0 and t >= 1
    assert all(0 < mass <= rho for mass in masses)
    assert all(0 <= payment <= mass for payment, mass in zip(payments, masses))
    theta = [payment / mass for payment, mass in zip(payments, masses)]
    h = rho * sum(x * x for x in theta)
    j_squared = rho * sum(theta) ** 2 / n
    assert j_squared <= h
    x = c * t / rho
    blocks = max(1, x.numerator // x.denominator)
    owners = blocks * t * n + 1
    b = blocks * rho / t
    veto = b / (1 + b)
    final_payments = []
    for payment, mass, normalized in zip(payments, masses, theta):
        d = rho / mass - 1
        product_payment = rho * payment / (rho + (t - 1) * mass)
        product_mass = rho * mass / (rho + (t - 1) * mass)
        assert product_payment == rho * normalized / (t + d)
        assert product_mass == rho / (t + d) <= rho / t
        denominator = 1 + (blocks - 1) * rho / t + product_mass
        assert denominator == 1 + b - rho * d / (t * (t + d))
        scale = 1 / denominator
        assert scale * ((blocks - 1) * rho / t + product_mass) == 1 - scale
        final_payments.append(scale * product_payment)
    funding = veto + blocks * t * sum(final_payments)
    diagonal = veto * veto + blocks * t * sum(x * x for x in final_payments)
    funding_limit_squared = c * j_squared / (1 + c) ** 2
    diagonal_limit = (c * c + c * h) / (1 + c) ** 2
    return dict(H=h, J_squared=j_squared, N=owners,
                funding_squared=funding * funding / owners,
                diagonal=diagonal,
                funding_limit_squared=funding_limit_squared,
                diagonal_limit=diagonal_limit)


def main():
    rho = F(13, 36)
    compact_p = [F(5, 18)] + [F(1, 6)] * 12
    compact_l = [F(31, 108)] + [rho] * 12
    cube_tau = F(64, 9) + F(152 * 152, 247)
    cases = [
        ('identity_with_fractional_rhs', F(2), [F(1), F(1, 2)], [F(2), F(3, 2)]),
        ('compact_pointwise', rho, compact_p, compact_l),
        ('compact_plus_39_unused_owners', rho, compact_p + [F(0)] * 39, compact_l + [rho] * 39),
        ('hypercube_d8', F(1, 100), [F(8, 9) / cube_tau] * 256, [1 / cube_tau] * 256),
    ]
    checked = 0
    outputs = {}
    for name, rho, payments, masses in cases:
        for c in (F(1, 3), F(1), F(2), F(5)):
            for t in (1, 2, 10, 100, 10000, 1000000):
                result = certificate(rho, payments, masses, c, t)
                checked += 1
                if t == 1000000:
                    assert abs(result['funding_squared'] - result['funding_limit_squared']) < F(1, 10000)
                    assert abs(result['diagonal'] - result['diagonal_limit']) < F(1, 10000)
        outputs[name] = certificate(rho, payments, masses, F(1), 1000000)
    assert outputs['compact_plus_39_unused_owners']['H'] == outputs['compact_pointwise']['H']
    assert outputs['compact_plus_39_unused_owners']['J_squared'] == outputs['compact_pointwise']['J_squared'] / 4
    cube = outputs['hypercube_d8']
    assert cube['H'] == cube['J_squared'] == F(4096, 2025)
    optimal_c = cube['H'] / (cube['H'] - 2)
    finite_diagonal = certificate(cases[-1][1], cases[-1][2], cases[-1][3], optimal_c, 1000000)
    assert finite_diagonal['diagonal'] > 1
    optimization_checks = 0
    for h in (F(0), F(1), F(2), F(5, 2), F(4), F(5)):
        for c in (F(1, 3), F(1), F(2), F(7)):
            diagonal = (c * c + c * h) / (1 + c) ** 2
            assert diagonal - 1 == (c * (h - 2) - 1) / (1 + c) ** 2
            if h > 2:
                maximum = h * h / (4 * (h - 1))
                assert maximum - diagonal == (h - (h - 2) * c) ** 2 / (4 * (h - 1) * (1 + c) ** 2)
            else:
                assert diagonal < 1
            # j_squared=3 is only a scalar identity check, not a claimed base.
            j_squared = F(3)
            assert j_squared / 4 - c * j_squared / (1 + c) ** 2 == j_squared * (c - 1) ** 2 / (4 * (1 + c) ** 2)
            optimization_checks += 1
    print(json.dumps({'verified': True, 'finite_product_cases': checked,
                      'optimization_identity_cases': optimization_checks,
                      'valid_base_padding_H_unchanged': True,
                      'valid_base_padding_J_squared_factor': '1/4',
                      'funding_gate_without_roots': 'rho*(sum theta_i)^2 > 4n',
                      'scope': 'Selected-certificate limits; no arbitrary-base true-envelope upper bound.',
                      'recommended_scope_clarification': 'J<=2 blocks the strict asymptotic criterion, not every finite amplification by the limit argument alone.'}, indent=2))


if __name__ == '__main__':
    main()
