"""Exact bounded checks for UNIFORM_MIXTURE_OBSTRUCTION.txt; no dependencies.

Pool order is fixed cut priority. Zero owners may be omitted: they contribute
no score, and the relative permutation of positive owners is uniform.
These checks supplement the symbolic proof, not replace it.
"""
from fractions import Fraction as F
from itertools import permutations
from math import comb, factorial

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def flatten(pools):
    weights = []
    group = []
    for i, pool in enumerate(pools):
        for weight in pool:
            require(weight > 0, 'exact verification failed')
            weights.append(F(weight))
            group.append(i)
    return (weights, group)

def subset_budget(pools):
    """Integrate each owner's conditional predecessor mask exactly."""
    weights, group = flatten(pools)
    n = len(weights)
    total = F(0)
    for mask in range(1 << n):
        k = mask.bit_count()
        if k == n:
            continue
        scores = [F(0) for _ in pools]
        residuals = [F(0) for _ in pools]
        for e, weight in enumerate(weights):
            if mask >> e & 1:
                scores[group[e]] += weight
            else:
                residuals[group[e]] += weight
        selected = min(range(len(pools)), key=lambda i: scores[i])
        total += residuals[selected] / (n * comb(n - 1, k))
    return total

def permutation_budget(pools):
    """Independent direct implementation, used only with <=6 owners."""
    weights, group = flatten(pools)
    n = len(weights)
    require(n <= 6, 'exact verification failed')
    total = F(0)
    for order in permutations(range(n)):
        scores = [F(0) for _ in pools]
        charge = F(0)
        for e in order:
            selected = min(range(len(pools)), key=lambda i: scores[i])
            if group[e] == selected:
                charge += weights[e]
            scores[group[e]] += weights[e]
        total += charge
    return total / factorial(n)

def record_lower(sizes):
    """Exact first-arrival-record sum by finite inclusion-exclusion."""
    total = F(0)
    for i, size in enumerate(sizes):
        probability = F(0)
        for subset in range(1 << i):
            earlier = sum((sizes[j] for j in range(i) if subset >> j & 1))
            probability += (-1) ** subset.bit_count() * F(size, size + earlier)
        total += probability
    return total

def unit_pools(sizes):
    return [[F(1)] * size for size in sizes]

def main():
    for sizes, expected in [([2, 1], F(7, 3)), ([3, 1], F(9, 4)), ([9, 3, 1], F(2193, 715))]:
        actual = subset_budget(unit_pools(sizes))
        require(actual == expected, (sizes, actual, expected))
        lower = record_lower(sizes)
        require(actual >= lower, 'exact verification failed')
        if sum(sizes) <= 6:
            require(permutation_budget(unit_pools(sizes)) == actual, 'exact verification failed')
        print(f'sizes={sizes}: budget={actual}, first-arrival lower={lower}')
    require(record_lower([9, 3, 1]) == F(161, 65), 'exact verification failed')
    for k in range(1, 7):
        pools = unit_pools([1] * k)
        harmonic = sum((F(1, j) for j in range(1, k + 1)), F(0))
        require(subset_budget(pools) == harmonic, 'exact verification failed')
        require(permutation_budget(pools) == harmonic, 'exact verification failed')
    for m, r in [(2, 1), (3, 1), (2, 3), (3, 2), (1, 4)]:
        pools = [[F(1)] * m, [F(1, r)] * r]
        actual = subset_budget(pools)
        if m == 1:
            expected = F(3, 2)
        else:
            expected = 1 + F(m, m + 1) + F(factorial(m) * factorial(r + 1), factorial(m + r))
        require(actual == expected, (m, r, actual, expected))
        require(permutation_budget(pools) == actual, 'exact verification failed')
    for k in range(2, 7):
        for base in (3, 5, 10):
            sizes = [base ** (k - i - 1) for i in range(k)]
            exact = record_lower(sizes)
            union = F(k) - sum((F(1, base ** d) for i in range(1, k + 1) for d in range(1, i)), F(0))
            coarse = F(k) * (1 - F(1, base - 1))
            require(exact >= union >= coarse, 'exact verification failed')
    print('All exact subset, permutation, tie-correction, and record checks passed.')
if __name__ == '__main__':
    main()
