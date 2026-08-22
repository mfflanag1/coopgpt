#!/usr/bin/env python3
"""Mixed-decoration n=6 search for a shortest cover cycle above length two.

Unlike the complete both-top census, this lane admits every proper
nonsingleton coalition row and therefore every top-decoration pattern.  It
uses the complete 766-cover incidence universe, precomputes exact staged
edge data for all potentially failing supports (sizes at most three), and
samples unions of those covers.  Any retained menu is closed under *all*
extreme covers supported by its rows before the universal-failure test.

This remains incidence discovery: comparison with x, exactness, singleton
witnesses, and complete-Cx realizability are not encoded.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
DIV = HERE.parents[1]
sys.path[:0] = [str(DIV), str(HERE.parent)]

from verify_n6_extreme_cover_rank_fidelity import enumerate_covers  # noqa: E402
from verify_pxc108_invariant_cover_blocker_circuits import (  # noqa: E402
    all_descent_slots,
    direction,
)


def shortest_cycle(edges, vertices):
    vertices = set(vertices)
    best = None
    for start in vertices:
        queue = deque([start])
        distance = {start: 0}
        parent = {}
        while queue:
            vertex = queue.popleft()
            if vertex != start and start in edges[vertex]:
                path = [vertex]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                path.reverse()
                if best is None or len(path) < len(best):
                    best = path
                continue
            for nxt in edges[vertex] & vertices:
                if nxt == start or nxt in distance:
                    continue
                if best is not None and distance[vertex] + 2 >= len(best):
                    continue
                distance[nxt] = distance[vertex] + 1
                parent[nxt] = vertex
                queue.append(nxt)
    return best


def asymmetric_dag_order(edges):
    asymmetric = [
        {j for j in targets if i not in edges[j]}
        for i, targets in enumerate(edges)
    ]
    indegree = [0] * len(edges)
    for targets in asymmetric:
        for j in targets:
            indegree[j] += 1
    queue = deque(i for i, value in enumerate(indegree) if value == 0)
    order = []
    while queue:
        i = queue.popleft()
        order.append(i)
        for j in asymmetric[i]:
            indegree[j] -= 1
            if indegree[j] == 0:
                queue.append(j)
    return asymmetric, order


def precompute_cover(payload):
    record, z, x, coalition_rows = payload
    from audit_sign_coherent_staged_lifts import payoff_blocks
    base = {"label": "mixed n6 strict", "x": x, "z": z,
            "top": (0, 1), "cx": (), "covers": (record,),
            "menu": record["rows"]}
    failure = bool(list(all_descent_slots(base, record["rows"])))
    negative = set()
    blocks = payoff_blocks(z, "max")
    for stage in range(1, len(blocks)):
        for designated in blocks[stage]:
            for blocker in coalition_rows:
                if direction(base, record["rows"], designated, stage, blocker) is not None:
                    negative.add(blocker)
    return failure, tuple(sorted(negative))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20260822)
    parser.add_argument("--covers-per-union-min", type=int, default=2)
    parser.add_argument("--covers-per-union-max", type=int, default=5)
    parser.add_argument("--stop-after", type=int, default=5)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    _candidates, all_covers_raw = enumerate_covers()
    # Positive z coordinates exclude outsider singleton rows in this lane.
    all_covers = {
        rows: cert for rows, cert in all_covers_raw.items()
        if all(row.bit_count() >= 2 for row in rows)
    }
    if len(all_covers) != 766:
        raise AssertionError(("nonsingleton cover universe", len(all_covers)))
    low_rows = tuple(rows for rows in all_covers if len(rows) <= 3)
    if len(low_rows) != 98:
        raise AssertionError(("low support universe", len(low_rows)))

    # Strict outsider order exercises every later stage separately.
    z = tuple(map(F, (6, 6, 5, 4, 3, 2)))
    x = tuple([sum(z, F(0)) / 6] * 6)
    base = {"label": "mixed n6 strict", "x": x, "z": z, "top": (0, 1), "cx": ()}
    coalition_rows = tuple(row for row in range(1, 63) if row.bit_count() >= 2)
    records = []
    for rows in low_rows:
        cert = all_covers[rows]
        records.append({
            "rows": tuple(rows), "weights": tuple(cert["weights"]),
            "eta": cert["eta"],
        })
    index = {tuple(record["rows"]): i for i, record in enumerate(records)}

    jobs = [(record, z, x, coalition_rows) for record in records]
    if args.workers == 1:
        profiles = list(map(precompute_cover, jobs))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            profiles = list(pool.map(precompute_cover, jobs))
    failing = [q[0] for q in profiles]
    negative_rows = [frozenset(q[1]) for q in profiles]

    edges = [set() for _ in records]
    for i, negative in enumerate(negative_rows):
        for j, target in enumerate(records):
            if i != j and negative.intersection(target["rows"]):
                edges[i].add(j)
    asymmetric, dag_order = asymmetric_dag_order(edges)
    if len(dag_order) != len(records):
        raise AssertionError(
            "a directed cycle without a reciprocal edge exists in the complete cover graph"
        )

    rng = random.Random(args.seed)
    stats = Counter()
    seen_menus = set()
    longer = []
    two_cycle_controls = []
    for _round in range(args.rounds):
        count = rng.randint(args.covers_per_union_min, args.covers_per_union_max)
        chosen = rng.sample(range(len(records)), count)
        menu = tuple(sorted({row for i in chosen for row in records[i]["rows"]}))
        if menu in seen_menus:
            stats["duplicate_menus"] += 1
            continue
        seen_menus.add(menu)
        stats["menus"] += 1
        menu_set = set(menu)
        induced_all = tuple(
            rows for rows in all_covers if set(rows).issubset(menu_set)
        )
        if any(len(rows) == 4 for rows in induced_all):
            stats["full_rank_cover"] += 1
            continue
        induced = tuple(index[rows] for rows in induced_all)
        if len(induced) < 2 or any(not failing[i] for i in induced):
            stats["not_universal_failure"] += 1
            continue
        stats["universal_failure"] += 1
        cycle = shortest_cycle(edges, induced)
        if cycle is None:
            stats["common_by_sink"] += 1
            continue
        if len(cycle) == 2:
            stats["two_cycle"] += 1
            if len(two_cycle_controls) < 5:
                two_cycle_controls.append({
                    "menu": list(menu),
                    "covers": [list(records[i]["rows"]) for i in induced],
                    "cycle": cycle,
                })
            continue
        union = tuple(sorted({row for i in induced for row in records[i]["rows"]}))
        instance = base | {"covers": tuple(records[i] for i in induced), "menu": union}
        common = list(all_descent_slots(instance, union))
        if common:
            stats["long_cycle_but_common"] += 1
            continue
        stats["pure_long_cycle"] += 1
        longer.append({
            "menu": list(menu),
            "covers": [list(records[i]["rows"]) for i in induced],
            "cycle": cycle,
            "promotion_status": "mixed-decoration incidence blueprint; exactification required",
        })
        if len(longer) >= args.stop_after:
            break

    payload = {
        "claim": "mixed-decoration n=6 search for PXC108 cycles of girth at least three",
        "parameters": vars(args) | {"output": str(args.output) if args.output else None},
        "cover_universe": {
            "all_nonsingleton_extreme_covers": len(all_covers),
            "potentially_failing_support_at_most_3": len(records),
            "strict_positive_outsider_strata": list(map(str, z[2:])),
            "invariant_edges": sum(len(q) for q in edges),
            "reciprocal_edge_pairs": sum(
                1 for i in range(len(edges)) for j in edges[i] if i < j and i in edges[j]
            ),
            "asymmetric_edges": sum(len(q) for q in asymmetric),
            "asymmetric_edge_graph_is_DAG": True,
            "asymmetric_topological_order": dag_order,
        },
        "stats": dict(stats),
        "two_cycle_controls": two_cycle_controls,
        "pure_long_cycle_blueprints": longer,
        "scope": (
            "seeded menu-union search after exact complete cover closure; "
            "mixed top decorations included, but no exact-game/Cx realization"
        ),
        "finite_incidence_consequence": (
            "for the stated strict-stratum/no-active-Cx universe, every cyclic "
            "induced cover graph contains a reciprocal edge and hence a two-cycle; "
            "this follows from the exact DAG audit of all asymmetric edges and "
            "does not depend on the seeded menu sample"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
