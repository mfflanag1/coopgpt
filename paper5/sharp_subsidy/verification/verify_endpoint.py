#!/usr/bin/env python3
"""Exact finite checks for the fixed twelve-owner endpoint example.

This is the two-hop flow game with five source owners P,A,G,M,B and seven
sink owners Q,R,D,E,F,L,N. A coalition's worth is the minimum of its total
source and sink capacities. Every owner is fixed; no splitting is used.

Checks: all 4,096 coalition inequalities for EACH of the published U and V
witnesses, their nonnegativity and total196, U >= H/3, and the exact subset
conditions used by the conventional proof of ideal/support upper bounds.
This program neither solves an LP nor proves optimality by finite search.
In particular, H is the theorem's supplied ideal vector, not computed here.
All checks use explicit exceptions and remain active under python -O.

Usage:
  python3 -B -O coop-verify-endpoint.py --output endpoint-check.json
Omit --output to print the deterministic JSON report without writing a file.
Only Python's standard library is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SOURCE_NAMES = ("P", "A", "G", "M", "B")
SINK_NAMES = ("Q", "R", "D", "E", "F", "L", "N")
NAMES = SOURCE_NAMES + SINK_NAMES
SOURCE_CAPACITIES = (2, 12, 46, 62, 75)
SINK_CAPACITIES = (6, 10, 16, 22, 24, 56, 62)
BASELINE = (1, 6, 23, 31, 37, 3, 5, 8, 11, 12, 28, 31)
U = (1, 6, 23, 31, 37, 3, 5, 8, 11, 12, 28, 31)
V = (1, 5, 23, 31, 38, 3, 5, 8, 11, 12, 28, 31)
H = (1, 6, 23, 31, 38, 6, 10, 16, 22, 24, 56, 62)
T = 196


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def subset_sum(values: tuple[int, ...], mask: int) -> int:
    return sum(value for i, value in enumerate(values) if mask & (1 << i))


def coalition_worth(mask: int) -> int:
    return min(subset_sum(SOURCE_CAPACITIES, mask & 31),
               subset_sum(SINK_CAPACITIES, mask >> 5))


def check_witness(name: str, witness: tuple[int, ...]) -> int:
    require(len(witness) == 12, name + ": wrong coordinate count")
    require(all(type(x) is int and x >= 0 for x in witness),
            name + ": invalid/nonnegative integer coordinate")
    require(sum(witness) == T, name + ": incorrect efficient total")
    checks = 0
    for mask in range(1 << 12):
        require(subset_sum(witness, mask) >= coalition_worth(mask),
                name + ": coalition coverage failed at mask " + str(mask))
        checks += 1
    return checks


def named_weight(labels: tuple[str, ...]) -> int:
    require(len(labels) == len(set(labels)), "Repeated player in subset")
    require(all(label in NAMES for label in labels), "Unknown subset player")
    weights = dict(zip(NAMES, BASELINE))
    return sum(weights[label] for label in labels)


def verify() -> dict:
    require(len(set(NAMES)) == 12, "Owner identities are not distinct")
    require(sum(SOURCE_CAPACITIES) == 197 and sum(SINK_CAPACITIES) == T,
            "Incorrect source/sink totals")
    require(sum(BASELINE[:5]) == sum(BASELINE[5:]) == 98,
            "Incorrect baseline side totals")
    require(SOURCE_CAPACITIES == tuple(2 * x + int(i == 4)
                                      for i, x in enumerate(BASELINE[:5])),
            "Source capacities do not match the baseline perturbation")
    require(SINK_CAPACITIES == tuple(2 * x for x in BASELINE[5:]),
            "Sink capacities do not match twice the baseline")
    counts = {"U": check_witness("U", U), "V": check_witness("V", V)}
    for i, (payment, ideal) in enumerate(zip(U, H)):
        require(3 * payment >= ideal, "U fails H/3 at " + NAMES[i])
    require(sum(U[:5]) == sum(V[:5]) == 98,
            "U/V do not attain the stated source support")
    require(U[1] + U[4] == V[1] + V[4] == 43,
            "U/V do not attain the stated A+B support")
    require(sum(H[:5]) == 99 and H[1] + H[4] == 44,
            "Supplied ideal incompatibility figures do not match")

    weights = dict(zip(NAMES, BASELINE))
    small_names = ("P", "Q", "R", "D", "E", "F")
    small = tuple(weights[label] for label in small_names)
    small_sums = [subset_sum(small, mask) for mask in range(1 << len(small))]
    require(sum(small) == 40, "Small subset total")
    for forbidden in (2, 7, 10):
        require(forbidden not in small_sums,
                "Small forbidden subset exists: " + str(forbidden))

    c0_names = tuple(label for label in NAMES if label not in ("A", "B"))
    c0 = tuple(weights[label] for label in c0_names)
    require(len(c0) == 10 and sum(c0) == 153, "C0 inventory/total")
    c0_sums = [subset_sum(c0, mask) for mask in range(1 << len(c0))]
    require(61 not in c0_sums and 92 not in c0_sums,
            "C0 has a forbidden weight61 or weight92 subset")

    weight98_count = 0
    for mask in range(1 << 12):
        if subset_sum(BASELINE, mask) == 98:
            require(bool(mask & (1 << 1)) == bool(mask & (1 << 4)),
                    "A and B differ in a weight98 subset")
            weight98_count += 1

    weight55 = (
        ("P", "G", "M"), ("P", "G", "N"),
        ("P", "E", "F", "M"), ("P", "Q", "D", "F", "M"),
        ("R", "D", "E", "M"), ("P", "Q", "G", "L"),
        ("P", "Q", "R", "E", "F", "G"),
        ("P", "D", "E", "F", "G"),
    )
    weight54 = (("M", "E", "D", "Q", "P"),
                ("L", "F", "D", "R", "P"))
    weight97 = (("B", "M", "L", "P"),
                ("A",) + tuple(label for label in c0_names
                                if label not in ("M", "N")))
    for labels in weight55:
        require(all(label in c0_names for label in labels), "Weight55 scope")
        require(named_weight(labels) == 55, "Incorrect weight55 subset")
        require(named_weight(("A", "B") + labels) == 98,
                "Weight55 completion does not have weight98")
    for labels in weight54:
        require(all(label in c0_names for label in labels), "Weight54 scope")
        require(named_weight(labels) == 54, "Incorrect weight54 subset")
        require(named_weight(("A", "B") + labels) == 97,
                "Weight54 completion does not have weight97")
    for labels in weight97:
        require(named_weight(labels) == 97, "Incorrect additional weight97 subset")

    # Reject a budget-feasible but non-covering counterfeit witness. This tests
    # the coverage check itself without changing any canonical fixture.
    bad = (T,) + (0,) * 11
    rejected = False
    try:
        check_witness("negative control", bad)
    except ValueError as exc:
        require("coalition coverage failed" in str(exc),
                "Negative control failed for an unintended reason")
        rejected = True
    require(rejected, "Coverage mutation was accepted")

    fixture = {
        "source_names": SOURCE_NAMES, "sink_names": SINK_NAMES,
        "source_capacities": SOURCE_CAPACITIES, "sink_capacities": SINK_CAPACITIES,
        "baseline": BASELINE, "U": U, "V": V, "supplied_H": H,
    }
    return {
        "status": "PASS",
        "model": "fixed twelve-owner two-hop flow game; all returns one",
        "fixture": fixture,
        "checks": {
            "coalition_inequalities_per_witness": counts,
            "total_coalition_inequalities": sum(counts.values()),
            "efficient_witness_totals": 2,
            "U_protection_floor_inequalities": 12,
            "small_subset_enumeration": len(small_sums),
            "C0_subset_enumeration": len(c0_sums),
            "all_baseline_subset_enumeration": 1 << 12,
            "weight98_subsets_with_equal_A_B_membership": weight98_count,
            "listed_weight55_tie_subsets": len(weight55),
            "listed_weight54_strict_subsets": len(weight54),
            "additional_weight97_strict_subsets": len(weight97),
            "rejected_coverage_mutations": 1,
        },
        "scope": (
            "Exact witness feasibility, supplied-H floor and subset conditions only. "
            "No LP solver is used, no ideals or support optimum are inferred from "
            "a numerical search, and no all-size or novelty claim follows. "
            "The written proof supplies real-valued ideal/support upper bounds."
        ),
        "fixture_sha256": hashlib.sha256(json.dumps(
            fixture, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dependencies": "Python3 standard library only; no external data files",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="Optional JSON report path; no other file is written")
    args = parser.parse_args()
    result = verify()
    report = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(report)
    print(report, end="")


if __name__ == "__main__":
    main()
