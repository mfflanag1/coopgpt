#!/usr/bin/env python3
"""Independent exact checks of the two products and fixed-owner star embedding.

No strict H>2 cover witness is supplied or claimed. Parameter tests with H>2
are arithmetic-only synthetic tests, explicitly separated in the output.
"""
from fractions import Fraction as F
from itertools import combinations, product
import json
import random


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def solve(a, b):
    n = len(b)
    aug = [[F(v) for v in row] + [F(rhs)] for row, rhs in zip(a, b)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i][j]), None)
        if pivot is None:
            return None
        aug[j], aug[pivot] = aug[pivot], aug[j]
        d = aug[j][j]
        aug[j] = [v/d for v in aug[j]]
        for i in range(n):
            if i != j:
                d = aug[i][j]
                aug[i] = [x-d*y for x, y in zip(aug[i], aug[j])]
    return [row[-1] for row in aug]


def stationarity(rows, lam, n):
    return [sum((lam[j] for j, row in enumerate(rows) if i in row), F(0))
            for i in range(n)]


def check_kkt(rows, rhs, q, lam):
    assert len(rows) == len(rhs) == len(lam)
    assert all(v >= 0 for v in q + lam)
    assert q == stationarity(rows, lam, len(q))
    for row, b, multiplier in zip(rows, rhs, lam):
        slack = sum((q[i] for i in row), F(0))-b
        assert slack >= 0
        assert multiplier*slack == 0
    assert dot(q, q) == dot(lam, rhs)


def projection(rows, rhs, n):
    for size in range(min(n, len(rows))+1):
        for active in combinations(range(len(rows)), size):
            gram = [[len(rows[j] & rows[k]) for k in active] for j in active]
            lam_active = solve(gram, [rhs[j] for j in active])
            if lam_active is None or any(v < 0 for v in lam_active):
                continue
            lam = [F(0)]*len(rows)
            for j, v in zip(active, lam_active):
                lam[j] = v
            q = stationarity(rows, lam, n)
            if all(sum((q[i] for i in row), F(0)) >= b for row, b in zip(rows, rhs)):
                check_kkt(rows, rhs, q, lam)
                return q, lam
    raise AssertionError("No exact independent-support KKT representation found")


def union_system(rows, n, z, lam_full, t):
    rho = dot(z, z)
    tuples = list(product(range(len(rows)), repeat=t))
    new_rows = [frozenset(k*n+i for k, j in enumerate(js) for i in rows[j])
                for js in tuples]
    new_lam = []
    for js in tuples:
        v = F(1, t)/rho**(t-1)
        for j in js:
            v *= lam_full[j]
        new_lam.append(v)
    new_z = [v/t for _ in range(t) for v in z]
    check_kkt(new_rows, [F(1)]*len(new_rows), new_z, new_lam)
    assert dot(new_z, new_z) == rho/t
    return tuples, new_rows, new_z, new_lam


def union_witness(rows, n, z, lam_full, witness, t, focal_block=0):
    rhs, q, lam = witness
    rho, mass = dot(z, z), sum(lam)
    assert mass > 0
    alpha = rho/(rho+(t-1)*mass)
    beta = mass/(rho+(t-1)*mass)
    tuples, new_rows, _, _ = union_system(rows, n, z, lam_full, t)
    new_q = [v*(alpha if k == focal_block else beta) for k in range(t) for v in (q if k == focal_block else z)]
    new_rhs, new_lam = [], []
    for js in tuples:
        new_rhs.append(alpha*rhs[js[focal_block]]+(t-1)*beta)
        value = alpha*lam[js[focal_block]]/rho**(t-1)
        for k, j in enumerate(js):
            if k != focal_block:
                value *= lam_full[j]
        new_lam.append(value)
    check_kkt(new_rows, new_rhs, new_q, new_lam)
    assert sum(new_lam) == alpha*mass
    return new_rhs, new_q, new_lam


def veto_system(rows, n, z, lam_full, copies):
    rho = dot(z, z)
    root = copies*n
    new_rows = [frozenset([root]+[k*n+i for i in row])
                for k in range(copies) for row in rows]
    scale = 1/(1+copies*rho)
    new_z = [scale*v for _ in range(copies) for v in z]+[1-scale]
    new_lam = [scale*v for _ in range(copies) for v in lam_full]
    check_kkt(new_rows, [F(1)]*len(new_rows), new_z, new_lam)
    assert dot(new_z, new_z) == new_z[root]
    return new_rows, new_z, new_lam


def veto_witness(rows, n, z, lam_full, witness, copies, focal_copy=0):
    rhs, q, lam = witness
    rho, mass = dot(z, z), sum(lam)
    scale = 1/(1+(copies-1)*rho+mass)
    u = 1-scale
    new_rows, _, _ = veto_system(rows, n, z, lam_full, copies)
    new_q = [scale*v for k in range(copies) for v in (q if k == focal_copy else z)]+[u]
    new_rhs = [u+scale*b if k == focal_copy else F(1)
               for k in range(copies) for b in rhs]
    new_lam = [scale*v for k in range(copies) for v in (lam if k == focal_copy else lam_full)]
    check_kkt(new_rows, new_rhs, new_q, new_lam)
    return new_rhs, new_q, new_lam


def coalition_value(rows, rhs, coalition):
    return max((b for row, b in zip(rows, rhs) if row <= coalition), default=F(0))


