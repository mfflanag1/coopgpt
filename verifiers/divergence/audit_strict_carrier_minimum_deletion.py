#!/usr/bin/env python3
r"""Exact minimum-deletion audit for strict carrier-cycle packets.

For every strict-loss nongainer carrier cycle in the full-menu
all-unaffordable branch, enumerate first one complete staged Lmin support and
then the entire Lmin-tight menu.  Retain rows which contain the cycle, omit at
least one gainer, and exclude at least one nongainer.  For a row ``I`` write
``P`` for its excluded nongainers and ``A`` for its omitted gainers.  This
script checks exactly the two lower certificates (PXC6) and (PXC11).  It
records simultaneous closure in the n=6 archive and exactifies a new n=7
control which refutes simultaneous closure while preserving their maximum.

The output is a finite archive theorem and hostile-control replay, not an
all-n selection theorem.  In particular, the script retains every arbitrary
row on which the target reserve is negative as a falsifier for the stronger
"every proper carrier row closes" statement.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import (  # noqa: E402
    carriers,
    directed_cycles,
    full_tight_support,
)
from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
)
from verify_labelled_branch_duals import CASES, verify_complete_selection  # noqa: E402


N7_SIMULTANEOUS_COUNTEREXAMPLE = {
    "name": "minimum_deletion_simultaneous_certificate_counterexample",
    "generators": (
        (1, 5, 0, 7, 0, 0, 0),
        (2, 0, 3, 1, 2, 3, 2),
        (0, 2, 0, 0, 5, 4, 2),
        (0, 1, 5, 6, 0, 1, 0),
    ),
    "x": (F(7, 4), F(7, 4), F(7, 4), F(17, 8), F(7, 4), F(17, 8), F(7, 4)),
    "z": (F(5, 3), F(5, 3), F(5, 3), F(2), F(2), F(2), F(2)),
}


def reserve_row(x, z, support_row, cycle, target):
    n = len(x)
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = tuple(i for i in range(n) if z[i] <= x[i])
    omitted_gainers = tuple(i for i in gainers if not support_row >> i & 1)
    excluded = tuple(i for i in nongainers if not support_row >> i & 1)
    if not omitted_gainers or not excluded:
        return None
    if any(not support_row >> i & 1 for i in cycle):
        return None

    p = len(excluded)
    coefficient = F(len(gainers) * n, (n - p) * (p + 1))
    total = sum(x, F(0))
    total_gain = sum((z[i] - x[i] for i in gainers), F(0))
    actual = (
        (F(1) - target) * total
        - total_gain
        - coefficient * sum((z[i] for i in excluded), F(0))
    )
    payment = coalition_sum(z, support_row) - coalition_sum(x, support_row)
    if payment < 0:
        raise AssertionError("an Lmin-tight row has negative comparison payment")
    comparison = (
        (F(1) - target) * total
        - total_gain
        - coefficient * sum((x[i] for i in excluded), F(0))
        + coefficient
        * sum((z[i] - x[i] for i in omitted_gainers), F(0))
    )
    if actual - comparison != coefficient * payment:
        raise AssertionError("PXC10 comparison decomposition failed")

    retained = tuple(i for i in nongainers if support_row >> i & 1)
    block = tuple(cycle)
    extra = tuple(i for i in retained if i not in set(block))
    maximum = z[block[0]]
    if any(z[i] != maximum for i in block):
        raise AssertionError("carrier cycle is not one Lmax root block")
    next_level = max((z[i] for i in excluded), default=F(0))
    ordered = (
        len(block) * maximum
        + sum((z[i] for i in extra), F(0))
        + sum((x[i] for i in gainers), F(0))
        - target * total
        - p * max(coefficient - 1, F(0)) * next_level
    )
    if ordered > actual:
        raise AssertionError("PXC6 ordered-cut lower bound failed")
    return {
        "support_row": support_row,
        "excluded_nongainers": list(excluded),
        "omitted_gainers": list(omitted_gainers),
        "p": p,
        "coefficient": str(coefficient),
        "actual_target_reserve": str(actual),
        "comparison_lower_bound": str(comparison),
        "ordered_cut_lower_bound": str(ordered),
        "comparison_payment": str(payment),
    }


def audit_pair(
    source,
    trail,
    values,
    x,
    z,
    selected_support,
    target,
    counters,
    profiles,
    require_both=False,
):
    n = len(x)
    if target != F(n, n * n // 4):
        raise AssertionError("wrong sharp target for player count")
    if any(coalition_sum(x, coalition) != values[coalition] for coalition in selected_support):
        raise AssertionError("selected staged support contains a non-tight row")
    full_support = full_tight_support(values, x)
    roots = maximum_overlap_roots(x, z)
    gates = tuple(solve_labelled_cover(full_support, root, n) for root in roots)
    if any(gate["affordable"] for gate in gates):
        return []
    graph = {
        gate["root"]: tuple(carrier for carrier in carriers(gate) if carrier in roots)
        for gate in gates
    }
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = set(range(n)) - set(gainers)
    negative_rows = []
    for cycle in directed_cycles(graph):
        if not set(cycle) <= nongainers or x[cycle[0]] <= z[cycle[0]]:
            continue
        rows = tuple(
            row
            for coalition in selected_support
            if (row := reserve_row(x, z, coalition, cycle, target)) is not None
        )
        if not rows:
            raise AssertionError((source, trail, cycle, "no admissible carrier row"))
        minimum_p = min(row["p"] for row in rows)
        minimum_rows = tuple(row for row in rows if row["p"] == minimum_p)
        all_both = not any(
            F(row["comparison_lower_bound"]) < 0
            or F(row["ordered_cut_lower_bound"]) < 0
            for row in minimum_rows
        )
        all_either = all(
            max(
                F(row["comparison_lower_bound"]),
                F(row["ordered_cut_lower_bound"]),
            )
            >= 0
            for row in minimum_rows
        )
        if not all_either:
            raise AssertionError((source, trail, cycle, "minimum-deletion max-certificate failure"))
        if require_both and not all_both:
            raise AssertionError((source, trail, cycle, "minimum-deletion failure"))

        counters["strict_carrier_cycles"] += 1
        counters["admissible_rows"] += len(rows)
        counters["minimum_deletion_rows"] += len(minimum_rows)
        counters["cycles_all_minimum_rows_close_either_certificate"] += all_either
        counters["cycles_all_minimum_rows_close_both_certificates"] += all_both
        counters["cycles_some_minimum_row_closes_both_certificates"] += any(
            F(row["comparison_lower_bound"]) >= 0
            and F(row["ordered_cut_lower_bound"]) >= 0
            for row in minimum_rows
        )
        counters["arbitrary_negative_reserve_rows"] += sum(
            F(row["actual_target_reserve"]) < 0 for row in rows
        )
        counters["arbitrary_rows_closing_both_certificates"] += sum(
            F(row["comparison_lower_bound"]) >= 0
            and F(row["ordered_cut_lower_bound"]) >= 0
            for row in rows
        )
        profiles[
            (
                len(gainers),
                len(cycle),
                minimum_p,
                min(len(row["omitted_gainers"]) for row in minimum_rows),
                max(len(row["omitted_gainers"]) for row in minimum_rows),
            )
        ] += 1
        negative_rows.extend(
            {
                "source": source,
                "trail": trail,
                "cycle": list(cycle),
                **row,
            }
            for row in rows
            if F(row["actual_target_reserve"]) < 0
        )
    return negative_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    extracted_counters, extracted_profiles = Counter(), Counter()
    full_counters, full_profiles = Counter(), Counter()
    extracted_negative_rows, full_negative_rows = [], []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            if len(x) != 6:
                continue
            extracted_negative_rows.extend(
                audit_pair(
                    path.name,
                    trail,
                    values,
                    x,
                    z,
                    complete_lmin_support(values, x),
                    F(2, 3),
                    extracted_counters,
                    extracted_profiles,
                    require_both=True,
                )
            )
            full_negative_rows.extend(
                audit_pair(
                    path.name,
                    trail,
                    values,
                    x,
                    z,
                    full_tight_support(values, x),
                    F(2, 3),
                    full_counters,
                    full_profiles,
                    require_both=True,
                )
            )

    hostile = []
    for case in CASES:
        if len(case["x"]) != 7:
            continue
        x, z = tuple(case["x"]), tuple(case["z"])
        generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
        values = tuple(
            min(coalition_sum(generator, coalition) for generator in generators)
            for coalition in range(1 << 7)
        )
        case_counters, case_profiles = Counter(), Counter()
        found = audit_pair(
            case["name"],
            "fixed hostile control",
            values,
            x,
            z,
            tuple(case["support_x"]),
            F(7, 12),
            case_counters,
            case_profiles,
        )
        hostile.append(
            {
                "name": case["name"],
                **dict(case_counters),
                "negative_arbitrary_rows": found,
            }
        )

    case = N7_SIMULTANEOUS_COUNTEREXAMPLE
    generators = tuple(tuple(map(F, row)) for row in case["generators"])
    values = tuple(
        min(coalition_sum(generator, coalition) for generator in generators)
        for coalition in range(1 << 7)
    )
    if any(values[1 << i] != 0 for i in range(7)):
        raise AssertionError("new control is not singleton-normalized")
    for generator in generators:
        if sum(generator, F(0)) != values[-1] or any(
            coalition_sum(generator, coalition) < values[coalition]
            for coalition in range(1 << 7)
        ):
            raise AssertionError("lower-envelope generator is not a core point")
    x, z = case["x"], case["z"]
    support_x = full_tight_support(values, x)
    support_z = full_tight_support(values, z)
    verify_complete_selection(values, x, "min", support_x)
    verify_complete_selection(values, z, "max", support_z)
    case_counters, case_profiles = Counter(), Counter()
    found = audit_pair(
        case["name"],
        "exact lower-envelope control",
        values,
        x,
        z,
        support_x,
        F(7, 12),
        case_counters,
        case_profiles,
    )
    roots = maximum_overlap_roots(x, z)
    gates = tuple(solve_labelled_cover(support_x, root, 7) for root in roots)
    graph = {
        gate["root"]: tuple(carrier for carrier in carriers(gate) if carrier in roots)
        for gate in gates
    }
    cycles = directed_cycles(graph)
    if roots != (3, 5) or any(gate["affordable"] for gate in gates) or cycles != ((3, 5),):
        raise AssertionError("new n=7 control lost its unaffordable carrier cycle")
    control_rows = tuple(
        row
        for coalition in support_x
        if (row := reserve_row(x, z, coalition, cycles[0], F(7, 12))) is not None
    )
    if len(control_rows) != 2 or any(
        F(row["actual_target_reserve"]) != F(13, 24)
        or F(row["comparison_lower_bound"]) != F(13, 24)
        or F(row["ordered_cut_lower_bound"]) != F(-1, 12)
        for row in control_rows
    ):
        raise AssertionError("new n=7 two-colour margins changed")
    hostile.append(
        {
            "name": case["name"],
            "generators": [[str(q) for q in row] for row in generators],
            "lmin": [str(q) for q in x],
            "lmax": [str(q) for q in z],
            "overlap": str(sum((min(x[i], z[i]) for i in range(7)), F(0))),
            "maximum_overlap_roots": list(roots),
            "minimum_deletion_row_details": list(control_rows),
            **dict(case_counters),
            "negative_arbitrary_rows": found,
            "interpretation": (
                "every minimum-deletion row has PXC11=13/24 but PXC6=-1/12; "
                "this refutes simultaneous closure, not the max-certificate"
            ),
        }
    )

    report = {
        "status": "exact finite archive theorem; not an all-n selection proof",
        "inputs": [path.name for path in args.paths],
        "statement_checked": (
            "in the n=6 archive, every minimum-deletion row simultaneously has "
            "nonnegative PXC6 and PXC11 lower certificates; a new exact n=7 "
            "control refutes simultaneous closure but every minimum row retains "
            "a nonnegative max(PXC6,PXC11) certificate"
        ),
        "n6_extracted_support_counts": dict(extracted_counters),
        "n6_full_tight_menu_counts": dict(full_counters),
        "extracted_cycle_profiles_g_cycleSize_p_minA_maxA": {
            ",".join(map(str, key)): value
            for key, value in sorted(extracted_profiles.items())
        },
        "full_menu_cycle_profiles_g_cycleSize_p_minA_maxA": {
            ",".join(map(str, key)): value
            for key, value in sorted(full_profiles.items())
        },
        "negative_rows_in_extracted_support": extracted_negative_rows,
        "negative_rows_in_full_tight_menu": full_negative_rows,
        "n7_hostile_and_sharp_controls": hostile,
        "limitations": (
            "the n=6 count uses two archived harvest files and one extracted "
            "complete staged support per record; the n=7 replay is a fixed "
            "control family; neither archive is exhaustive in all exact games"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
