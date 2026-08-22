#!/usr/bin/env python3
"""Complete n=6 both-top incidence classification for PXC108.

There are fifteen nonempty traces on four non-top players and forty-one
positive extreme covers of the full both-top menu.  This driver precomputes,
for each of the eight ordered residual stratum shapes, every cover's staged
failure status and every invariant blocker edge.  It then exhausts all
``2^15-1`` labelled trace menus without repeating LP work.

This is a complete theorem only for the stated incidence universe: every row
contains both top players, Cx contributes no active trace, and no zero-valued
singleton normal is present.  It is a deliberately scoped six-player
classification, not a classification of all exact games.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, deque
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
DIV = HERE.parents[1]
sys.path[:0] = [str(DIV), str(HERE.parent)]

from search_pxc103_incidence_second_mechanism import (  # noqa: E402
    covers_for_menu,
    ordered_compositions,
    z_for_shape,
)
from verify_pxc108_invariant_cover_blocker_circuits import (  # noqa: E402
    all_descent_slots,
    direction,
)


FULL_TRACES = tuple(range(1, 16))


def trace_mask(traces):
    answer = 0
    for trace in traces:
        answer |= 1 << (trace - 1)
    return answer


def shortest_cycle(edges, vertices):
    best = None
    vertices = set(vertices)
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


def precompute(shape, cover_records):
    z = z_for_shape(shape)
    x = tuple([sum(z, F(0)) / 6] * 6)
    base = {"label": str(shape), "x": x, "z": z, "top": (0, 1), "cx": ()}
    failing = []
    negative_traces = []
    for cover in cover_records:
        instance = base | {"covers": (cover,), "menu": cover["rows"]}
        failing.append(bool(list(all_descent_slots(instance, cover["rows"]))))
        negative = set()
        blocks = []
        # Rows containing both tops have masks 3|(trace<<2).
        from audit_sign_coherent_staged_lifts import payoff_blocks
        payoff = payoff_blocks(z, "max")
        for stage in range(1, len(payoff)):
            for designated in payoff[stage]:
                for trace in FULL_TRACES:
                    mask = 3 | (trace << 2)
                    if direction(instance, cover["rows"], designated, stage, mask) is not None:
                        negative.add(trace)
                        blocks.append((stage, designated, trace))
        negative_traces.append(frozenset(negative))
    edges = [set() for _ in cover_records]
    for i, negative in enumerate(negative_traces):
        for j, cover in enumerate(cover_records):
            if i != j and negative.intersection(cover["traces"]):
                edges[i].add(j)
    return base, tuple(failing), tuple(negative_traces), tuple(edges)


def common_direction(base, cover_records, indices):
    union = tuple(sorted({row for i in indices for row in cover_records[i]["rows"]}))
    instance = base | {"covers": tuple(cover_records[i] for i in indices), "menu": union}
    slots = list(all_descent_slots(instance, union))
    return slots[0] if slots else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    raw_covers = covers_for_menu(FULL_TRACES)
    cover_records = []
    for rows, certificate in raw_covers:
        weights, eta, alpha = certificate
        traces = tuple(mask >> 2 for mask in rows)
        cover_records.append({
            "rows": tuple(rows), "traces": traces,
            "trace_mask": trace_mask(traces),
            "weights": tuple(weights), "eta": eta, "alpha": tuple(alpha),
        })
    if len(cover_records) != 41:
        raise AssertionError(("cover count", len(cover_records)))

    totals = Counter()
    shape_results = []
    longer_pure_cycles = []
    for shape in ordered_compositions(4):
        base, failing, negative, edges = precompute(shape, cover_records)
        stats = Counter()
        girths = Counter()
        common_cycle_menus = 0
        for menu_bits in range(1, 1 << 15):
            indices = tuple(
                i for i, cover in enumerate(cover_records)
                if cover["trace_mask"] & ~menu_bits == 0
            )
            if len(indices) < 2 or any(not failing[i] for i in indices):
                continue
            stats["universal_failure_menus"] += 1
            cycle = shortest_cycle(edges, indices)
            if cycle is None:
                # A finite acyclic graph has a sink.  Any descent of that
                # failing cover is nonnegative on the cover union and hence,
                # by the positive identities, is a common direction.
                stats["common_by_sink_menus"] += 1
                continue
            girths[str(len(cycle))] += 1
            if len(cycle) >= 3:
                common = common_direction(base, cover_records, indices)
                if common is not None:
                    common_cycle_menus += 1
                else:
                    longer_pure_cycles.append({
                        "shape": list(shape), "menu_bits": menu_bits,
                        "menu_traces": [i + 1 for i in range(15) if menu_bits >> i & 1],
                        "cover_indices": list(indices), "cycle": cycle,
                    })
            stats["cyclic_menus"] += 1
        totals.update(stats)
        shape_results.append({
            "shape": list(shape), "stats": dict(stats),
            "cycle_girths": dict(girths),
            "cycles_length_at_least_3_with_common_direction": common_cycle_menus,
        })

    payload = {
        "claim": "complete n=6 both-top PXC108 incidence classification",
        "cover_universe": {
            "nonempty_traces": 15, "positive_extreme_covers": 41,
            "support_histogram": dict(Counter(str(len(q["rows"])) for q in cover_records)),
            "covers": [
                {"traces": list(q["traces"]), "weights": list(map(str, q["weights"])),
                 "eta": str(q["eta"]), "alpha": list(map(str, q["alpha"]))}
                for q in cover_records
            ],
        },
        "menus_per_shape": (1 << 15) - 1,
        "ordered_residual_shapes": 8,
        "shape_results": shape_results,
        "aggregate": dict(totals),
        "pure_shortest_cycles_length_at_least_3": longer_pure_cycles,
        "third_branch": (
            "none: cyclic cells have a directed cycle; acyclic universal "
            "cells have a sink whose descent collapses to the common branch"
        ),
        "scope": (
            "all 32767 labelled menus for each of eight outsider stratum "
            "shapes; every row contains both tops and a nonempty outsider "
            "trace, active Cx and zero-coordinate normals omitted"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