def star_realization_check(rows, rhs_by_owner, n, root):
    """All rows include root; full generator demands are one."""
    assert all(root in row for row in rows)
    coalitions = [frozenset(i for i in range(n) if mask >> i & 1)
                  for mask in range(1 << n)]
    full_rhs = [F(1)]*len(rows)
    games = {None: full_rhs, **rhs_by_owner}
    forms = []
    for owner, rhs in games.items():
        for a in coalitions[1:]:
            val = coalition_value(rows, rhs, a)
            p = [F(i not in a) for i in range(n)]
            if root in a:
                p[root] = val
            forms.append((owner, p))
    count = 0
    for low_owner in games:
        for coalition in coalitions:
            target = coalition_value(rows, games[low_owner], coalition)
            actual = min(sum((p[i] for i in coalition), F(0)) +
                         F(owner is not None and owner in coalition and owner != low_owner)
                         for owner, p in forms)
            assert actual == target
            count += 1
    return count


def main():
    rng = random.Random(20261021)
    bases = [
        (3, [frozenset([0,1]), frozenset([1,2])]),
        (3, [frozenset([1,2]), frozenset([0,1]), frozenset([0,2]), frozenset([0])]),
    ]
    for _ in range(6):
        n = 3 + rng.randrange(2)
        pool = [frozenset(c) for k in range(1, n+1) for c in combinations(range(n), k)]
        bases.append((n, rng.sample(pool, min(5, len(pool)))))
    counters = {"base_systems": len(bases), "base_witnesses": 0,
                "union_witnesses": 0, "veto_witnesses": 0,
                "realized_star_coalition_values": 0,
                "nonunique_mass_representations": 0,
                "synthetic_parameter_checks_not_cover_witnesses": 0}
    for index, (n, rows) in enumerate(bases):
        full_rhs = [F(1)]*len(rows)
        z, lam_full = projection(rows, full_rhs, n)
        rho = dot(z, z)
        assert rho == sum(lam_full)
        witnesses = []
        for owner in range(n):
            rhs = [F(rng.randrange(5), 4) if owner in row else F(1) for row in rows]
            q, lam = projection(rows, rhs, n)
            if not sum(lam):
                rhs, q, lam = full_rhs[:], z[:], lam_full[:]
            assert dot(q, q) <= sum(lam) <= 2*sum(lam)-dot(q, q) <= rho
            witnesses.append((rhs, q, lam))
            counters["base_witnesses"] += 1
        for t in (1, 2, 3):
            _, union_rows, union_z, union_lam = union_system(rows, n, z, lam_full, t)
            for owner, witness in enumerate(witnesses):
                uw = union_witness(rows, n, z, lam_full, witness, t)
                assert all(b == 1 for row, b in zip(union_rows, uw[0]) if owner not in row)
                counters["union_witnesses"] += 1
                for copies in (1, 2, 3):
                    vw = veto_witness(union_rows, n*t, union_z, union_lam, uw, copies)
                    final_rows, _, _ = veto_system(union_rows, n*t, union_z, union_lam, copies)
                    assert all(b == 1 for row, b in zip(final_rows, vw[0]) if owner not in row)
                    assert all(0 <= b <= 1 for b in vw[0])
                    counters["veto_witnesses"] += 1
        if n == 3:
            final_rows, _, _ = veto_system(rows, n, z, lam_full, 1)
            rhs_by_owner = {owner: veto_witness(rows, n, z, lam_full, w, 1)[0]
                            for owner, w in enumerate(witnesses)}
            rhs_by_owner[n] = [F(1)]*len(final_rows)
            counters["realized_star_coalition_values"] += star_realization_check(final_rows, rhs_by_owner, n+1, n)
    # Same q and relaxed RHS, different valid dual masses 3/5 and 7/10.
    rows = bases[1][1]
    z, full_lam = projection(rows, [F(1)]*4, 3)
    rhs, q = [F(1), F(7,10), F(7,10), F(1,5)], [F(1,5), F(1,2), F(1,2)]
    for lam in ([F(2,5), F(1,10), F(1,10), F(0)],
                [F(1,2), F(0), F(0), F(1,5)]):
        check_kkt(rows, rhs, q, lam)
        for t in (1,2,3):
            uw = union_witness(rows, 3, z, full_lam, (rhs,q,lam), t)
            _, ur, uz, ul = union_system(rows, 3, z, full_lam, t)
            veto_witness(ur, 3*t, uz, ul, uw, 3)
        counters["nonunique_mass_representations"] += 1
    # Pure arithmetic of the explicit finite parameter bound, not cover data.
    for hs, aa, rho in [([F(5,2)], [F(7)], F(2,3)),
                        ([F(3,2), F(3,4)], [F(0),F(100)], F(7,5)),
                        ([F(3)], [F(0)], F(1))]:
        h = sum(hs)
        s = dot(hs, aa)
        t = max(1, (2*s/(h-2)).numerator//(2*s/(h-2)).denominator + 1)
        ratio = sum((v/(1+a/t)**2 for v,a in zip(hs,aa)), F(0))
        assert ratio >= h-2*s/t > 2
        need = F(t)/(rho*(ratio-2))
        copies = need.numerator//need.denominator + 1
        assert copies*(rho/t)*(ratio-2) > 1
        counters["synthetic_parameter_checks_not_cover_witnesses"] += 1
    print(json.dumps({"status": "passed", "counts": counters,
                      "scope": "Exact algebra audit; no H>2 cover witness found or asserted."}, indent=2))


if __name__ == "__main__":
    main()
