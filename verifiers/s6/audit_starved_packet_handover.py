#!/usr/bin/env python3
"""Discover one-sided staged-packet handovers on starved-only refinements."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_equality_refinement_neighborhood import COARSE_TYPES, refines  # noqa: E402
from audit_starved_refinement_direction import coarse_roles  # noqa: E402
from core_closure_pipeline import pipeline2_generator_normal_form  # noqa: E402
from diagnose_refinement_unsat_groups import semantic_group  # noqa: E402


def one_sided(configuration, retained):
    r = tuple(configuration[0])
    c = tuple(configuration[1])
    table = tuple(tuple(row) for row in configuration[2])
    data = pipeline2_generator_normal_form(6, r, c, table, F(2, 3), fail=True)
    original = tuple(data["solver"].assertions())
    solver = z3.Solver()
    for position, assertion in enumerate(original):
        group = semantic_group(assertion, position, len(original))
        if retained == "min" and (
            group.startswith("ceiling_") or group == "lmax_support_eligibility"
        ):
            continue
        if retained == "max" and (
            group.startswith("floor_") or group == "lmin_support_eligibility"
        ):
            continue
        solver.add(assertion)
    _, roles = coarse_roles(configuration, COARSE_TYPES[0])
    x, z = data["lmin"], data["lmax"]
    for player, role in enumerate(roles):
        solver.add(x[player] > z[player] if role in ("N", "R") else z[player] > x[player])
    return solver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    survivors = json.loads(args.triage.read_text())["survivors"]
    starved, positive = COARSE_TYPES
    indices = [
        index
        for index, configuration in enumerate(survivors)
        if refines(*configuration, starved) and not refines(*configuration, positive)
    ]
    assert len(indices) == 504
    stop = len(indices) if args.stop is None else args.stop
    rows = []
    for position in range(args.start, stop):
        index = indices[position]
        verdicts = {}
        for retained in ("min", "max"):
            solver = one_sided(survivors[index], retained)
            solver.set(timeout=args.timeout_ms)
            verdicts[retained] = str(solver.check())
        rows.append({"position": position, "survivor_index": index, **verdicts})
    payload = {
        "schema": "starved-one-sided-packet-handover-shard-v1",
        "scope": "exact QF_LRA discovery audit; not proof objects",
        "start": args.start,
        "stop": stop,
        "total": len(indices),
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"start": args.start, "stop": stop, "counts": {side: {verdict: sum(row[side] == verdict for row in rows) for verdict in sorted({row[side] for row in rows})} for side in ("min", "max")}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
