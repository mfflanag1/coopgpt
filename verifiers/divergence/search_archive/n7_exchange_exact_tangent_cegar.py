#!/usr/bin/env python3
"""Exact lower-envelope tangent CEGAR for one n=7 overlap sign cell.

The outer QF_LRA model supplies x, z, and seven singleton-zero witnesses.
Their lower envelope is an exact singleton-normalized game.  Exact rational
PXC92b tangent LPs either certify both proposed selectors or return a missing
weighted staged direction, which is fed back as a necessary blocker formula.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path

import z3


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve().parent
RELAX = load("n7_relax", HERE / "n7_exchange_relaxation_scratch.py")
SEPARATE = load("n7_separate", HERE / "n7_exchange_tangent_separator.py")


def rational(model, value):
    rendered = model.eval(value, model_completion=True)
    if not z3.is_rational_value(rendered):
        raise TypeError(rendered)
    return F(rendered.as_fraction())


def write_checkpoint(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-menu", type=Path, required=True)
    parser.add_argument("--resume-cegar", type=Path, action="append", default=[])
    parser.add_argument("--rounds", type=int, default=40)
    parser.add_argument("--timeout-ms", type=int, default=600_000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--extra-direction", action="append", default=[])
    args = parser.parse_args()

    solver, x, z, witnesses, base_directions, ties, atoms = RELAX.build(
        3, 4, 1, 2, args.timeout_ms
    )
    prior = json.loads(args.seed_menu.read_text())
    menu = [
        (item["side"], tuple(item["direction"]))
        for item in prior["rows"][0].get("active_extra_menu", [])
    ]
    for rendered in args.extra_direction:
        side, values = rendered.split(":", 1)
        menu.append((side, tuple(int(value) for value in values.split(","))))
    for resume_path in args.resume_cegar:
        old = json.loads(resume_path.read_text())
        for old_round in old.get("rounds", []):
            for item in old_round.get("additions", []):
                menu.append((item["side"], tuple(item["direction"])))
    menu = list(dict.fromkeys(menu))

    def add(side, direction):
        point = x if side == "min" else z
        solver.add(
            z3.Implies(
                RELAX.lex_improves(point, direction, side),
                RELAX.blocker_formula(atoms[side], direction),
            )
        )

    for item in menu:
        add(*item)

    payload = {
        "schema": "n7-exact-lower-envelope-tangent-cegar-scratch-v1",
        "scope": "p3/n4/no-tie necessary-system cell; SAT terminal is an exact game only after both tangent separators return none",
        "seed_menu": str(args.seed_menu),
        "resumed_from": [str(path) for path in args.resume_cegar],
        "initial_weighted_menu_size": len(menu),
        "base_direction_count_per_side": len(base_directions),
        "rounds": [],
        "terminal": None,
    }
    for round_index in range(args.rounds):
        verdict = solver.check()
        row = {
            "round": round_index,
            "verdict": str(verdict),
            "weighted_menu_size": len(menu),
        }
        if verdict == z3.unknown:
            row["reason_unknown"] = solver.reason_unknown()
            payload["rounds"].append(row)
            payload["terminal"] = "UNKNOWN"
            write_checkpoint(args.output, payload)
            print(json.dumps(row, sort_keys=True), flush=True)
            break
        if verdict == z3.unsat:
            payload["rounds"].append(row)
            payload["terminal"] = "UNSAT_CELL_CLOSED_BY_RETAINED_MENU"
            write_checkpoint(args.output, payload)
            print(json.dumps(row, sort_keys=True), flush=True)
            break
        model = solver.model()
        model_x = tuple(rational(model, value) for value in x)
        model_z = tuple(rational(model, value) for value in z)
        model_w = tuple(
            tuple(rational(model, value) for value in witness)
            for witness in witnesses
        )
        generators = (model_x, model_z) + model_w
        separated = {
            side: SEPARATE.separate(point, generators, side)
            for side, point in (("min", model_x), ("max", model_z))
        }
        row["x"] = list(map(str, model_x))
        row["z"] = list(map(str, model_z))
        row["separators"] = {
            side: (
                None
                if result["direction"] is None
                else list(result["primitive_direction"])
            )
            for side, result in separated.items()
        }
        additions = []
        for side, result in separated.items():
            if result["direction"] is None:
                continue
            item = (side, tuple(result["primitive_direction"]))
            if item not in menu:
                menu.append(item)
                add(*item)
                additions.append({"side": side, "direction": list(item[1])})
        row["additions"] = additions
        payload["rounds"].append(row)
        if not additions:
            payload["terminal"] = "EXACT_N7_COUNTEREXAMPLE"
            payload["witness"] = {
                "x": list(map(str, model_x)),
                "z": list(map(str, model_z)),
                "singleton_witnesses": [list(map(str, point)) for point in model_w],
                "distance": str(sum(abs(a - b) for a, b in zip(model_x, model_z))),
            }
            write_checkpoint(args.output, payload)
            print(json.dumps(row, sort_keys=True), flush=True)
            break
        write_checkpoint(args.output, payload)
        print(json.dumps(row, sort_keys=True), flush=True)
    else:
        payload["terminal"] = "ROUND_LIMIT"
        write_checkpoint(args.output, payload)


if __name__ == "__main__":
    main()
