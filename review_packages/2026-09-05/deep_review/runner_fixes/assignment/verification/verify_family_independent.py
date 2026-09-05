from verification_io import RESULTS
"""Exact raw-polytope calibration of the independent construction generator."""
from fractions import Fraction as F
import json
from pathlib import Path
import z3
from triple_recurrence_family import build_family, require
from exact_three import Q, selector, optimize


def verify(levels, copies):
    game = build_family(levels, copies)
    names = sum(game['sectors'], [])
    var = {n: z3.FreshReal(n) for n in names}
    players = [var[n] for n in names]
    core = [p>=0 for p in players] + [sum(players)==game['total']]
    core += [sum(var[n] for n in edge)>=value for edge,value in game['weights'].items()]
    x, xstages = selector(core, players, True)
    z, zstages = selector(core, players, False)
    require(x==[game['lmin'][n] for n in names], 'full leximin disagrees')
    require(z==[game['lmax'][n] for n in names], 'full leximax-min disagrees')
    topv = game['pairs'][f'L{levels}',0][1]
    maximum = optimize(core, var[topv], True)
    require(maximum==1, 'coordinate max is not 1')
    expected_ratio = F(2,2**levels+2)
    require(game['lmin'][topv]/maximum==expected_ratio, 'coordinate ratio mismatch')
    # Check all raw-core points satisfy the proposed parametrization.
    q = [var[game['pairs']['L0',i][0]]-1 for i in range(3)]
    required = [var[g]==0 for g in game['globals']]+[a>=0 for a in q]
    for level in range(levels+1):
        for i in range(3):
            u,v,d = game['pairs'][f'L{level}',i]
            required.extend([var[d]==0,var[u]==q[i]+(1 if level==0 else 0),var[v]==1-q[i]])
        if level != levels:
            q = [sum(q[j] for j in range(3) if j!=i) for i in range(3)]
    for copy in range(copies):
        for i in range(3):
            u,v,d = game['pairs'][f'R{copy}',i]
            required.extend([var[d]==0,var[u]==q[i],var[v]==1-q[i]])
    solver = z3.Solver(); solver.set(timeout=60000)
    solver.add(*core,z3.Not(z3.And(required)))
    require(solver.check()==z3.unsat,'raw core extends outside proposed parametrization')
    result = dict(L=levels,R=copies,n=len(players),T=game['total'],rho=str(game['rho']),
                  coordinate_ratio=str(expected_ratio),x_stages=xstages,z_stages=zstages,
                  sparse_positive_triples=len(game['weights']),
                  raw_full_selector_equalities=True,raw_entire_core_inclusion=True,
                  coordinate_maximum=str(maximum))
    print('PASS', {k:result[k] for k in ['L','R','n','T','rho','coordinate_ratio']},flush=True)
    return result


if __name__=='__main__':
    records = [verify(L,R) for L,R in [(1,0),(2,1),(3,0),(4,16)]]
    (RESULTS/'independent_family_calibration.json').write_text(json.dumps(records,indent=2)+'\n')
