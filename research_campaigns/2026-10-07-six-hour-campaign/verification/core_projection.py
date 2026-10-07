#!/usr/bin/env python3
"""Exact four-owner full-core projection diagnostic; standard library only.

The LP/KKT oracles are tailored to the two listed reports and their coalitions;
they are not general optimization solvers. Every returned optimum has a checked
certificate. Counts below are incremented only by actual successful checks.
"""
from fractions import Fraction as Q
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


EDGES = ((0, 2), (0, 3), (1, 2), (1, 3))
LOW = (Q(1, 2), Q(1), Q(1), Q(1))
HIGH = (Q(1, 2), Q(1), Q(2), Q(1))
COUNTS = dict(linear_coalition_LP_certificates=0,
              concave_coalition_KKT_certificates=0,
              full_core_coalition_checks=0, projection_KKT_certificates=0)


def utility(t):
    return 10 * t / (10 + t)


def derivative(t):
    return Q(100) / (10 + t)**2


def loads(flow):
    return tuple(sum(flow[k] for k, edge in enumerate(EDGES) if i in edge) for i in range(4))


def linear_certificate(c):
    remaining = list(c)
    flow = []
    for i, j in EDGES:
        z = min(remaining[i], remaining[j])
        flow.append(z)
        remaining[i] -= z
        remaining[j] -= z
    prices = (1, 1, 0, 0) if c[0] + c[1] <= c[2] + c[3] else (0, 0, 1, 1)
    require(all(z >= 0 for z in flow), 'LP primal nonnegativity')
    require(all(use <= cap for use, cap in zip(loads(flow), c)), 'LP primal resources')
    require(all(prices[i] + prices[j] >= 1 for i, j in EDGES), 'LP dual activity')
    optimum = sum(flow)
    require(optimum == sum(price * cap for price, cap in zip(prices, c)), 'LP primal/dual gap')
    require(optimum == min(c[0] + c[1], c[2] + c[3]), 'two-pool formula')
    COUNTS["linear_coalition_LP_certificates"] += 1
    return optimum


def concave_certificate(c):
    A = [i for i in (0, 1) if c[i] > 0]
    B = [j for j in (2, 3) if c[j] > 0]
    flows = {edge: Q(0) for edge in EDGES}
    prices = [Q(0) if cap else Q(1) for cap in c]
    if A and len(B) == 2:
        for i in A:
            prices[i] = derivative(c[i] / 2)
            for j in B:
                flows[i, j] = c[i] / 2
    elif A and len(B) == 1:
        j = B[0]
        if sum(c[i] for i in A) <= c[j]:
            for i in A:
                flows[i, j] = c[i]
                prices[i] = derivative(c[i])
        else:
            require(A == [0, 1] and c[j] == 1, 'unexpected bottleneck case')
            prices[j] = derivative(Q(1, 2))
            for i in A:
                flows[i, j] = Q(1, 2)
    flow = tuple(flows[edge] for edge in EDGES)
    use = loads(flow)
    require(all(z >= 0 for z in flow), 'utility primal nonnegativity')
    require(all(u <= cap for u, cap in zip(use, c)), 'utility primal resources')
    require(all(price >= 0 for price in prices), 'utility multiplier nonnegativity')
    require(all(price * (cap - u) == 0 for price, cap, u in zip(prices, c, use)),
            'utility resource complementarity')
    for z, (i, j) in zip(flow, EDGES):
        reduced = prices[i] + prices[j] - derivative(z)
        require(reduced >= 0 and z * reduced == 0, 'utility activity KKT')
    COUNTS["concave_coalition_KKT_certificates"] += 1
    return sum(utility(z) for z in flow)


def worths(c, oracle):
    return tuple(oracle(tuple(cap if mask >> i & 1 else Q(0) for i, cap in enumerate(c)))
                 for mask in range(16))


def marginal(values):
    return tuple(values[15] - values[15 ^ (1 << i)] for i in range(4))


def core(x, values):
    require(sum(x) == values[15], 'core efficiency')
    for mask, value in enumerate(values):
        require(sum(x[i] for i in range(4) if mask >> i & 1) >= value, 'core coalition ' + str(mask))
        COUNTS["full_core_coalition_checks"] += 1


def projection_kkt(x, center, values, lam, cover_multipliers):
    core(x, values)
    for mask, mu in cover_multipliers.items():
        require(mu >= 0, 'projection nonnegative multiplier')
        require(mu * (values[mask] - sum(x[i] for i in range(4) if mask >> i & 1)) == 0,
                'projection complementarity')
    for i in range(4):
        require(x[i] - center[i] + lam
                - sum(mu for mask, mu in cover_multipliers.items() if mask >> i & 1) == 0,
                'projection stationarity')
    COUNTS["projection_KKT_certificates"] += 1


def run():
    for key in COUNTS:
        COUNTS[key] = 0
    vl, vh = worths(LOW, linear_certificate), worths(HIGH, linear_certificate)
    ul, uh = marginal(vl), marginal(vh)
    xl = (Q(1, 4), Q(3, 4), Q(1, 4), Q(1, 4))
    xh = (Q(1, 2), Q(1), Q(0), Q(0))
    require(ul == (Q(1, 2), Q(1), Q(1, 2), Q(1, 2)), 'linear low marginal')
    require(uh == (Q(1, 2), Q(1), Q(1, 2), Q(0)), 'linear high marginal')
    projection_kkt(xl, ul, vl, Q(1, 4), {})
    projection_kkt(xh, uh, vh, Q(1), {7: Q(1, 2), 9: Q(1, 2), 10: Q(1, 2)})
    require(vh[7] == vh[15] == vh[9] + vh[10], 'linear singleton-core forcing identities')
    require(xl[2] > xh[2], 'linear own-payment decrease')

    vl, vh = worths(LOW, concave_certificate), worths(HIGH, concave_certificate)
    a, b = 2 * utility(Q(1, 4)), 2 * utility(Q(1, 2))
    T = a + b
    delta = T - utility(Q(1, 2)) - utility(Q(1))
    ul, uh = marginal(vl), marginal(vh)
    xl = (a / 2, b - a / 2, a / 2, a / 2)
    require(vl[15] == vh[15] == T == Q(1240, 861), 'utility grand values')
    require(ul == (a, b, a, a), 'utility low marginal')
    require(uh == (a, b, a, delta), 'utility high marginal')
    projection_kkt(xl, ul, vl, a / 2, {})
    core((a, b, Q(0), Q(0)), vh)
    require(T - vh[7] == delta == Q(520, 9471), 'high x3 bound')
    require(vh[9] + vh[10] == vh[7], 'high x2-minus-x3 bound')
    require(0 < 2 * delta < xl[2], 'strict nonlinear own-payment decrease')
    require(xl[2] - 2 * delta == Q(1270, 9471), 'exact nonlinear decrease bound')
    require([i for i in range(4) if LOW[i] != HIGH[i]] == [2] and LOW[2] < HIGH[2],
            'fixed-owner unilateral increasing report')
    return dict(status='PASS', **COUNTS, linear_low_projection=['1/4', '3/4', '1/4', '1/4'],
                linear_high_projection=['1/2', '1', '0', '0'],
                utility_low_projection=list(map(str, xl)), utility_high_owner2_upper=str(2 * delta),
                utility_strict_decrease_lower=str(xl[2] - 2 * delta),
                scope='Full original efficient-core projection only; high nonlinear projection coordinates are not claimed.')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
