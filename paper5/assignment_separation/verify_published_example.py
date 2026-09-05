"""Reconstruct Figure 1 of Vazirani arXiv:2402.11437v6 from its six edges."""
from fractions import Fraction as F
from pathlib import Path
import json
import z3
from exact_assignment import Q, check, core, require


if __name__ == '__main__':
    matrix = [[136,140,0,0],[0,76,0,0],[0,0,68,56],[0,0,0,118]]
    record = check(matrix,full=True)
    expected_min = [100,36,34,59,36,40,34,59]
    expected_max = [70,6,34,59,66,70,34,59]
    printed_min = [100,36,28,90,36,40,40,28]
    printed_max = [70,6,3,65,66,70,65,53]
    require(list(map(F,record['Lmin'])) == expected_min,'reconstructed leximin mismatch')
    require(list(map(F,record['Lmax'])) == expected_max,'reconstructed leximax-min mismatch')
    require(record['rho'] == '60/199','example distance mismatch')
    players,constraints,_ = core(matrix,full=True)
    for point in (printed_min,printed_max):
        require(all(z3.is_true(z3.simplify(z3.substitute(c,*[(p,Q(v)) for p,v in zip(players,point)]))) for c in constraints),'printed point is not feasible for transcribed graph')
    require(sorted(expected_min) > sorted(printed_min),'printed leximin is not strictly improved')
    require(sorted(expected_max,reverse=True) < sorted(printed_max,reverse=True),'printed leximax-min is not strictly improved')
    record['source'] = 'https://arxiv.org/html/2402.11437v6'
    record['printed_feasible_but_suboptimal'] = dict(Lmin=printed_min,Lmax=printed_max)
    record['independent_Lmin_fixture'] = 'https://github.com/Lluc24/leximin/blob/main/tests/fixtues.py'
    Path(__file__).with_name('published_example_replay.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('PASS exact reconstruction and both strict improvement witnesses')
