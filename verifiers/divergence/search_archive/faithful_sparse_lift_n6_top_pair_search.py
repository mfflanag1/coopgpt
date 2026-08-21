#!/usr/bin/env python3
"""Necessary-system search for the n=6 eta=0/top-pair boundary.

This is discovery code, not a game verifier.  After the tight row {r,h}
pins the two-player Lmax top, it enumerates inclusion-minimal non-top trace
families that close the tied {a,b} second-stage tangent cone.  Traces are
decorated by arbitrary memberships of r,h and tested against bounded integer
selector profiles.  Every promoted cell satisfies comparison compatibility,
the packet-reserve violation, the complete exact direct-packet negation, and
exact LP witnesses for all six singleton coordinates in the retained-row
polytope.  Lmin/Lmax selector realization is deliberately not asserted.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "verifiers" / "divergence")]

from exactlp import exact_linprog  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402

N = 6
R, H, A, B, J, K = range(N)
TARGET = F(2, 3)


def csum(point, row):
    return sum((point[i] for i in range(N) if row >> i & 1), F(0))


def feasible(total, constraints, fixed=()):
    aub, bub = [], []
    for row, bound in constraints.items():
        aub.append([-F(int(bool(row >> i & 1))) for i in range(N)])
        bub.append(-bound)
    for i in range(N):
        row = [F(0)] * N; row[i] = -1
        aub.append(row); bub.append(F(0))
    aeq, beq = [[F(1)] * N], [total]
    for i, value in fixed:
        row = [F(0)] * N; row[i] = 1
        aeq.append(row); beq.append(value)
    status, _value, point = exact_linprog([F(0)] * N, aub, bub, aeq, beq)
    if status == "optimal":
        return tuple(F(q) for q in point)
    if status == "infeasible":
        return None
    raise RuntimeError(("unexpected feasibility LP status", status))


def tangent_improvement(traces, target):
    """Exact feasible improving direction, normalized by d_target=-1."""
    # Four variables are a,b,j,k.  Earlier top coordinates are zero and
    # efficiency is sum d=0.  Current-block coordinates must be nonpositive.
    aub, bub = [], []
    for trace in traces:
        aub.append([-F(int(bool(trace >> q & 1))) for q in range(4)])
        bub.append(F(0))
    for q in (0, 1):
        row = [F(0)] * 4; row[q] = 1
        aub.append(row); bub.append(F(0))
    aeq = [[F(1)] * 4, [F(int(q == target)) for q in range(4)]]
    beq = [F(0), F(-1)]
    status, _value, point = exact_linprog([F(0)] * 4, aub, bub, aeq, beq)
    if status == "optimal":
        return tuple(F(q) for q in point)
    if status == "infeasible":
        return None
    raise RuntimeError(("unexpected tangent LP status", status))


def closes(traces):
    return tangent_improvement(traces, 0) is None and tangent_improvement(traces, 1) is None


def minimal_trace_families(max_size):
    traces = tuple(range(1, 16))
    answer = []
    for size in range(1, max_size + 1):
        for family in itertools.combinations(traces, size):
            family_set = set(family)
            if any(set(known) <= family_set for known in answer):
                continue
            if not closes(family):
                continue
            answer.append(family)
    return tuple(answer)


def direct_interval_data(total, x, z):
    """The two PXC93b singleton-outsider direct-packet intervals."""
    gain = (z[H] - x[H], z[A] - x[A], z[B] - x[B])
    energy = sum(gain, F(0)) - max(gain)
    ell = x[R] - z[R]
    x_gainers = x[H] + x[A] + x[B]
    answer = []
    for p, u in ((J, K), (K, J)):
        lower = ell + x[u] - z[u]
        upper = (
            -x_gainers - 3 * x[p] - (z[R] + z[u])
            + F(8, 5) * (total - z[p])
        ) / 3
        answer.append({
            "p": p, "u": u, "energy": energy,
            "lower": lower, "upper": upper,
            "interval_hits": lower <= energy <= upper,
        })
    return tuple(answer)


def profiles(total_max):
    """Bounded integer ordered single-heavy profiles, labels fixed."""
    for total in range(6, total_max + 1):
        for xr in range(1, total + 1):
            for xh in range(0, xr + 1):
                for xa in range(0, xh + 1):
                    for xj in range(0, xa + 1):
                        if xr + xh + 2 * xa + 2 * xj != total:
                            continue
                        x = tuple(map(F, (xr, xh, xa, xa, xj, xj)))
                        for top in range(xh + 1, xr):
                            for sub in range(xa + 1, top):
                                remainder = total - 2 * top - 2 * sub
                                for zj in range(remainder + 1):
                                    zk = remainder - zj
                                    if not (0 <= zj <= zk < sub):
                                        continue
                                    z = tuple(map(F, (top, top, sub, sub, zj, zk)))
                                    # Exactly h,a,b gain; j,k are nongainers.
                                    if z[J] > x[J] or z[K] > x[K]:
                                        continue
                                    # Pair compatibility and the necessary relaxed
                                    # reserve failure E>ell from the PXC93 system.
                                    if xr + xh < 2 * top:
                                        continue
                                    gains = (z[H] - x[H], z[A] - x[A], z[B] - x[B])
                                    loss = x[R] - z[R]
                                    if sum(gains, F(0)) - max(gains) <= loss:
                                        continue
                                    intervals = direct_interval_data(F(total), x, z)
                                    if any(item["interval_hits"] for item in intervals):
                                        continue
                                    if has_direct_packet(x, z, TARGET):
                                        continue
                                    yield total, x, z, intervals


def decorate(trace, top_code):
    # trace bits 0..3 correspond to a,b,j,k.
    row = sum((1 << (q + 2)) for q in range(4) if trace >> q & 1)
    if top_code & 1: row |= 1 << R
    if top_code & 2: row |= 1 << H
    return row


def search(total_max, max_family_size, max_hits):
    families = minimal_trace_families(max_family_size)
    profs = tuple(profiles(total_max))
    hits = []
    tested_decorations = compatible = root_witness = all_witness = 0
    for family in families:
        for codes in itertools.product(range(4), repeat=len(family)):
            rows = tuple(decorate(trace, code) for trace, code in zip(family, codes))
            if len(set(rows)) != len(rows):
                continue
            tested_decorations += 1
            for total, x, z, _intervals in profs:
                if any(csum(x, row) < csum(z, row) for row in rows):
                    continue
                compatible += 1
                constraints = {3: 2 * z[R]}
                constraints.update({row: csum(z, row) for row in rows})
                witnesses = []
                point = feasible(total, constraints, ((R, F(0)),))
                if point is None:
                    continue
                root_witness += 1; witnesses.append(point)
                for player in range(1, N):
                    point = feasible(total, constraints, ((player, F(0)),))
                    if point is None:
                        break
                    witnesses.append(point)
                else:
                    all_witness += 1
                    hits.append({
                        "total": str(total), "x": list(map(str, x)), "z": list(map(str, z)),
                        "traces": list(family), "top_codes": list(codes), "rows": list(rows),
                        "singleton_witnesses": [list(map(str, p)) for p in witnesses],
                    })
                    if len(hits) >= max_hits:
                        return families, profs, hits, {
                            "decorations": tested_decorations, "compatible_cells": compatible,
                            "root_witness_cells": root_witness, "all_singleton_cells": all_witness,
                            "truncated_at_hits": max_hits,
                        }
    return families, profs, hits, {
        "decorations": tested_decorations, "compatible_cells": compatible,
        "root_witness_cells": root_witness, "all_singleton_cells": all_witness,
        "truncated_at_hits": None,
    }


def calibrations():
    # Feasible eta=0 base with all singleton witnesses.
    total = F(18); z = tuple(map(F, (5, 5, 3, 3, 1, 1)))
    base = {3: F(10)}
    base_witnesses = [feasible(total, base, ((i, F(0)),)) is not None for i in range(N)]
    if not all(base_witnesses): raise AssertionError("top-pair base lost singleton witnesses")
    # Fixed PXC88 Cx no-go: row 023>=10 and M>4 contradict root zero.
    z0 = (F(21, 5), F(21, 5), F(19, 5), F(19, 5), F(1), F(1))
    fixed = {3: F(42, 5), 13: F(10)}
    if feasible(F(18), fixed, ((R, F(0)),)) is not None:
        raise AssertionError("fixed-Cx root obstruction disappeared")
    return {
        "feasible_pair_base": {"total": "18", "z": list(map(str, z)),
                               "pair_row": {"3": "10"}, "all_singletons": True},
        "fixed_Cx_no_go": {"z": list(map(str, z0)), "rows": {"3": "42/5", "13": "10"},
                              "root_singleton_feasible": False},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-max", type=int, default=24)
    parser.add_argument("--max-family-size", type=int, default=15)
    parser.add_argument("--max-hits", type=int, default=50)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    families, profs, hits, stats = search(args.total_max, args.max_family_size, args.max_hits)
    payload = {
        "claim": "bounded exact necessary-system search for n=6 eta=0 boundary",
        "calibrations": calibrations(),
        "bounds": {"total_max": args.total_max, "max_trace_family_size": args.max_family_size,
                   "max_hits": args.max_hits},
        "minimal_trace_family_count": len(families),
        "minimal_trace_families": [list(q) for q in families],
        "trace_family_enumeration_exhaustive": args.max_family_size >= 15,
        "maximum_minimal_trace_family_size": max(map(len, families), default=0),
        "trace_bit_order": ["a", "b", "j", "k"],
        "top_code_legend": {"0": "none", "1": "r", "2": "h", "3": "r,h"},
        "profile_cell": (
            "integer x=(xr,xh,xa,xa,xo,xo), "
            "z=(M,M,q,q,zj,zk), xr>M>xh>=xa>=xo>=0, "
            "M>q>zk>=zj>=0, with exactly h,a,b gaining and j,k nongaining"
        ),
        "reserve_direct_failing_profile_count": len(profs),
        "reserve_direct_failing_profiles": [
            {
                "total": str(total), "x": list(map(str, x)), "z": list(map(str, z)),
                "direct_interval_disjunctions": [
                    {key: (value if key in ("p", "u") or isinstance(value, bool)
                           else str(value)) for key, value in item.items()}
                    for item in intervals
                ],
            }
            for total, x, z, intervals in profs
        ],
        "stats": stats, "feasible_cells": hits,
        "scope": ("necessary conditions only in the displayed bounded integer profile cell: "
                  "exact tangent closure through the stated trace-family bound, comparison, "
                  "efficiency, necessary reserve failure, both PXC93b interval failures, full "
                  "direct failure, and six singleton witnesses; does not assert existence of "
                  "a complete Lmin certificate or either selector"),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__": main()
