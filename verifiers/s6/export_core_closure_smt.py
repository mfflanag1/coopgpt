#!/usr/bin/env python3
"""Freeze one six-player generator-normal-form query as exact SMT-LIB.

The exported formula contains no archived solver verdict.  It rebuilds the
selected stratum/table configuration from ``triage32.json`` and is intended
for replay by independent QF_LRA solvers.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core_closure_pipeline import (  # noqa: E402
    pipeline2_generator_normal_form,
    require_equality_without_common_uniform_triple_anchor,
    require_equality_with_uniform_triple_anchor,
    require_equality_with_subthird_overcover,
    require_equality_without_uniform_triple_anchor,
)


def build(index: int, mode: str, source: Path) -> z3.Solver:
    survivors = json.loads(source.read_text())["survivors"]
    if not 0 <= index < len(survivors):
        raise ValueError(f"index must lie in [0,{len(survivors)})")
    r, c, table = survivors[index]
    data = pipeline2_generator_normal_form(
        6, tuple(r), tuple(c), table, F(2, 3), mode == "failure"
    )
    if mode == "equality":
        data["solver"].add(data["distance"] == z3.RealVal("2/3"))
    elif mode == "equality-triple":
        require_equality_with_uniform_triple_anchor(data, tuple(c))
    elif mode == "equality-no-triple":
        require_equality_without_uniform_triple_anchor(data, tuple(c))
    elif mode == "equality-no-common-triple":
        require_equality_without_common_uniform_triple_anchor(data, tuple(c))
    elif mode == "equality-subthird":
        require_equality_with_subthird_overcover(data, tuple(c))
    elif mode == "equality-noncanonical":
        canonical = {
            1408: (
                ("1/12", "1/12", "1/12", "1/12", "1/3", "1/3"),
                ("0", "0", "1/4", "1/4", "1/4", "1/4"),
            ),
            2236: (
                ("1/9", "1/9", "1/9", "1/9", "1/9", "4/9"),
                ("1/18", "1/18", "2/9", "2/9", "2/9", "2/9"),
            ),
        }
        if index not in canonical:
            raise ValueError(
                "equality-noncanonical is defined only for equality indices "
                "1408 and 2236"
            )
        expected_lmin, expected_lmax = canonical[index]
        data["solver"].add(data["distance"] == z3.RealVal("2/3"))
        data["solver"].add(
            z3.Or(
                [
                    value != z3.RealVal(expected)
                    for value, expected in zip(data["lmin"], expected_lmin)
                ]
                + [
                    value != z3.RealVal(expected)
                    for value, expected in zip(data["lmax"], expected_lmax)
                ]
            )
        )
    return data["solver"]


def rational_token(value: z3.RatNumRef) -> str:
    numerator = value.numerator_as_long()
    denominator = value.denominator_as_long()
    magnitude = str(abs(numerator))
    if denominator != 1:
        magnitude = f"(/ {magnitude} {denominator})"
    return f"(- {magnitude})" if numerator < 0 else magnitude


def smt_term(term: z3.ExprRef) -> str:
    """Serialize the small QF_LRA/Boolean vocabulary without local lets."""
    if z3.is_true(term):
        return "true"
    if z3.is_false(term):
        return "false"
    if z3.is_rational_value(term):
        return rational_token(term)
    if term.num_args() == 0:
        return str(term.decl().name())
    operator = str(term.decl().name())
    if operator == "if":
        operator = "ite"
    # Z3 permits unary ``(+ x)``/``(* x)`` nodes, while strict SMT-LIB and
    # cvc5 require these operators to have at least two arguments.
    if operator in {"+", "*"} and term.num_args() == 1:
        return smt_term(term.arg(0))
    return f"({operator} {' '.join(smt_term(child) for child in term.children())})"


def qf_lra_smt2(solver: z3.Solver) -> str:
    # Emit each asserted premise without Z3's local ``let`` aliases.  cvc5
    # expands those aliases in Alethe, while Carcara 1.1 compares assumptions
    # to the original premises syntactically.
    variables: dict[str, z3.ExprRef] = {}
    stack = list(solver.assertions())
    while stack:
        term = stack.pop()
        if (
            term.num_args() == 0
            and not z3.is_rational_value(term)
            and not z3.is_true(term)
            and not z3.is_false(term)
        ):
            name = str(term.decl().name())
            previous = variables.setdefault(name, term)
            if previous.sort() != term.sort():
                raise ValueError(f"symbol {name!r} occurs with two sorts")
        stack.extend(term.children())
    lines = ["(set-logic QF_LRA)"]
    lines.extend(
        f"(declare-fun {name} () {variables[name].sort().sexpr()})"
        for name in sorted(variables)
    )
    lines.extend(
        f"(assert (! {smt_term(term)} :named a{index}))"
        for index, term in enumerate(solver.assertions())
    )
    lines.append("(check-sat)")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument(
        "--mode",
        choices=(
            "failure",
            "equality",
            "equality-triple",
            "equality-no-triple",
            "equality-no-common-triple",
            "equality-subthird",
            "equality-noncanonical",
        ),
        default="failure",
    )
    parser.add_argument("--source", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(qf_lra_smt2(build(args.index, args.mode, args.source)))


if __name__ == "__main__":
    main()
