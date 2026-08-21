#!/usr/bin/env python3
"""Exact blocker no-go checks for the two n=6 zero-loss cover boundaries.

The checks are necessary-relaxation arguments.  They retain the ordered
single-heavy allocation inequalities, efficiency, comparison compatibility,
the necessary pair-sum consequence of reserve failure, and one exactness
witness with y_r=0.  Infeasibility therefore excludes a completion satisfying
the full hypotheses, although the programs do not encode a whole game.
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


def coalition(*players):
    return sum(1 << player for player in players)


def z_sum(mask):
    rows = []
    for player, name in ((R, "M"), (H, "M"), (A, "q"), (B, "q"),
                         (J, "zj"), (K, "zk")):
        if mask >> player & 1:
            rows.append(vec(**{name: 1}))
    return add(*rows) if rows else [F(0)] * DIM


def x_minus_z(mask):
    rows = []
    for player, name, coefficient in (
        (R, "ell", 1), (H, "dh", -1), (A, "da", -1),
        (B, "db", -1), (J, "Lj", 1), (K, "Lk", 1),
    ):
        if mask >> player & 1:
            rows.append(vec(**{name: coefficient}))
    return add(*rows) if rows else [F(0)] * DIM


def witness_sum(mask):
    # The exactness witness used here has y_r=0.
    rows = []
    for player, name in ((H, "yh"), (A, "ya"), (B, "yb"),
                         (J, "yj"), (K, "yk")):
        if mask >> player & 1:
            rows.append(vec(**{name: 1}))
    return add(*rows) if rows else [F(0)] * DIM


def base_system(cover_rows):
    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    def ge(row, rhs=0):
        A_ub.append(scale(row, -1))
        b_ub.append(F(-rhs))

    # All genuinely strict homogeneous inequalities use a common margin one.
    ge(add(vec(M=1), vec(q=-1)), 1)
    ge(add(vec(q=1), vec(zj=-1)), 1)
    ge(add(vec(q=1), vec(zk=-1)), 1)
    ge(vec(zj=1))
    ge(vec(zk=1))
    for name in ("ell", "dh", "da", "db"):
        ge(vec(**{name: 1}), 1)
    # Outsider losses are weak: the boundary cases have one loss equal to zero.
    ge(vec(Lj=1))
    ge(vec(Lk=1))

    # Nonnegative ordered x coordinates.
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

    # Efficiency and comparison compatibility of every retained cover row.
    A_eq.append(add(vec(dh=1), vec(da=1), vec(db=1),
                    vec(ell=-1), vec(Lj=-1), vec(Lk=-1)))
    b_eq.append(F(0))
    for mask in cover_rows:
        ge(x_minus_z(mask))

    # Reserve failure implies every two-gain sum is strictly above ell.
    for left, right in (("dh", "da"), ("dh", "db"), ("da", "db")):
        ge(add(vec(**{left: 1}), vec(**{right: 1}), vec(ell=-1)), 1)

    # A root exactness witness, required to satisfy all retained cover rows.
    for name in ("yh", "ya", "yb", "yj", "yk"):
        ge(vec(**{name: 1}))
    total_z = add(vec(M=2), vec(q=2), vec(zj=1), vec(zk=1))
    A_eq.append(add(vec(yh=1), vec(ya=1), vec(yb=1), vec(yj=1), vec(yk=1),
                    scale(total_z, -1)))
    b_eq.append(F(0))
    for mask in cover_rows:
        ge(add(witness_sum(mask), scale(z_sum(mask), -1)))
    return A_ub, b_ub, A_eq, b_eq


def add_tight_row(system, mask):
    A_ub, b_ub, A_eq, b_eq = (list(part) for part in system)
    for row in (x_minus_z(mask), add(witness_sum(mask), scale(z_sum(mask), -1))):
        A_ub.append(scale(row, -1))
        b_ub.append(F(0))
    return A_ub, b_ub, A_eq, b_eq


def feasible(system):
    status, _optimum, point = exact_linprog([F(0)] * DIM, *system)
    return status == "optimal", point


def closes_negative_quadrant(forms):
    # Homogeneity replaces (t,s)<=0, (t,s)!=0 by t+s<=-1.
    A_ub = [[F(1), F(0)], [F(0), F(1)], [F(1), F(1)]]
    b_ub = [F(0), F(0), F(-1)]
    for ct, cs in forms:
        A_ub.append([F(-ct), F(-cs)])
        b_ub.append(F(0))
    status, _optimum, _point = exact_linprog(
        [F(0), F(0)], A_ub, b_ub, [], []
    )
    return status == "infeasible"


def outsider_partition_audit():
    # Cover rows rhj and rhabk imply u_j=0 and u_k=-u_a-u_b.
    cover_rows = (coalition(R, H, J), coalition(R, H, A, B, K))
    system = base_system(cover_rows)
    base_ok, base_point = feasible(system)
    if not base_ok:
        raise AssertionError("outsider-partition base system is infeasible")

    def form(mask):
        return (
            int(bool(mask >> A & 1)) - int(bool(mask >> K & 1)),
            int(bool(mask >> B & 1)) - int(bool(mask >> K & 1)),
        )

    rows = tuple(
        mask for mask in range(1, FULL)
        if mask.bit_count() >= 2 and form(mask) != (0, 0)
    )
    closing = []
    survivors = []
    for size in (1, 2):
        for family in itertools.combinations(rows, size):
            if not closes_negative_quadrant(tuple(form(mask) for mask in family)):
                continue
            closing.append(family)
            answer, point = feasible(
                add_tight_row(add_tight_row(system, family[0]), family[1])
                if size == 2 else add_tight_row(system, family[0])
            )
            if answer:
                survivors.append((family, point))
    if len(closing) != 381:
        raise AssertionError(("unexpected outsider-partition count", len(closing)))
    if survivors:
        raise AssertionError(("outsider-partition blocker survived", survivors[:3]))

    distinct_forms = sorted({form(mask) for mask in rows})
    if distinct_forms != [
        (-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1),
    ]:
        raise AssertionError(("unexpected tangent-form set", distinct_forms))
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
                raise AssertionError(("closing form family needs over two rows", family))
    if closing_form_families != 40:
        raise AssertionError(("unexpected closing form-family count", closing_form_families))

    singleton_forms = {
        "j": list(form(1 << J)),
        "k": list(form(1 << K)),
    }
    if singleton_forms != {"j": [0, 0], "k": [-1, -1]}:
        raise AssertionError(("singleton trace mismatch", singleton_forms))
    return {
        "cover_rows": ["rhj", "rhabk"],
        "tangent": "u_j=0, u_k=-u_a-u_b; set (t,s)=(u_a,u_b)",
        "proper_nonsingleton_nonzero_row_masks": len(rows),
        "distinct_nonzero_tangent_forms": [list(form) for form in distinct_forms],
        "closing_distinct_form_families": closing_form_families,
        "maximum_minimal_closing_family_size": 2,
        "closing_labelled_one_or_two_row_families": len(closing),
        "feasible_closing_families": 0,
        "singleton_traces": {
            "j": {"form": singleton_forms["j"], "effect": "zero form"},
            "k": {
                "form": singleton_forms["k"],
                "effect": "-(t+s) is nonnegative on the descent cone and cannot close it",
            },
        },
        "base_system_feasible": True,
        "base_witness": {name: str(value) for name, value in zip(NAMES, base_point)},
    }


def h2_boundary_audit():
    # The cover rows force da=ell, Lj=0, Lk=dh+db.  Its tangent is
    # (u_a,u_b,u_j,u_k)=(0,-t,0,t), so a blocker contains b and avoids k.
    cover_rows = (coalition(R, A), coalition(R, H, J), coalition(H, B, K))
    system = base_system(cover_rows)
    base_ok, base_point = feasible(system)
    if not base_ok:
        raise AssertionError("H2 boundary base system is infeasible")
    witness = dict(zip(NAMES, base_point))
    if not (witness["da"] == witness["ell"] and witness["Lj"] == 0
            and witness["Lk"] == witness["dh"] + witness["db"]):
        raise AssertionError(("H2 base witness misses forced boundary", witness))

    candidates = tuple(
        mask for mask in range(1, FULL)
        if mask.bit_count() >= 2 and mask >> B & 1 and not (mask >> K & 1)
    )
    survivors = []
    for mask in candidates:
        answer, point = feasible(add_tight_row(system, mask))
        if answer:
            survivors.append((mask, point))
    if len(candidates) != 15:
        raise AssertionError(("unexpected H2 blocker count", len(candidates)))
    if survivors:
        raise AssertionError(("H2 blocker survived", survivors[:3]))

    return {
        "cover_rows": ["ra", "rhj", "hbk"],
        "forced_boundary_equalities": ["d_a=ell", "L_j=0", "L_k=d_h+d_b"],
        "tangent": "(u_a,u_b,u_j,u_k)=(0,-t,0,t)",
        "candidate_rule": "proper nonsingleton row contains b and avoids k",
        "candidate_blockers": len(candidates),
        "feasible_candidate_blockers": 0,
        "singleton_traces": {
            "b": "would have blocking derivative -t but is not z-tight because z_b=q>0",
            "j": "zero derivative",
            "k": "positive derivative along the improving orientation and does not block",
        },
        "base_system_feasible": True,
        "base_witness": {name: str(value) for name, value in zip(NAMES, base_point)},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "exact n=6 zero-loss top-cover boundary blocker no-go",
        "hypotheses": [
            "M>q>z_j,z_k>=0; ell,d_h,d_a,d_b>0; L_j,L_k>=0",
            "d_h+d_a+d_b=ell+L_j+L_k",
            "x is nonnegative and ordered from root through gainers to outsiders",
            "every two-gain sum exceeds ell (necessary consequence of reserve failure)",
            "the displayed cover rows are z-tight and comparison-compatible with x",
            "a nonnegative efficient root exactness witness y with y_r=0 satisfies every retained z-tight row",
        ],
        "encoding_scope": (
            "homogeneous strict inequalities are scaled to margin one; this is a "
            "necessary relaxation, not a full exact-game or direct-failure encoding"
        ),
        "outsider_partition": outsider_partition_audit(),
        "h2_equality_boundary": h2_boundary_audit(),
        "conclusion": (
            "neither zero-loss boundary cover can acquire the later z-tight blockers "
            "required by staged Lmax optimality"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
