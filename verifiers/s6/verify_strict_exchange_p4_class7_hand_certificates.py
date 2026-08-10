#!/usr/bin/env python3
"""Check the exact class-7 relay proof without a solver or production encoder.

The blocker census is recomputed by exact Fourier--Motzkin elimination in the
six payoff-difference variables.  Sixteen source-specific blocker filters and
nine activation certificates are then checked as exact rational affine
identities.  Inequality multipliers must be nonnegative.  Two mutation
controls guard both halves of the checker.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations
from math import lcm
from pathlib import Path


def R(stage, coalition, source, target, ineq, eq):
    return {"stage": stage, "coalition": coalition, "source": source,
            "target": target, "ineq": ineq, "eq": eq}


FILTER_ROWS = [
R("root-q",[1,3,4],"q","D-1/3",{"x4>=0":"1","z0>=0":"1/3","z2>=0":"1/3","z3>=0":"1/3","q0>=0":"1","d1>=0":"1","x0<=x5":"1","z4<=z1":"2/3","z5<=z1":"2/3","P5q":"1","Cq":"1"},{"sumz":"-2/3","sumq":"1","q1":"1"}),
R("B0-terminal-q",[3,5],"q","d0",{"q0>=0":"1","d1>=0":"2","d2>=0":"1","x0<=x4":"1","z4<=z1":"1","P4q":"1","P5q":"1","B0q":"1","Cq":"1"},{"sumx":"-1","sumz":"-1","sumq":"2","q1":"1"}),
R("B0-terminal-q",[1,3,5],"q","D-1/3",{"x2>=0":"1/3","x4>=0":"2/3","x5>=0":"1/3","z0>=0":"2/3","z3>=0":"1/3","q0>=0":"1/3","d1>=0":"2/3","x0<=x4":"2/3","z4<=z1":"1","P4q":"1/3","P5q":"1/3","B0o":"2/3","B0q":"1/3","Cq":"1/3"},{"sumz":"-1/3","sumq":"2/3","q1":"2/3"}),
R("B1-terminal-q",[2,3,4],"q","D-1/3",{"x5>=0":"1","z0>=0":"1/3","z2>=0":"1/3","z3>=0":"1/3","q0>=0":"1","d1>=0":"1","x0<=x4":"1","z4<=z1":"2/3","z5<=z1":"2/3","P4q":"1","P5q":"1","B1q":"1","Cq":"1"},{"sumx":"-1","sumz":"-2/3","sumq":"2","q1":"1"}),
R("B1-terminal-q",[1,2,3,4],"q","D-1/3",{"x4>=0":"1/2","x5>=0":"1","z0>=0":"1/3","z2>=0":"1/3","z3>=0":"1/3","q0>=0":"1/2","d1>=0":"1","x0<=x4":"1/2","z4<=z1":"2/3","z5<=z1":"2/3","P4q":"1/2","P5q":"1/2","B1q":"1/2","Cq":"1/2"},{"sumz":"-2/3","sumq":"1","q1":"1"}),
R("B1-terminal-o",[2,3,5],"o","D-1/3",{"x5>=0":"1","z0>=0":"1","q2>=0":"1/3","q3>=0":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z5<=z1":"1","P4q":"2/3","P5q":"1/3","B1q":"1/3","Co":"1"},{"sumx":"-1/3","sumq":"2/3","q1":"2/3"}),
R("B2-h10-q",[1],"q","D-1/3",{"x4>=0":"1","x5>=0":"1","z0>=0":"1/3","z2>=0":"1/3","z3>=0":"1/3","z4<=z1":"2/3","z5<=z1":"2/3","Cq":"1"},{"sumx":"1","sumz":"-2/3","q1":"1"}),
R("B2-h10-q",[1,3],"q","D-1/3",{"x0>=0":"1/3","x4>=0":"1","x5>=0":"2","z2>=0":"1/3","z3>=0":"1/3","d0>=0":"2/3","d1>=0":"2","z4<=z1":"2/3","z5<=z1":"5/3","P4q":"1","P5q":"1","B2o":"1","Cq":"1"},{"sumz":"-2/3","sumq":"1","q1":"2"}),
R("B2-h10-q",[1,2,3],"q","d0",{"z0>=0":"1/2","q4>=0":"1/2","d1>=0":"1","x0<=x5":"1/2","z4<=z1":"1/2","z5<=z1":"1/2","P4q":"1/2","P5q":"1/2","B2q":"1/2","Cq":"1/2"},{"sumx":"-1/2","sumz":"-1/2","sumq":"1","q1":"1"}),
R("B2-h10-q",[1,2,4],"q","D-1/3",{"x0>=0":"1/3","x4>=0":"1/3","x5>=0":"2","z2>=0":"1/3","q3>=0":"1/3","d1>=0":"4/3","z5<=z1":"5/3","P4q":"1/3","P5o":"2/3","P5q":"1/3","B2q":"1","Cq":"1"},{"sumz":"-1","sumq":"4/3","q1":"4/3"}),
R("B2-h10-q",[1,3,4],"q","D-1/3",{"x5>=0":"2","z3>=0":"1/3","q0>=0":"2/3","q2>=0":"1/3","d0>=0":"2/3","d1>=0":"4/3","x0<=x4":"1/3","z5<=z1":"5/3","P4q":"1/3","P5q":"1","B2o":"2/3","B2q":"1/3","Cq":"1"},{"sumz":"-1","sumq":"4/3","q1":"4/3"}),
R("B2-h10-q",[1,2,3,4],"q","D-1/3",{"x0>=0":"1/3","x4>=0":"1","x5>=0":"2","z2>=0":"1/3","z3>=0":"1/3","d0>=0":"2/3","d1>=0":"2","z4<=z1":"2/3","z5<=z1":"5/3","P4q":"1","P5q":"1","B2q":"1","Cq":"1"},{"sumz":"-5/3","sumq":"2","q1":"2"}),
R("B2-h10-q",[1,2,3,5],"q","d0",{"z0>=0":"1/2","d1>=0":"1/2","x0<=x4":"1/2","z4<=z1":"1/2","P4q":"1/2","Cq":"1/2"},{"sumz":"-1/2","sumq":"1/2","q1":"1/2"}),
R("B3-terminal-q",[3,4],"q","D-1/3",{"x5>=0":"4/3","z0>=0":"2/3","z2>=0":"1/3","z3>=0":"1/3","x0<=x4":"1/3","z5<=z1":"1","P4q":"1/3","P5q":"1/3","B2q":"1/3","B3q":"1/3","B5o":"2/3","Cq":"1/3"},{"sumz":"-1/3","sumq":"2/3","q1":"2/3"}),
R("B3-terminal-q",[1,3,4],"q","D-1/3",{"x5>=0":"4/3","z0>=0":"1/2","z2>=0":"1/3","z3>=0":"1/3","q0>=0":"1/6","x0<=x4":"1/3","z5<=z1":"1","P4q":"1/6","P5q":"1/3","B2o":"1/6","B2q":"1/6","B3q":"1/6","B5o":"1/2","Cq":"1/3"},{"sumx":"1/6","sumz":"-1/3","sumq":"1/2","q1":"2/3"}),
R("B4-terminal-q",[1,3,4],"q","D-1/3",{"x5>=0":"4/3","z0>=0":"2/3","z3>=0":"1/3","q2>=0":"1/3","x0<=x4":"1/3","z5<=z1":"1","P4q":"1/3","P5q":"1/3","B2q":"1/3","B5o":"2/3","Cq":"1/3"},{"sumz":"-1/3","sumq":"2/3","q1":"2/3"}),
]


def A(stage, target, ineq, eq):
    return {"stage": stage, "target": target, "ineq": ineq, "eq": eq}


ACTIVATION_ROWS = [
A("B0-h12-fail-z0","D-1/3",{"x4>=0":"2/3","x5>=0":"2/3","z2>=0":"1/3","z3>=0":"1/3","x0<=x4":"1/3","z4<=z1":"1/3","B0o":"1/3","z4<=z0":"1/3","z5<=z0":"1/3"},{"sumx":"2/3","sumz":"-1/3"}),
A("B0-h12-fail-z2","D-1/3",{"x4>=0":"1/3","x5>=0":"1/3","z0>=0":"1","z3>=0":"1/3","x0<=x4":"2/3","z4<=z1":"1/3","B0o":"2/3","z4<=z2":"1/3"},{"sumx":"1/3"}),
A("B2-h10-fail","D-1/3",{"x4>=0":"1/3","x5>=0":"1","z2>=0":"1/3","z3>=0":"1/3","d0>=0":"2/3","x0<=x4":"2/3","z4<=z1":"2/3","z5<=z1":"2/3","z1<=z0":"1"},{"sumx":"1","sumz":"-2/3"}),
A("B3-h18-fail-x2<=x5","D-1/3",{"z0>=0":"1/3","z2>=0":"4/3","z3>=0":"1/3","q4>=0":"1/3","z5<=z1":"2/3","B2o":"2/3","B2q":"1/3","B3q":"1/3","x2<=x5":"1"},{"sumq":"1/3","q1":"1/3"}),
A("B3-B5-h12-fail-z0","D-1/3",{"x4>=0":"1/3","x5>=0":"1","z2>=0":"1/3","z3>=0":"1/3","x0<=x5":"1/3","z5<=z1":"1/3","P5o":"1/3","B2o":"1/3","B5o":"1/3","z5<=z0":"2/3"},{"sumx":"1/3"}),
A("B3-B5-h12-fail-z2","D-1/3",{"x4>=0":"1/3","x5>=0":"1","z0>=0":"2/3","q3>=0":"1/3","x0<=x5":"1/3","z5<=z1":"2/3","P4q":"1/3","P5q":"1/3","B2o":"1/3","B5o":"2/3","z5<=z2":"1/3"},{"sumq":"1/3","q1":"1/3"}),
A("B4-h18-fail-x2<=x5","D-1/3",{"x0>=0":"1/3","x4>=0":"1/3","z2>=0":"4/3","q3>=0":"1/3","d1>=0":"1/3","z5<=z1":"2/3","P4q":"1/3","B2o":"1","B4q":"1/3","x2<=x5":"1"},{"sumq":"1/3","q1":"1/3"}),
A("B4-B5-h12-fail-z0","D-1/3",{"x4>=0":"1/3","x5>=0":"1","z2>=0":"1/3","z3>=0":"1/3","x0<=x5":"1/3","z5<=z1":"1/3","P5o":"1/3","B2o":"1/3","B5o":"1/3","z5<=z0":"2/3"},{"sumx":"1/3"}),
A("B4-B5-h12-fail-z2","D-1/3",{"x4>=0":"1/3","x5>=0":"1","z0>=0":"2/3","q3>=0":"1/3","x0<=x5":"1/3","z5<=z1":"2/3","P4q":"1/3","P5q":"1/3","B2o":"1/3","B5o":"2/3","z5<=z2":"1/3"},{"sumq":"1/3","q1":"1/3"}),
]


H17=(0,-1,0,-1,1,1); H12=(1,0,1,0,-1,-1)
H10=(1,-1,0,0,0,0); H18=(0,0,-1,-1,1,1)
B0=(1,2,3,4); B1=(1,3,5); B2=(0,1,3,5)
B3=(1,2); B4=(1,2,5); B5=(2,3,5)


def linear(*terms):
    out={}
    for multiplier,form in terms:
        multiplier=Fraction(multiplier)
        for name,coefficient in form.items():
            value=out.get(name,Fraction())+multiplier*coefficient
            if value: out[name]=value
            else: out.pop(name,None)
    return out


def variable(name): return {name:Fraction(1)}
def constant(value): return {"constant":Fraction(value)} if Fraction(value) else {}
def point_sum(point,players): return linear(*((1,point[p]) for p in players))


def comparison(table,name,coalition,left,right):
    table[name]=linear((1,point_sum(left,coalition)),(-1,point_sum(right,coalition)))


def branches_for(stage):
    if stage.startswith("B0-"): return (("B0",B0,"min"),)
    if stage.startswith("B1-"): return (("B1",B1,"min"),)
    if stage.startswith("B2-h10"): return (("B2",B2,"min"),)
    if stage.startswith("B3-h18"): return (("B2",B2,"min"),("B3",B3,"max"))
    if stage.startswith("B4-h18"): return (("B2",B2,"min"),("B4",B4,"max"))
    if stage.startswith("B3-"): return (("B2",B2,"min"),("B3",B3,"max"),("B5",B5,"min"))
    if stage.startswith("B4-"): return (("B2",B2,"min"),("B4",B4,"max"),("B5",B5,"min"))
    return ()


def named_system(row):
    x=[variable(f"x{i}") for i in range(6)]
    z=[variable(f"z{i}") for i in range(6)]
    q=[variable(f"q{i}") for i in range(6)]
    inequalities={}
    for name,point in (("x",x),("z",z),("q",q)):
        for i in range(6): inequalities[f"{name}{i}>=0"]=linear((-1,point[i]))
    for i in range(4): inequalities[f"d{i}>=0"]=linear((1,z[i]),(-1,x[i]))
    for i in (4,5): inequalities[f"delta{i}>=0"]=linear((1,x[i]),(-1,z[i]))
    for i in range(1,6): inequalities[f"x0<=x{i}"]=linear((1,x[0]),(-1,x[i]))
    for i in (0,2,3,4,5): inequalities[f"z{i}<=z1"]=linear((1,z[i]),(-1,z[1]))
    for name,coalition in (("P4",(0,1,4)),("P5",(1,2,5))):
        comparison(inequalities,name+"o",coalition,x,z)
        comparison(inequalities,name+"q",coalition,x,q)
    for name,coalition,side in branches_for(row["stage"]):
        reference=x if side=="min" else z
        opposite=z if side=="min" else x
        comparison(inequalities,name+"o",coalition,reference,opposite)
        comparison(inequalities,name+"q",coalition,reference,q)
    if "coalition" in row:
        coalition=tuple(row["coalition"])
        if row["stage"].endswith("q"):
            side="max" if row["stage"] in {"B0-terminal-q","B2-h10-q","B3-terminal-q","B4-terminal-q"} else "min"
            reference=z if side=="max" else x
            comparison(inequalities,"Cq",coalition,reference,q)
        else:
            comparison(inequalities,"Co",coalition,x,z)
    hypothesis_forms={
        "z4<=z0":linear((1,z[4]),(-1,z[0])), "z5<=z0":linear((1,z[5]),(-1,z[0])),
        "z4<=z2":linear((1,z[4]),(-1,z[2])), "z5<=z2":linear((1,z[5]),(-1,z[2])),
        "z1<=z0":linear((1,z[1]),(-1,z[0])), "x2<=x5":linear((1,x[2]),(-1,x[5])),
    }
    for name in row["ineq"]:
        if name in hypothesis_forms: inequalities[name]=hypothesis_forms[name]
    equalities={
        "sumx":linear((1,point_sum(x,range(6))),(-1,constant(1))),
        "sumz":linear((1,point_sum(z,range(6))),(-1,constant(1))),
        "sumq":linear((1,point_sum(q,range(6))),(-1,constant(1))),
        "q1":q[1],
    }
    distance=linear((1,point_sum(x,(0,1,2,3))),(-1,point_sum(z,(0,1,2,3))))
    targets={"D-1/3":linear((1,distance),(-1,constant(Fraction(1,3)))),
             "d0":linear((1,x[0]),(-1,z[0]))}
    return inequalities,equalities,targets[row["target"]]


def verify_row(row):
    inequalities,equalities,target=named_system(row)
    terms=[]
    for name,multiplier in row["ineq"].items():
        if name not in inequalities or Fraction(multiplier)<0:
            raise AssertionError(f"bad inequality {name}={multiplier}")
        terms.append((Fraction(multiplier),inequalities[name]))
    for name,multiplier in row["eq"].items():
        if name not in equalities: raise AssertionError(f"bad equality {name}")
        terms.append((Fraction(multiplier),equalities[name]))
    residual=linear((1,linear(*terms)),(-1,target))
    if residual: raise AssertionError(f"certificate identity failed: {residual}")
    values=[*(Fraction(v) for v in row["ineq"].values()),*(Fraction(v) for v in row["eq"].values())]
    scale=1
    for value in values: scale=lcm(scale,value.denominator)
    return {"stage":row["stage"],**({"coalition":row["coalition"],"source":row["source"]} if "coalition" in row else {}),
            "target":row["target"],"integer_scale":scale,
            "inequality_multipliers":{k:int(Fraction(v)*scale) for k,v in row["ineq"].items()},
            "equality_multipliers":{k:int(Fraction(v)*scale) for k,v in row["eq"].items()},
            "identity":f"weighted sum = {scale}*({row['target']})"}


def eligible(direction):
    return [coalition for size in range(1,6) for coalition in combinations(range(6),size)
            if sum(direction[i] for i in coalition)<0]


def normalize(rows):
    best={}
    for coefficients,rhs in rows:
        key=tuple(coefficients)
        if key not in best or rhs<best[key]: best[key]=rhs
    return [(key,rhs) for key,rhs in best.items()]


def fourier_motzkin_feasible(rows,variable_count):
    rows=normalize(rows)
    for index in reversed(range(variable_count)):
        positive=[]; negative=[]; zero=[]
        for coefficients,rhs in rows:
            value=coefficients[index]
            if value>0: positive.append((coefficients,rhs))
            elif value<0: negative.append((coefficients,rhs))
            else: zero.append((coefficients[:index]+coefficients[index+1:],rhs))
        combined=list(zero)
        if positive and negative:
            for p,pr in positive:
                for n,nr in negative:
                    coefficients=tuple((-n[index])*p[j]+p[index]*n[j] for j in range(len(p)) if j!=index)
                    combined.append((coefficients,(-n[index])*pr+p[index]*nr))
        rows=normalize(combined)
        if any(not coefficients and rhs<0 for coefficients,rhs in rows): return False
    return not any(rhs<0 for _,rhs in rows)


def d_form(coalition):
    # Variables are d0,d1,d2,d3,delta4; efficiency substitutes
    # delta5=d0+d1+d2+d3-delta4.
    out=[Fraction() for _ in range(5)]
    for i in coalition:
        if i<4: out[i]+=1
        elif i==4: out[4]-=1
        else:
            for j in range(4): out[j]-=1
            out[4]+=1
    return tuple(out)


def dcone_rows(branches):
    rows=[]
    # All six original difference magnitudes are strictly positive.  By
    # homogeneity scale their minimum to at least one.
    for i in range(5):
        coefficients=[Fraction() for _ in range(5)]; coefficients[i]=-1
        rows.append((tuple(coefficients),Fraction(-1)))
    rows.append(((-1,-1,-1,-1,1),Fraction(-1)))  # delta5 >= 1
    rows.extend([
        ((1,1,0,0,-1),Fraction()),       # delta4 >= d0+d1
        ((-1,0,0,-1,1),Fraction()),      # delta5 >= d1+d2, after substitution
    ])
    for coalition,side in branches:
        form=d_form(coalition)
        rows.append((form if side=="min" else tuple(-v for v in form),Fraction()))
    return rows


STRUCTURAL_STAGES={
    "root":(H17,"min",(),{(1,3,4),(1,3,5),(0,1,3,5),(1,2,3,4)}),
    "B0-terminal":(H12,"max",((B0,"min"),),{(3,5),(1,3,5)}),
    "B1-terminal":(H18,"min",((B1,"min"),),{(2,3,4),(2,3,5),(1,2,3,4)}),
    "B2-h10":(H10,"max",((B2,"min"),),{(1,),(1,2),(1,3),(1,2,3),(1,2,4),(1,2,5),(1,3,4),(1,2,3,4),(1,2,3,5)}),
    "B3-h18":(H18,"min",((B2,"min"),(B3,"max")),{B5}),
    "B4-h18":(H18,"min",((B2,"min"),(B4,"max")),{B5}),
    "B3-terminal":(H12,"max",((B2,"min"),(B3,"max"),(B5,"min")),{(3,4),(1,3,4)}),
    "B4-terminal":(H12,"max",((B2,"min"),(B4,"max"),(B5,"min")),{(1,3,4)}),
}


def structural_census():
    result={}
    for name,(direction,side,branches,expected) in STRUCTURAL_STAGES.items():
        actual=set()
        for coalition in eligible(direction):
            form=d_form(coalition)
            blocker=form if side=="min" else tuple(-v for v in form)
            if fourier_motzkin_feasible([*dcone_rows(branches),(blocker,Fraction())],5):
                actual.add(coalition)
        if actual!=expected: raise AssertionError(f"structural census changed at {name}: {actual}")
        result[name]={"eligible_cut_count":len(eligible(direction)),"opposite_candidate_count":len(actual),
                      "opposite_candidates":[list(c) for c in sorted(actual)]}
    return result


def audit_filter_exhaustiveness():
    expected={
        "root-q":{(1,3,4)}, "B0-terminal-q":{(3,5),(1,3,5)},
        "B1-terminal-q":{(2,3,4),(1,2,3,4)}, "B1-terminal-o":{(2,3,5)},
        "B2-h10-q":STRUCTURAL_STAGES["B2-h10"][3]-{B3,B4},
        "B3-terminal-q":STRUCTURAL_STAGES["B3-terminal"][3],
        "B4-terminal-q":STRUCTURAL_STAGES["B4-terminal"][3],
    }
    actual={name:{tuple(r["coalition"]) for r in FILTER_ROWS if r["stage"]==name} for name in expected}
    if actual!=expected: raise AssertionError(f"filter rows are not exhaustive: {actual}")
    return {name:len(rows) for name,rows in expected.items()}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path); args=parser.parse_args()
    census=structural_census(); counts=audit_filter_exhaustiveness()
    rows=[verify_row(row) for row in (*FILTER_ROWS,*ACTIVATION_ROWS)]
    changed={**FILTER_ROWS[0],"ineq":{**FILTER_ROWS[0]["ineq"],"Cq":"2"}}
    try: verify_row(changed)
    except AssertionError: coefficient_mutation="rejected coefficient perturbation"
    else: raise AssertionError("coefficient mutation unexpectedly passed")
    changed_census=dict(STRUCTURAL_STAGES); changed_census["root"]=(H17,"min",(),{(1,3,5)})
    saved=STRUCTURAL_STAGES["root"]
    try:
        STRUCTURAL_STAGES["root"]=changed_census["root"]
        structural_census()
    except AssertionError: census_mutation="rejected candidate-set deletion"
    else: raise AssertionError("census mutation unexpectedly passed")
    finally: STRUCTURAL_STAGES["root"]=saved
    payload={"schema":"strict-exchange-p4-class7-hand-certificates-v1","status":"PASS",
             "scope":"exact difference-cone blocker census plus 16 blocker filters and 9 activation identities; pure rational arithmetic, no solver call, no production encoder import",
             "packet":{"first_optional_players":[0],"second_optional_players":[2]},
             "structural_census":census,"filter_certificate_counts":counts,
             "filter_target_counts":{"D-1/3":sum(r["target"]=="D-1/3" for r in FILTER_ROWS),
                                     "d0":sum(r["target"]=="d0" for r in FILTER_ROWS)},
             "strict_target_semantics":{"d0":"strictly positive by the original P-sign premise"},
             "blocker_filter_certificate_count":len(FILTER_ROWS),"activation_certificate_count":len(ACTIVATION_ROWS),
             "certificate_count":len(rows),"coefficient_mutation_control":coefficient_mutation,
             "census_mutation_control":census_mutation,"rows":rows}
    rendered=json.dumps(payload,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__": main()
