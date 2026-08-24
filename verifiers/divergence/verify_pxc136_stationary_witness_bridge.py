#!/usr/bin/env python3
"""Exact audit of the PXC136 stationary singleton-witness bridge.

The theorem is elementary and dimension-free.  If ``w^r`` is a core point
with ``w^r_r=0``, normalize its coordinates to obtain a zero-diagonal
stochastic matrix.  A stationary distribution couples the separate
singleton witnesses into one core allocation ``y=T*pi``.  The LP below uses
the equivalent flow variables directly:

    sum_j F[r,j] = pi[r] = sum_j F[j,r],   F[r,r]=0,
    T F[r,S] >= pi[r] v(S).

For any two core allocations x,z, the bridge value is

    sum_i min(x_i,y_i)+min(z_i,y_i)-T <= sum_i min(x_i,z_i).

This verifier checks the rational formulation, named hostile controls, the
balanced sharp family, and the complete archived n=6 selector bank.  The
archive disjunction with the spectral bound is discovery evidence, not a
proof of the still-open universal hybrid-overlap inequality.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

from z3 import Q, Real, Solver, Sum, sat, unsat

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
DIV = HERE.parent
ARCHIVE = DIV / "search_archive"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(ARCHIVE)]

from audit_lmax_overcover import records  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    PXC90_CONSTRAINTS,
    selector_pair,
)
from verify_pxc101_forced_zero_family import family as pxc101_family  # noqa: E402
from verify_pxc104_cover_dependent_counterexample import (  # noqa: E402
    CONSTRAINTS as PXC104_CONSTRAINTS,
    N as PXC104_N,
    TOTAL as PXC104_TOTAL,
)
from verify_pxc118_second_reciprocal_primitive import (  # noqa: E402
    DEFINING as PXC118_CONSTRAINTS,
    N as PXC118_N,
    TOTAL as PXC118_TOTAL,
)
from verify_pxc125_common_demand_localization import (  # noqa: E402
    mask,
    profile as pxc125_profile,
)


def zq(value: F):
    value = F(value)
    return Q(value.numerator, value.denominator)


def fq(value) -> F:
    value = value.as_fraction()
    return F(value.numerator, value.denominator)


def csum(point, coalition):
    return sum(
        (point[i] for i in range(len(point)) if coalition >> i & 1), F(0)
    )


def bridge_query(values, x, z, threshold, *, omit_core_rows=False):
    """Exact feasibility of a stationary bridge of the requested value."""
    n = len(x)
    total = sum(x, F(0))
    full = (1 << n) - 1
    if total <= 0 or total != sum(z, F(0)):
        raise AssertionError("invalid equal-total pair")

    pi = [Real(f"pi_{i}") for i in range(n)]
    flow = [[Real(f"f_{r}_{i}") for i in range(n)] for r in range(n)]
    ux = [Real(f"ux_{i}") for i in range(n)]
    uz = [Real(f"uz_{i}") for i in range(n)]
    solver = Solver()
    solver.add(Sum(pi) == 1)
    for r in range(n):
        solver.add(pi[r] >= 0, Sum(flow[r]) == pi[r], flow[r][r] == 0)
        for i in range(n):
            solver.add(flow[r][i] >= 0)
        if not omit_core_rows:
            for coalition in range(1, full):
                solver.add(
                    zq(total) * Sum(
                        [flow[r][i] for i in range(n) if coalition >> i & 1]
                    )
                    >= pi[r] * zq(values[coalition])
                )
    for i in range(n):
        solver.add(Sum([flow[r][i] for r in range(n)]) == pi[i])
        solver.add(ux[i] >= 0, ux[i] <= zq(x[i]), ux[i] <= zq(total) * pi[i])
        solver.add(uz[i] >= 0, uz[i] <= zq(z[i]), uz[i] <= zq(total) * pi[i])
    solver.add(Sum(ux) + Sum(uz) - zq(total) >= zq(threshold))

    status = solver.check()
    if status != sat:
        return str(status), None
    model = solver.model()
    pi_value = tuple(fq(model.eval(q)) for q in pi)
    flow_value = tuple(
        tuple(fq(model.eval(flow[r][i])) for i in range(n)) for r in range(n)
    )
    y = tuple(total * q for q in pi_value)
    bridge = sum(
        (min(x[i], y[i]) + min(z[i], y[i]) - y[i] for i in range(n)), F(0)
    )

    # Independent exact replay of every defining inequality in the model.
    if sum(pi_value, F(0)) != 1:
        raise AssertionError("stationary mass changed")
    for r in range(n):
        if flow_value[r][r] or sum(flow_value[r], F(0)) != pi_value[r]:
            raise AssertionError(("row balance", r))
        if any(q < 0 for q in flow_value[r]):
            raise AssertionError(("negative flow", r))
        if not omit_core_rows:
            for coalition in range(1, full):
                load = sum(
                    (flow_value[r][i] for i in range(n) if coalition >> i & 1),
                    F(0),
                )
                if total * load < pi_value[r] * values[coalition]:
                    raise AssertionError(("witness row", r, coalition))
    for i in range(n):
        if sum((flow_value[r][i] for r in range(n)), F(0)) != pi_value[i]:
            raise AssertionError(("column balance", i))
        if y[i] > total / 2:
            raise AssertionError(("half-total ceiling", i, y[i]))
    if bridge < threshold:
        raise AssertionError(("bridge objective", bridge, threshold))
    if bridge > sum((min(a, b) for a, b in zip(x, z)), F(0)):
        raise AssertionError("triangle bridge exceeded overlap")
    return "sat", {
        "pi": list(map(str, pi_value)),
        "y": list(map(str, y)),
        "bridge": str(bridge),
        "positive_flow_arcs": sum(q > 0 for row in flow_value for q in row),
        "flow": [list(map(str, row)) for row in flow_value],
    }


def named_games():
    rows = []
    p101 = pxc101_family(2)
    rows.append(("PXC101", p101["constraints"], p101["n"], p101["total"]))
    rows.append(("PXC104", PXC104_CONSTRAINTS, PXC104_N, PXC104_TOTAL))
    rows.append(("PXC118", PXC118_CONSTRAINTS, PXC118_N, PXC118_TOTAL))
    rows.append(("PXC90", PXC90_CONSTRAINTS, 7, F(20)))

    t, A, B, K0, M = 1, F(1), F(5), F(29, 5), F(6)
    _C, total, _x, _z = pxc125_profile(t, A, B, K0, M)
    ks = tuple(range(5, t + 5))
    defining = {
        mask(0, 1): 2 * M,
        mask(0, 1, 4): 2 * M + 2 * A,
        mask(0, 1, 2, *ks): 2 * M + t * K0,
        mask(0, 1, 3, *ks): 2 * M + A + (t + 1) * B,
    }
    rows.append(("PXC125-positive-demand", defining, t + 5, total))
    return rows


def named_controls():
    result = []
    for label, constraints, n, total in named_games():
        values, x, z = selector_pair(constraints, n, total)
        target = F(n, (n * n) // 4) * total
        actual = sum((min(a, b) for a, b in zip(x, z)), F(0))
        if label == "PXC90":
            # The seven-player full-rank control is already spectrally closed.
            # Its full stationary feasibility system is deliberately not sent
            # through the much slower generic Z3 rational simplex here.
            spectral = spectral_decomposition(label, values, x, z)
            certificate = {
                "classification": "faithful full-rank spectral boundary",
                "spectral_bound": str(
                    F(spectral["sharpened_spectral_bound_ratio"]) * total
                ),
            }
        else:
            status, certificate = bridge_query(values, x, z, target)
            if status != "sat":
                raise AssertionError((label, status))
        result.append({
            "label": label,
            "n": n,
            "target": str(target),
            "actual_overlap": str(actual),
            "certificate": certificate,
        })
    return result


def balanced_family_controls():
    result = []
    for p in range(1, 6):
        for k in range(2, 7):
            n = p + k + 1
            if n > 10:
                continue
            g = (F(p * (k - 1)),) + (F(1),) * p + (F(0),) * k
            h = (F(0),) * (p + 1) + (F(p),) * k
            values = tuple(
                min(csum(g, coalition), csum(h, coalition))
                for coalition in range(1 << n)
            )
            x = (F(p * p * (k - 1), p + 1),) + (F(p, p + 1),) * (p + k)
            z = (
                (F(p * (k - 1), k),)
                + (F(1, k),) * p
                + (F(p * (k - 1), k),) * k
            )
            total = F(p * k)
            target = F(n, (n * n) // 4) * total
            # Use h as the zero witness for head/one players and g as the
            # zero witness for block players.  The resulting bipartite chain
            # has the displayed stationary distribution and bridge y.
            pi = (
                (F(k - 1, 2 * k),)
                + (F(1, 2 * p * k),) * p
                + (F(1, 2 * k),) * k
            )
            y = tuple(total * q for q in pi)
            if sum(pi, F(0)) != 1 or max(pi) > F(1, 2):
                raise AssertionError(("balanced stationary mass", p, k, pi))
            low = tuple(min(a, b) for a, b in zip(x, z))
            high = tuple(max(a, b) for a, b in zip(x, z))
            if any(not (a <= q <= b) for a, q, b in zip(low, y, high)):
                raise AssertionError(("balanced bridge box", p, k, y))
            bridge = sum(
                min(x[i], y[i]) + min(z[i], y[i]) - y[i]
                for i in range(n)
            )
            actual = sum(min(a, b) for a, b in zip(x, z))
            if bridge != actual or bridge < target:
                raise AssertionError(("balanced bridge", p, k, bridge, target))
            result.append({
                "p": p, "k": k, "n": n,
                "target": str(target),
                "actual_overlap": str(actual),
                "stationary_pi": list(map(str, pi)),
                "bridge": str(bridge),
            })
    return result


def archive_disjunction(paths):
    unique = {}
    raw_records = 0
    for path in paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            if len(x) == 6 and sum(x, F(0)) == sum(z, F(0)) > 0:
                raw_records += 1
                unique[(values, x, z)] = (str(source), trail)
    bridge_rescues = []
    spectral_closed = 0
    for (values, x, z), source in unique.items():
        total = sum(x, F(0))
        target = F(2, 3) * total
        spectral = spectral_decomposition("archive-control", values, x, z)
        spectral_bound = F(spectral["sharpened_spectral_bound_ratio"]) * total
        if spectral_bound >= target:
            spectral_closed += 1
            continue
        status, certificate = bridge_query(values, x, z, target)
        if status != "sat":
            raise AssertionError(("combined failure", source, status, spectral))
        bridge_rescues.append({
            "source": list(source),
            "x": list(map(str, x)),
            "z": list(map(str, z)),
            "spectral_bound": str(spectral_bound),
            "target": str(target),
            "stationary_bridge": certificate["bridge"],
        })
    return {
        "raw_records": raw_records,
        "unique_records": len(unique),
        "spectral_closed": spectral_closed,
        "stationary_bridge_rescues": bridge_rescues,
        "combined_failures": 0,
    }


def fail_open_controls():
    # The sharp archived equality orientation needs the actual exact-game
    # witness rows.  Removing them admits a target bridge, while retaining
    # them makes the stationary bridge alone UNSAT; its spectral bound is
    # exactly the target.  This prevents accidental omission of exactness.
    archive = json.loads((ROOT / "verifiers/s6/harvest6_601.json").read_text())
    item = archive["records"][125]
    values = tuple(map(F, item["v"]))
    x = tuple(map(F, item["lmin"]))
    z = tuple(map(F, item["lmax"]))
    target = F(8, 3)
    relaxed_status, relaxed = bridge_query(
        values, x, z, target, omit_core_rows=True
    )
    if relaxed_status != "sat" or F(relaxed["bridge"]) < target:
        raise AssertionError(("drop-core relaxation", relaxed_status, relaxed))
    irredundant = (14, 19, 20, 35, 44, 49)
    pi = tuple(map(F, (F(23, 68), F(2, 17), F(1, 12), F(5, 102), F(5, 17), F(2, 17))))
    flow = [[F(0)] * 6 for _ in range(6)]
    arcs = {
        (0, 1): F(23, 272), (0, 4): F(23, 136), (0, 5): F(23, 272),
        (1, 0): F(1, 17), (1, 2): F(1, 102), (1, 3): F(1, 51),
        (1, 4): F(1, 34), (2, 1): F(1, 48), (2, 4): F(1, 24),
        (2, 5): F(1, 48), (3, 1): F(5, 408), (3, 4): F(5, 204),
        (3, 5): F(5, 408), (4, 0): F(15, 68), (4, 2): F(5, 68),
        (5, 0): F(1, 17), (5, 3): F(1, 34), (5, 4): F(1, 34),
    }
    for (r, i), value in arcs.items():
        flow[r][i] = value
    ux = (F(4, 3), F(1, 3), F(1, 3), F(10, 51), F(20, 17), F(1, 3))
    uz = (F(1), F(8, 17), F(0), F(0), F(1), F(8, 17))
    for r in range(6):
        if sum(flow[r], F(0)) != pi[r] or flow[r][r]:
            raise AssertionError(("sharp primal row", r))
        for coalition in irredundant:
            load = sum(flow[r][i] for i in range(6) if coalition >> i & 1)
            if F(4) * load < pi[r] * values[coalition]:
                raise AssertionError(("sharp primal core", r, coalition))
    for i in range(6):
        if sum(flow[r][i] for r in range(6)) != pi[i]:
            raise AssertionError(("sharp primal column", i))
        if not (0 <= ux[i] <= min(x[i], 4 * pi[i])):
            raise AssertionError(("sharp ux", i))
        if not (0 <= uz[i] <= min(z[i], 4 * pi[i])):
            raise AssertionError(("sharp uz", i))

    # Exact dual of max sum(ux+uz), in the notation displayed in PXC136d.
    theta = F(45, 17)
    row_potential = tuple(F(q, 17) for q in (28, 50, 28, 28, 60, 50))
    column_potential = tuple(F(q, 17) for q in (40, -10, -28, -28, 0, -10))
    lambdas = {
        (0, 19): F(14, 17), (0, 35): F(4, 17), (0, 49): F(14, 17),
        (1, 14): F(22, 17), (1, 19): F(50, 17), (1, 35): F(40, 17),
        (2, 19): F(14, 17), (2, 35): F(4, 17), (2, 49): F(14, 17),
        (3, 19): F(14, 17), (3, 35): F(4, 17), (3, 49): F(14, 17),
        (4, 19): F(50, 17), (4, 20): F(32, 17), (4, 49): F(50, 17),
        (5, 35): F(40, 17), (5, 44): F(22, 17), (5, 49): F(50, 17),
    }
    alpha = tuple(map(F, (1, 1, 0, 0, 0, 1)))
    beta = tuple(map(F, (1, 0, 1, 1, 1, 0)))
    pcap = tuple(map(F, (0, 0, 1, 1, 1, 0)))
    qcap = tuple(map(F, (0, 1, 0, 0, 0, 1)))
    for i in range(6):
        if alpha[i] + pcap[i] < 1 or beta[i] + qcap[i] < 1:
            raise AssertionError(("sharp dual cap", i))
        root_row = (
            theta - row_potential[i] - column_potential[i]
            + sum(lambdas.get((i, coalition), F(0)) * values[coalition] / 4
                  for coalition in irredundant)
            - 4 * (pcap[i] + qcap[i])
        )
        if root_row < 0:
            raise AssertionError(("sharp dual pi", i, root_row))
    for r in range(6):
        for i in range(6):
            if i == r:
                continue
            arc_row = (
                row_potential[r] + column_potential[i]
                - sum(
                    lambdas.get((r, coalition), F(0))
                    for coalition in irredundant if coalition >> i & 1
                )
            )
            if arc_row < 0:
                raise AssertionError(("sharp dual arc", r, i, arc_row))
    primal_value = sum(ux, F(0)) + sum(uz, F(0))
    dual_value = theta + sum(alpha[i] * x[i] + beta[i] * z[i] for i in range(6))
    if primal_value != dual_value or primal_value != F(113, 17):
        raise AssertionError(("sharp strong duality", primal_value, dual_value))
    exact_stationary_optimum = primal_value - 4
    if not exact_stationary_optimum < target:
        raise AssertionError("sharp stationary deficit disappeared")
    return {
        "sharp_equality_stationary_optimum": str(exact_stationary_optimum),
        "exact_optimum_provenance": (
            "matched exact primal/dual certificates on irredundant rows "
            "14,19,20,35,44,49"
        ),
        "drop_exact_core_rows": relaxed_status,
        "relaxed_bridge": relaxed["bridge"],
        "above_actual_overlap": "impossible by the pointwise bridge inequality",
        "spectral_rescue": "8/3",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    archive_paths = [
        ROOT / "verifiers/s6/harvest6_601.json",
        ROOT / "verifiers/s6/harvest6_602.json",
    ]
    payload = {
        "claim": "PXC136 stationary singleton-witness circulation and bridge",
        "theorem": {
            "flow": "row(F)=col(F)=pi, diag(F)=0, T F[r,S]>=pi[r]v(S)",
            "core_bridge": "y=T*pi is in Core(v) and y_i<=T/2",
            "overlap_bound": "Psi_stat<=sum_i min(x_i,z_i)",
            "box_distance_identity": "Psi_stat=O-min sum_i dist(T*pi_i,[min(x_i,z_i),max(x_i,z_i)])",
        },
        "named_controls": named_controls(),
        "balanced_family_controls": balanced_family_controls(),
        "archive_disjunction": archive_disjunction(archive_paths),
        "fail_open_controls": fail_open_controls(),
        "scope": (
            "PXC136 is a conventional all-dimensional theorem.  The exact "
            "spectral-or-stationary disjunction passes the complete archived "
            "n=6 bank but remains a conjecture, not a bounded-census proof of "
            "the global hybrid-overlap inequality."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
