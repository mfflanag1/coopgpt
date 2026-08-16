#!/usr/bin/env python3
"""Classify every archived search packet violation by (top_uniform, fed).

Reads the finding lines of the archived search logs, recomputes exact
selectors for each distinct generator set, and reports how the packet
violations split against the (PXC75) hypotheses.  Output on 2026-08-16:

    violation classes (top_uniform, fed) -> count: {(False, False): 8,
                                                    (True, True): 2}
    archived violation generator sets: 10

Together with the sixteen audited grid violations (top-uniform and fed by
construction), top-uniformity and co-star feeding coincide on every
audited packet violation; no mixed class occurs.
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
COOPGAMES = HERE.parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors, margins  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402


def main():
    generator_sets = set()
    for log in ("ds_pxc63b.log", "ds_combined.log", "ds_pxc76.log",
                "ds_n8.log"):
        for line in open(HERE / log):
            if '"kind"' not in line:
                continue
            row = json.loads(line)
            if row.get("kind") not in (
                "pxc63b_violation", "combined_failure", "combined_or_uncovered"
            ):
                continue
            generator_sets.add(
                tuple(
                    tuple(int(F(q)) for q in generator)
                    for generator in row["generators"]
                )
            )
    classes = {}
    for generators in sorted(generator_sets):
        n = len(generators[0])
        values = lower_envelope(
            tuple(tuple(F(q) for q in g) for g in generators)
        )
        x, z = selectors(values, n)
        for root, gainers, outsiders, _dec in ordered_saturated_roots(
            values, x, z
        ):
            if margins(values, x, z)["packet_margin"] >= 0:
                continue
            ceiling = max(z)
            top_uniform = (
                z[root] == ceiling
                and all(z[a] == ceiling for a in gainers)
                and all(z[j] < ceiling for j in outsiders)
            )
            fed = True
            for a in gainers:
                for j in outsiders:
                    coalition = (1 << root) | (1 << j)
                    for b in gainers:
                        if b != a:
                            coalition |= 1 << b
                    if coalition_sum(z, coalition) != values[coalition]:
                        fed = False
            classes[(top_uniform, fed)] = classes.get(
                (top_uniform, fed), 0
            ) + 1
    print("violation classes (top_uniform, fed) -> count:", classes)
    print("archived violation generator sets:", len(generator_sets))


if __name__ == "__main__":
    main()
