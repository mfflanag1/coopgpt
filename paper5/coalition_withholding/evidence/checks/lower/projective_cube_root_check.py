#!/usr/bin/env python3
"""Independent exact checks of the projective cap-exchange proof ingredients.

Standard library only. No LP solution or floating-point premise is imported.
The arbitrary-real-domain symmetrization argument is mathematical, not encoded.
Default enumeration stops at M=8 (511 rows); exact scalar checks reach M=256.
"""

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from math import comb


def linear(x, images):
    out = 0
    for bit, image in enumerate(images):
        if x & (1 << bit):
            out ^= image
    return out


def triples(M):
    d = (1 << (M + 1)) - 1
    return [(a, b, a ^ b) for a in range(1, d + 1)
            for b in range(a + 1, d + 1) if b < (a ^ b)]


def owners(M, R):
    highs, lows = {}, {}
    cursor = 1
    for j in range(1, M + 1):
        highs[j] = tuple(range(cursor, cursor + R))
        cursor += R
        lows[j] = tuple(range(cursor, cursor + R))
        cursor += R
    assert cursor == 1 + 2 * M * R
    return highs, lows


def profile(M, R, m, seed=False):
    highs, lows = owners(M, R)
    p = [0] * (1 + 2 * M * R)
    p[0] = 1
    for j in range(1, M + 1):
        for owner in highs[j]:
            p[owner] = 1 << j
        if j <= m:
            for owner in lows[j]:
                p[owner] = (1 << j) ^ 1
    if seed:
        assert m == 1
        for owner in lows[1][1:]:
            p[owner] = 0
    return tuple(p)


def check_symmetry(p, images, permutation):
    """Check the resource map, then the explicitly supplied owner permutation."""
    d = (1 << len(images)) - 1
    mapped = [linear(row, images) for row in range(1, d + 1)]
    assert sorted(mapped) == list(range(1, d + 1)), "resource map singular"
    assert sorted(permutation) == list(range(len(p))), "not an owner bijection"
    transformed = [None] * len(p)
    for owner, row in enumerate(p):
        transformed[permutation[owner]] = linear(row, images)
    assert tuple(transformed) == p, "map does not preserve full profile"


def swap_groups(permutation, left, right):
    assert len(left) == len(right)
    for i, j in zip(left, right):
        permutation[i], permutation[j] = j, i


