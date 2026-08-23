#!/usr/bin/env python3
"""Primary exact audit of the second minimal reciprocal obstruction PXC118.

The witness is obtained from PXC104 by adjoining the common-tight row
``ajk >= 7``.  This is not treated as a perturbative argument: the script
reconstructs the complete lower-envelope game, both staged selectors, every
complete proper-row Lmin certificate, every positive extreme top cover, and
every retained-row lift over exact rational arithmetic.
"""
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
from verify_pxc108_invariant_cover_blocker_circuits import recognize  # noqa: E402


N = 6
TOTAL = F(23)
DEFINING = {
    7: F(16), 11: F(16), 19: F(13), 23: F(18),
    35: F(13), 39: F(18), 52: F(7),
}
X = (F(41, 6), F(41, 6), F(7, 3), F(7, 3), F(7, 3), F(7, 3))
Z = tuple(map(F, (6, 6, 5, 4, 1, 1)))
COMPLETE_CX = ((7, 11), (7, 11, 52))
COVER_ROWS = ((3,), (11, 55), (11, 19, 39), (11, 23, 35))
COVER_DATA = (
    {"rows": (3,), "weights": (F(1, 2),), "eta": F(0)},
    {"rows": (11, 55), "weights": (F(1, 2),) * 2, "eta": F(1, 2)},
    {"rows": (11, 19, 39), "weights": (F(1, 4),) * 3, "eta": F(1, 4)},
    {"rows": (11, 23, 35), "weights": (F(1, 4),) * 3, "eta": F(1, 4)},
)
REDUCED = (
    tuple(map(F, (6, 6, 4, 4, F(3, 2), F(3, 2)))),
    tuple(map(F, (6, 6, 4, 4, F(3, 2), F(3, 2)))),
    tuple(map(F, (6, 6, 4, 4, 1, 2))),
    tuple(map(F, (6, 6, 4, 4, 2, 1))),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values, x, z = selector_pair(DEFINING, N, TOTAL)
    if (x, z) != (X, Z):
        raise AssertionError((x, z))
    if any(values[1 << i] for i in range(N)):
        raise AssertionError("singleton normalization failed")
    if tight_rows(values, X) != (7, 11, 52):
        raise AssertionError(("x-tight", tight_rows(values, X)))
    if tight_rows(values, Z) != (3, 11, 19, 23, 35, 39, 52, 55):
        raise AssertionError(("z-tight", tight_rows(values, Z)))

    item = audit_game(
        "PXC118_second_reciprocal_primitive", values, X, Z,
        pool_max=20, replay_exact=False,
    )
    if item is None or not item["cx_subsets_exhausted"]:
        raise AssertionError("full exact audit rejected candidate")
    complete = tuple(tuple(q["cx_rows"]) for q in item["complete_cx_cover_matrix"])
    if complete != COMPLETE_CX or item["complete_cx_count"] != 2:
        raise AssertionError(("complete Cx", complete))
    covers = tuple(tuple(q["rows"]) for q in item["covers"])
    if covers != COVER_ROWS:
        raise AssertionError(("covers", covers))
    if any(q["fixed_faithful"] for q in item["covers"]):
        raise AssertionError("a cover became faithful")
    if tuple(tuple(map(F, q["fixed_lmax"])) for q in item["covers"]) != REDUCED:
        raise AssertionError("reduced Lmax list changed")
    if any(tuple(map(F, q["fixed_lmin"])) != X for q in item["covers"]):
        raise AssertionError("a cover lift changed Lmin")
    if any(not q["fixed_lift_singleton_normalized"] for q in item["covers"]):
        raise AssertionError("a cover lift lost singleton normalization")

    graph_rows = []
    for cx in COMPLETE_CX:
        common = common_staged_direction_xz(X, Z, cx, item["covers"])
        if common is not None:
            raise AssertionError(("unexpected common direction", cx, common))
        graph = recognize({
            "label": f"PXC118 Cx={cx}", "x": X, "z": Z,
            "top": (0, 1), "cx": cx, "covers": COVER_DATA,
        })
        edges = graph["invariant_edges"]
        if 3 not in edges["2"] or 2 not in edges["3"]:
            raise AssertionError(("reciprocal edge disappeared", cx, edges))
        if graph["classification"] != "invariant chordless cover cycle":
            raise AssertionError((cx, graph["classification"]))
        graph_rows.append({
            "cx": list(cx),
            "classification": graph["classification"],
            "edges": edges,
            "shortest_induced_cycle": graph["shortest_induced_cycle"],
            "common_descent_slots": graph["common_descent_slots"],
        })

    left = tuple(a - b for a, b in zip(REDUCED[2], Z))
    right = tuple(a - b for a, b in zip(REDUCED[3], Z))
    if not (csum(left, 23) < 0 and csum(left, 39) == 0):
        raise AssertionError("left cross blocker changed")
    if not (csum(right, 39) < 0 and csum(right, 23) == 0):
        raise AssertionError("right cross blocker changed")

    # Fail-open controls.  Removing the new common row recovers exactly the
    # three-cover PXC104 game; restoring the two cross blockers to either
    # cyclic lift recovers the original selector z.
    base = dict(DEFINING)
    del base[52]
    base_values, base_x, base_z = selector_pair(base, N, TOTAL)
    base_item = audit_game("PXC104_control", base_values, base_x, base_z,
                           pool_max=20, replay_exact=False)
    if (
        base_item is None or (base_x, base_z) != (X, Z)
        or len(base_item["covers"]) != 3
    ):
        raise AssertionError("drop-common-row control did not recover PXC104")
    repair_selectors = []
    for index, cover_rows in enumerate(COVER_ROWS[2:], start=2):
        constraints = {row: csum(X, row) for row in COMPLETE_CX[0]}
        constraints.update({row: csum(Z, row) for row in cover_rows})
        blocker = 23 if index == 2 else 39
        constraints[blocker] = csum(Z, blocker)
        _rv, rx, rz = selector_pair(constraints, N, TOTAL)
        if (rx, rz) != (X, Z) or any(_rv[1 << i] for i in range(N)):
            raise AssertionError(("cross-blocker fail-open", index, rx, rz))
        repair_selectors.append({
            "cover_index": index, "added_blocker": blocker,
            "lmin": list(map(str, rx)), "lmax": list(map(str, rz)),
        })

    payload = {
        "claim": (
            "PXC118 second dimension-minimal exact reciprocal obstruction; "
            "literal PXC104 reciprocal-incidence canonicality is false"
        ),
        "game": {
            "n": N, "total": str(TOTAL),
            "defining_rows": {str(k): str(v) for k, v in DEFINING.items()},
            "all_coalition_values": list(map(str, values)),
            "exactness": "compact lower-envelope construction",
            "singleton_normalized": True,
        },
        "selectors": {"lmin": list(map(str, X)), "lmax": list(map(str, Z))},
        "tight_menus": {
            "x": list(tight_rows(values, X)),
            "z": list(tight_rows(values, Z)),
        },
        "complete_cx_classes": [list(q) for q in COMPLETE_CX],
        "complete_cx_cover_matrix": item["complete_cx_cover_matrix"],
        "covers": item["covers"],
        "reciprocal_graphs": graph_rows,
        "cross_directions": {
            "left": list(map(str, left)), "right": list(map(str, right)),
        },
        "fail_open_controls": {
            "drop_row_52_recovers_PXC104_cover_count": len(base_item["covers"]),
            "cross_blocker_repairs": repair_selectors,
        },
        "nonisomorphism": (
            "four qualifying extreme covers versus PXC104's three; cover "
            "count is invariant under player relabeling"
        ),
        "dimension_minimality_dependency": (
            "PXC100 proves every five-player literal instance faithful"
        ),
        "scope": (
            "full exact six-player game; all proper x-tight subsets, both "
            "complete Cx classes, all positive extreme covers, every lift, "
            "and both reciprocal graphs are exhausted"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
