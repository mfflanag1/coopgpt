#!/usr/bin/env python3
"""Exact audit of the ceiling-root interpolation lower bound.

The human argument is dimension free.  This script checks its arithmetic on
the archived hard controls and on a symbolic family attaining equality.  It
does not recompute either egalitarian selection and is therefore an audit,
not a proof dependency.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from verify_labelled_branch_duals import CASES
from verify_n7_neutral_rectangle_control import X as NEUTRAL_X
from verify_n7_neutral_rectangle_control import Z as NEUTRAL_Z


def target(n: int) -> F:
    return F(4 * n, n * n - (n % 2))


def audit_pair(name, x, z):
    x, z = tuple(x), tuple(z)
    n = len(x)
    total = sum(x, F(0))
    if total <= 0 or sum(z, F(0)) != total:
        raise AssertionError("payoff vectors must have the same positive total")
    mu, ceiling = min(x), max(z)
    if mu < 0 or ceiling <= 0:
        raise AssertionError("normalization/nonnegativity premise failed")
    roots = tuple(
        i for i, (xi, zi) in enumerate(zip(x, z))
        if zi == ceiling and xi >= ceiling
    )
    if not roots:
        raise AssertionError("archived pair has no ceiling root")
    overlap = sum((min(xi, zi) for xi, zi in zip(x, z)), F(0))
    lower_bound = ceiling - mu + total * mu / ceiling
    if overlap < lower_bound:
        raise AssertionError("ceiling-root interpolation inequality failed")
    threshold = target(n) * total
    normalized_ceiling = ceiling / total
    normalized_floor = mu / total
    if normalized_ceiling < target(n):
        wedge_ceiling = (
            normalized_ceiling
            * (target(n) - normalized_ceiling)
            / (1 - normalized_ceiling)
        )
    else:
        wedge_ceiling = F(0)
    return {
        "name": name,
        "n": n,
        "ceiling_roots": roots,
        "floor_over_T": str(normalized_floor),
        "ceiling_over_T": str(normalized_ceiling),
        "overlap_over_T": str(overlap / total),
        "interpolation_bound_over_T": str(lower_bound / total),
        "target_over_T": str(target(n)),
        "bound_slack": str(overlap - lower_bound),
        "interpolation_alone_closes_target": lower_bound >= threshold,
        "unresolved_wedge_floor_ceiling": str(wedge_ceiling),
    }


def equality_control(q: int, low: F, ceiling: F, n: int = 7):
    """Create the {0,M}-spectrum equality pattern from the human proof."""
    if not (1 <= q < n) or not (F(0) < low <= ceiling):
        raise AssertionError("invalid equality-family parameters")
    # Root 0 gets M from each vector.  The other q-1 top players get x=mu,
    # while the residual players share the remaining x mass.  All remaining
    # z mass is zero, so T=qM.  The chosen controls make that residual share
    # at least mu, as required for mu=min(x).
    total = q * ceiling
    residual = (total - ceiling - (q - 1) * low) / (n - q)
    if residual < low:
        raise AssertionError("residual player would lower the asserted floor")
    x = (ceiling,) + (low,) * (q - 1) + (residual,) * (n - q)
    z = (ceiling,) * q + (F(0),) * (n - q)
    row = audit_pair(f"equality_q{q}", x, z)
    if row["bound_slack"] != "0":
        raise AssertionError("claimed equality control is not tight")
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    controls = [audit_pair(case["name"], case["x"], case["z"]) for case in CASES]
    controls.append(audit_pair("neutral_rectangle", NEUTRAL_X, NEUTRAL_Z))
    equalities = (
        equality_control(2, F(1, 10), F(1)),
        equality_control(3, F(1, 4), F(1)),
        equality_control(4, F(1, 5), F(1)),
    )
    report = {
        "status": "exact ceiling-root interpolation arithmetic audit",
        "human_theorem": (
            "if mu=min(x)>0, M=max(z), and some top player r has x_r>=M, "
            "then overlap(x,z)>=M-mu+T*mu/M"
        ),
        "normalized_form": "O/T >= t-u+u/t, where t=M/T and u=mu/T",
        "target_reduction": (
            "the target c is automatic when t>=c; for t<c a remaining "
            "failure must have u<t(c-t)/(1-t)"
        ),
        "archived_controls": controls,
        "equality_controls": equalities,
        "controls_closed_by_interpolation_alone": sum(
            row["interpolation_alone_closes_target"] for row in controls
        ),
        "scope": (
            "solver-free exact arithmetic on fixed selections; selection "
            "validity and ceiling-root existence come from earlier certificates"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
