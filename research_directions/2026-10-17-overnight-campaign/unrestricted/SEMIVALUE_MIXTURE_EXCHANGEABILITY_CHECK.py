"""Exact finite sampling-law comparison used by the architecture lower proof."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json


def falling(n, k):
    if k > n:
        return 0
    out = 1
    for j in range(k):
        out *= n-j
    return out


checks = moment_checks = 0
for population in range(1, 31):
    for active in range(min(population, 7)+1):
        for selected in range(population+1):
            p = Q(selected, population)
            hyper, bernoulli = [], []
            for ones in range(active+1):
                coefficient = comb(active, ones)
                hyper.append(Q(coefficient * falling(selected, ones)
                                 * falling(population-selected, active-ones),
                                 falling(population, active)))
                bernoulli.append(coefficient * p**ones * (1-p)**(active-ones))
            assert sum(hyper, Q(0)) == sum(bernoulli, Q(0)) == 1
            # Both laws are exchangeable across active slots; grouping by number
            # of ones preserves the full binary-vector total variation exactly.
            variation = sum((abs(x-y) for x,y in zip(hyper, bernoulli)), Q(0))/2
            bound = min(Q(1), Q(active*(active-1), 2*population))
            assert variation <= bound
            checks += 1
            # Probability that every required other pure owner is selected.
            assert hyper[-1] == Q(falling(selected, active), falling(population, active))
            assert abs(hyper[-1]-p**active) <= bound
            moment_checks += 1

out = {"status":"PASS", "exact_sampling_law_checks":checks,
       "pure_owner_moment_checks":moment_checks,
       "scope":"Finite exact checks of normalization, total variation coupling bound and unanimity moment. Analytic weak compactness and support necessity are separate proofs."}
Path(__file__).with_name("SEMIVALUE_MIXTURE_EXCHANGEABILITY_CHECKS.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
