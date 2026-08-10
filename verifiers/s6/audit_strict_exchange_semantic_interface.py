#!/usr/bin/env python3
"""Independently reconstruct every assertion in the frozen strict suite.

This audit checks semantic equivalence assertion by assertion.  It imports no
production encoder, lex predicate, blocker builder, direction generator,
minimizer, exporter, or serializer.  The retained menus are theorem data.
It does not prove the human convexity and tight-blocker lemmas.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent


def vector_sum(vector, players):
    terms = [vector[player] for player in players]
    if not terms:
        return z3.RealVal(0)
    if len(terms) == 1:
        return terms[0]
    return z3.Sum(*terms)


def disjoin(items):
    if not items:
        return z3.BoolVal(False)
    if len(items) == 1:
        return items[0]
    return z3.Or(*items)


def first_affected_improves(point, direction, side):
    """Sufficient sorted-lex improvement test, independently formulated."""
    alternatives = []
    if side == "min":
        for pivot, coefficient in enumerate(direction):
            if coefficient <= 0:
                continue
            alternatives.append(
                z3.And(
                    *[
                        point[pivot] <= point[player]
                        for player, value in enumerate(direction)
                        if value != 0
                    ],
                    *[
                        point[pivot] < point[player]
                        for player, value in enumerate(direction)
                        if value < 0
                    ],
                )
            )
    elif side == "max":
        for pivot, coefficient in enumerate(direction):
            if coefficient >= 0:
                continue
            alternatives.append(
                z3.And(
                    *[
                        point[pivot] >= point[player]
                        for player, value in enumerate(direction)
                        if value != 0
                    ],
                    *[
                        point[pivot] > point[player]
                        for player, value in enumerate(direction)
                        if value > 0
                    ],
                )
            )
    else:
        raise ValueError(side)
    return disjoin(alternatives)


def negative_cuts(direction):
    return [
        tuple(player for player in range(6) if mask & (1 << player))
        for mask in range(1, 63)
        if sum(direction[player] for player in range(6) if mask & (1 << player)) < 0
    ]


def blocker_disjunction(x, z, witnesses, direction, side):
    selected = x if side == "min" else z
    opposite = z if side == "min" else x
    alternatives = []
    for coalition in negative_cuts(direction):
        selected_sum = vector_sum(selected, coalition)
        alternatives.append(
            z3.And(
                vector_sum(opposite, coalition) >= selected_sum,
                *[
                    vector_sum(witness, coalition) >= selected_sum
                    for witness in witnesses
                ],
            )
        )
    if not alternatives:
        raise AssertionError(f"direction has no negative cut: {direction}")
    return disjoin(alternatives)


def anchors(x, z):
    no_unique_top = z3.Not(
        z3.Or(
            *[
                z3.And(*[z[player] > z[other] for other in range(6) if other != player])
                for player in range(6)
            ]
        )
    )
    top_cross = z3.Or(
        *[
            z3.And(
                *[z[player] >= z[other] for other in range(6)],
                x[player] >= z[player],
            )
            for player in range(6)
        ]
    )
    bottom_cross = z3.Or(
        *[
            z3.And(
                *[x[player] <= x[other] for other in range(6)],
                z[player] <= x[player],
            )
            for player in range(6)
        ]
    )
    return [no_unique_top, top_cross, bottom_cross]


def expected_assertions(row):
    x = [z3.Real(f"equality_exchange_x_{player}") for player in range(6)]
    z = [z3.Real(f"equality_exchange_z_{player}") for player in range(6)]
    witnesses = [
        [z3.Real(f"equality_exchange_q_{zero}_{player}") for player in range(6)]
        for zero in range(6)
    ]
    positive_count = row["positive_count"]
    negative_count = row["negative_count"]
    tie_count = row["tie_count"]
    if positive_count + negative_count + tie_count != 6:
        raise AssertionError(f"bad sign counts in {row['case']}")
    positive = range(positive_count)
    negative = range(positive_count, positive_count + negative_count)
    tied = range(positive_count + negative_count, 6)

    base = [z3.Sum(*x) == 1, z3.Sum(*z) == 1]
    base.extend(coordinate >= 0 for coordinate in (*x, *z))
    base.extend(x[player] > z[player] for player in positive)
    base.extend(z[player] > x[player] for player in negative)
    base.extend(x[player] == z[player] for player in tied)
    base.append(
        2 * z3.Sum(*[x[player] - z[player] for player in positive])
        > z3.RealVal(2) / 3
    )
    base.extend(anchors(x, z))
    for zero, witness in enumerate(witnesses):
        base.extend(
            [
                z3.Sum(*witness) == 1,
                witness[zero] == 0,
                *(coordinate >= 0 for coordinate in witness),
            ]
        )
    if len(base) != 72:
        raise AssertionError(f"bad independent base length in {row['case']}: {len(base)}")

    implications = []
    metadata = []
    for item in row["retained_menu"]:
        side = item["side"]
        direction = tuple(int(value) for value in item["direction"])
        if side not in ("min", "max"):
            raise AssertionError(side)
        if len(direction) != 6 or sum(direction) != 0 or not any(direction):
            raise AssertionError(direction)
        point = x if side == "min" else z
        cuts = negative_cuts(direction)
        implications.append(
            z3.Implies(
                first_affected_improves(point, direction, side),
                blocker_disjunction(x, z, witnesses, direction, side),
            )
        )
        metadata.append(
            {
                "side": side,
                "direction": list(direction),
                "negative_proper_cut_count": len(cuts),
                "comparison_count": 7 * len(cuts),
            }
        )
    return [*base, *implications], metadata


def equivalence_verdict(actual, expected, timeout_ms):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(z3.Xor(actual, expected))
    return solver.check()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    args = parser.parse_args()

    mutation_probe = z3.Real("semantic_interface_mutation_probe")
    mutation_status = equivalence_verdict(
        mutation_probe >= 0, mutation_probe <= -1, args.timeout_ms
    )
    if mutation_status != z3.sat:
        raise AssertionError(f"semantic inequivalence control is {mutation_status}")

    menu = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    rows = []
    total_base = 0
    total_implications = 0
    total_cuts = 0
    total_comparisons = 0
    for row in menu["rows"]:
        case = row["case"]
        formula = HERE / "certificates" / f"strict_exchange_{case}.smt2"
        actual = list(z3.parse_smt2_file(str(formula)))
        expected, metadata = expected_assertions(row)
        if len(actual) != len(expected):
            raise AssertionError(
                f"{case}: actual/expected lengths {len(actual)}/{len(expected)}"
            )
        for index, (actual_item, expected_item) in enumerate(
            zip(actual, expected, strict=True)
        ):
            status = equivalence_verdict(actual_item, expected_item, args.timeout_ms)
            if status != z3.unsat:
                raise AssertionError(f"{case}: a{index} semantic difference is {status}")
        case_cuts = sum(item["negative_proper_cut_count"] for item in metadata)
        case_comparisons = sum(item["comparison_count"] for item in metadata)
        total_cuts += case_cuts
        total_comparisons += case_comparisons
        total_base += 72
        total_implications += len(metadata)
        rows.append(
            {
                "case": case,
                "assertion_count": len(actual),
                "base_assertions_semantically_equivalent": 72,
                "direction_implications_semantically_equivalent": len(metadata),
                "negative_cut_instances_reconstructed": case_cuts,
                "blocker_comparisons_reconstructed": case_comparisons,
            }
        )

    if len(rows) != 15 or total_implications != 252:
        raise AssertionError("strict semantic suite coverage changed")
    payload = {
        "schema": "strict-exchange-semantic-interface-v1",
        "status": "PASS",
        "scope": (
            "independent assertion-by-assertion semantic reconstruction; imports no "
            "production encoder/predicate/blocker/exporter and does not rerun theorem "
            "satisfiability"
        ),
        "case_count": len(rows),
        "base_semantic_equivalence_checks": total_base,
        "direction_semantic_equivalence_checks": total_implications,
        "total_semantic_equivalence_checks": total_base + total_implications,
        "inequivalence_mutation_control": "sat",
        "negative_cut_instances_reconstructed": total_cuts,
        "blocker_comparisons_reconstructed": total_comparisons,
        "no_unique_top_reconstruction": "negated unique maximum",
        "lex_reconstruction": "direct first affected payoff level",
        "blocker_reconstruction": (
            "all negative nonempty proper cuts, seven comparisons each"
        ),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
