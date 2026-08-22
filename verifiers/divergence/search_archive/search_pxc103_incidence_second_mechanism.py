#!/usr/bin/env python3
"""Finite incidence search for a cover-dependent PXC103 obstruction.

Rows contain both top players and a nonempty trace on four outsiders.  The
driver exhausts trace menus, enumerates every positive extreme normalized top
cover, and seeks the smallest menu such that

* every extreme cover is rank deficient and leaves some staged Lmax descent;
* the union of all cover supports has outsider rank four and leaves no common
  staged descent.

Such a menu is only an oriented-matroid blueprint.  It is not an exact-game
counterexample until compatible payoffs, singleton witnesses, both selectors,
and every complete Cx are constructed and independently replayed.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DIV = ROOT / "verifiers" / "divergence"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(HERE.parent)]

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    csum,
    matrix_rank,
    normalized_cover,
)
from search_pxc103_cover_dependent_failure import (  # noqa: E402
    common_staged_direction_xz,
)


N = 6
TOP_MASK = 3


def coalition(trace):
    return TOP_MASK | (trace << 2)


def covers_for_menu(menu):
    rows = tuple(coalition(trace) for trace in menu)
    answer = []
    for size in range(1, 5):
        for support in itertools.combinations(rows, size):
            cert = normalized_cover(support, (0, 1), N)
            if cert is not None:
                answer.append((support, cert))
    return tuple(answer)


def rank_on_outsiders(rows):
    return matrix_rank([
        [F((row >> i) & 1) for row in rows] for i in range(2, 6)
    ])


def z_for_shape(shape):
    # Blocks are listed from high to low; integers keep every boundary exact.
    levels = list(range(len(shape) + 1, 1, -1))
    outsiders, cursor = [], 0
    for size, level in zip(shape, levels):
        outsiders.extend([F(level)] * size)
        cursor += size
    if cursor != 4:
        raise AssertionError(shape)
    top = F(len(shape) + 2)
    z = (top, top, *outsiders)
    return tuple(z)


def ordered_compositions(total):
    for cuts in range(1 << (total - 1)):
        block, out = 1, []
        for gap in range(total - 1):
            if cuts >> gap & 1:
                out.append(block)
                block = 1
            else:
                block += 1
        out.append(block)
        yield tuple(out)


def audit_menu(menu, shape, covers=None):
    covers = covers_for_menu(menu) if covers is None else covers
    if len(covers) < 2:
        return None
    if any(rank_on_outsiders(rows) == 4 for rows, _ in covers):
        return None
    union = tuple(sorted({row for rows, _ in covers for row in rows}))
    if rank_on_outsiders(union) != 4:
        return None
    z = z_for_shape(shape)
    x = tuple([sum(z, F(0)) / N] * N)
    records = [{"rows": list(rows)} for rows, _ in covers]
    individual = [
        common_staged_direction_xz(x, z, (), (record,)) for record in records
    ]
    if any(direction is None for direction in individual):
        return None
    common = common_staged_direction_xz(x, z, (), records)
    if common is not None:
        return None
    return {
        "menu_traces": list(menu),
        "menu_rows": [coalition(trace) for trace in menu],
        "shape": list(shape),
        "z": list(map(str, z)),
        "cover_count": len(covers),
        "covers": [
            {
                "rows": list(rows),
                "traces": [row >> 2 for row in rows],
                "weights": list(map(str, cert[0])),
                "eta": str(cert[1]),
                "alpha": list(map(str, cert[2])),
                "outsider_rank": rank_on_outsiders(rows),
                "surviving_direction": individual[index],
            }
            for index, (rows, cert) in enumerate(covers)
        ],
        "cover_union": list(union),
        "cover_union_rank": rank_on_outsiders(union),
        "common_direction": common,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu-max", type=int, default=8)
    parser.add_argument("--stop-after", type=int, default=20)
    parser.add_argument("--exclude-traces", type=str, default="")
    parser.add_argument("--shape", type=str, default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    excluded = {int(item) for item in args.exclude_traces.split(",") if item}
    shapes = tuple(ordered_compositions(4))
    if args.shape:
        requested = tuple(int(item) for item in args.shape.split(","))
        if requested not in shapes:
            raise ValueError((requested, shapes))
        shapes = (requested,)
    checked = 0
    hits = []
    size_counts = {}
    for size in range(2, args.menu_max + 1):
        size_checked = 0
        for menu in itertools.combinations(range(1, 16), size):
            if excluded.intersection(menu):
                continue
            size_checked += 1
            for shape in shapes:
                checked += 1
                hit = audit_menu(menu, shape)
                if hit is not None:
                    hits.append(hit)
                    if len(hits) >= args.stop_after:
                        break
            if len(hits) >= args.stop_after:
                break
        size_counts[str(size)] = size_checked
        if hits:
            break
    payload = {
        "claim": "finite incidence search for a cover-dependent second mechanism",
        "parameters": vars(args) | {"output": str(args.output) if args.output else None},
        "ordered_residual_shapes": [list(shape) for shape in shapes],
        "incidence_cells_checked": checked,
        "menu_counts_checked": size_counts,
        "minimum_hit_menu_size": None if not hits else len(hits[0]["menu_traces"]),
        "hits": hits,
        "scope": (
            "exact 0/1 incidence and rational tangent arithmetic with both-top "
            "rows only; hits are blueprints, not exact games"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
