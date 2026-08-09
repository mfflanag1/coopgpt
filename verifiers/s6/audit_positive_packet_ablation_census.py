#!/usr/bin/env python3
"""Exhaust the two one-sided staged-packet ablations near the positive type.

The universe is the 1,659 hand-net survivors refining the positive 5+1 by
2+4 equality table.  For each refinement we impose the critical-triple
theorem, the local cross-cell signs, exactness witnesses, and strict distance
greater than 2/3.  We then retain either the complete staged Lmin packet or
the complete staged Lmax packet and delete the other packet.

The frozen census is solver evidence, not an independently checkable
infeasibility proof.  ``--recompute`` regenerates every verdict from the same
public model used by the two exact ablation controls.  The fast default checks
that the frozen indices still select precisely 38 and 257 positive refinements
and that the two residual sets are disjoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_equality_refinement_neighborhood import (  # noqa: E402
    COARSE_TYPES,
    refines,
)
from audit_positive_two_sided_ablation import build_ablation  # noqa: E402


POSITIVE = COARSE_TYPES[1]
EXPECTED = {
    "lmin_only": (
        40, 234, 239, 404, 542, 543, 548, 631, 667, 697, 889, 925, 1024,
        1200, 1227, 1289, 1290, 1294, 1446, 1499, 1541, 1763, 1767, 1794,
        1800, 1801, 1861, 2171, 2269, 2407, 2444, 2448, 2867, 2935, 2959,
        2981, 2993, 3255,
    ),
    "lmax_only": (
        35, 73, 78, 82, 86, 107, 117, 130, 132, 146, 168, 181, 182, 186,
        198, 199, 201, 207, 212, 228, 247, 251, 264, 270, 271, 273, 279,
        280, 317, 322, 341, 356, 403, 409, 413, 458, 465, 471, 472, 474,
        476, 479, 486, 497, 531, 533, 536, 596, 597, 613, 623, 632, 634,
        635, 636, 673, 679, 686, 727, 728, 732, 741, 746, 748, 750, 752,
        760, 763, 769, 777, 794, 801, 818, 819, 826, 827, 828, 877, 907,
        914, 919, 979, 983, 1011, 1019, 1020, 1021, 1031, 1035, 1047,
        1054, 1058, 1079, 1091, 1096, 1097, 1189, 1193, 1229, 1246,
        1273, 1277, 1285, 1286, 1293, 1296, 1302, 1310, 1312, 1319,
        1330, 1344, 1347, 1352, 1356, 1364, 1370, 1371, 1374, 1386,
        1392, 1393, 1419, 1442, 1443, 1476, 1485, 1486, 1498, 1501,
        1544, 1561, 1589, 1593, 1645, 1649, 1651, 1653, 1656, 1657,
        1744, 1747, 1769, 1798, 1825, 1826, 1855, 1863, 1864, 1889,
        1899, 1929, 1934, 1948, 1949, 2001, 2038, 2044, 2049, 2066,
        2090, 2095, 2098, 2099, 2124, 2127, 2133, 2141, 2153, 2156,
        2169, 2181, 2198, 2202, 2203, 2214, 2221, 2268, 2271, 2303,
        2305, 2311, 2343, 2358, 2361, 2390, 2391, 2412, 2423, 2424,
        2425, 2430, 2432, 2445, 2469, 2475, 2492, 2503, 2505, 2507,
        2508, 2509, 2511, 2515, 2516, 2582, 2597, 2603, 2635, 2659,
        2666, 2699, 2709, 2717, 2724, 2726, 2729, 2734, 2790, 2795,
        2804, 2805, 2808, 2810, 2811, 2812, 2815, 2820, 2864, 2868,
        2893, 2927, 2950, 2954, 2992, 3000, 3006, 3010, 3054, 3058,
        3064, 3105, 3193, 3200, 3229, 3237, 3239, 3242, 3250, 3271,
        3273, 3274, 3282, 3298, 3315, 3328, 3333,
    ),
}


def digest(indices):
    payload = ",".join(str(index) for index in indices).encode()
    return hashlib.sha256(payload).hexdigest()


def positive_indices(survivors):
    return tuple(
        index
        for index, configuration in enumerate(survivors)
        if refines(
            tuple(configuration[0]),
            tuple(configuration[1]),
            tuple(tuple(row) for row in configuration[2]),
            POSITIVE,
        )
    )


def recompute(side, indices, survivors, timeout_ms):
    retained = "min" if side == "lmin_only" else "max"
    sat = []
    unknown = []
    started = time.monotonic()
    for offset, index in enumerate(indices, 1):
        solver, _, _ = build_ablation(index, survivors[index], retained)
        solver.set(timeout=timeout_ms)
        verdict = solver.check()
        if verdict == z3.sat:
            sat.append(index)
        elif verdict == z3.unknown:
            unknown.append(index)
        if offset % 200 == 0:
            print(
                f"{side}: {offset}/{len(indices)}; "
                f"sat={len(sat)} unknown={len(unknown)}",
                file=sys.stderr,
            )
    return tuple(sat), tuple(unknown), round(time.monotonic() - started, 3)


def length_tally(indices, survivors):
    counts = Counter(
        (len(survivors[index][0]), len(survivors[index][1]))
        for index in indices
    )
    return {
        f"{row_strata}_by_{column_strata}": count
        for (row_strata, column_strata), count in sorted(counts.items())
    }


def rich_column_signature(configuration):
    """Return the positive type's rich-player Lmax-column data."""
    _, columns, table = configuration
    low_column_count = next(
        stop for stop in range(1, len(columns) + 1) if sum(columns[:stop]) == 2
    )
    rich_column = next(column for column, value in enumerate(table[-1]) if value)
    return {
        "low_column_count": low_column_count,
        "rich_column": rich_column,
        "rich_column_relative_to_high_block": rich_column - low_column_count,
        "rich_column_size": columns[rich_column],
        "P_players_sharing_rich_column": sum(
            row[rich_column] for row in table[:-1]
        ),
    }


