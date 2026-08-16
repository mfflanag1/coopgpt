#!/usr/bin/env python3
r"""Exact controls for chosen-family co-star closure (PXC76).

The decorated co-star family in (PXC59) is a selectable object: each type
may use any $x$-tight decorated co-star, subject to the outsider load cap,
and the aligned common row's decoration loss is pinned by (PXC72) at
`D-d_a-ell_r`.  Maximizing the priced decoration mass over admissible
families therefore evaluates the strongest packet-side certificate on the
arm.  This driver enumerates all admissible families exactly on the named
packet-violation controls: every uniform-family violation closes, with the
mutation control at margin `29/30`, so the earlier claim that no
packet-side certificate closes it is corrected; only the split-top clean
control leaves the certificate's hypotheses (no aligned common row) and is
direct-closed.  Chosen-family closure is finite evidence, not a selection
theorem.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import (  # noqa: E402
    family_instance,
    margins,
    selectors,
)


CONTROLS = (
    ("mutation_control", ((2, 0, 7, 2, 0, 1, 0), (0, 4, 0, 0, 4, 0, 4)),
     "29/30"),
    ("clean_control", ((0, 3, 0, 0, 0, 3, 6), (1, 0, 1, 2, 8, 0, 0)),
     None),
    ("family_4_4_4__7__311", family_instance((4, 4, 4), 7, (3, 1, 1)),
     "31/20"),
    ("family_4_4_4__7__221", family_instance((4, 4, 4), 7, (2, 2, 1)),
     "29/30"),
    ("family_6_6_6__10__422", family_instance((6, 6, 6), 10, (4, 2, 2)),
     "27/10"),
    ("family_4x4__11__221", family_instance((4, 4, 4, 4), 11, (2, 2, 1)),
     "15/14"),
    ("family_5x4__13__1114", family_instance((5, 5, 5, 5), 13, (1, 1, 1, 4)),
     "13/5"),
)


def best_family_margin(values, x, z, root, gainers, outsiders):
    """Maximize mu*A + slack - L_a over admissible PXC59 families."""
    n = len(x)
    g = len(gainers)
    total = sum(x, F(0))
    mu = F((g - 1) * n, g * (n - g))
    slack = (F(n, g * (n - g)) - F(n, (n * n) // 4)) * total
    z_top = max(z[a] for a in gainers)
    rows = {a: [] for a in gainers}
    for size in range(0, len(outsiders) + 1):
        for K in itertools.combinations(outsiders, size):
            for a in gainers:
                coalition = 1 << root
                for b in gainers:
                    if b != a:
                        coalition |= 1 << b
                for j in K:
                    coalition |= 1 << j
                if coalition_sum(x, coalition) != values[coalition]:
                    continue
                z_tight = coalition_sum(z, coalition) == values[coalition]
                rows[a].append((K, z_tight))
    if any(not rows[a] for a in gainers):
        return None
    best = None
    for a_star in gainers:
        if z[a_star] != z_top or z[root] < z[a_star]:
            continue
        for K_star, z_tight in rows[a_star]:
            if not z_tight:
                continue
            loss = sum((x[j] - z[j] for j in K_star), F(0))
            others = [a for a in gainers if a != a_star]
            for combo in itertools.product(*(rows[a] for a in others)):
                load = {}
                for j in K_star:
                    load[j] = load.get(j, 0) + 1
                feasible = True
                for K, _ in combo:
                    for j in K:
                        load[j] = load.get(j, 0) + 1
                        if load[j] > g - 1:
                            feasible = False
                if not feasible:
                    continue
                decoration = F(1, g - 1) * (
                    sum((x[j] for j in K_star), F(0))
                    + sum(
                        (x[j] for K, _ in combo for j in K), F(0)
                    )
                )
                value = mu * decoration + slack - loss
                if best is None or value > best:
                    best = value
    return best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for name, generators, expected in CONTROLS:
        generators = tuple(
            tuple(F(value) for value in generator) for generator in generators
        )
        n = len(generators[0])
        values = lower_envelope(generators)
        x, z = selectors(values, n)
        roots = ordered_saturated_roots(values, x, z)
        if len(roots) != 1:
            raise AssertionError(f"control {name} lost its unique root")
        root, gainers, outsiders, _decoration = roots[0]
        packet = margins(values, x, z)["packet_margin"]
        if packet >= 0:
            raise AssertionError(f"control {name} is no longer a violation")
        best = best_family_margin(values, x, z, root, gainers, outsiders)
        observed = None if best is None else str(best)
        if observed != expected:
            raise AssertionError(
                f"control {name} drifted: {observed!r} != {expected!r}"
            )
        if best is not None and best < 0:
            raise AssertionError(f"control {name} not closed by chosen family")
        rows.append(
            {
                "name": name,
                "packet_margin": str(packet),
                "chosen_family_margin": observed,
            }
        )

    summary = {
        "controls": len(rows),
        "chosen_family_closures": sum(
            row["chosen_family_margin"] is not None for row in rows
        ),
        "inapplicable": [
            row["name"] for row in rows if row["chosen_family_margin"] is None
        ],
        "minimum_closure_margin": str(
            min(
                F(row["chosen_family_margin"])
                for row in rows
                if row["chosen_family_margin"] is not None
            )
        ),
    }
    expected_summary = {
        "controls": 7,
        "chosen_family_closures": 6,
        "inapplicable": ["clean_control"],
        "minimum_closure_margin": "29/30",
    }
    for key, value in expected_summary.items():
        if summary[key] != value:
            raise AssertionError(
                f"summary[{key!r}] = {summary[key]!r} != {value!r}"
            )

    payload = {
        "claim": (
            "chosen-family PXC59 closes every named uniform packet violation; "
            "only the split-top clean control leaves its hypotheses"
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
