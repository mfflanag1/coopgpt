#!/usr/bin/env python3
r"""Exact controls for the generalized packet-deficit quota (PXC58).

The dimension-free theorem is a displayed aggregate identity.  This driver
checks its coefficient expansion over a broad parameter grid and replays the
primitive hostile branch and both balanced sharp-family orientations.  The
finite controls audit signs and scope; they are not a universal selection
theorem.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402


def aggregate_coefficients(p: int, g: int, h: int, s: int):
    """Coefficients of R-L after xG=zG-D and xP=zP+D-L."""
    q = g + h
    d = p + g - s
    # Ordered as (zP,zG,zH,D,L).  Build the left side directly from
    # xG=zG-D, xP=zP+D-L, and the displayed definition of R.
    z_p = (F(1), F(0), F(0), F(0), F(0))
    z_g = (F(0), F(1), F(0), F(0), F(0))
    z_h = (F(0), F(0), F(1), F(0), F(0))
    loss = (F(0), F(0), F(0), F(0), F(1))
    x_g = (F(0), F(1), F(0), F(-1), F(0))
    x_p = (F(1), F(0), F(0), F(1), F(-1))

    def add(*vectors):
        return tuple(sum((vector[i] for vector in vectors), F(0)) for i in range(5))

    def scale(value, vector):
        return tuple(F(value) * coordinate for coordinate in vector)

    z_gh = add(z_g, z_h)
    numerator = add(
        scale(p - s, x_g),
        scale(-g, x_p),
        scale(p - s, add(z_h, scale(F(-h, q), z_gh))),
        scale(F(g * s, q), z_gh),
    )
    derived = add(scale(F(1, g), numerator), scale(-1, loss))
    quota = (
        F(-1),
        F(p, q),
        F(p, q),
        -F(d, g),
        F(0),
    )
    return derived, quota


def row_certificate(case, coalition: int, root: int):
    x, z = tuple(case["x"]), tuple(case["z"])
    n = len(x)
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = tuple(i for i in range(n) if i not in gainers)
    j_set = tuple(i for i in gainers if coalition >> i & 1)
    h_set = tuple(i for i in nongainers if coalition >> i & 1)
    p_set = tuple(i for i in nongainers if not (coalition >> i & 1))
    if root not in h_set or not p_set or len(j_set) >= len(gainers):
        raise AssertionError("row does not have the required rooted comparison form")
    row = master_identity(x, z, p_set, gainers, h_set, j_set)
    total = sum(x, F(0))
    total_gain = sum((z[i] - x[i] for i in gainers), F(0))
    h_loss = sum((x[i] - z[i] for i in h_set), F(0))
    p, g, s = len(p_set), len(gainers), len(j_set)
    quota = sum((F(total, n) - z[i] for i in p_set), F(0))
    quota_margin = F(n, n - p) * quota - F(p + g - s, g) * total_gain
    combined_margin = F(row["residual_budget"]) - h_loss
    if quota_margin != combined_margin:
        raise AssertionError("generalized packet-deficit quota identity failed")
    if F(row["normalized_budget_margin"]) != F(g, p + g - s) * quota_margin:
        raise AssertionError("quota/direct-master normalization failed")
    return {
        "coalition": coalition,
        "P": list(p_set),
        "H": list(h_set),
        "J": list(j_set),
        "sizes": {"p": p, "g": g, "h": len(h_set), "s": s},
        "base": row["base_bound_ratio"],
        "below_mean_quota": str(quota),
        "required_quota": str(F((n - p) * (p + g - s), n * g) * total_gain),
        "quota_margin": str(quota_margin),
        "direct_combined_margin": row["normalized_budget_margin"],
        "quota_closes": quota_margin >= 0,
    }


def fixed_controls():
    primitive = next(
        row for row in CASES if row["name"] == "primitive_coefficient_seven_failure"
    )
    hostile = [row_certificate(primitive, coalition, 6) for coalition in (70, 85, 90, 104, 204)]
    if any(row["quota_closes"] for row in hostile):
        raise AssertionError("primitive hostile quota obstruction disappeared")

    sharp_rows = []
    for name, root, coalitions in (
        ("sharp_family_p2_k4", 0, (57, 89, 105, 113)),
        ("sharp_family_p3_k3", 0, (49, 81, 97)),
    ):
        case = next(row for row in CASES if row["name"] == name)
        rows = [row_certificate(case, coalition, root) for coalition in coalitions]
        if any(F(row["quota_margin"]) != 0 for row in rows):
            raise AssertionError("sharp-family quota equality changed")
        sharp_rows.append({"name": name, "rows": rows})
    return hostile, sharp_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=32)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_n < 8:
        raise ValueError("parameter cutoff must be at least eight")

    coefficient_rows = 0
    for n in range(4, args.max_n + 1):
        for g in range(1, n - 1):
            for h in range(1, n - g):
                p = n - g - h
                for s in range(g):
                    derived, quota = aggregate_coefficients(p, g, h, s)
                    if derived != quota:
                        raise AssertionError(("coefficient identity failed", n, g, h, s))
                    coefficient_rows += 1

    hostile, sharp = fixed_controls()
    report = {
        "status": "exact generalized packet-deficit quota controls verified",
        "human_identity": (
            "R_s-L_H = n Q(P)/(n-p) - (p+g-s)D/g, where "
            "Q(P)=sum_{i in P}(T/n-z_i)"
        ),
        "closing_criterion": (
            "the combined comparison/residual term is nonnegative iff "
            "Q(P)>=[(n-p)(p+g-s)/(ng)]D"
        ),
        "coefficient_grid": {
            "minimum_n": 4,
            "maximum_n": args.max_n,
            "rows": coefficient_rows,
        },
        "primitive_hostile_rows": hostile,
        "balanced_sharp_family_equalities": sharp,
        "scope": (
            "dimension-free human identity with exact coefficient and fixed-branch "
            "controls; does not select P or supply the missing Lmax quota payment"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
