#!/usr/bin/env python3
"""Bounded discovery test: all perfect-matching rows of irregular bipartite graphs.

This imports the frozen normalized formulation. It never substitutes a subset
of perfect matchings and computes every edge owner's optimization. The graph
families are sparse structural perturbations: a deleted circulant edge, a
deleted bidirected cycle edge, a path of adjacent transpositions, and star
swaps with a peripheral directed triangle. Stop on any H>1 signal: even below
the campaign's H>2 threshold this refutes the tentative matching-family H=1
claim. Numerical nonhits are not a theorem.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import time

import numpy as np
import normalized_mass_search as core


def cases():
    for N in (5,6):
        cyclic={(j,(j+d)%N) for j in range(N) for d in (0,1,2)}-{(0,2)}
        yield f'circulant3_delete_edge_N{N}',N,cyclic
        cyclic={(j,(j+d)%N) for j in range(N) for d in (-1,0,1)}-{(0,1)}
        yield f'bidirected_cycle_delete_edge_N{N}',N,cyclic
        path={(j,j) for j in range(N)}|{(j,j+1) for j in range(N-1)}|{(j+1,j) for j in range(N-1)}
        yield f'path_transpositions_N{N}',N,path
        star={(j,j) for j in range(N)}|{(0,j) for j in range(1,N)}|{(j,0) for j in range(1,N)}
        star|={(1,2),(2,3),(3,1)}
        yield f'star_peripheral_triangle_N{N}',N,star


def matrix(N,edges):
    perms=[perm for perm in itertools.permutations(range(N)) if all((j,perm[j]) in edges for j in range(N))]
    labels=sorted({(j,perm[j]) for perm in perms for j in range(N)});index={v:j for j,v in enumerate(labels)}
    rows=[sorted(index[(j,perm[j])] for j in range(N)) for perm in perms]
    A=np.array([[int(j in S) for j in range(len(labels))] for S in rows],dtype=float)
    return A,labels,perms


def exact_full(report):
    rows=report['rows'];n=report['n']
    q=[F(float(x)).limit_denominator(1000000) for x in report['full']['q']]
    lam=[F(float(x)).limit_denominator(1000000) for x in report['full']['lambda']]
    ok=all(x>=0 for x in q+lam)
    ok=ok and all(q[j]==sum((lam[r] for r,S in enumerate(rows) if j in S),F(0)) for j in range(n))
    ok=ok and all(sum(q[j] for j in S)>=1 and lam[r]*(sum(q[j] for j in S)-1)==0 for r,S in enumerate(rows))
    return {'certified':ok,'q':list(map(str,q)),'lambda':list(map(str,lam)),'rho':str(sum(x*x for x in q))}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--seconds',type=float,default=3);parser.add_argument('--budget',type=float,default=800);args=parser.parse_args()
    todo=list(cases());started=time.monotonic();results=[]
    payload={'discovery_only':True,'question':'Does any all-perfect-matchings incidence cover of these irregular bipartite graphs have H>1?','formulation_sha256':hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest(),'results':results,'planned_cases':len(todo),'pending_cases':[c[0] for c in todo]}
    for name,N,edges in todo:
        if time.monotonic()-started>args.budget:break
        A,labels,perms=matrix(N,edges)
        report=core.analyze(A,name,seconds=args.seconds)
        report['bipartite_order']=N;report['column_labels']=labels;report['perfect_matchings']=perms
        report['allowed_graph_edges']=sorted(edges)
        report['left_degrees']=[sum((j,k) in edges for k in range(N)) for j in range(N)]
        report['right_degrees']=[sum((j,k) in edges for j in range(N)) for k in range(N)]
        report['full']['fraction_certificate']=exact_full(report)
        report['H_above_one']=report['H'] is not None and report['H']>1+1e-7
        report['H_exact']=None
        if report['exact_witnesses'] and report['full']['fraction_certificate']['certified']:
            rho=F(report['full']['fraction_certificate']['rho'])
            report['H_exact']=str(rho*sum(F(o['exact']['theta'])**2 for o in report['owners']))
        results.append(report);payload['pending_cases'].remove(name);payload['elapsed']=time.monotonic()-started
        payload['timed_out_cases']=[r['name'] for r in results if any(o['status']==1 for o in r['owners'])]
        Path(args.output).write_text(json.dumps(payload,indent=2)+'\n')
        print(json.dumps({key:report[key] for key in ('name','n','m','H','H_exact','H_solver_upper','all_milp_optimal','H_above_one')}),flush=True)
        if report['H_above_one']:break


if __name__=='__main__':main()