def check_geometry(M, R):
    highs, lows = owners(M, R)
    n = 1 + 2 * M * R
    identity = [1 << j for j in range(M + 1)]
    edges = triples(M)
    d = (1 << (M + 1)) - 1
    assert len(edges) == d * (d - 1) // 6
    assert all(len(set(edge)) == 3 and edge[0] ^ edge[1] ^ edge[2] == 0
               for edge in edges)
    seed = profile(M, R, 1, seed=True)

    # Cap/low seed transvection fixes every high row, including inactive highs.
    transvection = identity.copy()
    transvection[0] ^= 2
    perm = list(range(n))
    swap_groups(perm, (0,), (lows[1][0],))
    check_symmetry(seed, transvection, perm)

    # For R=1 the second seed generator swaps cap/high and fixes the low row.
    if R == 1:
        cap_high = identity.copy()
        cap_high[0], cap_high[1] = cap_high[1], cap_high[0]
        perm = list(range(n))
        swap_groups(perm, (0,), highs[1])
        check_symmetry(seed, cap_high, perm)

    # The initial R-owner restoration uses the same actual low group.
    first = profile(M, R, 1)
    difference = {i for i in range(n) if seed[i] != first[i]}
    assert difference == set(lows[1][1:])
    assert len(lows[1]) == R <= R * (2 * M - 1)

    geometry_profiles = [seed] + [profile(M, R, m) for m in range(1, M + 1)]
    for p in geometry_profiles:
        positive = set(p) - {0}
        supported = {edge for edge in edges if set(edge) <= positive}
        expected = {(1, 1 << j, (1 << j) ^ 1)
                    for j in range(1, M + 1) if (1 << j) ^ 1 in positive}
        assert supported == expected
        assert len(supported) >= 1
        # Full-technology dual, not merely the supported subproblem.
        price = {row: int(row == 1 or row not in positive)
                 for row in range(1, d + 1)}
        assert all(sum(price[row] for row in edge) >= 1 for edge in edges)
        counts = Counter(p)
        assert sum(counts[row] * price[row] for row in positive) == 1
        # One activity at level 1 is an exact primal certificate.
        edge = next(iter(supported))
        assert all(counts[row] >= 1 for row in edge)

    # Explicit coalition coverage witnesses used at both seed and terminal.
    # These are the same actual three owners, not the grand coalition.
    cover_coalition = (0, highs[1][0], lows[1][0])
    assert len(set(cover_coalition)) == 3
    for p in (seed, profile(M, R, M)):
        coalition_counts = Counter(p[i] for i in cover_coalition)
        assert coalition_counts == Counter({1: 1, 2: 1, 3: 1})
        assert (1, 2, 3) in edges  # primal quantity1
        coalition_price = {row: int(row == 1 or row not in coalition_counts)
                           for row in range(1, d + 1)}
        assert all(sum(coalition_price[row] for row in edge) >= 1 for edge in edges)
        assert sum(count * coalition_price[row]
                   for row, count in coalition_counts.items()) == 1

    for m in range(1, M + 1):
        p = profile(M, R, m)
        # Independent flips act within every active pair.
        for j in range(1, m + 1):
            flip = identity.copy()
            flip[j] ^= 1
            perm = list(range(n))
            swap_groups(perm, highs[j], lows[j])
            check_symmetry(p, flip, perm)
        # Transpositions of active indices plus flips generate transitivity.
        for j in range(2, m + 1):
            exchange = identity.copy()
            exchange[1], exchange[j] = exchange[j], exchange[1]
            perm = list(range(n))
            swap_groups(perm, highs[1], highs[j])
            swap_groups(perm, lows[1], lows[j])
            check_symmetry(p, exchange, perm)
        # Within each pure-row owner group, owner permutations preserve profile.
        for j in range(1, m + 1):
            for group in (highs[j], lows[j]):
                assert len({p[i] for i in group}) == 1
        if m == 1:
            continue
        old = profile(M, R, m - 1)
        changed = {i for i in range(n) if old[i] != p[i]}
        assert changed == set(lows[m])
        coalition = set(lows[m])
        for j in range(1, m):
            coalition.update(highs[j])
            coalition.update(lows[j])
        assert len(coalition) == R * (2 * m - 1)
        assert len(coalition) <= R * (2 * M - 1)
        assert 0 not in coalition and not (set(highs[m]) & coalition)
        assert all(old[i] == p[i] for i in coalition - changed)
        assert all(old[i] == 0 and p[i] != 0 for i in changed)
        assert all(old[i] == p[i] for i in set(range(n)) - coalition)
    return {"M": M, "R": R, "rows": d, "activities": len(edges), "owners": n}


def Q(M):
    result = F(1)
    for m in range(2, M + 1):
        result *= F(2 * m, 2 * m - 1)
    return result


def add_row(total, row, rhs, weight):
    assert weight >= 0
    for key, coefficient in row.items():
        total[key] += weight * coefficient
    total["RHS"] += weight * rhs


def finish(total, factor, rhs):
    residual = {key: value for key, value in total.items() if value}
    assert residual == {"kappa": factor, "RHS": rhs}, residual


def check_scalar_certificate(M, strong_terminal=False):
    q = Q(M)
    total = defaultdict(F)
    scale = F(M - 1, M) if strong_terminal else F(1)
    add_row(total, {"q1": 3}, 1, scale * 2 * q / 3)
    weight = F(1)
    for m in range(M, 1, -1):
        weight *= F(2 * m, 2 * m - 1)
        add_row(total, {f"q{m}": 2 * m - 1,
                        f"q{m-1}": -2 * (m - 1)}, 0, scale * weight)
    if strong_terminal:
        add_row(total, {"z": 1, f"q{M}": 2}, 1, F(1))
        add_row(total, {"kappa": 1, "z": -1, f"q{M}": -2 * M}, 0, F(1))
        lower = 1 + scale * 2 * q / 3
    else:
        add_row(total, {"kappa": 1, f"q{M}": -2 * M}, 0, F(1))
        lower = 2 * q / 3
    finish(total, F(1), lower)
    return lower


