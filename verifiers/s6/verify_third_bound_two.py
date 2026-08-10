#!/usr/bin/env python3
"""Verify the third coefficient-two formulation and its independence controls."""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
FROZEN = HERE / "third_bound_two"
CASES = ("p2_n3_t1", "p3_n3_t0")


def audit_generator_imports():
    source = (HERE / "third_bound_two_direct_smt.py").read_text()
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    expected = {"__future__", "argparse", "hashlib", "itertools", "json", "pathlib"}
    if imports != expected:
        raise AssertionError(f"third generator import boundary changed: {sorted(imports)}")
    return sorted(imports)


def symbols(case, family):
    if family == "third":
        x = [z3.Real(f"tri_{case}_x_{player}") for player in range(6)]
        z = [z3.Real(f"tri_{case}_z_{player}") for player in range(6)]
        q = [[z3.Real(f"tri_{case}_q_{anchor}_{player}") for player in range(6)]
             for anchor in range(6)]
    elif family == "production":
        x = [z3.Real(f"equality_exchange_x_{player}") for player in range(6)]
        z = [z3.Real(f"equality_exchange_z_{player}") for player in range(6)]
        q = [[z3.Real(f"equality_exchange_q_{anchor}_{player}") for player in range(6)]
             for anchor in range(6)]
    elif family == "second":
        x = [z3.Real(f"ind_{case}_x{player}") for player in range(6)]
        z = [z3.Real(f"ind_{case}_z{player}") for player in range(6)]
        q = [[z3.Real(f"ind_{case}_q{anchor}_{player}") for player in range(6)]
             for anchor in range(6)]
    else:
        raise ValueError(family)
    return [*x, *z, *(coordinate for witness in q for coordinate in witness)]


def equivalent(left, right, substitutions=(), premises=()):
    if substitutions:
        left = z3.substitute(left, *substitutions)
    solver = z3.Solver()
    solver.set(timeout=60_000)
    solver.add(*premises, z3.Xor(left, right))
    return solver.check()


def verdict(assertions):
    solver = z3.Solver()
    solver.set(timeout=120_000)
    solver.add(*assertions)
    return solver.check()


def generate(directory, *flags):
    subprocess.run(
        [
            sys.executable,
            str(HERE / "third_bound_two_direct_smt.py"),
            "--output-dir",
            str(directory),
            *flags,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    frozen_generator_audit = json.loads((FROZEN / "audit.json").read_text())
    with tempfile.TemporaryDirectory(prefix="third-bound-two-") as name:
        root = Path(name)
        normal = root / "normal"
        nonstrict = root / "nonstrict"
        dropped = root / "dropped"
        generate(normal)
        generate(nonstrict, "--nonstrict-activation")
        generate(dropped, "--drop-first-cut")
        if json.loads((normal / "audit.json").read_text()) != frozen_generator_audit:
            raise AssertionError("third generator audit did not regenerate")
        for case in CASES:
            if (normal / f"{case}.smt2").read_bytes() != (FROZEN / f"{case}.smt2").read_bytes():
                raise AssertionError(f"{case}: third SMT-LIB did not byte-regenerate")

        rows = []
        total_equivalences = 0
        mutation_counts = {"nonstrict_activation": 0, "drop_first_cut": 0}
        for case in CASES:
            third = list(z3.parse_smt2_file(str(FROZEN / f"{case}.smt2")))
            production = list(z3.parse_smt2_file(
                str(HERE / "certificates" / f"strict_exchange_{case}.smt2")
            ))
            second = list(z3.parse_smt2_file(
                str(HERE / "independent_bound_two" / f"{case}.smt2")
            ))
            if not (len(third) == len(production) == len(second)):
                raise AssertionError(f"{case}: assertion lengths differ")

            third_symbols = symbols(case, "third")
            production_substitution = tuple(zip(third_symbols, symbols(case, "production"), strict=True))
            second_substitution = tuple(zip(third_symbols, symbols(case, "second"), strict=True))
            for index, assertion in enumerate(third):
                if equivalent(assertion, production[index], production_substitution) != z3.unsat:
                    raise AssertionError(f"{case}: third/production mismatch at a{index}")
                if equivalent(assertion, second[index], second_substitution) != z3.unsat:
                    raise AssertionError(f"{case}: third/second mismatch at a{index}")
                total_equivalences += 2

            base_status = verdict(third[:72])
            full_status = verdict(third)
            if base_status != z3.sat or full_status != z3.unsat:
                raise AssertionError(f"{case}: base/full statuses are {base_status}/{full_status}")

            for label, directory in (("nonstrict_activation", nonstrict), ("drop_first_cut", dropped)):
                mutated = list(z3.parse_smt2_file(str(directory / f"{case}.smt2")))
                if len(mutated) != len(third):
                    raise AssertionError(f"{case}: {label} assertion count changed")
                for original, changed in zip(third[72:], mutated[72:], strict=True):
                    # This is a local row-semantic mutation test.  A cut may
                    # be redundant after all 72 base assertions are imposed,
                    # while still being required for a complete reconstruction
                    # of the mathematical blocker disjunction.
                    if equivalent(original, changed) == z3.sat:
                        mutation_counts[label] += 1

            generator_row = next(row for row in frozen_generator_audit["rows"] if row["case"] == case)
            rows.append(
                {
                    "case": case,
                    "assertion_count": len(third),
                    "base_status": str(base_status),
                    "full_status": str(full_status),
                    "third_vs_production_equivalences": len(third),
                    "third_vs_second_equivalences": len(third),
                    "negative_cut_count": generator_row["negative_cut_count"],
                    "comparison_count": generator_row["comparison_count"],
                    "formula_sha256": generator_row["formula_sha256"],
                }
            )

    if total_equivalences != 458:
        raise AssertionError(f"unexpected semantic equivalence total: {total_equivalences}")
    if not all(mutation_counts.values()):
        raise AssertionError(f"a mutation was not detected: {mutation_counts}")
    report = {
        "schema": "third-bound-two-verification-v1",
        "status": "PASS",
        "scope": (
            "byte regeneration, independent row semantics against both existing encodings, "
            "base SAT/full UNSAT, and two targeted mutation controls"
        ),
        "semantic_equivalence_check_count": total_equivalences,
        "generator_imports": audit_generator_imports(),
        "mutation_inequivalent_row_counts": mutation_counts,
        "rows": rows,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
