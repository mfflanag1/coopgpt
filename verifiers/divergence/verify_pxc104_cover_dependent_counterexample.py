#!/usr/bin/env python3
"""Primary exact audit of the PXC104 cover-dependent obstruction."""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
DIV = HERE.parent
ARCHIVE = DIV / "search_archive"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(ARCHIVE)]

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    csum,
    selector_pair,
    tight_rows,
)
from search_pxc103_cover_dependent_failure import (  # noqa: E402
    common_staged_direction_xz,
)

N = 6
TOTAL = F(23)
CONSTRAINTS = {
    7: F(16), 11: F(16), 19: F(13),
    23: F(18), 35: F(13), 39: F(18),
}
X = (F(41, 6), F(41, 6), F(7, 3), F(7, 3), F(7, 3), F(7, 3))
Z = tuple(map(F, (6, 6, 5, 4, 1, 1)))
CX = (7, 11)
EXPECTED_COVERS = ((3,), (11, 19, 39), (11, 23, 35))
EXPECTED_REDUCED = (
    tuple(map(F, (6, 6, 4, 4, F(3, 2), F(3, 2)))),
    tuple(map(F, (6, 6, 4, 4, 1, 2))),
    tuple(map(F, (6, 6, 4, 4, 2, 1))),
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values, x, z = selector_pair(CONSTRAINTS, N, TOTAL)
    if x != X or z != Z:
        raise AssertionError((x, z))
    if any(values[1 << i] for i in range(N)):
        raise AssertionError("singleton normalization failed")
    item = audit_game("PXC104_cover_dependent", values, x, z,
                      pool_max=10, replay_exact=False)
    if item is None:
        raise AssertionError("candidate left target domain")
    if item["tight_x_rows"] != list(CX) or item["canonical_cx"] != list(CX):
        raise AssertionError("complete Cx changed")
    if item["complete_cx_count"] != 1 or not item["cx_subsets_exhausted"]:
        raise AssertionError("complete Cx is no longer unique")
    covers = tuple(tuple(cover["rows"]) for cover in item["covers"])
    if covers != EXPECTED_COVERS:
        raise AssertionError(covers)
    if any(cover["fixed_faithful"] for cover in item["covers"]):
        raise AssertionError("a qualifying cover became faithful")
    reduced = tuple(tuple(map(F, cover["fixed_lmax"])) for cover in item["covers"])
    if reduced != EXPECTED_REDUCED:
        raise AssertionError(reduced)
    if not item["existential_cx_counterexample"]:
        raise AssertionError("all-Cx failure changed")
    common = common_staged_direction_xz(x, z, CX, item["covers"])
    if common is not None:
        raise AssertionError(("unexpected common direction", common))

    d_pair = tuple(a - b for a, b in zip(EXPECTED_REDUCED[0], Z))
    d_left = tuple(a - b for a, b in zip(EXPECTED_REDUCED[1], Z))
    d_right = tuple(a - b for a, b in zip(EXPECTED_REDUCED[2], Z))
    if not (csum(d_left, 23) < 0 and csum(d_left, 39) == 0):
        raise AssertionError("left cross-blocker arithmetic changed")
    if not (csum(d_right, 39) < 0 and csum(d_right, 23) == 0):
        raise AssertionError("right cross-blocker arithmetic changed")
    if not (csum(d_pair, 23) < 0 and csum(d_pair, 39) < 0):
        raise AssertionError("pair cross-blocker arithmetic changed")
    cover_union = tuple(sorted({row for cover in covers for row in cover}))
    if cover_union != (3, 11, 19, 23, 35, 39):
        raise AssertionError(cover_union)
    forced_zero_rows = tuple(
        row for row in tight_rows(values, z)
        if all(row not in cover for cover in covers)
    )
    # PXC104 has no load-bearing blocker outside the union of all covers.
    if 23 in forced_zero_rows or 39 in forced_zero_rows:
        raise AssertionError(forced_zero_rows)

    payload = {
        "claim": "PXC104 exact cover-dependent obstruction; PXC103 is not universal",
        "game": {
            "n": N, "total": str(TOTAL),
            "defining_rows": {str(k): str(v) for k, v in CONSTRAINTS.items()},
            "all_coalition_values": list(map(str, values)),
            "singleton_normalized": True,
            "exactness": "lower envelope of the displayed compact polytope",
        },
        "selectors": {"lmin": list(map(str, X)), "lmax": list(map(str, Z))},
        "tight_menus": {
            "x": list(tight_rows(values, X)),
            "z": list(tight_rows(values, Z)),
        },
        "complete_cx": list(CX),
        "complete_cx_count": item["complete_cx_count"],
        "covers": item["covers"],
        "cover_union": list(cover_union),
        "common_staged_direction": common,
        "cover_specific_directions": {
            "pair": list(map(str, d_pair)),
            "left": list(map(str, d_left)),
            "right": list(map(str, d_right)),
        },
        "cross_blockers": {
            "left_descent_blocked_by_row_23_positive_in_right_cover": True,
            "right_descent_blocked_by_row_39_positive_in_left_cover": True,
            "pair_descent_blocked_by_both_cross_rows": True,
        },
        "forced_zero_rows": list(forced_zero_rows),
        "fixed_cx_refuted": True,
        "existential_cx_refuted": True,
        "scope": (
            "full exact game, unique complete proper-row Cx, exhaustive positive "
            "extreme-cover census, and exact selector replay"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
