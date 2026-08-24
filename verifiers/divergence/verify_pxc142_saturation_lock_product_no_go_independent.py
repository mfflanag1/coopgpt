#!/usr/bin/env python3
"""Standalone SMT replay of the PXC142 n=6 product-route falsifier.

This file imports no project module.  It independently checks exactness and
both staged selectors and reconstructs the spectral minimum by enumeration.
The large release LP is deliberately not re-solved here: its explicit
rational primal--dual certificate is replayed by the primary verifier.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from z3 import Q, Real, Solver, Sum, sat, unsat

N=6; TOTAL=F(4); FULL=(1<<N)-1
VALUES=tuple(map(F,(
    "0","0","0","1/35","0","0","0","1/35","0","34/35","34/35","69/35",
    "0","34/35","1","69/35","0","2/35","0","3/35","1/35","2/35","1/35",
    "3/35","68/35","104/35","102/35","3","69/35","104/35","103/35","3",
    "0","1","34/35","36/35","0","1","34/35","36/35","0","1","34/35","2",
    "1/35","1","1","2","34/35","37/35","34/35","37/35","1","37/35","1",
    "37/35","68/35","3","102/35","139/35","69/35","3","103/35","4")))
X=tuple(map(F,("39/70","1/2","1/35","169/140","169/140","1/2")))
Z=tuple(map(F,("104/105","14/15","1/35","104/105","104/105","1/15")))
PHI0=F(7970384113,2714820780); PHI1=F(61849,19740)


def q(value):
    value=F(value); return Q(value.numerator,value.denominator)


def csum(point,coalition):
    return sum((point[i] for i in range(N) if coalition>>i&1),F(0))


def core(solver,y):
    solver.add(Sum(y)==q(TOTAL))
    for yi in y: solver.add(yi>=0)
    for coalition in range(1,FULL):
        solver.add(Sum([y[i] for i in range(N) if coalition>>i&1])>=q(VALUES[coalition]))


def payoff_blocks(point,reverse=False):
    levels=sorted(set(point),reverse=reverse)
    return [tuple(i for i,a in enumerate(point) if a==level) for level in levels]


def verify_selector(point,mode):
    blocks=payoff_blocks(point,reverse=(mode=="max")); previous=[]
    for stage,block in enumerate(blocks):
        free=[i for i in range(N) if i not in previous]; level=point[block[0]]
        s=Solver(); y=[Real(f"{mode}_{stage}_{i}") for i in range(N)]; core(s,y)
        for i in previous: s.add(y[i]==q(point[i]))
        if mode=="min": s.add(*[y[i]>q(level) for i in free])
        else: s.add(*[y[i]<q(level) for i in free])
        if s.check()!=unsat: raise AssertionError((mode,"level",stage))
        for i in block:
            s=Solver(); y=[Real(f"{mode}_{stage}_{i}_{j}") for j in range(N)]; core(s,y)
            for j in previous: s.add(y[j]==q(point[j]))
            if mode=="min":
                s.add(*[y[j]>=q(level) for j in free]); s.add(y[i]>q(level))
            else:
                s.add(*[y[j]<=q(level) for j in free]); s.add(y[i]<q(level))
            if s.check()!=unsat: raise AssertionError((mode,"pin",stage,i))
        previous.extend(block)


def exactness():
    for coalition in range(1<<N):
        s=Solver(); y=[Real(f"w_{coalition}_{i}") for i in range(N)]; core(s,y)
        s.add(Sum([y[i] for i in range(N) if coalition>>i&1])==q(VALUES[coalition]))
        if s.check()!=sat: raise AssertionError(("exactness",coalition))


def spectral_minimum():
    maximum=max(Z); actual=tuple(i for i,z in enumerate(Z) if z==maximum)
    # The tight top row {0,3,4}, with lambda=1/3 and eta=0, gives
    # alpha=(1/3,0,0,1/3,1/3,0), theta=1/3 and zero hinge surplus.
    row=25
    if VALUES[row]!=sum(Z[i] for i in actual): raise AssertionError("top row")
    alpha=tuple(F(1,3) if i in actual else F(0) for i in range(N)); theta=F(1,3)
    if sum(alpha)!=1 or sum(alpha[i]*X[i] for i in range(N))!=maximum:
        raise AssertionError("top cover")
    minimum=min(X); required=(maximum-minimum)/theta
    lower_z=sorted((a for a in Z if a<maximum),reverse=True)
    candidates=[]
    for chosen in itertools.combinations(range(N),len(actual)):
        if sum(X[i]-minimum for i in chosen)<required: continue
        residual_x=sorted(X[i] for i in range(N) if i not in chosen)
        bound=sum(min(X[i],maximum) for i in chosen)
        bound+=sum(min(a,b) for a,b in zip(residual_x,lower_z))
        candidates.append((bound,chosen))
    answer=min(candidates)
    if answer!=(F(559,210),actual): raise AssertionError(("spectral",answer))
    return answer[0]


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path); args=parser.parse_args()
    if any(VALUES[1<<i] for i in range(N)): raise AssertionError("singletons")
    exactness(); verify_selector(X,"min"); verify_selector(Z,"max")
    bstar=spectral_minimum(); target=F(8,3); overlap=sum(min(a,b) for a,b in zip(X,Z))
    chord=4*(PHI1-PHI0); lock=(X[2]==Z[2]>0 and VALUES[FULL^(1<<2)]==TOTAL-X[2])
    if not (lock and bstar<target and overlap-target==F(7,15) and chord>overlap-target):
        raise AssertionError("conclusion")
    payload={"claim":"independent PXC142 game/selector/spectral/lock replay","exact_coalitions":64,
             "selectors":{"x":list(map(str,X)),"z":list(map(str,Z))},
             "spectral":{"B_star":str(bstar),"target":str(target)},
             "lock":{"player":2,"tau_star":"1"},
             "release":{"Psi_0_upper":str(PHI0),"Psi_quarter_lower":str(PHI1),
                        "e0_lower_bound":str(chord),
                        "certificate_scope":"arithmetic cross-check; rational feasibility/duality is replayed in the primary verifier"},
             "available":str(overlap-target),"product_estimate":False,
             "main_inequality_counterexample":False}
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output: args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__": main()
