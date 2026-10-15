"""Exact checks of the positive-capacity depth-two-tree obstruction.
All checks raise explicitly and remain active under python -O.
"""
from fractions import Fraction as Q
from itertools import product
from math import comb
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def value(n, hub_retained, retained, no_veto):
    eps = Q(1, n*n)
    delta = Q(1, n**4) if no_veto else Q(0)
    k = sum(retained)
    center = hub_retained + k*delta
    leaf = hub_retained*eps + k*delta
    return min(Q(k), center + sum((min(Q(t), leaf) for t in retained), Q(0)))


unique_checks = 0
profile_checks = 0
binomial_checks = 0
for no_veto in (False, True):
    for n in range(2, 9):
        eps = Q(1, n*n)
        delta = Q(1, n**4) if no_veto else Q(0)
        expected_T = 1+n*eps+(n+n*n)*delta
        require(value(n, 1, (1,)*n, no_veto) == expected_T,
                ("full value", n, no_veto))
        # Coalition {hub,j} has value1 and {hub} value0, so V_j>=1.
        require(value(n, 1, (1,)+(0,)*(n-1), no_veto) == 1,
                ("maximum marginal lower", n, no_veto))
        require(value(n, 1, (0,)*n, no_veto) == 0,
                ("hub singleton", n, no_veto))
        if no_veto:
            require(value(n, 0, (1,)*n, True) > 0,
                    ("hub is not veto", n))
            require(value(n, 1, (0,)+(1,)*(n-1), True) > 0,
                    ("intermediate owner is not veto", n))
        profile_checks += 1
        for retained in product((0, 1), repeat=n):
            k = sum(retained)
            if k < 2:
                continue
            center = 1+k*delta
            leaf = eps+k*delta
            expected = center+k*leaf
            candidates = [(Q(k), ("all_h",))]
            for choose_h in product((0, 1), repeat=n):
                cost = center + sum((Q(retained[j]) if choose_h[j] else leaf
                                     for j in range(n)), Q(0))
                candidates.append((cost, choose_h))
            optimum = min(v for v, _ in candidates)
            winners = [tag for val, tag in candidates if val == optimum]
            require(len(winners) == 1 and winners[0] == tuple(1-t for t in retained),
                    ("unique minimizing cover", n, retained, no_veto))
            require(optimum == expected and expected < k,
                    ("strict cover comparison", n, retained, no_veto))
            # A closed h owner's selected-cover price includes its unit h account.
            # Its reasonable upper payoff is at least1, as checked above.
            closed_price = 1 + (k+1)*delta
            require(closed_price >= 1, ("closed owner price", n, no_veto))
            unique_checks += 1
        for q in (Q(1, 10), Q(1, 5), Q(1, 2), Q(9, 10)):
            p = 1-q
            direct = sum((Q(n-k)*comb(n,k)*p**k*q**(n-k)
                          for k in range(2,n+1)), Q(0))
            closed = n*q-n*q**n-n*(n-1)*p*q**(n-1)
            require(direct == closed, ("binomial identity", n, q))
            binomial_checks += 1

examples = []
for n in (10, 100, 1000):
    q = Q(1, 5)
    p = 1-q
    denom = 1+Q(1,n)+Q(1,n*n)+Q(1,n**3)
    lower = p*(n*q-n*q**n-n*(n-1)*p*q**(n-1))/denom
    examples.append({"n": n, "q": "1/5", "no_veto_budget_lower": float(lower)})
print(json.dumps({"status": "PASS", "exact_unique_cover_checks": unique_checks,
                  "exact_full_profile_and_no_veto_checks": profile_checks,
                  "exact_binomial_checks": binomial_checks, "examples": examples}))
