#!/usr/bin/env python3
r"""Exact controls for split-top spectral structure (PXC77).

The one audited violation class outside the two-stratum theorem has a
split top: the heavy gainer joins the root at the Lmax ceiling, the
remaining gainers form a sub-top stratum, and the Lmax-tight menu is
built from double co-stars containing the root, the heavy gainer, all
sub-top gainers but one, and one outsider.  On this class the canonical
over-cover concentrates its largest weight on the heavy gainer rather
than the root, both spectral currencies vanish, so the sharpened bound
equals the actual-top bound, and the bound is exactly tight at the
canonical control.  This driver enumerates the split family
`a=(2a',a',a')` with a root-heavy second generator on a fixed grid,
checks the structural hypotheses instance by instance, and pins the
closures; the canonical clean control is replayed with its exact
dispersion, over-cover weights, and tight spectral value.  These are
exact finite structure facts, not a split-top closure theorem; the
general theorem must be sharp, since the bound is tight at the control.
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
from audit_lmax_overcover import top_certificate  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from audit_spectral_or_reserve import margins, selectors  # noqa: E402


def split_instance(heavy, light, count_light, H, w):
    a = (heavy,) + (light,) * count_light
    g = len(a)
    k = len(w)
    generator_one = tuple([F(0)] + [F(q) for q in a] + [F(0)] * k)
    generator_two = tuple([F(H)] + [F(0)] * g + [F(q) for q in w])
    if sum(generator_one, F(0)) != sum(generator_two, F(0)):
        return None
    return (generator_one, generator_two)


def audit_instance(generators):
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    if x == z:
        return None
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        return None
    root, gainers, outsiders, _decoration = roots[0]
    ceiling = max(z)
    top_gainers = tuple(a for a in gainers if z[a] == ceiling)
    sub_gainers = tuple(a for a in gainers if z[a] < ceiling)
    if z[root] != ceiling or not top_gainers or not sub_gainers:
        return None
    sub_values = {z[a] for a in sub_gainers}
    if len(sub_values) != 1:
        return None
    sub_level = sub_values.pop()
    if not all(z[j] < sub_level for j in outsiders):
        return None
    # double co-stars: root + all top gainers + all sub gainers but one +
    # one outsider, all Lmax-tight
    fed = True
    for omitted in sub_gainers:
        for outsider in outsiders:
            coalition = (1 << root) | (1 << outsider)
            for a in top_gainers:
                coalition |= 1 << a
            for a in sub_gainers:
                if a != omitted:
                    coalition |= 1 << a
            if coalition_sum(z, coalition) != values[coalition]:
                fed = False
    cert = top_certificate(values, z)
    theta = F(cert["theta"])
    alpha = [F(value) for value in cert["alpha"]]
    heavy_weighted = all(
        alpha[a] >= alpha[root] for a in top_gainers
    )
    spec = spectral_decomposition("t", values, x, z)
    total = sum(x, F(0))
    bound = F(spec["sharpened_spectral_bound_ratio"]) * total
    target = F(spec["target_ratio"]) * total
    currencies_zero = (
        F(spec["top_selection_currency_ratio"]) == 0
        and F(spec["label_currency_ratio"]) == 0
    )
    packet = margins(values, x, z)["packet_margin"]
    overlap = sum(min(a, b) for a, b in zip(x, z))
    return {
        "generators": [
            [str(value) for value in generator] for generator in generators
        ],
        "n": n,
        "root": root,
        "top_gainers": list(top_gainers),
        "sub_gainers": list(sub_gainers),
        "double_costars_fed": fed,
        "theta": str(theta),
        "heavy_weighted": heavy_weighted,
        "currencies_zero": currencies_zero,
        "bound": str(bound),
        "target": str(target),
        "bound_closes": bound >= target,
        "bound_tight": bound == overlap,
        "packet_margin": str(packet),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for light in range(2, 6):
        heavy = 2 * light
        for count_light in (2,):
            total = heavy + count_light * light
            for k in (2, 3):
                for H in range(2, total - k + 1):
                    rest = total - H
                    for w in itertools.combinations_with_replacement(
                        range(1, rest + 1), k
                    ):
                        if sum(w) != rest:
                            continue
                        generators = split_instance(
                            heavy, light, count_light, H,
                            tuple(sorted(w, reverse=True)),
                        )
                        if generators is None:
                            continue
                        row = audit_instance(generators)
                        if row is not None:
                            rows.append(row)

    canonical = audit_instance(split_instance(6, 3, 2, 8, (2, 1, 1)))
    if canonical is None:
        raise AssertionError("canonical split-top control left the class")
    expected_canonical = {
        "theta": "4/7",
        "heavy_weighted": True,
        "currencies_zero": True,
        "double_costars_fed": True,
        "bound": "9",
        "target": "7",
        "bound_closes": True,
        "bound_tight": True,
        "packet_margin": "-5/7",
    }
    for key, value in expected_canonical.items():
        if canonical[key] != value:
            raise AssertionError(
                f"canonical[{key!r}] = {canonical[key]!r} != {value!r}"
            )

    summary = {
        "grid_split_top_instances": len(rows),
        "grid_double_costars_fed": sum(row["double_costars_fed"] for row in rows),
        "grid_heavy_weighted": sum(row["heavy_weighted"] for row in rows),
        "grid_currencies_zero": sum(row["currencies_zero"] for row in rows),
        "grid_bound_closes": sum(row["bound_closes"] for row in rows),
        "grid_bound_tight": sum(row["bound_tight"] for row in rows),
        "grid_packet_violations": sum(
            F(row["packet_margin"]) < 0 for row in rows
        ),
    }
    expected = {
        "grid_split_top_instances": 31,
        "grid_double_costars_fed": 11,
        "grid_heavy_weighted": 22,
        "grid_currencies_zero": 14,
        "grid_bound_closes": 31,
        "grid_bound_tight": 14,
        "grid_packet_violations": 2,
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(
                f"summary[{key!r}] = {summary[key]!r} != {value!r}"
            )

    payload = {
        "claim": (
            "split-top roots carry heavy-gainer-weighted over-covers with "
            "vanishing spectral currencies; the sharpened bound closes and "
            "is exactly tight at the canonical control"
        ),
        "summary": summary,
        "canonical": canonical,
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
