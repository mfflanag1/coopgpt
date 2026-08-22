#!/usr/bin/env python3
"""Exact recognition calibrations for the invariant cover--blocker theorem.

This verifier deliberately checks a different object from PXC107's graph of
chosen witnesses.  For fixed ``(x,z,Cx)`` and every qualifying extreme cover
R it constructs all *invariant* edges

    R -> R'  iff some staged descent tangent to R cuts a row of R'.

It also tests for a common staged descent tangent to the union of all cover
supports, finds a shortest directed cycle, checks that shortest cycle is
induced, and verifies the augmented-matrix circuit carried by every cover.
PXC98, PXC104, and PXC90 are the negative/common, cyclic, and faithful
calibrations respectively.

The LP layer is exact rational arithmetic.  No floating-point feasibility
decision is used.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(HERE.parent)]

from exactlp import exact_linprog  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402


def row(mask: int, n: int) -> list[F]:
    return [F((mask >> i) & 1) for i in range(n)]


def csum(direction, mask: int) -> F:
    return sum((direction[i] for i in range(len(direction)) if mask >> i & 1), F(0))


def rank(matrix) -> int:
    a = [list(map(F, r)) for r in matrix]
    if not a:
        return 0
    answer = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(answer, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[answer], a[pivot] = a[pivot], a[answer]
        scale = a[answer][col]
        a[answer] = [q / scale for q in a[answer]]
        for i in range(len(a)):
            if i != answer and a[i][col]:
                scale = a[i][col]
                a[i] = [q - scale * p for q, p in zip(a[i], a[answer])]
        answer += 1
    return answer


def transpose(columns):
    return [list(q) for q in zip(*columns)] if columns else []


def cover_circuit(instance, cover):
    """Check the augmented circuit [cover variables | -target].

    After eliminating the two top coefficients, a normalized cover satisfies
    A lambda - eta 1 = 0 on the non-top coordinates and
    sum_S |S cap Top| lambda_S - 2 eta = 1.  A zero ambient variable is
    omitted from the active support.  At a nondegenerate extreme cover the
    active columns are independent and adjoining the negative target column
    produces a minimally dependent set--a represented oriented-matroid
    circuit containing the distinguished normalization target.
    """
    n = len(instance["z"])
    top = instance["top"]
    outsiders = tuple(i for i in range(n) if i not in top)
    columns = []
    for mask in cover["rows"]:
        columns.append(
            [F((mask >> i) & 1) for i in outsiders]
            + [F(sum((mask >> i) & 1 for i in top))]
        )
    if cover["eta"] > 0:
        columns.append([F(-1)] * len(outsiders) + [F(-2)])
    target = [F(0)] * len(outsiders) + [F(1)]
    active_rank = rank(transpose(columns))
    augmented = columns + [[-q for q in target]]
    augmented_rank = rank(transpose(augmented))
    if active_rank != len(columns) or augmented_rank != len(columns):
        raise AssertionError((instance["label"], "not a circuit", cover))
    for omitted in range(len(augmented)):
        subset = augmented[:omitted] + augmented[omitted + 1 :]
        if rank(transpose(subset)) != len(subset):
            raise AssertionError((instance["label"], "circuit not minimal", omitted))

    outsider_matrix = [
        [F((mask >> i) & 1) for mask in cover["rows"]] for i in outsiders
    ]
    outsider_rank = rank(outsider_matrix)
    if cover["eta"] > 0 and outsider_rank != len(cover["rows"]):
        raise AssertionError((instance["label"], "positive cover rank", cover))
    return {
        "active_columns": len(columns),
        "active_rank": active_rank,
        "augmented_rank": augmented_rank,
        "circuit_size": len(augmented),
        "outsider_incidence_rank": outsider_rank,
        "outsider_dimension": len(outsiders),
    }


def direction(instance, support_rows, designated, stage, cut_row=None):
    """Return one normalized exact staged direction, if it exists."""
    x, z = instance["x"], instance["z"]
    n = len(z)
    blocks = payoff_blocks(z, "max")
    earlier = tuple(i for block in blocks[:stage] for i in block)
    block = tuple(blocks[stage])
    common_cx = tuple(mask for mask in instance["cx"] if csum(x, mask) == csum(z, mask))
    aub, bub = [], []
    for mask in common_cx:
        aub.append([-q for q in row(mask, n)])
        bub.append(F(0))
    for i, value in enumerate(z):
        if value == 0:
            coeff = [F(0)] * n
            coeff[i] = F(-1)
            aub.append(coeff)
            bub.append(F(0))
    for i in block:
        coeff = [F(0)] * n
        coeff[i] = F(1)
        aub.append(coeff)
        bub.append(F(-1) if i == designated else F(0))
    if cut_row is not None:
        aub.append(row(cut_row, n))
        bub.append(F(-1))
    aeq = [[F(1)] * n]
    beq = [F(0)]
    for i in earlier:
        coeff = [F(0)] * n
        coeff[i] = F(1)
        aeq.append(coeff)
        beq.append(F(0))
    for mask in support_rows:
        aeq.append(row(mask, n))
        beq.append(F(0))
    status, _optimum, point = exact_linprog(
        [F(0)] * n, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq
    )
    if status != "optimal":
        return None
    if point[designated] > -1:
        raise AssertionError("descent normalization lost")
    if cut_row is not None and csum(point, cut_row) > -1:
        raise AssertionError("blocker normalization lost")
    return tuple(point)


def all_descent_slots(instance, support_rows):
    blocks = payoff_blocks(instance["z"], "max")
    for stage in range(1, len(blocks)):
        for designated in blocks[stage]:
            witness = direction(instance, support_rows, designated, stage)
            if witness is not None:
                yield stage, designated, witness


def shortest_cycle(edges, count):
    best = None
    for start in range(count):
        queue = deque([start])
        distance = {start: 0}
        parent = {}
        while queue:
            vertex = queue.popleft()
            if vertex != start and start in edges.get(vertex, ()):
                path = [vertex]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                path.reverse()
                if best is None or len(path) < len(best):
                    best = path
                continue
            for nxt in sorted(edges.get(vertex, ())):
                if nxt == start or nxt in distance:
                    continue
                if best is not None and distance[vertex] + 2 >= len(best):
                    continue
                distance[nxt] = distance[vertex] + 1
                parent[nxt] = vertex
                queue.append(nxt)
    return best


def induced_directed_cycle(cycle, edges):
    size = len(cycle)
    allowed = {(cycle[i], cycle[(i + 1) % size]) for i in range(size)}
    return all(
        (u, v) in allowed
        for u in cycle for v in cycle
        if u != v and v in edges.get(u, ())
    )


def recognize(instance):
    covers = instance["covers"]
    union = tuple(sorted({mask for cover in covers for mask in cover["rows"]}))
    circuit_data = [cover_circuit(instance, cover) for cover in covers]
    descents = []
    faithful = []
    for index, cover in enumerate(covers):
        slots = list(all_descent_slots(instance, cover["rows"]))
        descents.append(slots)
        if not slots:
            faithful.append(index)

    common = list(all_descent_slots(instance, union))
    edges = {i: set() for i in range(len(covers))}
    edge_witnesses = []
    for i, cover in enumerate(covers):
        blocks = payoff_blocks(instance["z"], "max")
        for stage in range(1, len(blocks)):
            for designated in blocks[stage]:
                for j, target in enumerate(covers):
                    if i == j:
                        continue
                    for blocker in target["rows"]:
                        witness = direction(
                            instance, cover["rows"], designated, stage, blocker
                        )
                        if witness is not None:
                            edges[i].add(j)
                            edge_witnesses.append({
                                "source": i, "target": j, "stage": stage,
                                "designated": designated, "blocker": blocker,
                                "direction": list(map(str, witness)),
                            })
                            break
                    if j in edges[i]:
                        continue

    # Current-cover rows are equalities, so the invariant graph has no loops.
    if any(i in targets for i, targets in edges.items()):
        raise AssertionError((instance["label"], "self loop"))
    cycle = shortest_cycle(edges, len(covers))
    if cycle is not None and not induced_directed_cycle(cycle, edges):
        raise AssertionError((instance["label"], "shortest cycle has chord", cycle))

    if not faithful and not common and any(not edges[i] for i in range(len(covers))):
        raise AssertionError((instance["label"], "collapse lemma failed", edges))

    if faithful:
        classification = "faithful"
    elif common:
        classification = "common-direction forced-zero"
    else:
        if cycle is None:
            raise AssertionError((instance["label"], "universal failure without cycle"))
        classification = "invariant chordless cover cycle"

    support_bound = len(instance["z"]) - 2
    for index, cover in enumerate(covers):
        if len(cover["rows"]) > support_bound:
            raise AssertionError((instance["label"], "support bound", index))
        if descents[index] and cover["eta"] > 0 and len(cover["rows"]) == support_bound:
            raise AssertionError((instance["label"], "full rank cover failed", index))

    return {
        "classification": classification,
        "cover_union": list(union),
        "faithful_covers": faithful,
        "descent_slots": [
            [{"stage": s, "designated": i, "direction": list(map(str, d))}
             for s, i, d in slots]
            for slots in descents
        ],
        "common_descent_slots": [
            {"stage": s, "designated": i, "direction": list(map(str, d))}
            for s, i, d in common
        ],
        "invariant_edges": {str(i): sorted(v) for i, v in edges.items()},
        "edge_witnesses": edge_witnesses,
        "shortest_induced_cycle": cycle,
        "cover_circuits": circuit_data,
        "bounds": {
            "extreme_cover_support_at_most": support_bound,
            "failing_positive_ambient_support_at_most": support_bound - 1,
            "cycle_length_lower": 2,
            "cycle_length_upper": len(covers),
        },
    }


def instances():
    pxc98 = {
        "label": "PXC101/PXC98 common blocker",
        "x": tuple(map(F, (F(9, 2), F(9, 2), 2, 2, 2, 2))),
        "z": tuple(map(F, (4, 4, 3, 3, 2, 1))),
        "top": (0, 1), "cx": (7, 11), "menu": (3, 7, 11, 17, 51),
        "covers": (
            {"rows": (3,), "weights": (F(1, 2),), "eta": F(0)},
            {"rows": (7, 11, 51), "weights": (F(1, 4),) * 3, "eta": F(1, 4)},
        ),
    }
    pxc104 = {
        "label": "PXC104 cross-cover cycle",
        "x": (F(41, 6), F(41, 6)) + (F(7, 3),) * 4,
        "z": tuple(map(F, (6, 6, 5, 4, 1, 1))),
        "top": (0, 1), "cx": (7, 11), "menu": (3, 11, 19, 23, 35, 39),
        "covers": (
            {"rows": (3,), "weights": (F(1, 2),), "eta": F(0)},
            {"rows": (11, 19, 39), "weights": (F(1, 4),) * 3, "eta": F(1, 4)},
            {"rows": (11, 23, 35), "weights": (F(1, 4),) * 3, "eta": F(1, 4)},
        ),
    }
    pxc90 = {
        "label": "PXC90 full-rank faithful control",
        "x": tuple(map(F, (6, 4, 2, 2, 2, 2, 2))),
        "z": tuple(F(q, 7) for q in (29, 29, 28, 28, 8, 9, 9)),
        "top": (0, 1), "cx": (7, 11, 13), "menu": (23, 27, 39, 75, 114),
        "covers": ({
            "rows": (23, 27, 39, 75, 114),
            "weights": tuple(F(q, 7) for q in (1, 1, 2, 2, 1)),
            "eta": F(3, 7),
        },),
    }
    return pxc98, pxc104, pxc90


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = {instance["label"]: recognize(instance) for instance in instances()}
    if results["PXC101/PXC98 common blocker"]["classification"] != "common-direction forced-zero":
        raise AssertionError("PXC101 calibration changed")
    if results["PXC104 cross-cover cycle"]["shortest_induced_cycle"] is None:
        raise AssertionError("PXC104 cycle calibration changed")
    if len(results["PXC104 cross-cover cycle"]["shortest_induced_cycle"]) != 2:
        raise AssertionError("PXC104 is no longer the minimal two-cycle")
    if results["PXC90 full-rank faithful control"]["classification"] != "faithful":
        raise AssertionError("PXC90 calibration changed")

    payload = {
        "claim": "invariant cover--blocker graph and augmented-circuit recognition",
        "theorem_interfaces": {
            "invariant_edge": "R->R' iff an exact staged R-descent cuts a row used by R'",
            "common_branch": "a staged descent tangent to the union of all cover supports",
            "cycle_branch": "universal failure plus no common descent forces positive outdegree; a shortest directed cycle is induced",
            "cover_circuit": "active normalized-cover columns plus the negative normalization target form a represented circuit",
            "support_rank": "positive-ambient extreme support has independent outsider columns; full outsider rank implies fidelity",
        },
        "recognition_complexity": (
            "finite exact cover enumeration followed by rational staged LPs for "
            "cover failure, union-common descent, and ordered cover-row edge tests"
        ),
        "calibrations": results,
        "scope": (
            "exact recognition on the three required calibrations; the general "
            "theorem is the accompanying symbolic finite-graph/rank argument"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
