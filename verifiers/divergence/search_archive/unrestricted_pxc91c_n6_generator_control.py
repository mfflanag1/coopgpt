#!/usr/bin/env python3
"""Secondary exact generator control for unrestricted PXC91c at n=6.

This is a distinct discovery witness, not the PXC98 primary/independent
encoding and not evidence for a smaller dimension.
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
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(DIV / "search_archive")]

from unrestricted_pxc91c_exact_search import audit_game, csum  # noqa: E402

N = 6
GENERATORS = (
    (0, 13, 1, 3, 0, 1),
    (12, 0, 0, 1, 1, 4),
    (12, 5, 0, 0, 0, 1),
    (4, 10, 1, 0, 0, 3),
    (11, 3, 0, 1, 0, 3),
    (3, 11, 1, 3, 0, 0),
)
X = tuple(map(F, (F(25, 4), F(25, 4), F(1, 2), F(9, 4), F(1, 2), F(9, 4))))
Z = tuple(map(F, (6, 6, 0, 2, 1, 3)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    generators = tuple(tuple(map(F, g)) for g in GENERATORS)
    values = tuple(
        min(csum(g, mask) for g in generators) for mask in range(1 << N)
    )
    item = audit_game(
        "PXC91c_unrestricted_n6_candidate", values, X, Z,
        pool_max=10, replay_exact=True,
    )
    if item is None:
        raise AssertionError("candidate left the exact target domain")
    if item["tight_x_rows"] != [19, 43] or item["canonical_cx"] != [19, 43]:
        raise AssertionError("complete Lmin certificate changed")
    if item["cover_count"] != 5:
        raise AssertionError("qualifying extreme-cover census changed")
    if item["fixed_faithful_cover_exists"]:
        raise AssertionError("candidate acquired a faithful cover")
    if not item["cx_subsets_exhausted"] or item["complete_cx_count"] != 1:
        raise AssertionError("complete-Cx census is no longer unique")
    if item["existential_cx_faithful"] or item["universal_cx_faithful"]:
        raise AssertionError("fixed/existential Cx failure changed")
    payload = {
        "claim": (
            "secondary exact n=6 generator control failing both fixed- and "
            "existential-Cx unrestricted PXC91c"
        ),
        "generators": [list(g) for g in GENERATORS],
        "all_coalition_values": list(map(str, values)),
        "audit": item,
        "scope": (
            "full exact game and all complete Cx row subsets and qualifying "
            "positive extreme covers; discovery control distinct from PXC98"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
