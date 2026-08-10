#!/usr/bin/env python3
"""Audit an anchor-localized one-witness core for the (4,2,0) strict case.

The two cross-selection anchors select an x-bottom player a in P and a z-top
player b in P.  If a=b, the sign pattern is immediately contradictory.  If
a!=b, relabel a=0 and b=1.  The residual S_{2} x S_{2} symmetry acts on the
remaining P-players {2,3} and on M={4,5}.  This script freezes ten residual
direction orbits (nineteen labelled implications) and weakens every blocker
alternative to the opposite-selection comparison plus the single q^b
comparison.

UNSAT cores were discovery aids only.  The final formula is rebuilt without
guards, checked UNSAT, and subjected to direction-, orbit-, and source-level
SAT ablations.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_strict_exchange_large_case_orbit_cores import (  # noqa: E402
    SELECTED,
    build_reduced,
    role_signature,
)
from export_core_closure_smt import qf_lra_smt2  # noqa: E402


CASE = "p4_n2_t0"
ANCHOR_BOTTOM = 0
ANCHOR_TOP = 1
BLOCKER_SOURCES = (0, 2)  # opposite selection and q^1

# Residual orbits under swaps 2<->3 and 4<->5, after fixing a=0 and b=1.
RESIDUAL_ORBITS = (
    ("max", (0, -1, 0, 1, 0, 0)),
    ("max", (0, -1, 1, 1, -1, 0)),
    ("max", (1, -1, 0, 0, 0, 0)),
    ("max", (1, -1, 0, 1, -1, 0)),
    ("max", (1, 0, 0, 1, -1, -1)),
    ("min", (0, -1, -1, 0, 1, 1)),
    ("min", (0, -1, 0, 0, 0, 1)),
    ("min", (0, -1, 0, 1, 0, 0)),
    ("min", (0, 0, -1, -1, 1, 1)),
    ("min", (1, -1, 0, 0, 0, 0)),
)


def residual_signature(side, direction):
    images = []
    for swap_p, swap_m in product((False, True), repeat=2):
        permutation = list(range(6))
        if swap_p:
            permutation[2], permutation[3] = permutation[3], permutation[2]
        if swap_m:
            permutation[4], permutation[5] = permutation[5], permutation[4]
        images.append(tuple(direction[permutation[index]] for index in range(6)))
    return side, min(images)


def source_row():
    cores = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    orbit_audit = json.loads((HERE / "strict_exchange_sign_orbits.json").read_text())
    orbit_counts = {
        row["case"]: row["sign_preserving_orbit_count"] for row in orbit_audit["rows"]
    }
    row = next(row for row in cores["rows"] if row["case"] == CASE)
    return dict(row, sign_preserving_orbit_count=orbit_counts[CASE])


def canonical_constraints():
    x = [z3.Real(f"equality_exchange_x_{index}") for index in range(6)]
    z = [z3.Real(f"equality_exchange_z_{index}") for index in range(6)]
    return [
        *(x[ANCHOR_BOTTOM] <= x[index] for index in range(1, 6)),
        *(z[ANCHOR_TOP] >= z[index] for index in (0, 2, 3, 4, 5)),
    ]


def selected_implications(row, sources=BLOCKER_SOURCES):
    solver, groups = build_reduced(row, SELECTED[CASE], sources)
    assertions = list(solver.assertions())
    if len(assertions) != 71 + 68:
        raise AssertionError("unexpected reduced p4 assertion layout")

    # Keep the x/z block a0-a20 and only q^1's eight base assertions.  The two
    # cross-anchor disjunctions are replaced by the canonical extreme roles;
    # all other witness blocks are disconnected after the source weakening.
    base = assertions[:21] + assertions[31:39]
    if len(base) != 29:
        raise AssertionError("unexpected localized base size")

    chosen = []
    metadata = []
    for parent_signature in SELECTED[CASE]:
        menu = [
            item
            for item in row["retained_menu"]
            if role_signature(item, 4, 2) == parent_signature
        ]
        if len(menu) != len(groups[parent_signature]):
            raise AssertionError("menu/group alignment changed")
        parent_name = f"C{SELECTED[CASE].index(parent_signature) + 1}"
        for item, assertion in zip(menu, groups[parent_signature], strict=True):
            residual = residual_signature(item["side"], item["direction"])
            if residual not in RESIDUAL_ORBITS:
                continue
            chosen.append(assertion)
            metadata.append(
                {
                    "side": item["side"],
                    "direction": list(item["direction"]),
                    "parent_schema": parent_name,
                    "residual_orbit": RESIDUAL_ORBITS.index(residual) + 1,
                }
            )
    if len(chosen) != 19:
        raise AssertionError(f"expected 19 labelled directions, got {len(chosen)}")
    counts = Counter(item["residual_orbit"] for item in metadata)
    if set(counts) != set(range(1, 11)):
        raise AssertionError("the selected directions do not cover all ten residual orbits")
    return base, canonical_constraints(), chosen, metadata


def make_solver(base, canonical, implications, timeout_ms=0):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(*base, *canonical, *implications)
    return solver


def verdict(base, canonical, implications, timeout_ms):
    return make_solver(base, canonical, implications, timeout_ms).check()


def same_anchor_contradiction(timeout_ms):
    x = [z3.Real(f"same_anchor_x_{index}") for index in range(6)]
    z = [z3.Real(f"same_anchor_z_{index}") for index in range(6)]
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    # For m=4 in M: x_m >= x_a > z_a >= z_m > x_m.
    solver.add(x[4] >= x[0], x[0] > z[0], z[0] >= z[4], z[4] > x[4])
    return solver.check()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--formula", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    args = parser.parse_args()

    row = source_row()
    base, canonical, implications, metadata = selected_implications(row)
    if same_anchor_contradiction(args.timeout_ms) != z3.unsat:
        raise AssertionError("same-anchor four-inequality chain did not close")
    if verdict(base, canonical, [], args.timeout_ms) != z3.sat:
        raise AssertionError("distinct-anchor base is not SAT")
    full = make_solver(base, canonical, implications, args.timeout_ms)
    if full.check() != z3.unsat:
        raise AssertionError("distinct-anchor one-witness core is not UNSAT")

    direction_ablations = []
    for index, item in enumerate(metadata):
        trial = implications[:index] + implications[index + 1 :]
        trial_verdict = verdict(base, canonical, trial, args.timeout_ms)
        if trial_verdict != z3.sat:
            raise AssertionError(f"direction ablation {index} is {trial_verdict}")
        direction_ablations.append({**item, "verdict": "sat"})

    orbit_ablations = []
    for orbit_index in range(1, 11):
        trial = [
            assertion
            for assertion, item in zip(implications, metadata, strict=True)
            if item["residual_orbit"] != orbit_index
        ]
        trial_verdict = verdict(base, canonical, trial, args.timeout_ms)
        if trial_verdict != z3.sat:
            raise AssertionError(f"residual orbit {orbit_index} ablation is {trial_verdict}")
        representative = RESIDUAL_ORBITS[orbit_index - 1]
        orbit_ablations.append(
            {
                "removed": orbit_index,
                "side": representative[0],
                "canonical_direction": list(representative[1]),
                "verdict": "sat",
            }
        )

    source_ablations = []
    for removed, name in ((0, "opposite"), (2, "q1")):
        sources = tuple(source for source in BLOCKER_SOURCES if source != removed)
        trial_base, trial_canonical, trial, _ = selected_implications(row, sources)
        trial_verdict = verdict(trial_base, trial_canonical, trial, args.timeout_ms)
        if trial_verdict != z3.sat:
            raise AssertionError(f"source ablation {name} is {trial_verdict}")
        source_ablations.append({"removed": name, "verdict": "sat"})

    if args.formula:
        args.formula.parent.mkdir(parents=True, exist_ok=True)
        args.formula.write_text(qf_lra_smt2(full))

    orbit_rows = []
    for index, (side, direction) in enumerate(RESIDUAL_ORBITS, start=1):
        items = [item for item in metadata if item["residual_orbit"] == index]
        orbit_rows.append(
            {
                "orbit": index,
                "side": side,
                "canonical_direction": list(direction),
                "labelled_direction_count": len(items),
                "parent_schemas": sorted({item["parent_schema"] for item in items}),
            }
        )

    payload = {
        "schema": "strict-exchange-p4-anchor-core-v1",
        "status": "PASS",
        "scope": (
            "anchor-localized one-witness relaxation; UNSAT is a proof reduction, "
            "SAT ablations are irredundancy controls"
        ),
        "case": CASE,
        "anchor_roles": {
            "x_bottom": ANCHOR_BOTTOM,
            "z_top": ANCHOR_TOP,
            "same_player_branch": "contradiction by x_m>=x_a>z_a>=z_m>x_m",
            "same_player_four_inequality_verdict": "unsat",
        },
        "declared_real_count": 18,
        "base_assertion_count": len(base) + len(canonical),
        "blocker_comparison_sources": ["opposite", "q1"],
        "base_without_exchange_verdict": "sat",
        "unguarded_rebuild_verdict": "unsat",
        "selected_labeled_direction_count": len(implications),
        "selected_residual_orbit_count": len(orbit_rows),
        "residual_orbits": orbit_rows,
        "single_direction_ablations": direction_ablations,
        "single_residual_orbit_ablations": orbit_ablations,
        "single_blocker_source_ablations": source_ablations,
        "formula": args.formula.name if args.formula else None,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
