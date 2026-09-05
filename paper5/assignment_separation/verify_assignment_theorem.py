"""Independent full-coalition checks of the candidate structural theorems."""
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
import json
import z3
from exact_assignment import Q, require, core, check, optimize


def positive_matching_size(matrix):
    m, k = len(matrix), len(matrix[0])
    scores = []
    if m <= k:
        for order in permutations(range(k), m):
            weights = [F(matrix[i][j]) for i, j in enumerate(order)]
            scores.append((sum(weights), sum(w > 0 for w in weights)))
    else:
        for order in permutations(range(m), k):
            weights = [F(matrix[i][j]) for j, i in enumerate(order)]
            scores.append((sum(weights), sum(w > 0 for w in weights)))
    total = max(t for t, _ in scores)
    return min(count for t, count in scores if t == total)


def structural_check(record):
    matrix = record['matrix']
    players, constraints, total = core(matrix, full=True)
    x = list(map(F, record['Lmin']))
    z = list(map(F, record['Lmax']))
    caps = [optimize(constraints, player, True) for player in players]
    require(all(cap <= 2*pay for cap, pay in zip(caps,x)), 'half-payoff domination failed')
    k = positive_matching_size(matrix)
    bound = F(0) if k == 1 else F(k,k+1)
    require(F(record['rho']) <= bound, 'finite selector bound failed')
    # Prove the bound against every minimax point with an exact piecewise
    # linear L1 expression, only on the small calibration cases (n<=8).
    universal_minimax = None
    if len(players) <= 8:
        ceiling = max(z)
        s = z3.Solver()
        s.set(timeout=120000)
        s.add(*constraints, *[p <= Q(ceiling) for p in players])
        distance = sum(z3.If(p >= Q(v), p-Q(v), Q(v)-p) for p,v in zip(players,x))
        s.add(distance > Q(total*bound))
        verdict = s.check()
        require(verdict == z3.unsat, 'some minimax point violates finite bound')
        universal_minimax = str(verdict)
    return dict(n=len(players), positive_matching_size=k, bound=str(bound), maximum_core_payoffs=list(map(str,caps)), half_domination=True, all_minimax_points=universal_minimax)


def exactness_check(matrix):
    players, constraints, total = core(matrix, full=True)
    from exact_assignment import coalition_value
    m, k = len(matrix), len(matrix[0])
    for mask in range(1,2**(m+k)-1):
        rows = [i for i in range(m) if mask >> i & 1]
        cols = [j for j in range(k) if mask >> (m+j) & 1]
        ids = rows+[m+j for j in cols]
        worth = coalition_value(matrix, rows, cols)
        attained = optimize(constraints,sum(players[i] for i in ids),False)
        if attained != worth:
            return dict(exact=False, witness_coalition=ids, worth=str(worth), minimum_core_sum=str(attained))
    return dict(exact=True)


def negative_controls():
    # A first-stage maximin point may fail half domination because of fixed zeros.
    matrix = [[1,0],[0,0]]
    players, constraints, total = core(matrix,full=True)
    bad_x = [F(1),F(0),F(0),F(0)]
    y = [F(0),F(0),F(1),F(0)]
    floor = z3.FreshReal('floor')
    require(optimize(constraints+[p>=floor for p in players],floor,True)==0, 'negative floor is not optimal')
    for point in (bad_x,y):
        require(all(z3.is_true(z3.simplify(z3.substitute(c,*[(p,Q(v)) for p,v in zip(players,point)]))) for c in constraints),'negative point infeasible')
    require(y[2] > 2*bad_x[2], 'first-stage negative control failed')

    # The finite correction needs a minimax comparison point.
    record = check([[1,1],[1,1]])
    x = list(map(F,record['Lmin']))
    arbitrary = [F(0),F(0),F(1),F(1)]
    players, constraints, _ = core([[1,1],[1,1]],full=True)
    require(all(z3.is_true(z3.simplify(z3.substitute(c,*[(p,Q(v)) for p,v in zip(players,arbitrary)]))) for c in constraints),'arbitrary-core control infeasible')
    rho = sum(abs(a-b) for a,b in zip(x,arbitrary))/2
    require(rho == 1 and rho > F(2,3), 'arbitrary-core negative control failed')
    return dict(first_stage_only=dict(matrix=matrix,maximin_point=list(map(str,bad_x)),other_core_point=list(map(str,y))), arbitrary_core_comparison=dict(matrix=[[1,1],[1,1]],Lmin=record['Lmin'],other_core_point=list(map(str,arbitrary)),rho=str(rho)))


if __name__ == '__main__':
    here = Path(__file__).parent
    bounded = json.loads((here/'two_by_two_calibration.json').read_text())
    require(len(bounded['cases']) == 255, 'wrong bounded input coverage')
    enriched = []
    for record in bounded['cases']:
        enriched.append(dict(matrix=record['matrix'], **structural_check(record)))
    print('PASS half domination and finite bound on all 255 matrices',flush=True)

    matrices = [
        [[1,1,2]]*3,
        [[1,1,1]]*3,
        [[3,0,0],[0,2,0],[0,0,1]],
        [[2,1,0],[2,1,0],[0,0,0]],
        [[4,6,1],[2,3,5],[5,1,4]],
        [[1,2,0],[1,2,0]],
        [[2],[1]],
    ]
    targeted = []
    for matrix in matrices:
        record = check(matrix)
        record['structural'] = structural_check(record)
        record['exactness'] = exactness_check(matrix)
        if record['exactness']['exact']:
            require(record['rho'] == '0', 'exact assignment agreement failed')
        targeted.append(record)
        print('PASS targeted',len(matrix),len(matrix[0]),record['rho'],flush=True)

    families = []
    for k in (2,3,4,5,6):
        matrix = [[1]*(k-1)+[2] for _ in range(k)]
        record = check(matrix)
        require(F(record['rho']) == F(k,k+1), 'attaining family formula failed')
        players,constraints,total=core(matrix,full=True)
        t=players[0]
        proposed=[players[i]==t for i in range(k)]+[players[k+j]==Q(matrix[0][j])-t for j in range(k)]
        solver=z3.Solver()
        solver.set(timeout=120000)
        solver.add(*constraints,z3.Not(z3.And(*proposed)))
        require(solver.check()==z3.unsat,'attaining core is not a segment')
        record['entire_core_segment']=True
        families.append(record)
        print('PASS attaining family',k,record['rho'],flush=True)

    controls=negative_controls()
    print('PASS both negative controls',flush=True)
    payload=dict(evidence='Exact finite calibration; conventional theorem separate',two_by_two=enriched,targeted=targeted,attaining_families=families,negative_controls=controls)
    (here/'assignment_theorem_calibration.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
