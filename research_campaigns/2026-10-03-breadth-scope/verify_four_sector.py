"""Symbolic coefficient checks for K=4; no finite market search or optimizer."""
from collections import Counter
from itertools import product
import hashlib
import json
from pathlib import Path


def clean(counter):
    return {key:value for key,value in counter.items() if value}


def require(ok,why):
    if not ok:
        raise ValueError(why)


cases=0
for labels in product(range(4),repeat=4):
    ideals=Counter()
    budgets=Counter()
    diagonals=Counter()
    for b in range(4):
        for c in range(4):
            if b==c: continue
            ideals[c,labels[c]]+=1
            ideals[c,labels[b]]-=1
            diagonals[labels[b]]+=1
            for a in range(4):
                if a not in (b,c): budgets[a,labels[a]]+=1
    expected_ideals=Counter()
    expected_budgets=Counter()
    expected_diagonals=Counter()
    for a in range(4):
        expected_ideals[a,labels[a]]+=4
        expected_budgets[a,labels[a]]+=6
        expected_diagonals[labels[a]]+=3
        for b in range(4): expected_ideals[b,labels[a]]-=1
    require(clean(ideals)==clean(expected_ideals),'Ideal multiplicity error')
    require(clean(budgets)==clean(expected_budgets),'Budget multiplicity error')
    require(clean(diagonals)==clean(expected_diagonals),'Diagonal multiplicity error')
    cases+=1
coefficients=0
for a in range(4):
    lhs=Counter({'constant':3,('p',a):4-3})
    for b in range(4): lhs['p',b]-=1
    rhs=Counter({'constant':3})
    for b in range(4):
        if b!=a: rhs['p',b]-=1
    require(clean(lhs)==clean(rhs),'Residual polynomial identity error')
    coefficients+=1
print(json.dumps({'status':'PASS','K':4,'ordered_label_tuples':cases,
                  'linear_residual_identities':coefficients,
                  'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'scope':'Coefficient identities only. Four labels cover every coincidence pattern of a four-player team; no game instances or sharpness search.'},indent=2))
