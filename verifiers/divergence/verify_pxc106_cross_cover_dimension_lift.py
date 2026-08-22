#!/usr/bin/env python3
"""Exact finite anchors and symbolic audit for the PXC106 all-n lift."""
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
    selector_pair,
    tight_rows,
)
from search_pxc103_cover_dependent_failure import (  # noqa: E402
    common_staged_direction_xz,
)


def mask(players):
    return sum(1 << player for player in players)


def family(p: int, q: int, A: F):
    if p < 1 or q < 1:
        raise ValueError((p, q))
    m = p + q
    n = m + 4
    J = tuple(range(4, 4 + p))
    K = tuple(range(4 + p, n))
    rh = (0, 1)
    rows = {
        mask(rh + (2,)): F(16),
        mask(rh + (3,)): F(16),
        mask(rh + J): F(12 + p),
        mask(rh + (2,) + J): F(12 + p) + A,
        mask(rh + K): F(12 + q),
        mask(rh + (2,) + K): F(12 + q) + A,
    }
    total = F(16 + m) + A
    u = (A + m) / (m + 1)
    top = (16 - u) / 2
    x = (top, top) + (u,) * (m + 2)
    z = (F(6), F(6), A, F(4)) + (F(1),) * m
    cx = (mask(rh + (2,)), mask(rh + (3,)))
    covers = (
        (mask(rh),),
        (mask(rh + (3,)), mask(rh + J), mask(rh + (2,) + K)),
        (mask(rh + (3,)), mask(rh + (2,) + J), mask(rh + K)),
    )
    avg_all = 1 + (A - 4) / m
    avg_j = 1 + (A - 4) / p
    avg_k = 1 + (A - 4) / q
    reduced = (
        (F(6), F(6), F(4), F(4)) + (avg_all,) * m,
        (F(6), F(6), F(4), F(4)) + (F(1),) * p + (avg_k,) * q,
        (F(6), F(6), F(4), F(4)) + (avg_j,) * p + (F(1),) * q,
    )
    return {
        "p": p, "q": q, "m": m, "n": n, "J": J, "K": K,
        "A": A, "total": total, "rows": rows, "x": x, "z": z,
        "cx": cx, "covers": covers, "reduced": reduced,
        "slack_J": p * (A - 1) / (m + 1) - (A - 4),
        "slack_K": q * (A - 1) / (m + 1) - (A - 4),
    }


def audit_case(p, q, A):
    d = family(p, q, A)
    if not (F(4) < A < F(6) and d["slack_J"] > 0 and d["slack_K"] > 0):
        raise AssertionError(("outside chamber", p, q, A))
    values, x, z = selector_pair(d["rows"], d["n"], d["total"])
    if x != d["x"] or z != d["z"]:
        raise AssertionError((p, q, A, x, z))
    if any(values[1 << i] for i in range(d["n"])):
        raise AssertionError(("singleton normalization", p, q, A))
    item = audit_game(f"PXC106_{p}_{q}_{A}", values, x, z,
                      pool_max=10, replay_exact=False)
    if item is None:
        raise AssertionError(("target domain", p, q, A))
    if tuple(item["tight_x_rows"]) != d["cx"]:
        raise AssertionError(("x menu", p, q, A, item["tight_x_rows"]))
    if item["complete_cx_count"] != 1 or tuple(item["canonical_cx"]) != d["cx"]:
        raise AssertionError(("complete Cx", p, q, A))
    got_covers = tuple(tuple(c["rows"]) for c in item["covers"])
    if got_covers != d["covers"]:
        raise AssertionError(("covers", p, q, A, got_covers, d["covers"]))
    got_reduced = tuple(tuple(map(F, c["fixed_lmax"])) for c in item["covers"])
    if got_reduced != d["reduced"] or any(c["fixed_faithful"]
                                           for c in item["covers"]):
        raise AssertionError(("reduced", p, q, A, got_reduced))
    if common_staged_direction_xz(x, z, d["cx"], item["covers"]) is not None:
        raise AssertionError(("common staged descent", p, q, A))
    union = sorted({row for cover in got_covers for row in cover})
    if union != list(tight_rows(values, z)):
        raise AssertionError(("forced-zero row", p, q, A, union,
                              tight_rows(values, z)))
    return {
        "n": d["n"], "p": p, "q": q, "A": str(A),
        "total": str(d["total"]), "slack_J": str(d["slack_J"]),
        "slack_K": str(d["slack_K"]), "lmin": list(map(str, x)),
        "lmax": list(map(str, z)), "tight_x": item["tight_x_rows"],
        "tight_z": list(tight_rows(values, z)),
        "covers": item["covers"],
        "reduced_lmax": [list(map(str, r)) for r in got_reduced],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    exact_cases = [
        audit_case(1, 1, F(5)),
        audit_case(1, 2, F(17, 4)),
        audit_case(1, 3, F(21, 5)),
        audit_case(2, 2, F(5)),
    ]

    symbolic = []
    for n in range(6, 45):
        m = n - 4
        p, q = 1, m - 1
        A = 4 + F(1, m + 1)
        d = family(p, q, A)
        if not (d["slack_J"] > 0 and d["slack_K"] > 0):
            raise AssertionError(("specialization slack", n, d))
        # Incidence identities: each positive cover partitions every non-top
        # player once, all three rows contain both tops, and weights 1/4 give
        # eta=1/4 and alpha_r=alpha_h=1/2.
        for cover in d["covers"][1:]:
            for player in range(2, n):
                if sum((row >> player) & 1 for row in cover) != 1:
                    raise AssertionError(("partition", n, cover, player))
            if any(sum((row >> top) & 1 for row in cover) != 3
                   for top in (0, 1)):
                raise AssertionError(("top load", n, cover))
        if any(r == d["z"] for r in d["reduced"]):
            raise AssertionError(("faithful specialization", n))
        symbolic.append({
            "n": n, "p": p, "q": q, "A": str(A),
            "total": str(d["total"]), "u": str((A + m) / (m + 1)),
            "top": str((16 - (A + m) / (m + 1)) / 2),
            "slack_J": str(d["slack_J"]),
            "slack_K": str(d["slack_K"]),
        })

    payload = {
        "claim": "PXC106 genuine all-n cross-cover dimension lift",
        "theorem": {
            "n": "4+p+q with p,q>=1",
            "parameter_chamber": (
                "4<A<6, p(A-1)>(p+q+1)(A-4), and "
                "q(A-1)>(p+q+1)(A-4)"
            ),
            "explicit_all_n_specialization": (
                "p=1, q=n-5, A=4+1/(n-3)"
            ),
            "non_null": True,
            "top_players": 2,
            "complete_cx_count": 1,
            "extreme_cover_count": 3,
            "forced_zero_rows": 0,
        },
        "exact_project_replays": exact_cases,
        "symbolic_dimension_checks": symbolic,
        "scope": (
            "conventional block-family proof; exact all-coalition selector and "
            "cover replays at n=6,7,8 plus dimension-free incidence identities"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
