#!/usr/bin/env python3
"""Search for a pure long PXC108 cycle created by active common-Cx traces.

The universe is all positive independent both-top covers on four outsiders
with support at most three (the only ranks that can fail).  Residual payoffs
are strictly ordered.  We exhaust small common-Cx trace families and test the
exact PXC92b incidence LP by floating discovery.  A hit is only an incidence
blueprint until rational replay and exact-game/Cx realization.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


U = 4
TRACES = tuple(range(1, 1 << U))


def vec(mask):
    return [F((mask >> i) & 1) for i in range(U)]


def positive_balance(columns):
    width = len(columns)
    a = [[vec(mask)[i] for mask in columns] + [F(1)] for i in range(U)]
    cursor = 0
    for col in range(width):
        pivot = next((r for r in range(cursor, U) if a[r][col]), None)
        if pivot is None:
            return None
        a[cursor], a[pivot] = a[pivot], a[cursor]
        scale = a[cursor][col]
        a[cursor] = [q / scale for q in a[cursor]]
        for r in range(U):
            if r != cursor and a[r][col]:
                scale = a[r][col]
                a[r] = [q - scale * p for q, p in zip(a[r], a[cursor])]
        cursor += 1
    if any(not any(row[:width]) and row[-1] for row in a):
        return None
    out = tuple(a[r][-1] for r in range(width))
    return out if min(out) > 0 else None


def cuts(source, cx, trace):
    aeq = [[float((mask >> i) & 1) for i in range(U)] for mask in source]
    beq = [0.0] * len(aeq)
    common_aub = [[-float((mask >> i) & 1) for i in range(U)] for mask in cx]
    common_bub = [0.0] * len(cx)
    target = [float((trace >> i) & 1) for i in range(U)]
    for stage in range(U):
        eq = list(aeq)
        rhs = list(beq)
        for i in range(stage):
            row = [0.0] * U
            row[i] = 1.0
            eq.append(row)
            rhs.append(0.0)
        aub = list(common_aub)
        bub = list(common_bub)
        row = [0.0] * U
        row[stage] = 1.0
        aub.append(row)
        bub.append(-1.0)
        aub.append(target)
        bub.append(-1.0)
        answer = linprog(
            np.zeros(U), A_ub=np.asarray(aub), b_ub=np.asarray(bub),
            A_eq=np.asarray(eq), b_eq=np.asarray(rhs),
            bounds=[(None, None)] * U, method="highs",
        )
        if answer.success:
            return True
    return False


def find_cycle(edges):
    color = [0] * len(edges)
    parent = [-1] * len(edges)

    def visit(v):
        color[v] = 1
        for w in edges[v]:
            if color[w] == 0:
                parent[w] = v
                answer = visit(w)
                if answer:
                    return answer
            elif color[w] == 1:
                cycle = [v]
                while cycle[-1] != w:
                    cycle.append(parent[cycle[-1]])
                cycle.reverse()
                return cycle
        color[v] = 2
        return None

    for v in range(len(edges)):
        if not color[v]:
            answer = visit(v)
            if answer:
                return answer
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cx-size-max", type=int, default=3)
    parser.add_argument("--stop-after", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    supports = []
    weights = []
    for size in (2, 3):
        for columns in itertools.combinations(TRACES, size):
            answer = positive_balance(columns)
            if answer is not None:
                supports.append(columns)
                weights.append(answer)

    hits = []
    cells = 0
    for size in range(args.cx_size_max + 1):
        for cx in itertools.combinations(TRACES, size):
            cells += 1
            negative = [
                frozenset(q for q in TRACES if cuts(source, cx, q))
                for source in supports
            ]
            edges = []
            for i, cutset in enumerate(negative):
                targets = {j for j, target in enumerate(supports)
                           if i != j and cutset.intersection(target)}
                edges.append(targets)
            asymmetric = [
                {j for j in targets if i not in edges[j]}
                for i, targets in enumerate(edges)
            ]
            cycle = find_cycle(asymmetric)
            if cycle is None:
                continue
            hits.append({
                "cx_traces": list(cx), "cycle_indices": cycle,
                "cycle_supports": [list(supports[i]) for i in cycle],
                "cycle_weights_for_ambient_one": [
                    list(map(str, weights[i])) for i in cycle
                ],
            })
            if len(hits) >= args.stop_after:
                break
        if len(hits) >= args.stop_after:
            break

    payload = {
        "claim": "active-common-Cx incidence search for pure long PXC108 cycles",
        "parameters": vars(args) | {"output": str(args.output) if args.output else None},
        "positive_balanced_failing_supports": len(supports),
        "cx_cells_checked": cells,
        "pure_asymmetric_cycle_blueprints": hits,
        "scope": (
            "all u=4 both-top supports of size 2/3 and common-Cx trace families "
            "through the stated size; strict residual strata; incidence only"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
