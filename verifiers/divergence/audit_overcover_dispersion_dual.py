#!/usr/bin/env python3
"""Exact primal/dual audit for minimum-dispersion Lmax over-covers.

For the proper Lmax top block H and the family C of proper z-tight
coalitions, the primal dispersion LP is

    min theta
    sum_C lambda_C 1_C = eta 1 + alpha,
    sum_H alpha_i = 1,
    0 <= alpha_i <= theta, lambda, eta >= 0.

Its player-price dual is

    max t
    y(C) >= 0                 (C in C),
    y(N) <= 0,
    q_i >= t + y_i            (i in H),
    q >= 0, sum_H q_i <= 1.

The script independently solves both rational LPs and checks strong duality
and complementary slackness.  Archive counts are finite regression evidence;
the dual formula itself follows by ordinary LP duality.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from audit_lmax_overcover import coalition_sum, records, top_certificate  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def tight_data(values, z):
    n = len(z)
    full = (1 << n) - 1
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == values[coalition]
    )
    return top, tight


def dispersion_dual(values, z):
    """Solve the exact player-price dual and return a checkable witness."""
    n = len(z)
    top, tight = tight_data(values, z)

    # Variables are y[0:n] (free), q[top] (made nonnegative explicitly),
    # and t (free).  exact_linprog uses A u <= b.
    q_index = {player: n + j for j, player in enumerate(top)}
    t_index = n + len(top)
    width = t_index + 1
    inequalities, rhs = [], []

    for coalition in tight:
        row = [F(0)] * width
        for player in range(n):
            if coalition >> player & 1:
                row[player] = F(-1)  # y(C) >= 0
        inequalities.append(row)
        rhs.append(F(0))

    row = [F(0)] * width
    for player in range(n):
        row[player] = F(1)  # y(N) <= 0
    inequalities.append(row)
    rhs.append(F(0))

    for player in top:
        row = [F(0)] * width
        row[q_index[player]] = F(-1)  # q_i >= 0
        inequalities.append(row)
        rhs.append(F(0))

        row = [F(0)] * width
        row[player] = F(1)
        row[t_index] = F(1)
        row[q_index[player]] = F(-1)  # t+y_i <= q_i
        inequalities.append(row)
        rhs.append(F(0))

    row = [F(0)] * width
    for player in top:
        row[q_index[player]] = F(1)  # sum q <= 1
    inequalities.append(row)
    rhs.append(F(1))

    objective = [F(0)] * width
    objective[t_index] = F(-1)
    status, negative_t, solution = exact_linprog(
        objective, inequalities, rhs, [], []
    )
    if status != "optimal":
        raise RuntimeError(f"dispersion dual returned {status}")

    y = tuple(solution[player] for player in range(n))
    q = tuple(
        solution[q_index[player]] if player in q_index else F(0)
        for player in range(n)
    )
    t = solution[t_index]
    if negative_t != -t:
        raise AssertionError("dual objective orientation changed")
    if any(coalition_sum(y, coalition) < 0 for coalition in tight):
        raise AssertionError("negative tight-coalition price")
    if sum(y, F(0)) > 0 or any(value < 0 for value in q):
        raise AssertionError("dual sign condition failed")
    if sum(q, F(0)) > 1:
        raise AssertionError("dual probability budget failed")
    if any(t + y[player] > q[player] for player in top):
        raise AssertionError("dual top-player cap failed")
    return {"t": t, "y": y, "q": q, "top": top, "tight": tight}


def audit_pair(values, z):
    primal = top_certificate(values, z)
    dual = dispersion_dual(values, z)
    if dual["t"] != primal["theta"]:
        raise AssertionError(
            f"dispersion strong duality failed: {primal['theta']} != {dual['t']}"
        )

    # Complementarity for the independently returned optimal primal and dual.
    if sum(dual["q"], F(0)) != 1:
        raise AssertionError("positive theta must saturate the dual q budget")
    if any(coalition_sum(dual["y"], coalition) != 0 for coalition in primal["support"]):
        raise AssertionError("positive primal coalition misses its zero-price face")
    if primal["eta"] > 0 and sum(dual["y"], F(0)) != 0:
        raise AssertionError("positive eta misses total-price complementarity")
    for player, alpha in enumerate(primal["alpha"]):
        if alpha > 0 and dual["t"] + dual["y"][player] != dual["q"][player]:
            raise AssertionError("positive alpha misses its dual equality")
        if dual["q"][player] > 0 and alpha != primal["theta"]:
            raise AssertionError("positive q is not supported on a capped alpha coordinate")
    return primal, dual


def atomic_price_roots(values, z, theta):
    """Top roots for which the dual admits q=e_r at the optimum."""
    n = len(z)
    top, tight = tight_data(values, z)
    roots = []
    for root in top:
        inequalities, rhs = [], []
        for coalition in tight:
            row = [F(-1) if coalition >> player & 1 else F(0) for player in range(n)]
            inequalities.append(row)
            rhs.append(F(0))
        inequalities.append([F(1)] * n)
        rhs.append(F(0))
        for player in top:
            row = [F(0)] * n
            row[player] = F(1)
            inequalities.append(row)
            rhs.append((F(1) if player == root else F(0)) - theta)
        status, _objective, _solution = exact_linprog(
            [F(0)] * n, inequalities, rhs, [], []
        )
        if status == "optimal":
            roots.append(root)
    return tuple(roots)


def fixed_hostile_controls():
    controls = []
    for case in CASES:
        g = tuple(map(F, case["g"]))
        h = tuple(map(F, case["h"]))
        n = len(g)
        values = tuple(
            min(coalition_sum(g, coalition), coalition_sum(h, coalition))
            for coalition in range(1 << n)
        )
        x, z = tuple(case["x"]), tuple(case["z"])
        primal, _dual = audit_pair(values, z)
        atomic_roots = atomic_price_roots(values, z, primal["theta"])
        ceiling_roots = tuple(
            player
            for player in range(n)
            if z[player] == max(z) and x[player] >= max(z)
        )
        controls.append(
            {
                "name": case["name"],
                "n": n,
                "theta": str(primal["theta"]),
                "atomic_price_roots": atomic_roots,
                "ceiling_roots": ceiling_roots,
                "root_intersection": tuple(sorted(set(atomic_roots).intersection(ceiling_roots))),
            }
        )
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])

    seen = set()
    rows = []
    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for parsed_source, trail, values, x, z in records(data, source):
            if len(z) != args.n or sum(x, F(0)) <= 0 or sum(x, F(0)) != sum(z, F(0)):
                continue
            key = (values, z)
            if len(set(z)) == 1:
                continue
            primal, dual = audit_pair(values, z)
            atomic_roots = atomic_price_roots(values, z, primal["theta"])
            ceiling_roots = tuple(
                player
                for player in range(args.n)
                if z[player] == max(z) and x[player] >= max(z)
            )
            if not atomic_roots:
                raise AssertionError("no atomic dual price root")
            seen.add(key)
            rows.append(
                {
                    "source": parsed_source.name,
                    "trail": trail,
                    "theta": str(primal["theta"]),
                    "top_size": len(dual["top"]),
                    "primal_support": len(primal["support"]),
                    "dual_positive_q": sum(value > 0 for value in dual["q"]),
                    "dual_nonzero_y": sum(value != 0 for value in dual["y"]),
                    "atomic_price_roots": atomic_roots,
                    "ceiling_roots": ceiling_roots,
                }
            )

    if not rows:
        raise AssertionError("no nonuniform selected pairs found")
    report = {
        "status": "exact primal/dual minimum-dispersion over-cover audit",
        "dimension": args.n,
        "archive_records": len(rows),
        "distinct_nonuniform_pairs": len(seen),
        "strong_duality_failures": 0,
        "complementary_slackness_failures": 0,
        "atomic_price_root_failures": 0,
        "atomic_price_root_count_distribution": dict(
            sorted(Counter(len(row["atomic_price_roots"]) for row in rows).items())
        ),
        "atomic_ceiling_root_intersection_failures": sum(
            not set(row["atomic_price_roots"]).intersection(row["ceiling_roots"])
            for row in rows
        ),
        "atomic_ceiling_root_intersection_failure_records": [
            {
                "source": row["source"],
                "trail": row["trail"],
                "atomic_price_roots": row["atomic_price_roots"],
                "ceiling_roots": row["ceiling_roots"],
            }
            for row in rows
            if not set(row["atomic_price_roots"]).intersection(row["ceiling_roots"])
        ],
        "theta_counts": dict(sorted(Counter(row["theta"] for row in rows).items())),
        "maximum_primal_coalition_support": max(row["primal_support"] for row in rows),
        "maximum_dual_positive_q": max(row["dual_positive_q"] for row in rows),
        "maximum_dual_nonzero_y": max(row["dual_nonzero_y"] for row in rows),
        "fixed_hostile_controls": fixed_hostile_controls(),
        "dual": (
            "theta_plus=max t subject to y(S)>=0 on every proper z-tight coalition, "
            "y(N)<=0, q_i>=t+y_i on the top block, q>=0, and sum q<=1"
        ),
        "scope": (
            "LP duality proves the displayed formula; archive counts only audit the "
            "implementation and do not prove the hybrid-overlap conjecture"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
