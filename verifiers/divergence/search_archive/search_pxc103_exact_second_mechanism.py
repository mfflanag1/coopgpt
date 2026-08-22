#!/usr/bin/env python3
"""Exactify a cover-dependent PXC103 incidence blueprint at n=6.

The Lmin certificate consists of two rooted three-player rows ``rh+s`` and
``rh+t`` with a common bound L.  Its two-row polytope has the closed-form
leximin

    u=(T-L)/3 on all four outsiders,
    p=(4L-T)/6 on r,h.

The search allows comparison equalities but explicitly rechecks the staged
descent cone after the chosen Cx rows are retained.  Every retained candidate
is then reconstructed as an exact lower-envelope game and exhausts all
complete Cx subsets and all qualifying extreme covers.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DIV = ROOT / "verifiers" / "divergence"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(HERE.parent)]

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    csum,
    selector_pair,
)
from search_pxc103_cover_dependent_failure import (  # noqa: E402
    common_staged_direction_xz,
)
from search_pxc103_incidence_second_mechanism import (  # noqa: E402
    audit_menu,
    coalition,
    covers_for_menu,
    ordered_compositions,
)


def z_profiles(max_level):
    for top in range(3, max_level + 1):
        for outsider in itertools.product(range(1, top), repeat=4):
            if all(outsider[i] >= outsider[i + 1] for i in range(3)):
                yield tuple(map(F, (top, top, *outsider)))


def shape_of(z):
    blocks, last = [], None
    for value in z[2:]:
        if value != last:
            blocks.append(1)
            last = value
        else:
            blocks[-1] += 1
    return tuple(blocks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-level", type=int, default=9)
    parser.add_argument("--menu-size", type=int, default=5)
    parser.add_argument("--stop-after", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    shapes = tuple(ordered_compositions(4))
    profiles = tuple(z_profiles(args.max_level))
    stats = Counter()
    hits = []
    near_misses = []
    for menu in itertools.combinations(range(1, 16), args.menu_size):
        menu_covers = covers_for_menu(menu)
        blueprints = {
            shape: audit_menu(menu, shape, menu_covers) for shape in shapes
        }
        if not any(blueprints.values()):
            continue
        stats["incidence_blueprint_menus"] += 1
        menu_rows = tuple(coalition(trace) for trace in menu)
        for z in profiles:
            shape = shape_of(z)
            blueprint = blueprints.get(shape)
            if blueprint is None:
                continue
            total = sum(z, F(0))
            for left, right in itertools.combinations(range(2, 6), 2):
                cx = (3 | (1 << left), 3 | (1 << right))
                maximum_l = min(csum(z, row) for row in cx)
                for level in range(1, int(maximum_l) + 1):
                    level = F(level)
                    if any(csum(z, row) < level for row in cx):
                        continue
                    u = (total - level) / 3
                    p = (4 * level - total) / 6
                    if not (p > u > 0):
                        continue
                    x = (p, p, u, u, u, u)
                    if any(csum(x, row) < csum(z, row) for row in menu_rows):
                        continue
                    cover_records = blueprint["covers"]
                    active_cx = tuple(row for row in cx if csum(z, row) == level)
                    displayed_directions = [
                        tuple(map(F, cover["surviving_direction"]["direction"]))
                        for cover in cover_records
                    ]
                    if any(any(csum(direction, row) < 0 for row in active_cx)
                           for direction in displayed_directions):
                        continue
                    stats["comparison_compatible_cover_dependent_cells"] += 1
                    constraints = {cx[0]: level, cx[1]: level}
                    constraints.update({row: csum(z, row) for row in menu_rows})
                    values, rx, rz = selector_pair(constraints, 6, total)
                    stats["exact_replays"] += 1
                    if rx != x or rz != z:
                        stats["selector_mismatch"] += 1
                        continue
                    item = audit_game(
                        "PXC103_cover_dependent_candidate", values, x, z,
                        pool_max=14, replay_exact=False,
                    )
                    if item is None or not item["cx_subsets_exhausted"]:
                        stats["audit_rejected"] += 1
                        continue
                    if not item["existential_cx_counterexample"]:
                        stats["some_complete_cx_or_cover_faithful"] += 1
                        if len(near_misses) < 20:
                            near_misses.append({
                                "constraints": {str(row): str(bound)
                                                for row, bound in constraints.items()},
                                "x": list(map(str, x)), "z": list(map(str, z)),
                                "intended_cx": list(cx),
                                "menu_rows": list(menu_rows),
                                "tight_x_rows": item["tight_x_rows"],
                                "complete_cx_count": item["complete_cx_count"],
                                "covers": item["covers"],
                            })
                        continue
                    failing = item["pin"]["failing_complete_cx"]
                    directions = []
                    for failed in failing:
                        direction = common_staged_direction_xz(
                            x, z, tuple(failed["cx_rows"]), item["covers"]
                        )
                        directions.append(direction)
                    if any(direction is not None for direction in directions):
                        stats["common_direction_survived"] += 1
                        continue
                    hit = {
                        "constraints": {str(row): str(bound)
                                        for row, bound in constraints.items()},
                        "x": list(map(str, x)),
                        "z": list(map(str, z)),
                        "intended_cx": list(cx),
                        "menu_rows": list(menu_rows),
                        "incidence_blueprint": blueprint,
                        "exact_audit": item,
                        "common_directions_by_failing_cx": directions,
                    }
                    hits.append(hit)
                    stats["exact_second_mechanisms"] += 1
                    if len(hits) >= args.stop_after:
                        break
                if len(hits) >= args.stop_after:
                    break
            if len(hits) >= args.stop_after:
                break
        if len(hits) >= args.stop_after:
            break
    payload = {
        "claim": "targeted exact search for a cover-dependent second mechanism",
        "parameters": vars(args) | {"output": str(args.output) if args.output else None},
        "stats": dict(stats),
        "hits": hits,
        "near_misses": near_misses,
        "scope": (
            "finite integer payoff grid and two-row symmetric Lmin certificate; "
            "a hit is exact project-code evidence pending independent replay"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
