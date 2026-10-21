#!/usr/bin/env python3
"""Independent exact common-veto caps and direct real-report checks."""
from fractions import Fraction as F
from itertools import combinations, product
import json


def inverse(matrix):
    n = len(matrix)
    work = [[F(x) for x in row] + [F(int(i == j)) for j in range(n)]
            for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if work[r][col]), None)
        if pivot is None:
            return None
        work[col], work[pivot] = work[pivot], work[col]
        divisor = work[col][col]
        work[col] = [x / divisor for x in work[col]]
        for row in range(n):
            if row != col:
                factor = work[row][col]
                work[row] = [x - factor * y for x, y in zip(work[row], work[col])]
    return [row[n:] for row in work]


class Projection:
    def __init__(self, rows):
        self.rows = [tuple(row) for row in rows]
        self.n = len(rows[0])
        self.supports = []
        for size in range(1, min(len(rows), self.n) + 1):
            for indices in combinations(range(len(rows)), size):
                gram = [[sum(a * b for a, b in zip(rows[i], rows[j]))
                         for j in indices] for i in indices]
                inv = inverse(gram)
                if inv is not None:
                    self.supports.append((indices, inv))

    def solve(self, demands):
        demands = tuple(map(F, demands))
        if not any(demands):
            return [F(0)] * self.n, [F(0)] * len(self.rows)
        for indices, inv in self.supports:
            multipliers = [sum(a * demands[j] for a, j in zip(row, indices))
                           for row in inv]
            if any(x < 0 for x in multipliers):
                continue
            point = [sum(value * self.rows[row][col]
                         for row, value in zip(indices, multipliers))
                     for col in range(self.n)]
            if any(sum(a * x for a, x in zip(row, point)) < rhs
                   for row, rhs in zip(self.rows, demands)):
                continue
            full = [F(0)] * len(self.rows)
            for row, value in zip(indices, multipliers):
                full[row] = value
            assert all(x >= 0 for x in point)
            assert sum(x * x for x in point) == sum(a * b for a, b in zip(full, demands))
            return point, full
        raise ValueError('No feasible KKT support found')


def check_block_case(blocks):
    sizes = [len(block[0]) for block in blocks]
    offsets = []
    position = 1
    for size in sizes:
        offsets.append(position)
        position += size
    rows, row_blocks = [], []
    base_solvers = [Projection(block) for block in blocks]
    base_points = [solver.solve([1] * len(block))[0]
                   for solver, block in zip(base_solvers, blocks)]
    rhos = [sum(x * x for x in point) for point in base_points]
    total_rho = sum(rhos)
    for c, block in enumerate(blocks):
        for base_row in block:
            row = [0] * position
            row[0] = 1
            row[offsets[c]:offsets[c] + sizes[c]] = base_row
            rows.append(row)
            row_blocks.append(c)
    solver = Projection(rows)
    full, _ = solver.solve([1] * len(rows))
    assert full[0] == total_rho / (1 + total_rho)
    assert sum(x * x for x in full) == full[0]
    caps = [full[0]] + [rhos[c] / (1 + total_rho)
                       for c in range(len(blocks)) for _ in range(sizes[c])]
    grid = (F(0), F(1, 3), F(2, 3), F(1))
    cases = clipped = 0
    maxima = [F(0)] * position
    for owner in range(position):
        incident = [r for r, row in enumerate(rows) if row[owner]]
        for values in product(grid, repeat=len(incident)):
            demands = [F(1)] * len(rows)
            for row, value in zip(incident, values):
                demands[row] = value
            q, multipliers = solver.solve(demands)
            cases += 1
            maxima[owner] = max(maxima[owner], q[owner])
            assert q[0] == sum(multipliers) <= caps[0] < 1
            assert q[owner] <= caps[owner]
            if owner == 0:
                continue
            c = next(c for c in range(len(blocks))
                     if offsets[c] <= owner < offsets[c] + sizes[c])
            h = 1 - q[0]
            local_rows = [r for r, block in enumerate(row_blocks) if block == c]
            residuals = [max(F(0), (demands[r] - q[0]) / h) for r in local_rows]
            local_point, local_lam = base_solvers[c].solve(residuals)
            assert local_point == [x / h for x in q[offsets[c]:offsets[c] + sizes[c]]]
            mass = sum(multipliers[r] / h for r in local_rows)
            assert 0 <= mass <= rhos[c]
            assert local_point[owner - offsets[c]] <= mass
            assert q[0] == h * (total_rho - rhos[c] + mass)
            for row in local_rows:
                if demands[row] <= q[0]:
                    assert multipliers[row] == 0
                    clipped += int(demands[row] < q[0])
            for other in range(len(blocks)):
                if other != c:
                    assert q[offsets[other]:offsets[other] + sizes[other]] == [h * x for x in base_points[other]]
    assert maxima[0] == caps[0]
    condition_b = all(size * rho <= 4 for size, rho in zip(sizes, rhos))
    condition_c = all((size + 1) ** 2 * rho <= 4 * size for size, rho in zip(sizes, rhos))
    if condition_b:
        assert sum(cap * cap for cap in caps) <= F(4, 3)
    if condition_c:
        assert sum(caps) ** 2 <= sum(sizes)
    return {'private_owners': sum(sizes), 'rows': len(rows),
            'exact_KKT_witnesses': cases, 'strictly_negative_residuals_checked': clipped,
            'squared_condition': condition_b, 'funding_condition': condition_c}


