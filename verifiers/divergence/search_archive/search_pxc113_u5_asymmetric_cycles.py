#!/usr/bin/env python3
"""Incidence search for a genuine asymmetric cover cycle on five outsiders.

Rows contain both top players, so only their nonempty outsider traces matter.
Every support through size four is enumerated whose independent 0/1 columns
positively span the all-ones vector.  For strict residual payoff order, the
exact edge test is whether a source-kernel direction can have its first
nonzero coordinate negative while cutting a target trace.

This is an incidence falsifier/search, not an exact-game realization.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


U = 5
TRACES = tuple(range(1, 1 << U))


def vector(mask):
    return [F((mask >> i) & 1) for i in range(U)]


def solve_unique(columns):
    """Return positive lambda with A lambda=1, or None."""
    width = len(columns)
    a = [[vector(mask)[i] for mask in columns] + [F(1)] for i in range(U)]
    cursor = 0
    pivots = []
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
        pivots.append(col)
        cursor += 1
    if any(not any(row[:width]) and row[-1] for row in a):
        return None
    answer = [F(0)] * width
    for r, col in enumerate(pivots):
        answer[col] = a[r][-1]
    if min(answer) <= 0:
        return None
    if any(sum(vector(mask)[i] * w for mask, w in zip(columns, answer)) != 1
           for i in range(U)):
        raise AssertionError((columns, answer))
    return tuple(answer)


def cuttable(source, trace):
    """Floating discovery test; candidates are exactly replayable rationally."""
    aeq = []
    beq = []
    for mask in source:
        aeq.append([float((mask >> i) & 1) for i in range(U)])
        beq.append(0.0)
    qrow = [float((trace >> i) & 1) for i in range(U)]
    for stage in range(U):
        eq = list(aeq)
        rhs = list(beq)
        for i in range(stage):
            row = [0.0] * U
            row[i] = 1.0
            eq.append(row)
            rhs.append(0.0)
        aub = []
        bub = []
        row = [0.0] * U
        row[stage] = 1.0
        aub.append(row)
        bub.append(-1.0)
        aub.append(qrow)
        bub.append(-1.0)
        answer = linprog(
            np.zeros(U), A_ub=np.asarray(aub), b_ub=np.asarray(bub),
            A_eq=np.asarray(eq), b_eq=np.asarray(rhs),
            bounds=[(None, None)] * U, method="highs",
        )
        if answer.success:
            return True
    return False


def directed_cycle(edges):
    color = [0] * len(edges)
    parent = [-1] * len(edges)

    def visit(v):
        color[v] = 1
        for w in edges[v]:
            if color[w] == 0:
                parent[w] = v
                out = visit(w)
                if out:
                    return out
            elif color[w] == 1:
                cycle = [v]
                while cycle[-1] != w:
                    cycle.append(parent[cycle[-1]])
                cycle.reverse()
                return cycle
        color[v] = 2
        return None

    for v in range(len(edges)):
        if color[v] == 0:
            answer = visit(v)
            if answer:
                return answer
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--support-max", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    supports = []
    weights = []
    for size in range(2, args.support_max + 1):
        for columns in itertools.combinations(TRACES, size):
            answer = solve_unique(columns)
            if answer is not None:
                supports.append(columns)
                weights.append(answer)

    negative = []
    for source in supports:
        negative.append(frozenset(trace for trace in TRACES if cuttable(source, trace)))
    edges = []
    asymmetric = []
    for i, cuts in enumerate(negative):
        targets = {j for j, target in enumerate(supports)
                   if i != j and cuts.intersection(target)}
        edges.append(targets)
    for i, targets in enumerate(edges):
        asymmetric.append({j for j in targets if i not in edges[j]})
    cycle = directed_cycle(asymmetric)
    asymmetric_size_transitions = Counter(
        (len(supports[i]), len(supports[j]))
        for i, targets in enumerate(asymmetric) for j in targets
    )

    payload = {
        "claim": "complete u=5 both-top low-support incidence search for asymmetric cover cycles",
        "parameters": vars(args) | {"output": str(args.output) if args.output else None},
        "positive_balanced_supports": len(supports),
        "support_size_counts": {
            str(k): sum(len(q) == k for q in supports)
            for k in range(2, args.support_max + 1)
        },
        "directed_edges": sum(map(len, edges)),
        "asymmetric_edges": sum(map(len, asymmetric)),
        "asymmetric_support_size_transitions": {
            f"{a}->{b}": count
            for (a, b), count in sorted(asymmetric_size_transitions.items())
        },
        "asymmetric_cycle": None if cycle is None else {
            "indices": cycle,
            "supports": [list(supports[i]) for i in cycle],
            "weights_for_ambient_one": [list(map(str, weights[i])) for i in cycle],
        },
        "asymmetric_graph_acyclic": cycle is None,
        "scope": (
            "all independent positive 0/1 outsider supports through the stated size; "
            "both-top decoration and strict singleton residual strata; incidence only"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