def check_cube_certificate(M, R, sharp=False):
    assert R >= 1 and (not sharp or R > 1)
    q = Q(M)
    total = defaultdict(F)
    if sharp:
        add_row(total, {"a": 2, "b": 1}, 1, q * R / (R - 1))
        add_row(total, {"kappa": 1, "a": -2, "b": -R}, 0, q / (R - 1))
        factor, rhs = 1 + q / (R - 1), q * R / (R - 1)
    else:
        add_row(total, {"a": 2, "b": 1}, 1, q)
        add_row(total, {"kappa": 1, "b": -R}, 0, q / R)
        factor, rhs = 1 + q / R, q
    add_row(total, {"q1": R, "a": -1}, 0, 2 * q)
    weight = F(1)
    for m in range(M, 1, -1):
        weight *= F(2 * m, 2 * m - 1)
        add_row(total, {f"q{m}": R * (2 * m - 1),
                        f"q{m-1}": -2 * R * (m - 1)}, 0, weight)
    add_row(total, {"kappa": 1, f"q{M}": -2 * M * R}, 0, F(1))
    finish(total, factor, rhs)
    return rhs / factor


def polynomial_product(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def polynomial_subtract(a, b):
    out = [(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
           for i in range(max(len(a), len(b)))]
    while out and out[-1] == 0:
        out.pop()
    return out


def check_polynomials():
    # Coefficients are in ascending powers of M; these are identities, not samples.
    square_even = polynomial_product([2, 2], [2, 2])
    square_odd = polynomial_product([1, 2], [1, 2])
    lower = polynomial_subtract(polynomial_product(square_even, [1, 3]),
                                polynomial_product(square_odd, [4, 3]))
    upper = polynomial_subtract(polynomial_product(square_odd, [1, 1]),
                                polynomial_product(square_even, [0, 1]))
    assert lower == [0, 1]  # M
    assert upper == [1, 1]  # M+1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-geometry-m", type=int, default=8)
    parser.add_argument("--max-scalar-m", type=int, default=256)
    args = parser.parse_args()
    assert 1 <= args.max_geometry_m <= 10, "bounded checker: M<=10 geometry"
    assert 1 <= args.max_scalar_m <= 4096
    check_polynomials()
    geometry = []
    for M in range(1, args.max_geometry_m + 1):
        for R in (1, 2, 3):
            geometry.append(check_geometry(M, R))
    for M in range(1, args.max_scalar_m + 1):
        q = Q(M)
        assert q == F(4 ** M, 2 * comb(2 * M, M))
        assert 4 * q * q >= 3 * M + 1
        assert q * q <= M
        baseline = check_scalar_certificate(M)
        stronger = check_scalar_certificate(M, strong_terminal=True)
        assert stronger >= baseline and stronger >= 1
        for R in (1, 2, 3, 7):
            assert check_cube_certificate(M, R) == q * R / (R + q)
            if R > 1:
                assert check_cube_certificate(M, R, sharp=True) == q * R / (R - 1 + q)
    samples = [{"M": M, "s": 2 * M - 1,
                "square_root_bound": str(check_scalar_certificate(M)),
                "terminal_coverage_bound": str(check_scalar_certificate(M, True))}
               for M in (1, 2, 3, 4, 8, 16)]
    print(json.dumps({"status": "PASS", "arithmetic": "integer/Fraction only",
                      "polynomial_identities": ["M", "M+1"],
                      "geometry": geometry, "scalar_M_max": args.max_scalar_m,
                      "samples": samples,
                      "scope_limit": "real-domain group averaging is proved in prose, not formalized"},
                     indent=2))


if __name__ == "__main__":
    main()
