#!/usr/bin/env python3
"""Exact finite probe of a five-player PXC98-style forced-zero template.

The labelled roles are top players r=0,h=1 and outsiders a=2,b=3,j=4.
The retained certificate candidate is rha (mask 7), the unavoidable eta-zero
cover is the tight pair rh (mask 3), and the asymmetric later blocker is rj
(mask 17).  Total and displayed bounds are deliberately finite below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))

import unrestricted_pxc91c_exact_search as core  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    total = F(6)
    tested = 0
    reduced_lmin_preserving = 0
    full_lmin_preserving = 0
    selector_changing_two_top = []
    for certificate_bound in range(1, 6):
        certificate = {7: F(certificate_bound)}
        try:
            x = core.selector_from_constraints(certificate, 5, total, "min")
        except AssertionError:
            continue
        for pair_bound in range(1, 6):
            reduced = {**certificate, 3: F(pair_bound)}
            try:
                if core.selector_from_constraints(reduced, 5, total, "min") != x:
                    continue
                reduced_z = core.selector_from_constraints(reduced, 5, total, "max")
            except AssertionError:
                continue
            reduced_lmin_preserving += 1
            for blocker_bound in range(1, 6):
                tested += 1
                full = {**reduced, 17: F(blocker_bound)}
                try:
                    full_x = core.selector_from_constraints(full, 5, total, "min")
                    z = core.selector_from_constraints(full, 5, total, "max")
                except AssertionError:
                    continue
                if full_x != x:
                    continue
                full_lmin_preserving += 1
                top = tuple(i for i, q in enumerate(z) if q == max(z))
                if z != reduced_z and top == (0, 1):
                    selector_changing_two_top.append({
                        "certificate_bound": certificate_bound,
                        "pair_bound": pair_bound,
                        "blocker_bound": blocker_bound,
                        "x": list(map(str, x)), "z": list(map(str, z)),
                        "reduced_z": list(map(str, reduced_z)),
                    })
    if selector_changing_two_top:
        raise AssertionError(
            "promotion required: exact full-game/cover/Cx audit not encoded in this probe"
        )
    payload = {
        "claim": "finite exact PXC98-style n=5 forced-zero template probe",
        "roles": {"r": 0, "h": 1, "a": 2, "b": 3, "j": 4},
        "cell": {
            "total": "6", "certificate_row": 7, "top_pair_row": 3,
            "later_blocker_row": 17,
            "integer_bounds_each": [1, 2, 3, 4, 5],
        },
        "tested_full_cells": tested,
        "reduced_lmin_preserving_cells": reduced_lmin_preserving,
        "full_lmin_preserving_cells": full_lmin_preserving,
        "selector_changing_two_top_survivor_count": 0,
        "survivors": [],
        "provenance": {
            "driver": str(HERE.relative_to(ROOT)),
            "driver_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(),
            "core_driver_sha256": hashlib.sha256(
                (HERE.parent / "unrestricted_pxc91c_exact_search.py").read_bytes()
            ).hexdigest(),
            "exactlp_sha256": hashlib.sha256(
                (ROOT / "src/exactlp.py").read_bytes()
            ).hexdigest(),
            "replay_command": (
                "python3 verifiers/divergence/search_archive/"
                "unrestricted_pxc91c_n5_forced_zero_search.py --output "
                "verifiers/divergence/search_archive/"
                "unrestricted_pxc91c_n5_forced_zero_search.json"
            ),
            "completed": True,
        },
        "scope": ("Exact exhaustion only of the labelled three-row, total-six, integer-bound "
                  "template stated above. It does not cover other certificate supports, "
                  "additional closing rows, rational bounds, totals, permutations, or the "
                  "general five-player problem."),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
