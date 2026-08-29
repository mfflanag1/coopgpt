#!/usr/bin/env python3
"""Independent active-tangent replay for the all-m H_m theorem.

This file imports no project code and does not use the symbolic verifier.
It constructs the lower envelopes directly for m=1,2,3,4, checks the closed
forms, and proves every staged selector condition by fresh QF_LRA tangent
infeasibility queries.  The paper's incidence proof, not these finite
instances, supplies the universal quantifier m>=1.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3


def family(m):
    x=(F(1),)*m+(F(3*m),F(5*m),F(1),F(1),F(1),F(1))
    B=(F(0),)*m+(F(0),F(0),F(4*m+1),F(2*m+1),F(2*m+1),F(m+1))
    C=(F(0),)*m+(F(3*m+2),F(6*m+2),F(0),F(0),F(0),F(0))
    D=(F(0),)*m+(F(0),F(7*m+1,2),F(m+1,2),F(2*m+1),F(2*m+1),F(m+1))
    z=(F(1,5*m),)*m+(F(3,5),F(10*m+3,5),F(10*m+3,5),
                       F(10*m+3,5),F(10*m+3,5),F(5*m+4,5))
    return (x,B,C,D),x,z


def csum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask>>i&1),F(0))


def q(value): return z3.Q(value.numerator,value.denominator)


def blocks(point,reverse):
    return [tuple(i for i,a in enumerate(point) if a==level)
            for level in sorted(set(point),reverse=reverse)]


def tangent(values,point,mode):
    n=len(point); active=[s for s in range(1,(1<<n)-1) if csum(point,s)==values[s]]
    earlier=[]; audit=[]
    for stage,block in enumerate(blocks(point,mode=="max")):
        for player in block:
            d=[z3.Real(f"d_{mode}_{n}_{stage}_{player}_{i}") for i in range(n)]
            solver=z3.SolverFor("QF_LRA"); solver.add(z3.Sum(d)==0)
            for s in active:
                solver.add(z3.Sum([d[i] for i in range(n) if s>>i&1])>=0)
            for i,a in enumerate(point):
                if a==0: solver.add(d[i]>=0)
            for i in earlier: solver.add(d[i]==0)
            if mode=="min": solver.add(*[d[i]>=0 for i in block],d[player]>=1)
            else: solver.add(*[d[i]<=0 for i in block],d[player]<=-1)
            verdict=solver.check(); assert verdict==z3.unsat,(n,mode,stage,player,verdict)
            audit.append({"stage":stage,"player":player,"status":"unsat"})
        earlier.extend(block)
    return active,audit


def verify(m):
    gens,x,z=family(m);n=m+6;T=F(9*m+4)
    assert all(sum(g,F(0))==T and min(g)>=0 for g in gens)
    values=tuple(min(csum(g,s) for g in gens) for s in range(1<<n))
    assert values[-1]==T and all(values[1<<i]==0 for i in range(n))
    for point in (x,z):
        assert sum(point,F(0))==T
        assert all(csum(point,s)>=values[s] for s in range(1<<n))
    xa,xc=tangent(values,x,"min");za,zc=tangent(values,z,"max")
    rho=sum(abs(a-b) for a,b in zip(x,z))/T
    assert rho==F(14*(5*m-1),5*(9*m+4))
    return {"m":m,"n":n,"total":str(T),"Lmin":list(map(str,x)),"Lmax":list(map(str,z)),
            "rho":str(rho),"Lmin_active_count":len(xa),"Lmax_active_rows":za,
            "Lmin_tangent_checks":xc,"Lmax_tangent_checks":zc}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path);args=parser.parse_args()
    cases=[verify(m) for m in range(1,5)]
    payload={"claim":"independent active-tangent calibration of PXC146 for m=1,2,3,4",
             "implementation":"standalone Z3 QF_LRA; no project or primary-verifier imports",
             "universal_scope":"the conventional symbolic incidence proof supplies m>=1; this replay is a finite independent calibration",
             "cases":cases}
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output:args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__":main()
