#!/usr/bin/env python3
"""Check the twenty displayed weighted identities closing packet class 4.

Every named inequality is oriented as ``expression <= 0``.  Each row uses
nonnegative rational multipliers plus arbitrary efficiency/zero equalities;
the weighted sum is exactly ``D-1/3``.  This is a pure rational-coefficient
checker: it makes no solver call and imports no production encoder.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations
from math import lcm
from pathlib import Path

def q_row(coalition, terms, equalities):
    return {
        "leaf": "q1-only Lmax terminal",
        "hypothetical_complement": list(coalition),
        "inequality_multipliers": terms,
        "equality_multipliers": equalities,
    }


Q_ROWS = [
    q_row((2,), {"x4>=0":"2/3","z0>=0":"1","z3>=0":"1/3","q0>=0":"1/3","d1>=0":"1/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"2/3","P5q":"1/3","Bo":"2/3","Bq":"1/3","Lq":"1/3"}, {"sumq":"1/3","q1":"1/3"}),
    q_row((2,0), {"x4>=0":"2/3","z0>=0":"2/3","z3>=0":"1/3","q0>=0":"2/3","d1>=0":"1/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"2/3","P5q":"1/3","Bo":"2/3","Bq":"1/3","Lq":"1/3"}, {"sumq":"1/3","q1":"1/3"}),
    q_row((2,3), {"x4>=0":"2/3","z0>=0":"1","q0>=0":"1/3","q3>=0":"1/3","d1>=0":"1/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"2/3","P5q":"1/3","Bo":"2/3","Bq":"1/3","Lq":"1/3"}, {"sumq":"1/3","q1":"1/3"}),
    q_row((2,0,3), {"x4>=0":"2/3","z0>=0":"2/3","q0>=0":"2/3","q3>=0":"1/3","d1>=0":"1/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"2/3","P5q":"1/3","Bo":"2/3","Bq":"1/3","Lq":"1/3"}, {"sumq":"1/3","q1":"1/3"}),
    q_row((2,5), {"x4>=0":"2/3","z0>=0":"4/3","z3>=0":"1/3","d1>=0":"1/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"2/3","P5q":"1/3","Bo":"1","Lq":"1/3"}, {"sumz":"1/3","q1":"1/3"}),
    q_row((2,0,5), {"x2>=0":"1/3","x5>=0":"1/3","z0>=0":"1","z3>=0":"1/3","q0>=0":"1/3","d1>=0":"1/3","x0<=x4":"1","z4<=z1":"2/3","P5q":"1/3","Bo":"1","Lq":"1/3"}, {"sumz":"1/3","q1":"1/3"}),
    q_row((2,3,5), {"x2>=0":"1/3","x5>=0":"1/3","z0>=0":"4/3","q3>=0":"1/3","d1>=0":"1/3","x0<=x4":"1","z4<=z1":"2/3","P5q":"1/3","Bo":"1","Lq":"1/3"}, {"sumz":"1/3","q1":"1/3"}),
    q_row((2,0,3,5), {"x2>=0":"1/3","x5>=0":"1/3","z0>=0":"1","q0>=0":"1/3","q3>=0":"1/3","d1>=0":"1/3","x0<=x4":"1","z4<=z1":"2/3","P5q":"1/3","Bo":"1","Lq":"1/3"}, {"sumz":"1/3","q1":"1/3"}),
    q_row((2,4), {"x4>=0":"1","z0>=0":"1","z3>=0":"1/3","q0>=0":"1/3","d1>=0":"2/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"1","P4q":"1/3","P5q":"1/3","Bo":"2/3","Bq":"1/3","Lq":"1/3"}, {"sumq":"1/3","q1":"2/3"}),
    q_row((2,0,4), {"x4>=0":"1","z0>=0":"2/3","z3>=0":"1/3","q0>=0":"2/3","d1>=0":"2/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"1","P4q":"1/3","P5q":"1/3","Bo":"2/3","Bq":"1/3","Lq":"1/3"}, {"sumq":"1/3","q1":"2/3"}),
    q_row((2,3,4), {"x4>=0":"2/3","z0>=0":"1","z2>=0":"1/3","z3>=0":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"2/3","Bo":"1/3","Bq":"1/3","Lq":"1/3"}, {"sumx":"1/3","q1":"1/3"}),
    q_row((2,0,3,4), {"x4>=0":"1/3","x5>=0":"1/3","z0>=0":"2/3","z2>=0":"1/3","z3>=0":"1/3","q0>=0":"1/3","x0<=x4":"2/3","z4<=z1":"2/3","Bo":"1/3","Bq":"1/3","Lq":"1/3"}, {"sumx":"1/3","q1":"1/3"}),
    q_row((2,4,5), {"x4>=0":"1","z0>=0":"4/3","z3>=0":"1/3","d1>=0":"2/3","x0<=x2":"1/3","x0<=x4":"1/3","x0<=x5":"1/3","z4<=z1":"1","P4q":"1/3","P5q":"1/3","Bo":"1","Lq":"1/3"}, {"sumz":"1/3","q1":"2/3"}),
    q_row((2,0,4,5), {"x2>=0":"1/3","x4>=0":"2/3","z0>=0":"1","z3>=0":"1/3","q0>=0":"1/3","d1>=0":"2/3","x0<=x4":"2/3","x0<=x5":"1/3","z4<=z1":"1","P4q":"1/3","P5q":"1/3","Bo":"1","Lq":"1/3"}, {"sumz":"1/3","q1":"2/3"}),
    q_row((2,3,4,5), {"z0>=0":"4/3","z2>=0":"1/3","z3>=0":"1/3","q5>=0":"1/3","x0<=x4":"1","z4<=z1":"2/3","Bo":"2/3","Bq":"1/3","Lq":"1/3"}, {"sumz":"1/3","q1":"1/3"}),
    q_row((2,0,3,4,5), {"x4>=0":"1/3","x5>=0":"1/3","z0>=0":"1","z2>=0":"1/3","z3>=0":"1/3","x0<=x4":"2/3","z4<=z1":"2/3","Bo":"2/3","Lq":"1/3"}, {"sumx":"1/3","sumz":"1/3","sumq":"-1/3","q1":"1/3"}),
]


def opposite_row(branch, rich_player, terms, equalities):
    return {
        "leaf": "opposite-only Lmin terminal",
        "root_blocker": list(branch),
        "one_M_player": rich_player,
        "inequality_multipliers": terms,
        "equality_multipliers": equalities,
    }


OPPOSITE_ROWS = [
    opposite_row((1,3,5),4,{"z0>=0":"4/3","z2>=0":"1/6","q0>=0":"1/2","q2>=0":"1/6","q3>=0":"1/3","x0<=x4":"1","x0<=x5":"1/2","z4<=z1":"2/3","z5<=z1":"1/6","P4q":"1/2","P5o":"1/6","P5q":"1/3","Bo":"1/3","Bq":"1/6","terminal":"1"},{"sumx":"-1/2","sumz":"1/3","sumq":"1/2","q1":"1/2"}),
    opposite_row((1,3,5),5,{"x4>=0":"1/3","z0>=0":"1","q0>=0":"2/3","q2>=0":"1/3","q3>=0":"1/3","x0<=x5":"4/3","z5<=z1":"1","P4q":"2/3","P5q":"1/3","Bq":"1/3","terminal":"1"},{"sumx":"-1/3","sumq":"2/3","q1":"2/3"}),
    opposite_row((0,1,3,5),4,{"x5>=0":"1/6","z0>=0":"7/6","z2>=0":"1/3","z3>=0":"1/6","q0>=0":"1/6","q3>=0":"1/6","x0<=x4":"1/3","x0<=x5":"2/3","z5<=z1":"1/2","P4q":"1/6","P5o":"2/3","P5q":"1/6","Bo":"5/6","terminal":"1"},{"sumx":"-5/6","sumz":"1","sumq":"1/6","q1":"1/6"}),
    opposite_row((0,1,3,5),5,{"x4>=0":"1/3","x5>=0":"1/3","z0>=0":"1","q0>=0":"1/3","q2>=0":"1/3","q3>=0":"1/3","x0<=x5":"1","z5<=z1":"1","P4q":"2/3","P5q":"1/3","Bq":"1/3","terminal":"1"},{"sumx":"-1/3","sumq":"2/3","q1":"2/3"}),
]


def linear(*terms):
    """Add sparse affine forms represented as ``name -> Fraction`` maps."""
    result = {}
    for multiplier, form in terms:
        multiplier = Fraction(multiplier)
        for name, coefficient in form.items():
            value = result.get(name, Fraction(0)) + multiplier * coefficient
            if value:
                result[name] = value
            else:
                result.pop(name, None)
    return result


def variable(name):
    return {name: Fraction(1)}


def constant(value):
    return {"constant": Fraction(value)} if Fraction(value) else {}


def point_sum(point, players):
    return linear(*((1, point[player]) for player in players))


def named_system(branch, complement=None, rich_player=None):
    x = [variable(f"x{player}") for player in range(6)]
    z = [variable(f"z{player}") for player in range(6)]
    q = [variable(f"q{player}") for player in range(6)]
    inequalities = {}
    for name, point in (("x", x), ("z", z), ("q", q)):
        for player in range(6):
            inequalities[f"{name}{player}>=0"] = linear((-1, point[player]))
    inequalities["d1>=0"] = linear((1, z[1]), (-1, x[1]))
    for player in range(1, 6):
        inequalities[f"x0<=x{player}"] = linear((1, x[0]), (-1, x[player]))
    for player in (0, 2, 3, 4, 5):
        inequalities[f"z{player}<=z1"] = linear((1, z[player]), (-1, z[1]))
    p4 = (1, 4)
    p5 = (1, 2, 5)
    inequalities["P4o"] = linear((1, point_sum(x, p4)), (-1, point_sum(z, p4)))
    inequalities["P4q"] = linear((1, point_sum(x, p4)), (-1, point_sum(q, p4)))
    inequalities["P5o"] = linear((1, point_sum(x, p5)), (-1, point_sum(z, p5)))
    inequalities["P5q"] = linear((1, point_sum(x, p5)), (-1, point_sum(q, p5)))
    inequalities["Bo"] = linear((1, point_sum(x, branch)), (-1, point_sum(z, branch)))
    inequalities["Bq"] = linear((1, point_sum(x, branch)), (-1, point_sum(q, branch)))
    if complement is not None:
        inequalities["Lq"] = linear((1, point_sum(q, complement)), (-1, point_sum(z, complement)))
    if rich_player is not None:
        terminal = (2, 3, rich_player)
        inequalities["terminal"] = linear((1, point_sum(x, terminal)), (-1, point_sum(z, terminal)))
    equalities = {
        "sumx": linear((1, point_sum(x, range(6))), (-1, constant(1))),
        "sumz": linear((1, point_sum(z, range(6))), (-1, constant(1))),
        "sumq": linear((1, point_sum(q, range(6))), (-1, constant(1))),
        "q1": q[1],
    }
    distance = linear((1, point_sum(x, (0, 1, 2, 3))), (-1, point_sum(z, (0, 1, 2, 3))))
    return inequalities, equalities, distance


def scaled_integer_row(row):
    values = [
        *(Fraction(value) for value in row["inequality_multipliers"].values()),
        *(Fraction(value) for value in row["equality_multipliers"].values()),
    ]
    scale = 1
    for value in values:
        scale = lcm(scale, value.denominator)
    return {
        **{key: value for key, value in row.items() if not key.endswith("multipliers")},
        "integer_scale": scale,
        "inequality_multipliers": {
            key: int(Fraction(value) * scale)
            for key, value in row["inequality_multipliers"].items()
        },
        "equality_multipliers": {
            key: int(Fraction(value) * scale)
            for key, value in row["equality_multipliers"].items()
        },
        "identity": f"weighted sum = {scale}*(D-1/3)",
    }


def verify_row(row):
    if row["leaf"].startswith("q1-only"):
        branch = (1, 2, 3, 4)
        complement = tuple(row["hypothetical_complement"])
        inequalities, equalities, distance = named_system(
            branch, complement=complement
        )
    else:
        branch = tuple(row["root_blocker"])
        inequalities, equalities, distance = named_system(
            branch, rich_player=row["one_M_player"]
        )
    terms = []
    for name, multiplier in row["inequality_multipliers"].items():
        if name not in inequalities or Fraction(multiplier) < 0:
            raise AssertionError(f"bad inequality term {name}={multiplier}")
        terms.append((Fraction(multiplier), inequalities[name]))
    for name, multiplier in row["equality_multipliers"].items():
        if name not in equalities:
            raise AssertionError(f"bad equality term {name}")
        terms.append((Fraction(multiplier), equalities[name]))
    expression = linear(*terms)
    target = linear((1, distance), (-1, constant(Fraction(1, 3))))
    residual = linear((1, expression), (-1, target))
    if residual:
        raise AssertionError(f"certificate identity failed: {residual}")
    return scaled_integer_row(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    expected_complements = {
        frozenset((2, *subset))
        for size in range(5)
        for subset in combinations((0, 3, 4, 5), size)
    }
    actual_complements = {
        frozenset(row["hypothetical_complement"]) for row in Q_ROWS
    }
    if actual_complements != expected_complements or len(Q_ROWS) != 16:
        raise AssertionError("q1-complement rows are not the exhaustive 16 cuts")
    expected_opposite_rows = {
        (frozenset(branch), rich_player)
        for branch in ((1, 3, 5), (0, 1, 3, 5))
        for rich_player in (4, 5)
    }
    actual_opposite_rows = {
        (frozenset(row["root_blocker"]), row["one_M_player"])
        for row in OPPOSITE_ROWS
    }
    if actual_opposite_rows != expected_opposite_rows or len(OPPOSITE_ROWS) != 4:
        raise AssertionError("opposite-base-cut rows are not the exhaustive four cases")
    rows = [verify_row(row) for row in (*Q_ROWS, *OPPOSITE_ROWS)]
    mutated = {
        **Q_ROWS[0],
        "inequality_multipliers": {
            **Q_ROWS[0]["inequality_multipliers"],
            "Bo": "1",
        },
    }
    try:
        verify_row(mutated)
    except AssertionError:
        mutation_control = "rejected coefficient perturbation"
    else:
        raise AssertionError("mutation control unexpectedly passed")
    payload = {
        "schema": "strict-exchange-p4-class4-hand-certificates-v1",
        "status": "PASS",
        "scope": (
            "twenty exact weighted identities closing the three class-4 terminal leaves; "
            "pure rational coefficient arithmetic, no solver call, and no production encoder import"
        ),
        "q1_only_complement_certificate_count": len(Q_ROWS),
        "opposite_only_base_cut_certificate_count": len(OPPOSITE_ROWS),
        "certificate_count": len(rows),
        "mutation_control": mutation_control,
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
