#!/usr/bin/env python3
"""Classify payoff-only critical rows by feasible common-gap pairs.

For both handover branches this checks the exact structural dichotomy behind
the critical algebra: either no pair of P players can realize the two common
triple equalities, or exactly one pair can and the third comparison excludes
it.  Verdicts remain solver evidence rather than independent proof objects.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_positive_lmax_direction_layers import feasible_common_pairs  # noqa: E402
from search_positive_handover_directions import critical_all_witness_solver  # noqa: E402


EXPECTED = {
    "max": {"no_order_feasible_pair": 68, "unique_pair_third_gap_fails": 146},
    "min": {"no_order_feasible_pair": 293, "unique_pair_third_gap_fails": 266},
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    survivors = json.loads(args.triage.read_text())["survivors"]
    rows = []
    summary = {}
    for side, filename in (
        ("max", "positive_lmax_handover_directions.json"),
        ("min", "positive_lmin_handover_directions.json"),
    ):
        source = json.loads((HERE / filename).read_text())["rows"]
        counts = collections.Counter()
        for row in source:
            if row.get("critical_algebra_verdict") != "unsat":
                continue
            index = row["survivor_index"]
            configuration = survivors[index]
            payoff, _, _ = critical_all_witness_solver(
                index,
                configuration,
                include_distance=False,
                include_witnesses=False,
                include_triple_comparisons=True,
            )
            if payoff.check() != z3.unsat:
                continue
            common_only, _, _ = critical_all_witness_solver(
                index,
                configuration,
                include_distance=False,
                include_witnesses=False,
                include_triple_comparisons=False,
            )
            common_verdict = common_only.check()
            candidates = feasible_common_pairs(configuration, index, False)
            with_third = feasible_common_pairs(configuration, index, True)
            assert with_third == []
            if common_verdict == z3.unsat:
                assert candidates == []
                classification = "no_order_feasible_pair"
            else:
                assert common_verdict == z3.sat
                assert len(candidates) == 1
                classification = "unique_pair_third_gap_fails"
            counts[classification] += 1
            rows.append(
                {
                    "selected_side": side,
                    "survivor_index": index,
                    "classification": classification,
                    "order_feasible_common_pairs": candidates,
                    "pairs_feasible_with_third_comparison": with_third,
                }
            )
        summary[side] = dict(sorted(counts.items()))
    assert summary == EXPECTED
    payload = {
        "schema": "positive-common-gap-pair-audit-v1",
        "scope": "complete exact QF_LRA pair classification; solver evidence, not proof objects",
        "summary": summary,
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
