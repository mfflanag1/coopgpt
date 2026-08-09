#!/usr/bin/env python3
"""Group-minimize immediate-refinement UNSAT formulas for proof discovery.

The output is a navigation aid only.  An UNSAT core is not treated as proof
evidence anywhere in the paper or checkpoint verifier.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core_closure_pipeline import pipeline2_generator_normal_form  # noqa: E402


def semantic_group(assertion, index, total):
    if index == total - 1:
        return "strict_distance"
    text = assertion.sexpr()
    for tag in ("floor", "ceiling"):
        match = re.search(
            rf"{tag}_(?:weight|efficiency|old_pin|level_side)_([0-9]+)_([0-9]+)",
            text,
        )
        if match:
            return f"{tag}_stage{match.group(1)}_player{match.group(2)}"
    if "tight_x_" in text:
        return "lmin_support_eligibility"
    if "tight_z_" in text:
        return "lmax_support_eligibility"
    match = re.search(r"singleton_witness_([0-9]+)_", text)
    if match:
        return f"singleton_witness_{match.group(1)}"
    return "level_order_and_totals"


def minimized_group_core(data, timeout):
    assertions = tuple(data["solver"].assertions())
    groups = defaultdict(list)
    for index, assertion in enumerate(assertions):
        groups[semantic_group(assertion, index, len(assertions))].append(assertion)

    solver = z3.Solver()
    solver.set(timeout=timeout * 1000, unsat_core=True)
    tags = {}
    for number, (name, premises) in enumerate(sorted(groups.items())):
        tag = z3.Bool(f"group_{number}")
        tags[tag] = name
        solver.add(z3.Implies(tag, z3.And(premises)))
    verdict = solver.check(*tags)
    if verdict != z3.unsat:
        return str(verdict), (), {name: len(rows) for name, rows in groups.items()}
    core = list(solver.unsat_core())
    changed = True
    while changed:
        changed = False
        for tag in tuple(core):
            trial = [other for other in core if other is not tag]
            if solver.check(*trial) == z3.unsat:
                core = trial
                changed = True
    return "unsat", tuple(sorted(tags[tag] for tag in core)), {
        name: len(rows) for name, rows in groups.items()
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--refinements",
        type=Path,
        default=HERE / "equality_refinement_neighborhood_audit.json",
    )
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    args = parser.parse_args()

    indices = json.loads(args.refinements.read_text())[
        "immediate_union_survivor_indices"
    ]
    survivors = json.loads(args.triage.read_text())["survivors"]
    rows = []
    for index in indices:
        r, c, table = survivors[index]
        data = pipeline2_generator_normal_form(
            6, tuple(r), tuple(c), table, F(2, 3), fail=True
        )
        verdict, core, group_sizes = minimized_group_core(data, args.timeout)
        rows.append(
            {
                "index": index,
                "lmin": r,
                "lmax": c,
                "table": table,
                "result": verdict,
                "minimized_semantic_core": core,
                "group_sizes": group_sizes,
            }
        )
        if args.output:
            args.output.write_text(
                json.dumps(
                    {
                        "status": "proof-discovery navigation only; not proof evidence",
                        "rows": rows,
                    },
                    indent=2,
                )
                + "\n"
            )
        print(index, verdict, core, flush=True)


if __name__ == "__main__":
    main()
