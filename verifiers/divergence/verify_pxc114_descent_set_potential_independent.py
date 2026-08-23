#!/usr/bin/env python3
"""Independent SMT/combinatorial audit of the PXC114 core implication.

No game, selector, cover, or PXC implementation is imported.  Z3 checks over
the ordered real field that positive weights and nonnegative row derivatives
with zero weighted sum force every derivative to vanish.  A separate finite
set model checks that strict reverse inclusion cannot form a pure directed
cycle.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import z3


def collapse_unsat(size):
    weights = [z3.Real(f"w_{size}_{i}") for i in range(size)]
    derivatives = [z3.Real(f"g_{size}_{i}") for i in range(size)]
    solver = z3.Solver()
    solver.add(*[w > 0 for w in weights])
    solver.add(*[g >= 0 for g in derivatives])
    solver.add(sum(w * g for w, g in zip(weights, derivatives)) == 0)
    solver.add(z3.Or(*[g > 0 for g in derivatives]))
    return solver.check() == z3.unsat


def negative_control_sat(size):
    weights = [z3.Real(f"nw_{size}_{i}") for i in range(size)]
    derivatives = [z3.Real(f"ng_{size}_{i}") for i in range(size)]
    solver = z3.Solver()
    solver.add(*[w > 0 for w in weights])
    solver.add(sum(w * g for w, g in zip(weights, derivatives)) == 0)
    solver.add(z3.Or(*[g > 0 for g in derivatives]))
    solver.add(z3.Or(*[g < 0 for g in derivatives]))
    return solver.check() == z3.sat


def finite_strict_cycle_count(universe_size, length):
    subsets = [
        frozenset(i for i in range(universe_size) if mask >> i & 1)
        for mask in range(1 << universe_size)
    ]
    cycles = 0
    for chosen in itertools.product(subsets, repeat=length):
        if all(chosen[(i + 1) % length] < chosen[i] for i in range(length)):
            cycles += 1
    return cycles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    collapse = {str(size): collapse_unsat(size) for size in range(1, 9)}
    controls = {str(size): negative_control_sat(size) for size in range(2, 9)}
    if not all(collapse.values()) or not all(controls.values()):
        raise AssertionError((collapse, controls))

    cycle_counts = {
        f"u{u}_length{k}": finite_strict_cycle_count(u, k)
        for u in range(1, 5) for k in range(2, 5)
    }
    if any(cycle_counts.values()):
        raise AssertionError(cycle_counts)

    payload = {
        "claim": "independent ordered-field and strict-inclusion replay of PXC114",
        "positive_weight_collapse_unsat": collapse,
        "drop_nonnegative_derivatives_sat": controls,
        "finite_strict_inclusion_cycle_counts": cycle_counts,
        "conclusion": (
            "a missing reverse edge forces all target-row derivatives to zero; "
            "one-way edges strictly order descent sets and cannot form a cycle"
        ),
        "z3_version": z3.get_version_string(),
        "independence": (
            "standalone QF_NRA sign-collapse and finite-set inclusion audit; "
            "no project LP, game, selector, cover, or PXC code"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
