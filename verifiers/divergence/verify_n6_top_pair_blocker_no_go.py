#!/usr/bin/env python3
"""Exact necessary-system attack on the n=6 tight-top-pair boundary.

Assume the ordered single-heavy role pattern

    z_r=z_h=M > z_a=z_b=q > z_j,z_k,

with gainers h,a,b and nongainers r,j,k.  If the top pair {r,h} is
z-tight, its one-row cover pins the first Lmax stratum.  This verifier
enumerates every inclusion-minimal family of non-top incidence traces that
can exclude a second-stage descent of the tied block {a,b}, decorates those
traces by all possible r/h memberships, and tests a homogeneous exact-LP
relaxation containing:

* efficiency, nonnegativity, and the ordered role inequalities;
* comparison compatibility of every selected z-tight row with x;
* the necessary reserve-failure inequalities;
* failure of the two explicit n=6 direct intervals (all four branches);
* a root-zero exactness witness satisfying the pair and blocker rows.

Infeasibility would be a rigorous conditional no-go because the encoding
omits other game constraints.  Feasible cells are retained as countermodel
blueprints; this script never promotes them to exact games or selectors.
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
EXPECTED_MINIMAL_TRACE_FAMILIES = (
    (3,), (1, 2), (7, 11),
    (1, 6, 10), (1, 6, 11), (1, 7, 10),
    (2, 5, 9), (2, 5, 11), (2, 7, 9),
    (5, 6, 11), (7, 9, 10),
)
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


def z_sum(mask):
    rows = []
    if mask >> R & 1: rows.append(vec(M=1))
    if mask >> H & 1: rows.append(vec(M=1))
    if mask >> A & 1: rows.append(vec(q=1))
    if mask >> B & 1: rows.append(vec(q=1))
    if mask >> J & 1: rows.append(vec(zj=1))
    if mask >> K & 1: rows.append(vec(zk=1))
    return add(*rows) if rows else [F(0)] * DIM


def x_minus_z(mask):
    rows = []
    if mask >> R & 1: rows.append(vec(ell=1))
    if mask >> H & 1: rows.append(vec(dh=-1))
    if mask >> A & 1: rows.append(vec(da=-1))
    if mask >> B & 1: rows.append(vec(db=-1))
    if mask >> J & 1: rows.append(vec(Lj=1))
    if mask >> K & 1: rows.append(vec(Lk=1))
    return add(*rows) if rows else [F(0)] * DIM


def witness_sum(mask):
    # Root witness has y_r=0.
    rows = []
    if mask >> H & 1: rows.append(vec(yh=1))
    if mask >> A & 1: rows.append(vec(ya=1))
    if mask >> B & 1: rows.append(vec(yb=1))
    if mask >> J & 1: rows.append(vec(yj=1))
    if mask >> K & 1: rows.append(vec(yk=1))
    return add(*rows) if rows else [F(0)] * DIM


def improves(traces, target):
    """Return whether a normalized second-stage improving direction exists."""
    # Coordinates are a,b,j,k.  Top coordinates are fixed and efficiency is
    # sum d=0.  A designated current-block coordinate is normalized to -1.
    aub, bub = [], []
    for trace in traces:
        aub.append([-F(int(bool(trace >> i & 1))) for i in range(4)])
        bub.append(F(0))
    for i in (0, 1):
        row = [F(0)] * 4
        row[i] = F(1)
        aub.append(row)
        bub.append(F(0))
    aeq = [[F(1)] * 4, [F(int(i == target)) for i in range(4)]]
    beq = [F(0), F(-1)]
    status, _value, _point = exact_linprog([F(0)] * 4, aub, bub, aeq, beq)
    if status not in ("optimal", "infeasible"):
        raise RuntimeError(("unexpected tangent LP status", status, traces, target))
    return status == "optimal"


def closes(traces):
    return not improves(traces, 0) and not improves(traces, 1)


def minimal_trace_families():
    # Trace 15 is zero on the efficiency subspace, but retaining it here is a
    # useful guard that the minimal-family logic discards it automatically.
    # Search every subset size, but prune every superset of an already found
    # closing family before solving an LP.  This keeps the census exhaustive
    # without repeatedly solving the thousands of nonminimal supersets.
    traces = tuple(range(1, 16))
    closing = []
    for size in range(1, len(traces) + 1):
        for family in itertools.combinations(traces, size):
            family_set = set(family)
            if any(set(known) <= family_set for known in closing):
                continue
            if not closes(family):
                continue
            closing.append(family)
    return tuple(closing)


def decorate(trace, top_code):
    row = sum(1 << (i + 2) for i in range(4) if trace >> i & 1)
    if top_code & 1: row |= 1 << R
    if top_code & 2: row |= 1 << H
    return row


def row_allowed(row):
    if row == FULL:
        return False
    if row.bit_count() >= 2:
        return True
    return row in (1 << J, 1 << K)


def direct_budget(p):
    # PXC93b with p one outsider and u the other.
    if p == J:
        xp = add(vec(zj=1), vec(Lj=1))
        zu = vec(zk=1)
        zp = vec(zj=1)
    else:
        xp = add(vec(zk=1), vec(Lk=1))
        zu = vec(zj=1)
        zp = vec(zk=1)
    xg = add(vec(M=1), vec(q=2), vec(dh=-1), vec(da=-1), vec(db=-1))
    total = add(vec(M=2), vec(q=2), vec(zj=1), vec(zk=1))
    return scale(add(scale(xg, -1), scale(xp, -3), vec(M=-1), scale(zu, -1),
                     scale(add(total, scale(zp, -1)), F(8, 5))), F(1, 3))


def system(rows, maximum, direct_branches, include_witness=True):
    aub, bub, aeq, beq = [], [], [], []

    def ge(row, rhs=0):
        aub.append(scale(row, -1))
        bub.append(F(-rhs))

    # Homogeneous strict role cell, normalized to common margin one.
    ge(add(vec(M=1), vec(q=-1)), 1)
    ge(add(vec(q=1), vec(zj=-1)), 1)
    ge(add(vec(q=1), vec(zk=-1)), 1)
    ge(vec(zj=1))
    ge(vec(zk=1))
    for name in ("ell", "dh", "da", "db"):
        ge(vec(**{name: 1}), 1)
    ge(vec(Lj=1))
    ge(vec(Lk=1))

    # Nonnegative ordered x coordinates.
    xroot = add(vec(M=1), vec(ell=1))
    xgainers = (
        add(vec(M=1), vec(dh=-1)),
        add(vec(q=1), vec(da=-1)),
        add(vec(q=1), vec(db=-1)),
    )
    xoutsiders = (add(vec(zj=1), vec(Lj=1)), add(vec(zk=1), vec(Lk=1)))
    for xg in xgainers:
        ge(xg)
        ge(add(xroot, scale(xg, -1)))
        for xo in xoutsiders:
            ge(add(xg, scale(xo, -1)))

    # Efficiency and tight-top-pair comparison.
    aeq.append(add(vec(dh=1), vec(da=1), vec(db=1), vec(ell=-1),
                   vec(Lj=-1), vec(Lk=-1)))
    beq.append(F(0))
    ge(add(vec(ell=1), vec(dh=-1)))

    # Fix a branch of d_max and define E=D-d_max as a linear form.
    gains = {H: vec(dh=1), A: vec(da=1), B: vec(db=1)}
    for player, gain in gains.items():
        ge(add(gains[maximum], scale(gain, -1)))
    eform = add(*(gain for player, gain in gains.items() if player != maximum))

    # Reserve failure with nonnegative decoration implies E-ell>0.
    ge(add(eform, vec(ell=-1)), 1)

    # Each explicit direct interval must fail on its chosen lower/upper side.
    for p, branch in zip((J, K), direct_branches):
        other_loss = vec(Lk=1) if p == J else vec(Lj=1)
        if branch == "lower":
            # ell+L_u > E.
            ge(add(vec(ell=1), other_loss, scale(eform, -1)), 1)
        else:
            # E > B_p.
            ge(add(eform, scale(direct_budget(p), -1)), 1)

    # Selected rows are z-tight in the original game, hence x-compatible.
    for row in rows:
        ge(x_minus_z(row))
        if row == 1 << J:
            aeq.append(vec(zj=1)); beq.append(F(0))
        elif row == 1 << K:
            aeq.append(vec(zk=1)); beq.append(F(0))

    if include_witness:
        for name in ("yh", "ya", "yb", "yj", "yk"):
            ge(vec(**{name: 1}))
        total = add(vec(M=2), vec(q=2), vec(zj=1), vec(zk=1))
        aeq.append(add(vec(yh=1), vec(ya=1), vec(yb=1), vec(yj=1), vec(yk=1),
                       scale(total, -1)))
        beq.append(F(0))
        # Pair row at the root-zero witness.
        ge(add(vec(yh=1), vec(M=-2)))
        for row in rows:
            ge(add(witness_sum(row), scale(z_sum(row), -1)))

    return aub, bub, aeq, beq


def feasible(rows, maximum, branches, include_witness=True):
    status, _value, point = exact_linprog(
        [F(0)] * DIM, *system(rows, maximum, branches, include_witness)
    )
    if status not in ("optimal", "infeasible"):
        raise RuntimeError(("unexpected necessary-system LP status", status,
                            rows, maximum, branches, include_witness))
    return status == "optimal", point


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    families = minimal_trace_families()
    if families != EXPECTED_MINIMAL_TRACE_FAMILIES:
        raise AssertionError(("minimal trace census changed", families))

    decorated = []
    for family in families:
        for codes in itertools.product(range(4), repeat=len(family)):
            rows = tuple(decorate(trace, code) for trace, code in zip(family, codes))
            if len(set(rows)) != len(rows) or not all(map(row_allowed, rows)):
                continue
            decorated.append((family, codes, rows))

    survivors_without_witness = []
    survivors = []
    branches = tuple(itertools.product(("lower", "upper"), repeat=2))
    for family, codes, rows in decorated:
        for maximum in (H, A, B):
            for choice in branches:
                answer, point = feasible(rows, maximum, choice, include_witness=False)
                if not answer:
                    continue
                survivors_without_witness.append((family, codes, rows, maximum, choice))
                answer, point = feasible(rows, maximum, choice, include_witness=True)
                if answer:
                    survivors.append({
                        "traces": list(family),
                        "top_codes": list(codes),
                        "rows": list(rows),
                        "maximum_gainer": maximum,
                        "direct_failure_branches": list(choice),
                        "point": {name: str(value) for name, value in zip(NAMES, point)},
                    })

    # Fail-open control: the allocation/direct base is genuinely feasible.
    base_rows = ()
    base = None
    for maximum in (H, A, B):
        for choice in branches:
            answer, point = feasible(base_rows, maximum, choice, include_witness=True)
            if answer:
                base = {"maximum_gainer": maximum, "branches": list(choice),
                        "point": {name: str(value) for name, value in zip(NAMES, point)}}
                break
        if base is not None:
            break
    if base is None:
        raise AssertionError("top-pair allocation/direct base unexpectedly infeasible")

    payload = {
        "claim": "exact necessary-system audit of the n=6 tight-top-pair boundary",
        "minimal_trace_families": [list(family) for family in families],
        "maximum_minimal_trace_family_size": max(map(len, families)),
        "decorated_families": len(decorated),
        "allocation_direct_branches": len(decorated) * 3 * len(branches),
        "survivors_before_root_witness": len(survivors_without_witness),
        "survivors_after_root_witness": len(survivors),
        "survivors": survivors,
        "fail_open_base": base,
        "scope": (
            "continuous exact-rational necessary relaxation: closure of the second "
            "Lmax stratum, role order, comparison, reserve failure, two explicit direct-"
            "interval failures, and the root singleton witness; it omits saturation, "
            "other singleton witnesses, and full selector certificates"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
