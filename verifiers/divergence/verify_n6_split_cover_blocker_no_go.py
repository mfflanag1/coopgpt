#!/usr/bin/env python3
"""Exact finite proof of the n=6 two-row split-cover blocker no-go.

On the first-ceiling equality face of the split cover
  R_j={r,h,b,j}, R_k={r,h,a,k},
the only free second-stage directions have coordinates
  (d_a,d_b,d_j,d_k)=(t,s,-s,-t).
This audit enumerates every proper nonsingleton z-tight row type and every
one-/two-row subfamily that excludes the open negative (t,s) quadrant.  For
each such family it proves exact rational infeasibility of the necessary
allocation, cover-compatibility, reserve-failure, order, and root-singleton
witness constraints.

The result is conditional on this literal two-row split cover.  It is not a
classification of all positive extreme top covers at n=6.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402


N = 6
R, H, A, B, J, K = range(N)
FULL = (1 << N) - 1
NAMES = (
    "M", "q", "zj", "zk", "ell", "dh", "da", "db", "Lj", "Lk",
    "yh", "ya", "yb", "yj", "yk",
)
INDEX = {name: i for i, name in enumerate(NAMES)}
DIM = len(NAMES)


def vec(**terms):
    answer = [F(0)] * DIM
    for name, coefficient in terms.items():
        answer[INDEX[name]] = F(coefficient)
    return answer


def add(*rows):
    return [sum((row[i] for row in rows), F(0)) for i in range(DIM)]


def scale(row, coefficient):
    return [F(coefficient) * value for value in row]


def coalition(players):
    return sum(1 << player for player in players)


def z_sum(mask):
    rows = []
    if mask >> R & 1:
        rows.append(vec(M=1))
    if mask >> H & 1:
        rows.append(vec(M=1))
    if mask >> A & 1:
        rows.append(vec(q=1))
    if mask >> B & 1:
        rows.append(vec(q=1))
    if mask >> J & 1:
        rows.append(vec(zj=1))
    if mask >> K & 1:
        rows.append(vec(zk=1))
    return add(*rows) if rows else [F(0)] * DIM


def x_minus_z(mask):
    rows = []
    if mask >> R & 1:
        rows.append(vec(ell=1))
    if mask >> H & 1:
        rows.append(vec(dh=-1))
    if mask >> A & 1:
        rows.append(vec(da=-1))
    if mask >> B & 1:
        rows.append(vec(db=-1))
    if mask >> J & 1:
        rows.append(vec(Lj=1))
    if mask >> K & 1:
        rows.append(vec(Lk=1))
    return add(*rows) if rows else [F(0)] * DIM


def witness_sum(mask):
    # The root witness has y_r=0.
    rows = []
    if mask >> H & 1:
        rows.append(vec(yh=1))
    if mask >> A & 1:
        rows.append(vec(ya=1))
    if mask >> B & 1:
        rows.append(vec(yb=1))
    if mask >> J & 1:
        rows.append(vec(yj=1))
    if mask >> K & 1:
        rows.append(vec(yk=1))
    return add(*rows) if rows else [F(0)] * DIM


def tangent_form(mask):
    # d=(0,0,t,s,-s,-t) on the top-cover equality face.
    return (
        int(bool(mask >> A & 1)) - int(bool(mask >> K & 1)),
        int(bool(mask >> B & 1)) - int(bool(mask >> J & 1)),
    )


def closes_negative_quadrant(forms):
    # Seek t,s<=0, t+s<=-1 satisfying every retained tangent inequality.
    # Scaling is valid because this direction system is homogeneous.
    A_ub = [[F(1), F(0)], [F(0), F(1)], [F(1), F(1)]]
    b_ub = [F(0), F(0), F(-1)]
    for ct, cs in forms:
        A_ub.append([F(-ct), F(-cs)])  # ct*t+cs*s >= 0
        b_ub.append(F(0))
    status, _optimum, _point = exact_linprog([F(0), F(0)], A_ub, b_ub, [], [])
    return status == "infeasible"


def base_system(include_root_witness=True):
    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    def ge(row, rhs=0):
        A_ub.append(scale(row, -1))
        b_ub.append(F(-rhs))

    # Strict role inequalities and gains are homogenously scaled to margin 1.
    ge(add(vec(M=1), vec(q=-1)), 1)
    ge(add(vec(q=1), vec(zj=-1)), 1)
    ge(add(vec(q=1), vec(zk=-1)), 1)
    ge(vec(zj=1))
    ge(vec(zk=1))
    for name in ("ell", "dh", "da", "db"):
        ge(vec(**{name: 1}), 1)
    ge(vec(Lj=1))
    ge(vec(Lk=1))

    # Nonnegative and ordered x coordinates.
    ge(add(vec(M=1), vec(dh=-1)))
    ge(add(vec(q=1), vec(da=-1)))
    ge(add(vec(q=1), vec(db=-1)))
    x_root = add(vec(M=1), vec(ell=1))
    x_gainers = (
        add(vec(M=1), vec(dh=-1)),
        add(vec(q=1), vec(da=-1)),
        add(vec(q=1), vec(db=-1)),
    )
    x_outsiders = (
        add(vec(zj=1), vec(Lj=1)),
        add(vec(zk=1), vec(Lk=1)),
    )
    for xg in x_gainers:
        ge(add(x_root, scale(xg, -1)))
        for xo in x_outsiders:
            ge(add(xg, scale(xo, -1)))

    # Efficiency and compatibility of the two z-tight split-cover rows.
    A_eq.append(add(vec(dh=1), vec(da=1), vec(db=1),
                    vec(ell=-1), vec(Lj=-1), vec(Lk=-1)))
    b_eq.append(F(0))
    ge(add(vec(da=1), vec(Lk=-1)))
    ge(add(vec(db=1), vec(Lj=-1)))

    # Reserve failure implies every two-gain sum exceeds ell.  The decoration
    # term is nonnegative, so this is a necessary relaxation of PXC93a.
    for left, right in (("dh", "da"), ("dh", "db"), ("da", "db")):
        ge(add(vec(**{left: 1}), vec(**{right: 1}), vec(ell=-1)), 1)

    if include_root_witness:
        # Root singleton witness: nonnegative, efficient, and in both cover rows.
        for name in ("yh", "ya", "yb", "yj", "yk"):
            ge(vec(**{name: 1}))
        total_z = add(vec(M=2), vec(q=2), vec(zj=1), vec(zk=1))
        A_eq.append(add(vec(yh=1), vec(ya=1), vec(yb=1), vec(yj=1), vec(yk=1),
                        scale(total_z, -1)))
        b_eq.append(F(0))
        cover_j = coalition((R, H, B, J))
        cover_k = coalition((R, H, A, K))
        ge(add(witness_sum(cover_j), scale(z_sum(cover_j), -1)))
        ge(add(witness_sum(cover_k), scale(z_sum(cover_k), -1)))
    return A_ub, b_ub, A_eq, b_eq


def family_feasible(rows, include_root_witness=True):
    A_ub, b_ub, A_eq, b_eq = base_system(include_root_witness)

    def ge(row):
        A_ub.append(scale(row, -1))
        b_ub.append(F(0))

    for mask in rows:
        # A z-tight original-game row must contain x and, when requested, the
        # root singleton witness.
        ge(x_minus_z(mask))
        if include_root_witness:
            ge(add(witness_sum(mask), scale(z_sum(mask), -1)))
    status, _optimum, point = exact_linprog(
        [F(0)] * DIM, A_ub, b_ub, A_eq, b_eq
    )
    return status == "optimal", point


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = tuple(
        mask for mask in range(1, FULL)
        if mask.bit_count() >= 2 and tangent_form(mask) != (0, 0)
    )
    complete = []
    for size in (1, 2):
        for family in itertools.combinations(rows, size):
            forms = tuple(tangent_form(mask) for mask in family)
            if closes_negative_quadrant(forms):
                complete.append(family)
    # Deduplicate equal incidence families only; top membership remains
    # load-bearing in the compatibility and singleton-witness systems.
    feasible = []
    for family in complete:
        answer, point = family_feasible(family)
        if answer:
            feasible.append({
                "rows": list(family),
                "forms": [list(tangent_form(mask)) for mask in family],
                "point": [str(q) for q in point],
            })
    if feasible:
        raise AssertionError(("complete blocker family survived", feasible[:3]))

    a_rows = (
        ("aj", coalition((A, J))),
        ("haj", coalition((H, A, J))),
        ("ra", coalition((R, A))),
        ("rab", coalition((R, A, B))),
        ("raj", coalition((R, A, J))),
        ("rabj", coalition((R, A, B, J))),
        ("rha", coalition((R, H, A))),
        ("rhaj", coalition((R, H, A, J))),
    )
    b_rows = (
        ("bk", coalition((B, K))),
        ("hbk", coalition((H, B, K))),
        ("rb", coalition((R, B))),
        ("rab", coalition((R, A, B))),
        ("rbk", coalition((R, B, K))),
        ("rabk", coalition((R, A, B, K))),
        ("rhb", coalition((R, H, B))),
        ("rhbk", coalition((R, H, B, K))),
    )
    expected_table = (
        "IIFXIFXI", "IIXXIXXI", "FXFXFFXF", "XXXXXXXX",
        "IIFXIFXI", "FXFXFFXF", "XXXXXXXX", "IIFXIFXI",
    )
    observed_table = []
    for _a_name, a_row in a_rows:
        statuses = []
        for _b_name, b_row in b_rows:
            family = tuple(sorted({a_row, b_row}))
            forms = tuple(tangent_form(mask) for mask in family)
            if not closes_negative_quadrant(forms):
                status = "I"
            elif not family_feasible(family, include_root_witness=False)[0]:
                status = "X"
            elif not family_feasible(family, include_root_witness=True)[0]:
                status = "F"
            else:
                status = "S"
            statuses.append(status)
        observed_table.append("".join(statuses))
    if tuple(observed_table) != expected_table:
        raise AssertionError(("canonical I/X/F table changed", observed_table))

    # The first-ceiling constraints alone are feasible; this is the fail-open
    # control against an inconsistent base encoding.
    status, _optimum, base_point = exact_linprog(
        [F(0)] * DIM, *base_system()
    )
    if status != "optimal":
        raise AssertionError(("base system unexpectedly infeasible", status))

    distinct_forms = sorted({tangent_form(mask) for mask in rows})
    closing_form_families = 0
    for size in range(1, len(distinct_forms) + 1):
        for family in itertools.combinations(distinct_forms, size):
            if not closes_negative_quadrant(family):
                continue
            closing_form_families += 1
            if not any(
                closes_negative_quadrant(subfamily)
                for subsize in (1, 2)
                for subfamily in itertools.combinations(family, subsize)
            ):
                raise AssertionError(("closing form family needs more than two rows", family))
    payload = {
        "claim": "two-row n=6 split-cover later-stage blocker no-go",
        "row_types": len(rows),
        "distinct_tangent_forms": [list(form) for form in distinct_forms],
        "complete_single_or_pair_families": len(complete),
        "closing_distinct_form_families": closing_form_families,
        "maximum_minimal_closing_family_size": 2,
        "feasible_complete_families": 0,
        "canonical_table": {
            "columns": [name for name, _row in b_rows],
            "rows": {
                name: statuses for (name, _row), statuses in zip(a_rows, observed_table)
            },
            "legend": {
                "I": "tangent-incomplete",
                "X": "infeasible before the root singleton witness",
                "F": "scalar-feasible but root-witness-infeasible",
            },
        },
        "base_system_feasible": True,
        "base_witness": {name: str(value) for name, value in zip(NAMES, base_point)},
        "conclusion": (
            "under the literal two-row split cover, order, cover compatibility, "
            "reserve failure, and the root singleton witness exclude every "
            "one-/two-row family that can pin the tied second Lmax stratum"
        ),
        "scope": (
            "a two-dimensional cone has a closing subfamily of at most two in "
            "this finite form list; the result does not classify other n=6 "
            "positive extreme top-cover incidences"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
