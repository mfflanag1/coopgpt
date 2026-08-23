#!/usr/bin/env python3
"""Independent exact SMT replay of the PXC113 rank potential at u=4.

This file imports no PXC112/PXC113 implementation and does not use the
project LP.  Z3 checks every strict-stage source-support/target-trace edge in
the complete four-outsider positive-balanced support universe.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

import z3


U = 4
TRACES = tuple(range(1, 1 << U))


def incidence(mask):
    return tuple(F((mask >> i) & 1) for i in range(U))


def solve_balance(support):
    lambdas = [z3.Real(f"l_{i}") for i in range(len(support))]
    solver = z3.Solver()
    for i in range(U):
        solver.add(sum(lambdas[j] * int(bool(mask >> i & 1))
                       for j, mask in enumerate(support)) == 1)
    solver.add(*[q > 0 for q in lambdas])
    if solver.check() != z3.sat:
        return None
    model = solver.model()
    out = []
    for q in lambdas:
        value = model.eval(q)
        out.append(F(value.numerator_as_long(), value.denominator_as_long()))
    # Independence is checked over Q by rank.
    if rank([incidence(q) for q in support]) != len(support):
        return None
    return tuple(out)


def rank(columns):
    if not columns:
        return 0
    a = [list(q) for q in zip(*columns)]
    cursor = 0
    for col in range(len(a[0])):
        pivot = next((r for r in range(cursor, len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        a[cursor], a[pivot] = a[pivot], a[cursor]
        scale = a[cursor][col]
        a[cursor] = [q / scale for q in a[cursor]]
        for r in range(len(a)):
            if r != cursor and a[r][col]:
                scale = a[r][col]
                a[r] = [q - scale * p for q, p in zip(a[r], a[cursor])]
        cursor += 1
    return cursor


def edge_to_trace(source, trace):
    d = [z3.Real(f"d_{i}") for i in range(U)]
    for stage in range(U):
        solver = z3.Solver()
        for mask in source:
            solver.add(sum(d[i] for i in range(U) if mask >> i & 1) == 0)
        for i in range(stage):
            solver.add(d[i] == 0)
        solver.add(d[stage] <= -1)
        solver.add(sum(d[i] for i in range(U) if trace >> i & 1) <= -1)
        if solver.check() == z3.sat:
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    supports = []
    weights = []
    for size in (2, 3):
        for support in itertools.combinations(TRACES, size):
            answer = solve_balance(support)
            if answer is not None:
                supports.append(support)
                weights.append(answer)
    if len(supports) != 19:
        raise AssertionError(len(supports))

    negative = [
        frozenset(trace for trace in TRACES if edge_to_trace(source, trace))
        for source in supports
    ]
    edges = [
        {j for j, target in enumerate(supports)
         if i != j and negative[i].intersection(target)}
        for i in range(len(supports))
    ]
    asymmetric = [
        {j for j in targets if i not in edges[j]}
        for i, targets in enumerate(edges)
    ]
    if sum(map(len, edges)) != 294 or sum(map(len, asymmetric)) != 36:
        raise AssertionError((sum(map(len, edges)), sum(map(len, asymmetric))))
    transitions = []
    for i, targets in enumerate(asymmetric):
        for j in targets:
            transitions.append((len(supports[i]), len(supports[j])))
    if set(transitions) != {(2, 3)}:
        raise AssertionError(set(transitions))

    # An asymmetric-only directed cycle is impossible because support size
    # strictly increases on all 36 such edges.  Reciprocal controls exist.
    reciprocal_pairs = [
        (i, j) for i in range(len(supports)) for j in edges[i]
        if i < j and i in edges[j]
    ]
    if not reciprocal_pairs:
        raise AssertionError("no reciprocal control")
    first_source = next(i for i, targets in enumerate(asymmetric) if targets)
    first_target = next(iter(asymmetric[first_source]))

    payload = {
        "claim": "independent exact SMT replay of the four-outsider PXC113 rank potential",
        "positive_balanced_supports": len(supports),
        "support_size_counts": {
            "2": sum(len(q) == 2 for q in supports),
            "3": sum(len(q) == 3 for q in supports),
        },
        "directed_edges": sum(map(len, edges)),
        "asymmetric_edges": sum(map(len, asymmetric)),
        "asymmetric_size_transitions": {"2->3": len(transitions)},
        "reciprocal_edge_pairs": len(reciprocal_pairs),
        "representative_asymmetric_edge": {
            "source": list(supports[first_source]),
            "target": list(supports[first_target]),
        },
        "fail_open_controls": {
            "asymmetric_edges_nonempty": bool(transitions),
            "reciprocal_pairs_nonempty": bool(reciprocal_pairs),
        },
        "z3_version": z3.get_version_string(),
        "independence": (
            "standalone Z3 QF_LRA edge feasibility and separate Fraction rank; "
            "no project LP or PXC112/PXC113 code"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
