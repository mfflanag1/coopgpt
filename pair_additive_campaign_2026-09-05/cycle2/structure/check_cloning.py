"""Fresh raw LRA checks of matched-team cloning; no campaign scientific imports."""
from fractions import Fraction as F
from itertools import product, permutations
from pathlib import Path
import hashlib
import json
import z3


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def q(value):
    return z3.RealVal(str(value))


queries = 0


def impossible(constraints, bad, label):
    global queries
    solver = z3.Solver()
    solver.set(timeout=30000)
    solver.add(*constraints, bad)
    status = solver.check()
    queries += 1
    require(status == z3.unsat, label + ': expected UNSAT, got ' + str(status))


A = ((0, 0, 0), (2, 0, 1), (0, 1, 0))
B = ((0, 0, 1), (1, 0, 0), (0, 0, 0))
C = ((0, 1, 0), (3, 0, 0), (2, 0, 0))
match = ((0, 2, 2), (1, 0, 1), (2, 1, 0))
x = tuple(map(F, ('1/3', '4/3', '5/6', '5/6', '5/6', '1/3', '7/3', '5/6', '1/3')))
z = tuple(map(F, ('0', '3/2', '1', '1', '3/2', '1', '3/2', '1/2', '0')))


def weight(i, j, k):
    return A[i][j]+B[i][k]+C[j][k]


def core(values, types, T):
    m = len(types[0])
    return ([v >= 0 for v in values] + [z3.Sum(values) == T] +
            [values[i]+values[m+j]+values[2*m+k] >= weight(types[0][i], types[1][j], types[2][k])
             for i, j, k in product(range(m), repeat=3)])


def exact_selector(constraints, values, candidate, ascending, name):
    face = list(constraints)
    remaining = set(range(len(values)))
    for alpha in sorted(set(candidate), reverse=not ascending):
        group = [u for u in remaining if candidate[u] == alpha]
        strict = [values[u] > q(alpha) if ascending else values[u] < q(alpha)
                  for u in remaining]
        impossible(face, z3.And(strict), name+' stage improvement '+str(alpha))
        face += [values[u] >= q(alpha) if ascending else values[u] <= q(alpha)
                 for u in remaining]
        impossible(face, z3.Or([values[u] != q(alpha) for u in group]),
                   name+' forced coordinates '+str(alpha))
        face += [values[u] == q(alpha) for u in group]
        remaining.difference_update(group)
    require(not remaining, 'all selector coordinates checked')


cases = []
for r in ((1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2),
          (2, 2, 1), (1, 2, 2), (2, 2, 2)):
    types = [[match[t][s] for t in range(3) for _ in range(r[t])] for s in range(3)]
    m = sum(r)
    Tr = sum(r[t]*weight(*match[t]) for t in range(3))
    values = z3.Reals(' '.join('p_'+str(s)+'_'+str(i) for s in range(3) for i in range(m)))
    constraints = core(values, types, Tr)
    lx = tuple(x[3*s+t] for s in range(3) for t in types[s])
    lz = tuple(z[3*s+t] for s in range(3) for t in types[s])
    for candidate in (lx, lz):
        require(all(v >= 0 for v in candidate) and sum(candidate) == Tr, 'lift efficiency')
        require(all(candidate[i]+candidate[m+j]+candidate[2*m+k] >= weight(types[0][i], types[1][j], types[2][k])
                    for i, j, k in product(range(m), repeat=3)), 'lift cover')
    representatives = [values[s*m+types[s].index(t)] for s in range(3) for t in range(3)]
    bad = [values[s*m+i] != representatives[3*s+types[s][i]]
           for s in range(3) for i in range(m)]
    bad += [z3.Not(z3.And(core(representatives, [list(range(3))]*3, 8)))]
    impossible(constraints, z3.Or(bad), 'expanded core must be replicated original '+str(r))
    original = z3.Reals('a b c d e f g h i')
    original_constraints = core(original, [list(range(3))]*3, 8)
    lift = [original[3*s+t] for s in range(3) for t in types[s]]
    impossible(original_constraints, z3.Not(z3.And(core(lift, types, Tr))), 'every original core point lifts')
    exact_selector(constraints, values, lx, True, 'leximin '+str(r))
    exact_selector(constraints, values, lz, False, 'descending '+str(r))
    formula = sum(F(r[t])*sum(abs(x[u]-z[u]) for u in (match[t][0],3+match[t][1],6+match[t][2])) for t in range(3))/Tr
    require(sum(abs(a-b) for a, b in zip(lx, lz))/Tr == formula, 'distance identity')
    cases.append({'r': r, 'sector_size': m, 'T': Tr, 'rho': str(formula), 'status': 'PASS'})

# Reanalyze all optimal matchings of the existing floating screen; no new instances.
source = Path(__file__).resolve().parents[2] / 'experiment' / 'screen_records.json'
records = json.loads(source.read_text())
top = []
count = 0
for record in records:
    if not all(key in record for key in ('x', 'z', 'A', 'B', 'C')):
        continue
    m = record['m']
    aa, bb, cc = record['A'], record['B'], record['C']
    ww = lambda i,j,k: aa[i][j]+bb[i][k]+cc[j][k]
    matching_values = [(sum(ww(i,p[i],rr[i]) for i in range(m)), p, rr)
                       for p in permutations(range(m)) for rr in permutations(range(m))]
    optimum = max(entry[0] for entry in matching_values)
    teams = {(i,p[i],rr[i]) for total,p,rr in matching_values if total == optimum for i in range(m)}
    count += 1
    for i,j,k in teams:
        value = ww(i,j,k)
        if value:
            delta = sum(abs(record['x'][u]-record['z'][u]) for u in (i,m+j,2*m+k))
            top.append({'ratio_float': delta/value, 'label': record['label'], 'team': (i,j,k), 'weight': value})
top.sort(key=lambda row: row['ratio_float'], reverse=True)
print(json.dumps({'status': 'PASS', 'solver': z3.get_version_string(), 'queries': queries,
                  'unknown_policy': 'Any status except UNSAT raises; no optimization used',
                  'clone_cases': cases,
                  'saved_screen': {'source': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                                   'records_total': len(records), 'records_with_selectors': count,
                                   'all_optimal_matchings_scanned': True, 'top_local_ratios': top[:12],
                                   'scope': 'Floating discovery reanalysis; no novelty or exhaustive class claim'}}, indent=2))