def make_production(n, rows, demands):
    subsets = [frozenset(i for i in range(n) if mask >> i & 1) for mask in range(1 << n)]
    def game(array):
        return {s: max([a for row, a in zip(rows, array) if row <= s] + [F(0)])
                for s in subsets}
    v = game([F(1)] * len(rows))
    games = [game(array) for array in demands]
    def supporting(g):
        return [tuple(F(1) if i not in a else g[a] if i == 0 else F(0)
                      for i in range(n)) for a in subsets[1:]]
    forms = [h + (F(0),) * n for h in supporting(v)]
    for owner, g in enumerate(games):
        forms += [h + tuple(F(int(i == owner)) for i in range(n)) for h in supporting(g)]
    def production(x, z):
        aggregate = tuple(x) + tuple(z)
        return min(sum(a * b for a, b in zip(form, aggregate)) for form in forms)
    return subsets, v, games, production


def real_report_checks():
    n = 4
    rows = [frozenset(row) for row in ((0, 1), (0, 2), (0, 1, 3), (0, 2, 3))]
    demands = [[F(1)] * len(rows)]
    for owner in range(1, n):
        demands.append([F((owner + r) % 5, 4) if owner in row else F(1)
                        for r, row in enumerate(rows)])
    subsets, v, games, production = make_production(n, rows, demands)
    grid = (F(0), F(1, 3), F(1, 2), F(1))
    count = boundary = 0
    for owner in range(n):
        for t, z in product(grid, repeat=2):
            for s in subsets:
                x = [t if i == owner else F(1) if i in s else F(0) for i in range(n)]
                control = [z if i == owner else F(1) if i in s else F(0) for i in range(n)]
                if owner not in s:
                    x[owner] = control[owner] = F(0)
                actual = production(x, control)
                if owner == 0:
                    expected = t * v[s]
                else:
                    rhs = [min(F(1), t, demands[owner][r] + z) if owner in row else F(1)
                           for r, row in enumerate(rows)]
                    expected = max([a for row, a in zip(rows, rhs) if row <= s] + [F(0)])
                    if owner in s:
                        assert actual == min(v[s], v[s - {owner}] + t, games[owner][s] + z)
                assert actual == expected
                count += 1
                boundary += int(len(s) <= 1)
    # Test fractional-game veto forms separately from the control branches.
    veto_form_checks = 0
    for g in [v] + games:
        forms = [tuple(F(1) if i not in a else g[a] if i == 0 else F(0)
                       for i in range(n)) for a in subsets[1:]]
        for t in grid:
            for s in subsets:
                point = [t if i == 0 and i in s else F(int(i in s)) for i in range(n)]
                value = min(sum(a * b for a, b in zip(form, point)) for form in forms)
                assert value == t * g[s]
                veto_form_checks += 1
    # Exact refutation of the cross-model review's proposed counterexample.
    fractional_forms = [(F(0), F(1)), (F(1), F(0)), (F(1, 2), F(0))]
    point = (F(1, 2), F(1))
    form_values = [sum(a * b for a, b in zip(form, point)) for form in fractional_forms]
    assert form_values == [F(1), F(1, 2), F(1, 4)]
    assert min(form_values) == F(1, 2) * F(1, 2) != min(F(1, 2), F(1, 2))
    # An admissible simultaneous underreport need not preserve the generators.
    two_rows = [frozenset((0, 1)), frozenset((0, 2))]
    ss, _, _, function = make_production(3, two_rows, [[1, 1], [0, 1], [1, 0]])
    values = {}
    for s in ss:
        values[s] = function([F(int(i in s)) for i in range(3)],
                             [F(int(i == 0 and i in s)) for i in range(3)])
    assert values[two_rows[0]] == values[two_rows[1]] == 0
    assert values[frozenset(range(3))] == 1
    # Empty base row is invalid; after adding a veto, it can force u=1.
    try:
        Projection([[0]]).solve([1])
    except ValueError:
        pass
    else:
        raise AssertionError('Empty unit-demand base row was incorrectly feasible')
    assert Projection([[1, 0]]).solve([1])[0] == [1, 0]
    return {'real_report_coalition_values': count, 'empty_or_singleton_checks': boundary,
            'veto_supporting_form_checks': veto_form_checks,
            'cross_model_counterexample_form_values': [str(x) for x in form_values],
            'simultaneous_report_scope_counterexample': ['0', '0', '1'],
            'empty_base_row_rejected': True}


def main():
    block_cases = [
        [[[1, 0], [0, 1]], [[1, 1, 0], [1, 0, 1], [0, 1, 1]]],
        [[[1, 1]], [[1, 1, 0], [1, 0, 1], [0, 1, 1]], [[1]]],
    ]
    results = [check_block_case(blocks) for blocks in block_cases]
    real = real_report_checks()
    print(json.dumps({'verified': True,
                      'scope': 'Caps at the designated full bundles; every unilateral real underreport.',
                      'block_cases': results, 'real_report_checks': real}, indent=2))


if __name__ == '__main__':
    main()
