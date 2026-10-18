#!/usr/bin/env python3
"""Bounded exact affine-stabilizer scout for a polynomial-row candidate.

F9 parabola has eight candidate branches in 81 affine resource points.
No mechanism upper bound or growing theorem is inferred from this scout.
"""
from itertools import permutations
import json

D = 4
N = 3 ** D
vectors = [tuple((x // (3 ** i)) % 3 for i in range(D)) for x in range(N)]
def encode(v):
    return sum((x % 3) * 3 ** i for i, x in enumerate(v))
add = [[encode(tuple(a + b for a, b in zip(vectors[x], vectors[y])))
        for y in range(N)] for x in range(N)]
neg = [encode(tuple(-a for a in v)) for v in vectors]

def rank(rows):
    rows = [list(row) for row in rows]
    r = 0
    for col in range(D):
        pivot = next((j for j in range(r, len(rows)) if rows[j][col] % 3), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        multiplier = rows[r][col] % 3
        rows[r] = [(x * multiplier) % 3 for x in rows[r]]
        for j in range(len(rows)):
            if j != r:
                c = rows[j][col]
                rows[j] = [(x - c * y) % 3 for x, y in zip(rows[j], rows[r])]
        r += 1
    return r

high = []
for x in range(1, 9):
    a, b = x % 3, x // 3
    high.append(encode((a, b, a*a + 2*b*b, 2*a*b)))
assert len(set(high)) == 8
assert not (set(high) & {neg[x] for x in high})

basis = []
for x in high:
    if rank([vectors[y] for y in basis + [x]]) > len(basis):
        basis.append(x)
assert len(basis) == 4
coordinates = {}
for c in vectors:
    x = 0
    for scalar, b in zip(c, basis):
        if scalar:
            x = add[x][b if scalar == 1 else neg[b]]
    assert x not in coordinates
    coordinates[x] = c

def stabilizer(active):
    positive = set([0] + high + [neg[high[i]] for i in active])
    point_list = sorted(positive)
    # For m>=2, the root is unique degree m in the induced star hypergraph.
    origins = [0] if len(active) >= 2 else [0, high[active[0]], neg[high[active[0]]]]
    parent = {x: x for x in point_list}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    generators = []
    count = 0
    for origin in origins:
        targets = [x for x in point_list if x != origin]
        for raw_images in permutations(targets, D):
            images = [add[x][neg[origin]] for x in raw_images]
            if rank([vectors[x] for x in images]) != D:
                continue
            mapped = []
            for point in point_list:
                out = origin
                for scalar, target in zip(coordinates[point], images):
                    if scalar:
                        out = add[out][target if scalar == 1 else neg[target]]
                if out not in positive:
                    break
                mapped.append(out)
            else:
                assert len(set(mapped)) == len(point_list)
                count += 1
                changed = False
                for x, y in zip(point_list, mapped):
                    rx, ry = find(x), find(y)
                    if rx != ry:
                        parent[rx] = ry
                        changed = True
                if changed:
                    generators.append({"origin": origin, "basis_images": raw_images})
    orbits = {}
    for point in point_list:
        orbits.setdefault(find(point), []).append(point)
    active_points = {high[i] for i in active} | {neg[high[i]] for i in active}
    active_orbits = [sorted(set(orbit) & active_points) for orbit in orbits.values()
                     if set(orbit) & active_points]
    return {"active_indices": active, "positive_points": point_list,
            "group_size": count, "orbits": list(orbits.values()),
            "active_private_orbits": active_orbits,
            "active_private_transitive": len(active_orbits) == 1,
            "orbit_generators": generators}

def main():
    # Verify all full-tech supported triples are exactly root pairs.
    support = {0} | set(high) | {neg[x] for x in high}
    edges = {tuple(sorted((a, b, neg[add[a][b]])))
             for a in support for b in support if a != b and neg[add[a][b]] in support}
    expected = {tuple(sorted((0, x, neg[x]))) for x in high}
    assert edges == expected
    cases = [[0]] + [[0, j] for j in range(1, 8)] + [list(range(m)) for m in (3, 4, 6, 8)]
    print(json.dumps({"status": "exact bounded scout", "rows": N,
                      "branches": 8, "high": high, "basis": basis,
                      "supported_star_verified": True,
                      "cases": [stabilizer(case) for case in cases]}, indent=2))

if __name__ == "__main__":
    main()
