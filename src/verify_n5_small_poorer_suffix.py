"""Exact symbolic audit of small-poorer-side Lmin boundaries at n=5.

For every ordered payoff-stratum composition of five players, query each
strict boundary having one or two cumulative poorer players and require that
its richer suffix have positive slack.  The shared definition-level encoding
uses exact-face witnesses and stagewise Lmin KKT certificates.

This is finite exact-rational evidence and is not a dimension-free proof.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import z3

from verify_n4_exact_lmin_pes_bridge import build_query, compositions


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    player_count = 5
    cases = []
    for composition in compositions(player_count):
        if len(composition) == 1:
            continue
        cumulative = 0
        for boundary, block_size in enumerate(composition[:-1]):
            cumulative += block_size
            if cumulative > 2:
                continue
            solver, suffixes = build_query(
                player_count,
                composition,
                require_positive_suffix=False,
            )
            suffix = suffixes[boundary]
            solver.add(z3.Real(f"slack_{suffix}") > 0)
            status = solver.check()
            if status != z3.unsat:
                raise RuntimeError(
                    "small-poorer-side query was not excluded for "
                    f"composition {composition}, boundary {boundary}: {status}"
                )
            cases.append({
                "payoff_stratum_composition": composition,
                "boundary_after_players": cumulative,
                "richer_suffix_mask": suffix,
                "positive_suffix_slack_query": "unsatisfiable",
            })

    payload = {
        "status": "five-player small-poorer-side suffix queries excluded",
        "solver": f"z3 {z3.get_version_string()} exact linear rational arithmetic",
        "scope": (
            "all five-player Lmin payoff-stratum compositions and every strict "
            "boundary with at most two cumulative poorer players"
        ),
        "case_count": len(cases),
        "cases": cases,
        "limitation": (
            "finite symbolic theorem at n=5; does not establish the proposed "
            "dimension-free statement"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
