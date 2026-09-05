"""Rational assignment-core and complete lexicographic selector calibration."""
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import json
import z3


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def Q(value):
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def rational(value):
    value = z3.simplify(value)
    if z3.is_int_value(value):
        return F(value.as_long())
    require(z3.is_rational_value(value), 'non-rational or unbounded optimum')
    return F(value.numerator_as_long(), value.denominator_as_long())


def optimize(constraints, objective, upward):
    solver = z3.Optimize()
    solver.set(timeout=60000)
    solver.add(*constraints)
    handle = solver.maximize(objective) if upward else solver.minimize(objective)
    require(solver.check() == z3.sat, 'optimization failed or UNKNOWN')
    return rational(handle.value())


def selector(constraints, players, upward):
    fixed = {}
    stages = []
    while len(fixed) < len(players):
        free = [i for i in range(len(players)) if i not in fixed]
        prefix = constraints + [players[i] == Q(v) for i, v in fixed.items()]
        level = z3.FreshReal('level')
        caps = [players[i] >= level if upward else players[i] <= level for i in free]
        value = optimize(prefix + caps, level, upward)
        face = prefix + [players[i] >= Q(value) if upward else players[i] <= Q(value) for i in free]
        pinned = [i for i in free if optimize(face, players[i], upward) == value]
        require(bool(pinned), 'no coordinate fixed on optimal face')
        fixed.update({i: value for i in pinned})
        stages.append(dict(level=str(value), players=pinned))
    return [fixed[i] for i in range(len(players))], stages


def coalition_value(matrix, rows, cols):
    if not rows or not cols:
        return F(0)
    # Nonnegative complete matrices permit completion of a partial matching.
    if len(rows) <= len(cols):
        return max(sum(F(matrix[i][j]) for i, j in zip(rows, order)) for order in permutations(cols, len(rows)))
    return max(sum(F(matrix[i][j]) for i, j in zip(order, cols)) for order in permutations(rows, len(cols)))


def core(matrix, full=False):
    m, k = len(matrix), len(matrix[0])
    require(all(len(row) == k and all(F(v) >= 0 for v in row) for row in matrix), 'invalid matrix')
    total = coalition_value(matrix, list(range(m)), list(range(k)))
    require(total > 0, 'zero total is outside normalized problem')
    players = list(z3.Reals(' '.join(f'w{i}' for i in range(m+k))))
    constraints = [p >= 0 for p in players] + [sum(players) == Q(total)]
    if full:
        for mask in range(1, 2**(m+k)-1):
            rows = [i for i in range(m) if mask >> i & 1]
            cols = [j for j in range(k) if mask >> (m+j) & 1]
            value = coalition_value(matrix, rows, cols)
            ids = rows + [m+j for j in cols]
            constraints.append(sum(players[i] for i in ids) >= Q(value))
    else:
        constraints += [players[i] + players[m+j] >= Q(matrix[i][j]) for i in range(m) for j in range(k)]
    return players, constraints, total


def check(matrix, full=True):
    players, constraints, total = core(matrix, full=full)
    x, min_stages = selector(constraints, players, True)
    z, max_stages = selector(constraints, players, False)
    rho = sum(abs(a-b) for a, b in zip(x, z)) / total
    require(rho <= 2-F(2, len(players)-1), 'generic bound failed')
    return dict(matrix=matrix, n=len(players), T=str(total), Lmin=list(map(str,x)), Lmax=list(map(str,z)), rho=str(rho), Lmin_stages=min_stages, Lmax_stages=max_stages, full_coalitions=full)


if __name__ == '__main__':
    records = []
    best = F(-1)
    for values in product(range(4), repeat=4):
        if not any(values):
            continue
        matrix = [list(values[:2]), list(values[2:])]
        result = check(matrix)
        records.append(result)
        rho = F(result['rho'])
        if rho > best:
            best = rho
            print('NEW BOUNDED BEST',result,flush=True)
    require(len(records) == 255, 'coverage mismatch')
    payload = dict(scope='Every 2-by-2 matrix with entries 0,1,2,3 except the zero matrix; no symmetry quotient', cases=records, maximum_rho=str(best))
    Path(__file__).with_name('two_by_two_calibration.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print('PASS 255 full-coalition complete-selector cases; maximum',best,flush=True)