def lmax_side_case(configuration):
    """The empirical two-case handover rule extracted from the exact census.

    In this case the complete Lmax packet is the selected one-sided
    contradiction.  Outside it, the complete Lmin packet is selected.
    """
    signature = rich_column_signature(configuration)
    isolated = signature["P_players_sharing_rich_column"] == 0
    early_two_two_tie = (
        tuple(configuration[1]) == (1, 1, 2, 2)
        and signature["rich_column"] == 2
    )
    return isolated or early_two_two_tie


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--recompute", action="store_true")
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    args = parser.parse_args()

    triage_bytes = args.triage.read_bytes()
    survivors = json.loads(triage_bytes)["survivors"]
    indices = positive_indices(survivors)
    assert len(indices) == 1659
    assert all(set(values) <= set(indices) for values in EXPECTED.values())

    results = {}
    for side, expected in EXPECTED.items():
        if args.recompute:
            actual, unknown, seconds = recompute(
                side, indices, survivors, args.timeout_ms
            )
            assert not unknown
            assert actual == expected
        else:
            actual, unknown, seconds = expected, (), None
        results[side] = {
            "verdicts_recomputed_in_this_invocation": args.recompute,
            "sat_count": len(actual),
            "unknown_count": len(unknown),
            "sat_survivor_indices": actual,
            "sat_indices_sha256": digest(actual),
            "stratum_count_tally": length_tally(actual, survivors),
            "elapsed_seconds": seconds,
        }

    overlap = sorted(set(EXPECTED["lmin_only"]) & set(EXPECTED["lmax_only"]))
    assert not overlap
    # The 295 one-sided false survivors obey a particularly short separator.
    # Consequently this rule chooses an UNSAT one-sided packet on every one of
    # the 1,659 configurations, conditional on the frozen solver census.
    assert all(lmax_side_case(survivors[index]) for index in EXPECTED["lmin_only"])
    assert not any(
        lmax_side_case(survivors[index]) for index in EXPECTED["lmax_only"]
    )
    selected_packet_tally = Counter(
        "lmax" if lmax_side_case(survivors[index]) else "lmin"
        for index in indices
    )
    report = {
        "status": "PASS",
        "claim_scope": (
            "conditional solver census on the audited positive refinement universe; "
            "not independent rational infeasibility evidence"
        ),
        "coarse_type": POSITIVE["name"],
        "triage32_sha256": hashlib.sha256(triage_bytes).hexdigest(),
        "positive_hand_net_refinement_count": len(indices),
        "timeout_ms_per_instance": args.timeout_ms,
        "results": results,
        "intersection_of_one_sided_sat_sets": overlap,
        "intersection_count": len(overlap),
        "finite_disjunction": (
            "every audited refinement is UNSAT under at least one complete "
            "one-sided staged packet"
        ),
        "empirical_handover_rule": {
            "choose_complete_lmax_packet_when": (
                "the rich player is alone in its Lmax stratum, or the Lmax "
                "composition is (1,1,2,2) and the rich player lies in the "
                "first size-two high block"
            ),
            "choose_complete_lmin_packet_otherwise": True,
            "selected_packet_tally_on_all_positive_refinements": dict(
                sorted(selected_packet_tally.items())
            ),
            "all_lmin_only_sat_cases_choose_lmax": True,
            "all_lmax_only_sat_cases_choose_lmin": True,
            "status": (
                "exact separator of frozen solver verdicts; human structural "
                "proof of each selected one-sided contradiction remains open"
            ),
        },
        "interpretation": (
            "the remaining human-proof target is a disjunctive one-sided "
            "classification, not necessarily a within-configuration hybrid "
            "coupling inequality"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
