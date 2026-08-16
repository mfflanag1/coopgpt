#!/usr/bin/env python3
r"""Exact mixed-witness branch projections for the named hostile controls.

The mixed-witness projection of the labelled branch spanned by a
control's complete tight supports and payoff strata gives an exact
minimum overlap for every game in that branch.  Both named packet-
violation controls close: the mutation control's branch minimum is
`11/15` and the split-top clean control's is `16/25`, each equal to its
one-witness minimum after a single cut and both above the target ratio
`7/12`.  Together with the spectral chain and, on the uniform side, the
chosen-family certificate, the two named hostile controls carry three
independent proved closures.  Branch minima are finite branch theorems,
not universal selection.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

import verify_mixed_witness_projection as projection  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors  # noqa: E402
from verify_labelled_branch_duals import verify_complete_selection  # noqa: E402


CONTROLS = (
    ("mutation_control", (2, 0, 7, 2, 0, 1, 0), (0, 4, 0, 0, 4, 0, 4),
     "11/15"),
    ("clean_split_top_control", (0, 6, 3, 3, 0, 0, 0), (8, 0, 0, 0, 1, 1, 2),
     "16/25"),
)


def build_case(name, g, h):
    generators = (tuple(map(F, g)), tuple(map(F, h)))
    n = len(g)
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    full = (1 << n) - 1
    support_x = tuple(
        c for c in range(1, full) if coalition_sum(x, c) == values[c]
    )
    support_z = tuple(
        c for c in range(1, full) if coalition_sum(z, c) == values[c]
    )
    case = {
        "name": name,
        "g": tuple(map(F, g)),
        "h": tuple(map(F, h)),
        "x": x,
        "z": z,
        "support_x": support_x,
        "support_z": support_z,
    }
    return case, values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for name, g, h, expected in CONTROLS:
        case, values = build_case(name, g, h)
        verify_complete_selection(
            values, tuple(case["x"]), "min", case["support_x"]
        )
        verify_complete_selection(
            values, tuple(case["z"]), "max", case["support_z"]
        )
        audited = projection.audit_case(case)
        minima = [F(row["projected_minimum"]) for row in audited["roots"]]
        best = max(minima)
        if str(best) != expected:
            raise AssertionError(
                f"{name} branch minimum drifted: {best} != {expected}"
            )
        if best < F(7, 12):
            raise AssertionError(f"{name} branch does not close the target")
        for row in audited["roots"]:
            if row["projected_minimum"] != row["direct_witness_minimum"]:
                raise AssertionError(
                    f"{name} projected and one-witness minima diverged"
                )
        rows.append(
            {
                "name": name,
                "branch_minimum": expected,
                "roots": [
                    {
                        "root": row["root"],
                        "projected_minimum": row["projected_minimum"],
                        "cut_count": row["cut_count"],
                    }
                    for row in audited["roots"]
                ],
            }
        )

    summary = {
        "controls": len(rows),
        "branch_minima": [row["branch_minimum"] for row in rows],
    }
    payload = {
        "claim": (
            "the mixed-witness projection closes both named hostile "
            "controls' labelled branches above the target ratio"
        ),
        "summary": summary,
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
