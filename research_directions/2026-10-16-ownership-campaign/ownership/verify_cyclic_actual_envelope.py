#!/usr/bin/env python3
"""Exact scalar/constant replay for the analytic all-report-box proof."""
from fractions import Fraction as Q
import json


def require(test, message):
    if not test:
        raise ValueError(message)


def poly(x, degree):
    term = total = Q(1)
    for j in range(1, degree + 1):
        term *= -x / j
        total += term
    return total


def outward(lo, hi):
    scale = 10**15
    return Q(lo.numerator * scale // lo.denominator, scale), Q(-(-hi.numerator * scale // hi.denominator), scale)


def main():
    r, s, c = Q(19, 10), Q(83, 40), Q(9, 10)
    ql, qu = outward(poly(c, 25) / 2, poly(c, 24) / 2)
    zl, zu = 1 + c * ql, 1 + c * qu
    bl = 1 - qu
    require(s < 3 * bl, 'all-n uncapped condition failed')
    require(qu < Q(5, 24), 'local q ceiling failed')
    require(Q(4853, 2000) > Q(12, 5), 'positive exponential lower polynomial failed')
    require(Q(461, 960) < Q(1, 2), 'local derivative gap failed')
    require(zu < Q(19, 16), 'local total bound failed')
    require(s / zu > Q(166, 95) > Q(3, 2), 'outer u lower bound failed')
    require(Q(8, 3) > Q(8, 5)**2, 'sqrt(e) comparison failed')
    require(Q(1, 2) - Q(5, 7) * Q(15, 22) == Q(1, 77), 'whole-box derivative margin failed')
    require(Q(2, 3) * Q(19, 16) + s / 3 == Q(89, 60) < Q(3, 2), 'final rational upper bound failed')
    q0l, q0u = poly(s / zl - 1, 25) / 2, poly(s / zu - 1, 24) / 2
    el = zl + (s - zu) * q0l
    eu = zu + (s - zl) * q0u
    require(eu < Q(89, 60), 'exact scalar envelope exceeds analytic bound')
    lo, hi = outward(el, eu)
    print(json.dumps({'status': 'PASS', 'arithmetic': 'exact Fraction/integer',
                      'scope': 'scalar and constant replay; continuous whole-box theorem is in the proof',
                      'n_scope': 'all integers n>=3', 'q_interval': [str(ql), str(qu)],
                      'actual_envelope_ratio_interval': [str(lo), str(hi)],
                      'uniform_rational_upper_bound': '89/60',
                      'whole_box_derivative_bracket_margin': '1/77'}, indent=2))


if __name__ == '__main__':
    main()
