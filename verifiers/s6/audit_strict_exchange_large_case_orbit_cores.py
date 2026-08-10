#!/usr/bin/env python3
"""Freeze small sign-role-orbit cores for the three large strict cases.

The published strict formulas retain 52, 71, and 90 labelled direction
implications.  This audit groups those implications under relabellings inside
P={x>z}, M={z>x}, and E={x=z}, then checks fixed small orbit selections.  An
orbit means that every labelled direction in that orbit remains present; it
is one human lemma schema, not one representative assertion.

The selected orbit sets were discovered with assumption-literal UNSAT cores.
This script does not trust those cores: it rebuilds each selected formula
without guards, checks UNSAT, and checks that deleting any selected orbit makes
the formula SAT.  The resulting QF_LRA formulas may be exported for independent
proof checking.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from export_core_closure_smt import qf_lra_smt2  # noqa: E402
from minimize_equality_exchange_directions import rebuilt_solver_from_row  # noqa: E402


def orbit(side, positive, negative, tied=()):
    return side, tuple(positive), tuple(negative), tuple(tied)


SELECTED = {
    "p3_n2_t1": (
        orbit("min", (0, 0, 0), (0, 1), (-1,)),
        orbit("max", (-1, 0, 0), (0, 0), (1,)),
        orbit("min", (-1, 0, 0), (0, 1), (0,)),
        orbit("max", (0, 0, 1), (-1, -1), (1,)),
        orbit("min", (-1, 0, 0), (0, 0), (1,)),
        orbit("max", (0, 1, 1), (-1, 0), (-1,)),
        orbit("max", (0, 1, 1), (-1, -1), (0,)),
        orbit("min", (-1, -1, 0), (1, 1), (0,)),
    ),
    "p3_n3_t0": (
        orbit("min", (-1, 0, 0), (0, 0, 1)),
        orbit("min", (-1, -1, 0), (0, 1, 1)),
        orbit("max", (0, 0, 1), (-1, 0, 0)),
        orbit("max", (0, 1, 2), (-1, -1, -1)),
        orbit("min", (-2, -1, 0), (1, 1, 1)),
    ),
    "p4_n2_t0": (
        orbit("min", (-1, 0, 0, 0), (0, 1)),
        orbit("max", (-1, 0, 1, 1), (-1, 0)),
        orbit("max", (-1, 0, 0, 1), (0, 0)),
        orbit("max", (0, 0, 1, 1), (-1, -1)),
        orbit("min", (-1, 0, 0, 1), (0, 0)),
        orbit("min", (-1, -1, 0, 0), (1, 1)),
    ),
}


def role_signature(item, positive_count, negative_count):
    direction = item["direction"]
    return orbit(
        item["side"],
        sorted(direction[:positive_count]),
        sorted(direction[positive_count : positive_count + negative_count]),
        sorted(direction[positive_count + negative_count :]),
    )


def rendered_signature(signature):
    side, positive, negative, tied = signature
    return {
        "side": side,
        "P": list(positive),
        "M": list(negative),
        "E": list(tied),
    }


def build_reduced(row, selected):
    source = rebuilt_solver_from_row(row)
    assertions = list(source.assertions())
    if len(assertions) != 72 + row["retained_direction_count"]:
        raise AssertionError(f"unexpected assertion layout for {row['case']}")
    # The large-case orbit cores do not need the no-unique-Lmax-top anchor at
    # source assertion 21.  Retain the two cross-selection anchors 22 and 23.
    base = assertions[:21] + assertions[22:72]
    directional = assertions[72:]
    groups = {}
    for item, assertion in zip(row["retained_menu"], directional, strict=True):
        signature = role_signature(item, row["positive_count"], row["negative_count"])
        groups.setdefault(signature, []).append(assertion)
    if len(groups) != row["sign_preserving_orbit_count"]:
        raise AssertionError(f"orbit count changed for {row['case']}")
    missing = set(selected) - set(groups)
    if missing:
        raise AssertionError(f"missing selected orbits for {row['case']}: {missing}")
    solver = z3.Solver()
    solver.add(*base)
    for signature in selected:
        solver.add(*groups[signature])
    return solver, groups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--formula-dir", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    args = parser.parse_args()
    cores = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    orbit_audit = json.loads((HERE / "strict_exchange_sign_orbits.json").read_text())
    orbit_counts = {row["case"]: row["sign_preserving_orbit_count"] for row in orbit_audit["rows"]}
    rows = []
    if args.formula_dir:
        args.formula_dir.mkdir(parents=True, exist_ok=True)
    for row in cores["rows"]:
        case = row["case"]
        if case not in SELECTED:
            continue
        enriched = dict(row)
        enriched["sign_preserving_orbit_count"] = orbit_counts[case]
        selected = SELECTED[case]
        solver, groups = build_reduced(enriched, selected)
        solver.set(timeout=args.timeout_ms)
        verdict = solver.check()
        if verdict != z3.unsat:
            raise AssertionError(f"reduced {case} is {verdict}")
        reduced_assertions = list(solver.assertions())
        anchor_ablations = []
        for anchor, index in (("lmax_top_cross", 21), ("lmin_bottom_cross", 22)):
            trial = z3.Solver()
            trial.set(timeout=args.timeout_ms)
            trial.add(*(item for offset, item in enumerate(reduced_assertions) if offset != index))
            trial_verdict = trial.check()
            if trial_verdict != z3.sat:
                raise AssertionError(f"{case} {anchor} ablation is {trial_verdict}")
            anchor_ablations.append({"removed": anchor, "verdict": "sat"})
        ablations = []
        for removed in selected:
            trial, _ = build_reduced(enriched, tuple(item for item in selected if item != removed))
            trial.set(timeout=args.timeout_ms)
            trial_verdict = trial.check()
            if trial_verdict != z3.sat:
                raise AssertionError(f"{case} ablation is {trial_verdict}: {removed}")
            ablations.append({"removed": rendered_signature(removed), "verdict": "sat"})
        selected_directions = sum(len(groups[item]) for item in selected)
        shapes = sorted(
            {
                tuple(sorted(menu_item["direction"]))
                for menu_item in row["retained_menu"]
                if role_signature(menu_item, row["positive_count"], row["negative_count"])
                in selected
            }
        )
        formula_name = f"strict_exchange_orbit_core_{case}.smt2"
        if args.formula_dir:
            (args.formula_dir / formula_name).write_text(qf_lra_smt2(solver))
        rows.append(
            {
                "case": case,
                "original_labeled_direction_count": row["retained_direction_count"],
                "original_role_orbit_count": len(groups),
                "selected_labeled_direction_count": selected_directions,
                "selected_role_orbit_count": len(selected),
                "selected_oriented_coefficient_multisets": [list(shape) for shape in shapes],
                "selected_orbits": [rendered_signature(item) for item in selected],
                "unguarded_rebuild_verdict": "unsat",
                "single_orbit_ablations": ablations,
                "single_cross_anchor_ablations": anchor_ablations,
                "formula": formula_name,
            }
        )
    if len(rows) != 3:
        raise AssertionError("expected the three large strict cases")
    payload = {
        "schema": "strict-exchange-large-case-orbit-cores-v1",
        "status": "PASS",
        "scope": (
            "unguarded reduced formulas retaining complete sign-role orbits; "
            "UNSAT is a proof reduction, SAT ablations are irredundancy controls"
        ),
        "base_assertion_count_per_case": 71,
        "original_labeled_direction_count": sum(row["original_labeled_direction_count"] for row in rows),
        "selected_labeled_direction_count": sum(row["selected_labeled_direction_count"] for row in rows),
        "original_role_orbit_count": sum(row["original_role_orbit_count"] for row in rows),
        "selected_role_orbit_count": sum(row["selected_role_orbit_count"] for row in rows),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
