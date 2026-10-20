#!/usr/bin/env python3
"""Bounded exact geometry and unbounded-size rational certificate ingredients.

Uses only Python integer/Fraction arithmetic. Geometry samples do not replace
the stated symbolic support classification or arbitrary-domain symmetrization.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
import json


def xor(values):
    result = 0
    for x in values:
        result ^= x
    return result


def rank(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def linear(value, images):
    return xor(image for bit, image in enumerate(images) if value & (1 << bit))


def institution(k, M):
    dimension = 1 + (k - 1) * M
    basis = [1 << j for j in range(dimension)]
    highs = [[basis[1 + (k - 1) * j + l] for l in range(k - 1)]
             for j in range(M)]
    lows = [1 ^ xor(branch) for branch in highs]
    return dimension, basis, highs, lows


def profile(k, M, m):
    _, _, highs, lows = institution(k, M)
    return [1] + [row for j in range(M) for row in
                  (highs[j] + [lows[j] if j < m else 0])]


def preserves(p, images):
    assert rank(images) == len(images), "resource map is not invertible"
    # All positive reported rows have distinct owners; the unique row matching
    # supplies a bijection of those owners, while zero-report owners stay zero.
    assert sorted(linear(x, images) for x in p) == sorted(p)


def check_geometry(k, M):
    dimension, basis, highs, lows = institution(k, M)
    all_possible = [1] + [row for j in range(M) for row in highs[j] + [lows[j]]]
    expected = {frozenset([1] + highs[j] + [lows[j]]) for j in range(M)}
    actual = {frozenset(rows) for rows in combinations(all_possible, k + 1)
              if xor(rows) == 0}
    assert actual == expected
    assert all(rank(edge) == k for edge in actual), "supported set not minimal"

    # Independently check every dependency using low subsets and forced highs.
    for t in range(1, M + 1):
        for chosen in combinations(range(M), t):
            rows = [row for j in chosen for row in highs[j] + [lows[j]]]
            if t % 2:
                rows.append(1)
            assert xor(rows) == 0
            assert len(rows) == t * k + (t % 2)
            assert (len(rows) == k + 1) == (t == 1)

    seed = profile(k, M, 1)
    # Seed root exchanges with every high of its branch, then with its low.
    for l in range(k - 1):
        images = basis.copy()
        images[0], images[1 + l] = images[1 + l], images[0]
        preserves(seed, images)
    images = basis.copy()
    images[0] = lows[0]
    preserves(seed, images)

    for m in range(1, M + 1):
        p = profile(k, M, m)
        positive = set(p) - {0}
        supported = {edge for edge in actual if edge <= positive}
        assert supported == set(list(expected & supported))
        assert len(supported) == m
        assert all(1 in edge for edge in supported)
        assert len(set(p) - {0}) == 1 + (k - 1) * M + m
        for j in range(m):
            images = basis.copy()
            images[1 + (k - 1) * j] = lows[j]
            preserves(p, images)
            for l in range(1, k - 1):
                images = basis.copy()
                a, b = 1 + (k - 1) * j, 1 + (k - 1) * j + l
                images[a], images[b] = images[b], images[a]
                preserves(p, images)
        for j in range(1, m):
            images = basis.copy()
            for l in range(k - 1):
                a, b = 1 + l, 1 + (k - 1) * j + l
                images[a], images[b] = images[b], images[a]
            preserves(p, images)
        if m >= 2:
            old = profile(k, M, m - 1)
            changed = {i for i in range(len(p)) if p[i] != old[i]}
            assert changed == {k * m}
            coalition = set(range(1, k * (m - 1) + 1)) | changed
            assert len(coalition) == k * (m - 1) + 1 <= k * (M - 1) + 1
            assert all(old[i] == p[i] for i in coalition - changed)
            assert old[k * m] == 0
            assert all(old[i] == p[i] for i in set(range(len(p))) - coalition)

    # Enumerate the full technology only when the dimension is at most5.
    full_count = None
    if dimension <= 5:
        full_edges = [rows for rows in combinations(range(1, 1 << dimension), k + 1)
                      if xor(rows) == 0 and rank(rows) == k]
        full_count = len(full_edges)
        assert full_count > 0
        for m in range(1, M + 1):
            p = profile(k, M, m)
            positive = set(p) - {0}
            price = {row: int(row == 1 or row not in positive)
                     for row in range(1, 1 << dimension)}
            assert all(sum(price[row] for row in edge) >= 1 for edge in full_edges)
            assert sum(price[row] for row in p if row) == 1
            # The same actual root and first branch form a worth1 coalition.
            coalition_rows = p[:k + 1]
            assert tuple(sorted(coalition_rows)) in full_edges
            assert len(set(coalition_rows)) == k + 1
    return {"k": k, "arity": k + 1, "M": M, "dimension": dimension,
            "rows": (1 << dimension) - 1, "owners": 1 + k * M,
            "full_technology_columns_checked": full_count}


def scalar(k, M, terminal):
    Q = F(1)
    for m in range(2, M + 1):
        Q *= F(k * m, k * (m - 1) + 1)
    out = defaultdict(F)
    def add(row, rhs, w):
        assert w >= 0
        for var, val in row.items():
            out[var] += w * val
        out["RHS"] += w * rhs
    scale = F(M - 1, M) if terminal else F(1)
    add({"q1": k + 1}, 1, scale * k * Q / (k + 1))
    w = F(1)
    for m in range(M, 1, -1):
        w *= F(k * m, k * (m - 1) + 1)
        add({f"q{m}": k * (m - 1) + 1, f"q{m-1}": -k * (m - 1)}, 0, scale * w)
    if terminal:
        add({"z": 1, f"q{M}": k}, 1, F(1))
        add({"kappa": 1, "z": -1, f"q{M}": -k * M}, 0, F(1))
        bound = 1 + scale * k * Q / (k + 1)
    else:
        add({"kappa": 1, f"q{M}": -k * M}, 0, F(1))
        bound = k * Q / (k + 1)
    assert {var: val for var, val in out.items() if val} == {"kappa": 1, "RHS": bound}
    assert Q ** k >= F(M + 1, 2) ** (k - 1)
    return bound


def main():
    geometry = [check_geometry(k, M) for k in range(2, 7) for M in range(1, 5)]
    for k in range(2, 33):
        for M in range(1, 129):
            baseline = scalar(k, M, False)
            stronger = scalar(k, M, True)
            assert stronger >= baseline and stronger >= 1
    print(json.dumps({"status": "PASS", "arithmetic": "integer/Fraction only",
                      "geometry": geometry, "scalar_k_range": [2, 32],
                      "scalar_M_range": [1, 128],
                      "samples": [{"r": k + 1, "M": 8, "s": 7*k+1,
                                   "lower": str(scalar(k, 8, True))}
                                  for k in range(2, 7)],
                      "scope": "finite exact replay plus symbolic proof; no formalization of averaging"}, indent=2))


if __name__ == "__main__":
    main()
