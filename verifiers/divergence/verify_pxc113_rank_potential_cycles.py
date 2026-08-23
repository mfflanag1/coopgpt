#!/usr/bin/env python3
"""Exact incidence audit of the PXC113 rank-potential theorem.

For strictly ordered residual players and no active common-Cx normals, a
positive balanced cover R has equality kernel K_R.  The polar of the
lex-negative half of K_R is

    col(A_R) + R_{<=0} e_p,

where p is the first coordinate not fixed by col(A_R).  Positivity of the
two balanced representations then shows that a one-way cover edge strictly
increases outsider rank.  Directed cycles therefore contain a reciprocal
edge, so every primitive cyclic obstruction has length two.

All arithmetic below is exact Fraction linear algebra.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


def vector(mask, u):
    return tuple(F((mask >> i) & 1) for i in range(u))


def coordinates(columns, target):
    """Coordinates in independent columns, or None if target is outside."""
    if not columns:
        return () if not any(target) else None
    u = len(target)
    width = len(columns)
    a = [[F(columns[j][i]) for j in range(width)] + [F(target[i])]
         for i in range(u)]
    cursor = 0
    pivots = []
    for col in range(width):
        pivot = next((r for r in range(cursor, u) if a[r][col]), None)
        if pivot is None:
            return None
        a[cursor], a[pivot] = a[pivot], a[cursor]
        scale = a[cursor][col]
        a[cursor] = [q / scale for q in a[cursor]]
        for r in range(u):
            if r != cursor and a[r][col]:
                scale = a[r][col]
                a[r] = [q - scale * p for q, p in zip(a[r], a[cursor])]
        pivots.append(col)
        cursor += 1
    if any(not any(row[:width]) and row[-1] for row in a):
        return None
    out = [F(0)] * width
    for r, col in enumerate(pivots):
        out[col] = a[r][-1]
    return tuple(out)


def positive_balance(support, u):
    columns = [vector(mask, u) for mask in support]
    answer = coordinates(columns, (F(1),) * u)
    return answer if answer is not None and min(answer) > 0 else None


def first_free_coordinate(columns, u):
    for p in range(u):
        e = tuple(F(i == p) for i in range(u))
        if coordinates(columns, e) is None:
            return p
    raise AssertionError("full row space has no later-stage kernel")


def cuttable(source, trace, u):
    columns = [vector(mask, u) for mask in source]
    p = first_free_coordinate(columns, u)
    e = tuple(F(i == p) for i in range(u))
    answer = coordinates(columns + [e], vector(trace, u))
    # q is in the lex polar iff q=A beta+c e_p with c<=0.
    return answer is None or answer[-1] > 0


def partitions(items):
    items = tuple(items)
    if not items:
        yield ()
        return
    first = items[0]
    for rest in partitions(items[1:]):
        yield (frozenset((first,)),) + rest
        for i in range(len(rest)):
            yield rest[:i] + (rest[i] | {first},) + rest[i + 1:]


def canonical_partition(blocks):
    return tuple(sorted((tuple(sorted(q)) for q in blocks), key=lambda q: q[0]))


def refines(left, right):
    """Every left block is contained in one right block."""
    return all(any(set(block) <= set(target) for target in right) for block in left)


def partition_support(partition):
    return tuple(sum(1 << i for i in block) for block in partition)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--u-max", type=int, default=5)
    parser.add_argument("--partition-u-max", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    support_audits = {}
    total_asymmetric = 0
    rank_controls = []
    for u in range(2, args.u_max + 1):
        traces = tuple(range(1, 1 << u))
        supports = []
        weights = []
        for size in range(2, u):
            for support in itertools.combinations(traces, size):
                answer = positive_balance(support, u)
                if answer is not None:
                    supports.append(support)
                    weights.append(answer)
        edges = []
        for source in supports:
            negative = {q for q in traces if cuttable(source, q, u)}
            edges.append({j for j, target in enumerate(supports)
                          if negative.intersection(target)})
        asymmetric = [
            {j for j in targets if i not in edges[j]}
            for i, targets in enumerate(edges)
        ]
        transitions = Counter()
        for i, targets in enumerate(asymmetric):
            for j in targets:
                transitions[(len(supports[i]), len(supports[j]))] += 1
                if len(supports[i]) >= len(supports[j]):
                    raise AssertionError((u, supports[i], supports[j]))
        total_asymmetric += sum(map(len, asymmetric))
        support_audits[str(u)] = {
            "positive_balanced_failing_supports": len(supports),
            "support_size_counts": {
                str(k): sum(len(q) == k for q in supports) for k in range(2, u)
            },
            "directed_edges": sum(map(len, edges)),
            "asymmetric_edges": sum(map(len, asymmetric)),
            "asymmetric_rank_transitions": {
                f"{a}->{b}": count for (a, b), count in sorted(transitions.items())
            },
            "asymmetric_rank_strictly_increases": True,
        }
        if supports:
            rank_controls.append({
                "u": u, "support": list(supports[0]),
                "weights_for_ambient_one": list(map(str, weights[0])),
                "first_free_coordinate": first_free_coordinate(
                    [vector(q, u) for q in supports[0]], u
                ),
            })

    partition_audits = {}
    for u in range(2, args.partition_u_max + 1):
        plist = sorted({canonical_partition(q) for q in partitions(range(u))})
        checked = 0
        reciprocal = 0
        asymmetric = 0
        for left in plist:
            if len(left) == 1 or len(left) == u:
                continue
            source = partition_support(left)
            for right in plist:
                if left == right or len(right) == 1:
                    continue
                target = partition_support(right)
                edge = any(cuttable(source, trace, u) for trace in target)
                expected = not refines(left, right)
                if edge != expected:
                    raise AssertionError((u, left, right, edge, expected))
                reverse = not refines(right, left)
                checked += 1
                reciprocal += int(edge and reverse)
                asymmetric += int(edge and not reverse)
        partition_audits[str(u)] = {
            "partitions": len(plist), "ordered_pairs_checked": checked,
            "reciprocal_edges": reciprocal, "asymmetric_edges": asymmetric,
            "edge_iff_target_splits_source": True,
            "asymmetric_edge_iff_strict_refinement": True,
        }

    payload = {
        "claim": "dimension-free strict-stratum rank potential and partition forbidden-two-cycle theorem",
        "theorem": {
            "lex_polar": "D(K)^* = K^perp + R_{<=0} e_p",
            "one_way_edge": "R->R' and not R'->R implies col(A_R) proper-subset col(A_R')",
            "rank_potential": "every asymmetric edge strictly increases outsider incidence rank",
            "cycle_consequence": "every directed cycle contains a reciprocal pair; every shortest cycle has length two",
            "partition_specialization": "P->Q iff Q splits a P-block; one-way edges are strict refinements and primitive cycles are incomparable partition pairs",
        },
        "complete_low_support_audits": support_audits,
        "partition_lattice_audits": partition_audits,
        "rank_controls": rank_controls,
        "fail_open_controls": {
            "asymmetric_edges_exist": total_asymmetric > 0,
            "reciprocal_partition_edges_exist": any(
                q["reciprocal_edges"] > 0 for q in partition_audits.values()
            ),
            "strict_refinement_edges_exist": any(
                q["asymmetric_edges"] > 0 for q in partition_audits.values()
            ),
        },
        "scope": (
            "human theorem for arbitrary real positive balanced cover columns, strict singleton "
            "residual strata, and no active common-Cx normals; exact exhaustive 0/1 audits "
            "through the stated outsider dimensions"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
