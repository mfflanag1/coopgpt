#!/usr/bin/env python3
"""Audit the literal human-to-SMT assertion layout of the strict suite.

This is not another satisfiability run.  It parses the frozen formulas and
checks that each contains exactly the 72 mathematically documented base
assertions followed by the retained exchange implications, with no hidden
premise or game-value variable.  It also records the negative-cut universe of
every retained direction for line-by-line human review.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
ASSERTION = re.compile(r"^\(assert \(! .* :named a([0-9]+)\)\)$")
DECLARATION = re.compile(r"^\(declare-fun ([^ ]+) \(\) Real\)$")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def negative_proper_cut_count(direction):
    return sum(
        1
        for size in range(1, 6)
        for players in itertools.combinations(range(6), size)
        if sum(direction[player] for player in players) < 0
    )


def check_base_shape(assertions, case):
    if len(assertions) < 72:
        raise AssertionError(f"{case}: fewer than 72 base assertions")
    if not all(z3.is_eq(item) for item in assertions[0:2]):
        raise AssertionError(f"{case}: efficiency layout changed")
    if not all(item.decl().kind() == z3.Z3_OP_GE for item in assertions[2:14]):
        raise AssertionError(f"{case}: selection nonnegativity layout changed")
    if not all(item.decl().kind() in {z3.Z3_OP_GT, z3.Z3_OP_EQ} for item in assertions[14:20]):
        raise AssertionError(f"{case}: sign layout changed")
    if assertions[20].decl().kind() != z3.Z3_OP_LT:
        raise AssertionError(f"{case}: strict-distance layout changed")
    if not all(z3.is_or(item) for item in assertions[21:24]):
        raise AssertionError(f"{case}: anchor layout changed")
    for player in range(6):
        block = assertions[24 + 8 * player : 32 + 8 * player]
        if not z3.is_eq(block[0]) or not z3.is_eq(block[1]):
            raise AssertionError(f"{case}: witness {player} equalities changed")
        if not all(item.decl().kind() == z3.Z3_OP_GE for item in block[2:]):
            raise AssertionError(f"{case}: witness {player} nonnegativity changed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    menu = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    rows = []
    total_directions = 0
    for row in menu["rows"]:
        case = row["case"]
        formula = HERE / "certificates" / f"strict_exchange_{case}.smt2"
        record = json.loads((HERE / "certificates" / f"strict_exchange_{case}.json").read_text())
        lines = formula.read_text().splitlines()
        labels = [int(match.group(1)) for line in lines if (match := ASSERTION.match(line))]
        declarations = [match.group(1) for line in lines if (match := DECLARATION.match(line))]
        assertions = list(z3.parse_smt2_file(str(formula)))
        expected_count = 72 + row["retained_direction_count"]
        if labels != list(range(expected_count)) or len(assertions) != expected_count:
            raise AssertionError(f"{case}: named assertion sequence changed")
        expected_symbols = {
            *(f"equality_exchange_x_{i}" for i in range(6)),
            *(f"equality_exchange_z_{i}" for i in range(6)),
            *(f"equality_exchange_q_{i}_{j}" for i in range(6) for j in range(6)),
        }
        if set(declarations) != expected_symbols or len(declarations) != 48:
            raise AssertionError(f"{case}: unexpected declared symbols")
        check_base_shape(assertions, case)
        if not all(z3.is_implies(item) for item in assertions[72:]):
            raise AssertionError(f"{case}: non-implication in direction suffix")
        if record["formula_sha256"] != sha256(formula):
            raise AssertionError(f"{case}: formula record hash mismatch")
        directions = []
        for offset, item in enumerate(row["retained_menu"]):
            direction = tuple(item["direction"])
            cut_count = negative_proper_cut_count(direction)
            if cut_count == 0:
                raise AssertionError(f"{case}: direction has no negative proper cut")
            directions.append(
                {
                    "assertion": f"a{72 + offset}",
                    "side": item["side"],
                    "direction": list(direction),
                    "negative_proper_cut_count": cut_count,
                    "blocker_comparisons_per_cut": 7,
                }
            )
        total_directions += len(directions)
        assertion_map = {
            "a0-a1": "efficiency of x and z",
            "a2-a13": "nonnegativity of x and z",
            "a14-a19": "P/M/E comparison signs",
            "a20": "strict normalized distance greater than 2/3",
            "a21": "Lmax has no unique top player",
            "a22": "Lmax-top cross anchor",
            "a23": "Lmin-bottom cross anchor",
            "a24-a71": "six blocks of witness efficiency, zero coordinate, and nonnegativity",
        }
        if expected_count > 72:
            assertion_map[f"a72-a{expected_count - 1}"] = (
                "retained lex-improvement implies eligible negative-cut blocker"
            )
        rows.append(
            {
                "case": case,
                "formula": f"certificates/{formula.name}",
                "formula_sha256": sha256(formula),
                "declared_real_count": len(declarations),
                "assertion_count": expected_count,
                "assertion_map": assertion_map,
                "direction_implications": directions,
            }
        )
    if len(rows) != 15 or total_directions != 252:
        raise AssertionError("strict suite coverage changed")
    payload = {
        "schema": "strict-exchange-formula-interface-v1",
        "status": "PASS",
        "scope": (
            "literal assertion-layout and negative-cut manifest; verifies no hidden SMT premise, "
            "but does not replace the human soundness proof"
        ),
        "case_count": len(rows),
        "base_assertion_count_per_case": 72,
        "declared_reals_per_case": 48,
        "retained_direction_count": total_directions,
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
