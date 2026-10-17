"""Exact finite checks of the exchangeable-to-Bernoulli approximation lemma.

This checks probability distributions, not the universal mechanism theorem.
The all-population argument is the coupling proof in the final gate note.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


cases = 0
max_tv = Q(0)
for population in range(1, 31):
    for active in range(1, min(population, 6) + 1):
        for selected in range(population + 1):
            p = Q(selected, population)
            hyper = [
                Q(choose(selected, j) * choose(population - selected, active - j),
                  choose(population, active))
                for j in range(active + 1)
            ]
            bern = [
                choose(active, j) * p ** j * (1 - p) ** (active - j)
                for j in range(active + 1)
            ]
            if sum(hyper) != 1 or sum(bern) != 1:
                raise RuntimeError("Probability normalization failed")
            tv = sum(abs(x - y) for x, y in zip(hyper, bern)) / 2
            bound = min(Q(1), Q(active * (active - 1), 2 * population))
            if tv > bound:
                raise RuntimeError((population, active, selected, tv, bound))
            if active == 1 and tv != 0:
                raise RuntimeError("Single active label must be exact")
            if selected in (0, population) and tv != 0:
                raise RuntimeError("Endpoint sampling must be exact")
            max_tv = max(max_tv, tv)
            cases += 1

result = {
    "status": "PASS",
    "arithmetic": "exact fractions; checks remain active under Python optimization",
    "cases": cases,
    "population_range": [1, 30],
    "active_labels_max": 6,
    "largest_checked_total_variation": str(max_tv),
    "bound": "min(1,a(a-1)/(2M)) for M=n-1",
    "scope": "Finite probability-law checks only; no universal mechanism proof by testing.",
}
Path(__file__).with_name("SEMIVALUE_MIXTURE_EXCHANGEABLE_CHECKS.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
print(json.dumps(result, indent=2))
