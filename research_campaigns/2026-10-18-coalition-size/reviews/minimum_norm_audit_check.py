#!/usr/bin/env python3
"""Independent exact checks; no imports from the proposed root checker.

Enumerates actual subsets of named owners, not symmetry classes. For each
subset solves the two-activity packing LP by enumerating its feasible vertices.
Prints a compact report, writing nothing outside this owned review script.
"""
from fractions import Fraction as F
from itertools import combinations
import json


def packing_value(capacity):
    P, X1, Y1, X2, Y2 = capacity
    constraints = [((-1, 0), F(0)), ((0, -1), F(0)),
                   ((1, 1), P), ((1, 0), X1), ((1, 0), Y1),
                   ((0, 1), X2), ((0, 1), Y2)]
    best = F(0)
    for ((a, b), rhs1), ((c, d), rhs2) in combinations(constraints, 2):
        det = a*d-b*c
        if not det:
            continue
        x = (rhs1*d-b*rhs2)/det
        y = (a*rhs2-rhs1*c)/det
        if all(j*x+k*y <= rhs for (j, k), rhs in constraints):
            best = max(best, x+y)
    assert best == min(P, min(X1, Y1)+min(X2, Y2))
    return best


def profiles(R):
    power = [(F(1, R), F(0), F(0), F(0), F(0))] * R
    low = power + [(F(0), F(1), F(0), F(0), F(0)),
                   (F(0), F(0), F(1), F(0), F(0)),
                   (F(0), F(0), F(0), F(0), F(0)),
                   (F(0), F(0), F(0), F(0), F(1))]
    high = low.copy()
    high[R+2] = (F(0), F(0), F(0), F(1), F(0))
    return low, high


def values_for_every_subset(reports):
    n = len(reports)
    worth = {}
    for mask in range(1 << n):
        capacity = tuple(sum((reports[i][j] for i in range(n) if mask & (1 << i)), F(0)) for j in range(5))
        worth[mask] = packing_value(capacity)
    return worth


def certify(worth, payment, lam, coverage_multipliers):
    n = len(payment)
    assert all(x >= 0 for x in payment)
    for mask, value in worth.items():
        assert sum((payment[i] for i in range(n) if mask & (1 << i)), F(0)) >= value
    total = sum(payment)
    for mask, mu in coverage_multipliers.items():
        assert mu >= 0
        slack = sum((payment[i] for i in range(n) if mask & (1 << i)), F(0)) - worth[mask]
        assert mu*slack == 0
    residuals = []
    for i in range(n):
        # Objective gradient minus active coverage gradients equals the
        # multiplier on nonnegativity; nonnegative and complementary.
        residual = payment[i]+lam*total-sum(mu for mask, mu in coverage_multipliers.items() if mask & (1 << i))
        assert residual >= 0 and residual*payment[i] == 0
        residuals.append(residual)
    return residuals


def main():
    checks = 0
    report = []
    for R in (1, 2, 3, 4, 5, 10):
        low, high = profiles(R)
        low_worth, high_worth = values_for_every_subset(low), values_for_every_subset(high)
        checks += len(low_worth)+len(high_worth)
        full_power = (1 << R)-1
        pair1 = (1 << R)+(1 << (R+1))
        pair2 = (1 << (R+2))+(1 << (R+3))
        for lam in (F(0), F(1, 100), F(1, 3), F(2, 7), F(1), F(10)):
            v = F(1, R+2)
            y_low = [v]*(R+2)+[F(0)]*2
            certify(low_worth, y_low, lam, {full_power+pair1: v+lam})
            u = max(F(0), (1-R*lam)/(2+2*R+2*R*lam))
            t = (1-2*u)/R
            y_high = [t]*R+[u]*4
            T = sum(y_high)
            mu = (t+lam*T)/2
            residuals = certify(high_worth, y_high, lam,
                                {full_power+pair1: mu, full_power+pair2: mu})
            pair_change = 2*u-v
            assert (pair_change < 0) == (lam > F(1, R*(R+3)))
            if R*lam < 1:
                assert pair_change == (1-R*(R+3)*lam)/((R+2)*(1+R+R*lam))
            if R == 3:
                change = 3*u-2*v
                assert change <= -F(1, 40)
            if R*lam >= 1:
                assert u == 0 and t == F(1, R)
                assert y_high[R]+y_high[R+2]-y_low[R]-y_low[R+2] == -v
                assert residuals[R] == (lam-F(1, R))/2
            report.append({"R":R, "lambda":str(lam), "u":str(u), "t":str(t),
                           "pair_change":str(pair_change), "pair_failure_threshold":str(F(1,R*(R+3)))})
    # Lp formulas can also be exact for p=2,3/2,4/3 where a=1,2,3.
    lp = []
    for a in (1, 2, 3, 4):
        u = F(1, 3*2**a+2)
        t = 2**a*u
        assert 3*t+2*u == 1 and 3*u-F(2, 5) <= -F(1, 40)
        lp.append({"p":"1+1/"+str(a), "a":a, "u":str(u), "change":str(3*u-F(2, 5))})
    # p=3 star: choose M=N^2, making M^(1/(p-1))=N rational.
    stars = []
    for N in (2, 4, 16, 64):
        M=N*N
        u,t=F(1,N+1),F(N,N+1)
        assert t+u == 1 and t*t == M*u*u
        total=t+M*u
        assert total >= F(N,2)
        stars.append({"p":3,"leaves":M,"total":str(total),"F":1})
    print(json.dumps({"status":"PASS", "actual_subsets_solved_as_packing_LPs":checks,
                      "exact_primal_KKT_profiles":2*len(report),
                      "quadratic_cases":report, "Lp_rational_cases":lp,
                      "star_budget_cases":stars,
                      "scope":"Finite independent checks corroborate the written parametric proof; no unrestricted mechanism lower claim."}, indent=2))


if __name__ == "__main__":
    main()
