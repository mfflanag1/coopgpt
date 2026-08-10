#!/usr/bin/env python3
"""Extract small exact exchange menus for the equality classification.

Unsat cores are used only to navigate toward smaller formulas.  Every retained
formula is rebuilt without assumption literals and checked again exactly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_equality_universal_exchange_relaxation import (  # noqa: E402
    build,
    exchange_directions,
)


def case_configuration(positive, negative, distance_relation="eq"):
    ties = 6 - positive - negative
    if distance_relation == "gt":
        if (positive, negative, ties) in ((2, 3, 1), (3, 3, 0)):
            return 2, False, False
        return 1, False, False
    if (positive, negative, ties) == (3, 3, 0):
        return 2, False, True
    if (positive, negative, ties) == (4, 2, 0):
        return 1, True, True
    if (positive, negative, ties) == (2, 3, 1):
        return 2, False, False
    if (positive, negative, ties) == (3, 2, 1):
        return 1, True, False
    return 1, False, False


def rebuilt_solver_from_row(row, timeout_ms=0):
    solver, *_rest, direction_count, _ties = build(
        row["positive_count"],
        row["negative_count"],
        row["bound"],
        row["extra_coefficient_two"],
        False,
        False,
        row["exclude_canonical"],
        timeout_ms,
        row.get("distance_relation", "eq"),
    )
    assertions = list(solver.assertions())
    directional_count = 2 * direction_count
    base = assertions[:-directional_count]
    directional = assertions[-directional_count:]
    directions = exchange_directions(row["bound"], row["extra_coefficient_two"])
    lookup = {
        (side, tuple(direction)): assertion
        for (side, direction), assertion in zip(
            (
                (side, direction)
                for side in ("min", "max")
                for direction in directions
            ),
            directional,
            strict=True,
        )
    }
    rebuilt = z3.Solver()
    rebuilt.set(timeout=timeout_ms)
    rebuilt.add(*base)
    rebuilt.add(
        *[
            lookup[(item["side"], tuple(item["direction"]))]
            for item in row["retained_menu"]
        ]
    )
    return rebuilt


def minimize_case(
    positive, negative, timeout_ms, max_greedy_core_size, distance_relation="eq"
):
    bound, extra_coefficient_two, exclude_canonical = case_configuration(
        positive, negative, distance_relation
    )
    solver, *_rest, direction_count, ties = build(
        positive,
        negative,
        bound,
        extra_coefficient_two,
        False,
        False,
        exclude_canonical,
        timeout_ms,
        distance_relation,
    )
    assertions = list(solver.assertions())
    directional_count = 2 * direction_count
    base = assertions[:-directional_count]
    directional = assertions[-directional_count:]
    directions = exchange_directions(bound, extra_coefficient_two)
    metadata = [
        (side, direction)
        for side in ("min", "max")
        for direction in directions
    ]
    assert len(directional) == len(metadata)

    core_solver = z3.Solver()
    core_solver.set(timeout=timeout_ms, unsat_core=True)
    core_solver.add(*base)
    tags = []
    for index, assertion in enumerate(directional):
        tag = z3.Bool(f"equality_core_{positive}_{negative}_{index}")
        tags.append(tag)
        core_solver.add(z3.Implies(tag, assertion))
    verdict = core_solver.check(*tags)
    if verdict != z3.unsat:
        raise RuntimeError(
            f"full p{positive}n{negative} formula did not close: {verdict}"
        )
    core_names = {str(tag) for tag in core_solver.unsat_core()}
    retained = [index for index, tag in enumerate(tags) if str(tag) in core_names]

    greedily_minimized = len(retained) <= max_greedy_core_size
    if greedily_minimized:
        # Greedy deletion gives an irredundant core for this deterministic order.
        for candidate in tuple(retained):
            trial = [index for index in retained if index != candidate]
            verdict = core_solver.check(*[tags[index] for index in trial])
            if verdict == z3.unsat:
                retained = trial
            elif verdict != z3.sat:
                raise RuntimeError(
                    f"core minimization p{positive}n{negative} returned {verdict}"
                )

    rebuilt = z3.Solver()
    rebuilt.set(timeout=timeout_ms)
    rebuilt.add(*base)
    rebuilt.add(*[directional[index] for index in retained])
    rebuilt_verdict = rebuilt.check()
    if rebuilt_verdict != z3.unsat:
        raise RuntimeError(
            f"rebuilt p{positive}n{negative} core returned {rebuilt_verdict}"
        )
    menu = [
        {"side": metadata[index][0], "direction": list(metadata[index][1])}
        for index in retained
    ]
    return {
        "case": f"p{positive}_n{negative}_t{ties}",
        "positive_count": positive,
        "negative_count": negative,
        "tie_count": ties,
        "bound": bound,
        "extra_coefficient_two": extra_coefficient_two,
        "exclude_canonical": exclude_canonical,
        "distance_relation": distance_relation,
        "full_direction_count_per_side": direction_count,
        "initial_unsat_core_size": len(core_names),
        "greedily_minimized": greedily_minimized,
        "retained_direction_count": len(retained),
        "retained_menu": menu,
        "rebuilt_verdict": str(rebuilt_verdict),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--max-greedy-core-size", type=int, default=40)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--case")
    parser.add_argument("--distance-relation", choices=("eq", "gt"), default="eq")
    args = parser.parse_args()
    rows = []
    for positive in range(1, 6):
        for negative in range(1, 7 - positive):
            ties = 6 - positive - negative
            name = f"p{positive}_n{negative}_t{ties}"
            if args.case and name != args.case:
                continue
            rows.append(
                minimize_case(
                    positive,
                    negative,
                    args.timeout_ms,
                    args.max_greedy_core_size,
                    args.distance_relation,
                )
            )
            print(f"closed {name}", file=sys.stderr, flush=True)
    if args.case and not rows:
        parser.error(f"unknown case {args.case!r}")
    payload = {
        "schema": "exactness-exchange-direction-cores-v1",
        "distance_relation": args.distance_relation,
        "scope": (
            "complete sign-count classification; unsat cores are discovery aids, "
            "while every retained unguarded formula is rechecked"
        ),
        "case_count": len(rows),
        "status": "PASS",
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
