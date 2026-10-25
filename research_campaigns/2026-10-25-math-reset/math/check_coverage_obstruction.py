"""Exact checks of the fixed-coverage obstruction; symbolic proof is separate.

Read-only by default. Standard library; no floating-point optimization.
Owners each hold three private resource rows. A unit-profit activity consumes
those three rows, so every activity has arity exactly three.
"""
from fractions import Fraction as Q
import json


def check(m):
    n = 3 * m
    z = (Q(2),) * n
    profiles = {"z": z}
    edges = []
    coverage = []
    for k in range(m):
        i, j, h = range(3 * k, 3 * k + 3)
        a = list(z)
        for owner in (i, j, h):
            a[owner] = Q(1)
        b = a.copy()
        b[i] = Q(2)
        c = b.copy()
        c[j] = Q(2)
        names = [f"{label}{k}" for label in "abc"]
        profiles.update(zip(names, map(tuple, (a, b, c))))
        coverage.append((names[0], frozenset([i]), Q(1, 2)))
        edges.extend([
            (names[0], names[1], frozenset([i]), Q(1, 2)),
            (names[1], names[2], frozenset([i, j]), Q(1, 2)),
            (names[2], "z", frozenset([i, h]), Q(1, 2)),
            (names[2], "z", frozenset([j, h]), Q(1, 2)),
        ])

    # At selected profiles all three rows belonging to an owner coincide.
    # Therefore F = sum_i min(row_i1,row_i2,row_i3) = sum_i x_i.
    g = {p: [Q(0)] * n for p in profiles}
    objective = Q(0)
    covered_resources = [Q(0)] * n
    restored_resources = [Q(0)] * n
    for p, coalition, weight in coverage:
        objective += weight * sum(profiles[p][i] for i in coalition)
        for i in coalition:
            g[p][i] += weight
            covered_resources[i] += weight * profiles[p][i]
    for low, high, coalition, weight in edges:
        lo, hi = profiles[low], profiles[high]
        changed = {i for i in range(n) if hi[i] != lo[i]}
        assert changed <= coalition and len(coalition) <= 2
        assert all(a <= b for a, b in zip(lo, hi))
        delta = [hi[i] - lo[i] for i in range(n)]
        objective += weight * sum(delta)
        for i in range(n):
            restored_resources[i] += weight * delta[i]
        for i in coalition:
            g[low][i] -= weight
            g[high][i] += weight
    budgets = {p: Q(p == "z") for p in profiles}
    slacks = {p: [budgets[p] - x for x in g[p]] for p in profiles}
    assert all(x >= 0 for row in slacks.values() for x in row)
    assert all(x > 0 for row in profiles.values() for x in row)
    for i in range(n):
        assert z[i] - restored_resources[i] == covered_resources[i] + sum(
            slacks[p][i] * profiles[p][i] for p in profiles
        )

    # Exact finite witnesses to the symbolic disjoint-neighborhood proof.
    # Any common monotone upper bound of two sources is z, and getting
    # from either source to z changes three owners, exceeding s=2.
    for k in range(m):
        a = profiles[f"a{k}"]
        assert sum(x != y for x, y in zip(a, z)) == 3
        for ell in range(k):
            other = profiles[f"a{ell}"]
            assert tuple(max(x, y) for x, y in zip(a, other)) == z

    budget = sum(budgets[p] * sum(row) for p, row in profiles.items())
    repair_lower = sum(Q(1, 2) * sum(profiles[f"a{k}"]) for k in range(m))
    assert objective == Q(5 * m, 2)
    assert budget == 6 * m
    assert objective / budget == Q(5, 12)
    assert repair_lower / budget == Q(m, 2) - Q(1, 4)
    # Optional actual upper witness: retain every marked row locally, then
    # add one zero-coverage piece o -> h for a singleton restoring (2,2,2).
    # Weight m gives objective/budget 2m and homogeneous coefficients -m,+m.
    local_objective = Q(m, 2)
    extra_objective = Q(2 * m)
    extra_budget = Q(2 * m)
    assert local_objective + extra_objective == objective
    repair_upper = repair_lower + extra_budget
    assert repair_upper / budget == Q(m, 2) + Q(1, 12)
    # Stronger version: fill every original slack with legal coverage rows.
    # This keeps all marked a_g rows and turns the witness into an optimal
    # ratio-one certificate. Choosing a different optimum remains possible.
    optimal_g = {p: row.copy() for p, row in g.items()}
    added_coverage = []
    for k in range(m):
        added_coverage.extend([
            (f"b{k}", frozenset([3 * k + 1]), Q(1, 2)),
            (f"c{k}", frozenset([3 * k + 2]), Q(1)),
        ])
    added_coverage.append(("z", frozenset(i for i in range(n) if i % 3 != 2), Q(1, 2)))
    optimal_objective = objective
    for p, coalition, weight in added_coverage:
        optimal_objective += weight * sum(profiles[p][i] for i in coalition)
        for i in coalition:
            optimal_g[p][i] += weight
    assert all(x == budgets[p] for p, row in optimal_g.items() for x in row)
    assert optimal_objective == budget
    optimal_coverage_resources = [Q(0)] * n
    coverage_incidence = [Q(0)] * n
    for p, coalition, weight in coverage + added_coverage:
        for i in coalition:
            optimal_coverage_resources[i] += weight * profiles[p][i]
            coverage_incidence[i] += weight
    assert all(x == 1 for x in coverage_incidence)
    assert all(z[i] - restored_resources[i] == optimal_coverage_resources[i]
               for i in range(n))
    singleton_rows = [("z", frozenset([i]), Q(1, 2))
                      for i in range(n) if i % 3 != 2]
    assert sum(weight * sum(z[i] for i in coalition)
               for _, coalition, weight in singleton_rows) == 2 * m
    assert [sum(weight for _, coalition, weight in singleton_rows if i in coalition)
            for i in range(n)] == [Q(1, 2) if i % 3 != 2 else Q(0) for i in range(n)]
    return {
        "m": m, "owners": n, "resource_rows": 3 * n,
        "profiles": len(profiles), "comparisons": len(edges),
        "activity_arity": 3, "protected_size": 2,
        "L": str(objective), "D": str(budget),
        "L_over_D": str(objective / budget),
        "symbolic_repair_lower_over_D": str(repair_lower / budget),
        "explicit_repair_upper_over_D": str(repair_upper / budget),
        "optimal_variant_L": str(optimal_objective),
        "optimal_variant_L_over_D": "1",
        "optimal_variant_all_slacks_zero": True,
        "optimal_variant_coverage_incidence_one": True,
        "optimal_variant_resource_identity_without_slack": True,
        "singleton_terminal_variant_equivalent": True,
    }


if __name__ == "__main__":
    print(json.dumps({
        "scope": "Exact fixture and incidence checks; all-profile/layer impossibility is the symbolic proof, not finite testing.",
        "cases": [check(m) for m in (1, 2, 4, 8, 16, 64)],
    }, indent=2))
