#!/usr/bin/env python3
r"""Exact archive audit of the carrier-separator payment branch.

This is a discovery/falsification audit, not a proof of the all-n overlap
bound.  For each archived six-player pair for which every maximum-overlap
root is unaffordable on the *full* Lmin-tight menu, it enumerates every
full-menu carrier arrow r -> c with z_c < z_r and every Lmax-tight separator
D containing r but omitting c.

The complement C=N\D satisfies z(C)-x(C)=x(D)-z(D)>0.  We therefore test C
in the already proved multistage direct-gluing identity, keeping separately
the comparison payment, the cardinality base, and the order residual.  Rows
with no descending carrier arrow are classified through carrier cycles.
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

from audit_cover_to_direct_handover import direct_witnesses  # noqa: E402
from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
)
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402
from lexsimplex import lex_point  # noqa: E402


def full_tight_support(values, allocation):
    full = (1 << len(allocation)) - 1
    return tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(allocation, coalition) == values[coalition]
    )


def carriers(audit):
    if len(audit["tight_rooted_pairs"]) == 1:
        return tuple(audit["tight_rooted_pairs"])
    return tuple(audit["common_nonpair_carriers"])


def directed_cycles(graph):
    """Return canonical simple directed cycles of a finite digraph."""
    found = set()
    vertices = tuple(sorted(graph))
    for start in vertices:
        stack = [(start, (start,))]
        while stack:
            vertex, path = stack.pop()
            for nxt in graph.get(vertex, ()):
                if nxt == start and len(path) >= 2:
                    rotations = tuple(path[i:] + path[:i] for i in range(len(path)))
                    found.add(min(rotations))
                elif nxt in graph and nxt not in path and len(path) < len(vertices):
                    stack.append((nxt, path + (nxt,)))
    return tuple(sorted(found))


def separator_rows(values, x, z, root, carrier, target):
    n = len(x)
    full = (1 << n) - 1
    z_tight = full_tight_support(values, z)
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = tuple(i for i in range(n) if z[i] <= x[i])
    rows = []
    for separator in z_tight:
        if not (separator >> root & 1) or separator >> carrier & 1:
            continue
        complement = full ^ separator
        payment = coalition_sum(z, complement) - coalition_sum(x, complement)
        if payment <= 0:
            raise AssertionError(("separator complement is not strict", root, carrier))
        p_set = tuple(i for i in nongainers if separator >> i & 1)
        h_set = tuple(i for i in nongainers if complement >> i & 1)
        j_set = tuple(i for i in gainers if complement >> i & 1)
        # The current master theorem assumes all three sign blocks are
        # nonempty and J is a proper subset of the gainers.
        admissible = bool(p_set and h_set and len(j_set) < len(gainers))
        row = None
        if admissible:
            row = master_identity(x, z, p_set, gainers, h_set, j_set)
            if F(row["comparison_slack"]) != payment:
                raise AssertionError("complement payment mismatch")
        rows.append(
            {
                "root": root,
                "carrier": carrier,
                "separator": separator,
                "complement": complement,
                "P": list(p_set),
                "H": list(h_set),
                "G": list(gainers),
                "J": list(j_set),
                "payment": str(payment),
                "master_admissible": admissible,
                "base": row["base_bound_ratio"] if row else None,
                "residual_sum": (
                    str(F(row["x_order_residual"]) + F(row["z_order_residual"]))
                    if row
                    else None
                ),
                "packet_hits_interval": row["packet_hits_interval"] if row else False,
                "target_reached_by_master": (
                    bool(
                        F(row["base_bound_ratio"]) >= target
                        and F(row["comparison_slack"]) >= 0
                        and F(row["x_order_residual"])
                        + F(row["z_order_residual"])
                        >= 0
                    )
                    if row
                    else False
                ),
            }
        )
    if not rows:
        raise AssertionError(("missing Lmax separator", root, carrier))
    return rows


def partial_cycle_separator_rows(values, x, z, cycle, target):
    """Test complements of Lmax-tight coalitions separating a flat cycle."""
    n = len(x)
    full = (1 << n) - 1
    cycle_mask = sum(1 << i for i in cycle)
    rows = []
    for separator in full_tight_support(values, z):
        if (separator & cycle_mask) in (0, cycle_mask):
            continue
        complement = full ^ separator
        # Pick an included root and omitted carrier.  The cycle implication
        # proves strictness for every such partial separator.
        included = next(i for i in cycle if separator >> i & 1)
        omitted = next(i for i in cycle if not (separator >> i & 1))
        payment = coalition_sum(z, complement) - coalition_sum(x, complement)
        if payment <= 0:
            raise AssertionError(("partial cycle separator not strict", cycle))
        gainers = tuple(i for i in range(n) if z[i] > x[i])
        nongainers = tuple(i for i in range(n) if z[i] <= x[i])
        p_set = tuple(i for i in nongainers if separator >> i & 1)
        h_set = tuple(i for i in nongainers if complement >> i & 1)
        j_set = tuple(i for i in gainers if complement >> i & 1)
        admissible = bool(p_set and h_set and len(j_set) < len(gainers))
        master = None
        residual_sum = None
        if admissible:
            master = master_identity(x, z, p_set, gainers, h_set, j_set)
            if F(master["comparison_slack"]) != payment:
                raise AssertionError("partial separator payment mismatch")
            residual_sum = F(master["x_order_residual"]) + F(
                master["z_order_residual"]
            )
        rows.append(
            {
                "included_root": included,
                "omitted_carrier": omitted,
                "separator": separator,
                "complement": complement,
                "payment": str(payment),
                "master_admissible": admissible,
                "target_reached_by_master": bool(
                    master
                    and residual_sum >= 0
                    and F(master["actual_overlap_ratio"]) >= target
                ),
                "base_reaches_target": bool(
                    master and F(master["base_bound_ratio"]) >= target
                ),
                "base": master["base_bound_ratio"] if master else None,
                "residual_sum": (
                    str(residual_sum)
                    if master
                    else None
                ),
            }
        )
    return rows


def canonical_block_expansion(values, cycle):
    """Expand the quotient role game by the canonical full-block rule."""
    n = len(values).bit_length() - 1
    full_cycle = sum(1 << i for i in cycle)
    expanded = []
    for coalition in range(1 << n):
        completed = coalition & ~full_cycle
        if coalition & full_cycle == full_cycle:
            completed |= full_cycle
        expanded.append(values[completed])
    return tuple(expanded)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    target = F(2, 3)
    counts = Counter()
    exceptional = []
    block_expansion_controls = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            if len(x) != 6:
                continue
            roots = maximum_overlap_roots(x, z)
            x_tight = full_tight_support(values, x)
            audits = tuple(solve_labelled_cover(x_tight, root, 6) for root in roots)
            if any(audit["affordable"] for audit in audits):
                continue
            counts["all_full_menu_unaffordable_rows"] += 1
            graph = {
                audit["root"]: tuple(c for c in carriers(audit) if c in roots)
                for audit in audits
            }
            descending = []
            for audit in audits:
                root = audit["root"]
                for carrier in carriers(audit):
                    if z[carrier] < z[root]:
                        descending.extend(
                            separator_rows(values, x, z, root, carrier, target)
                        )
            if descending:
                counts["rows_with_separator_branch"] += 1
                admissible = [row for row in descending if row["master_admissible"]]
                target_rows = [row for row in descending if row["target_reached_by_master"]]
                counts["separator_rows_with_admissible_complement_master"] += bool(admissible)
                counts["separator_rows_closed_by_complement_master"] += bool(target_rows)
                if not target_rows:
                    exceptional.append(
                        {
                            "source": path.name,
                            "trail": trail,
                            "x": [str(value) for value in x],
                            "z": [str(value) for value in z],
                            "roots": list(roots),
                            "kind": "separator complement does not close target",
                            "best_rows": sorted(
                                descending,
                                key=lambda row: (
                                    row["target_reached_by_master"],
                                    F(row["base"]) if row["base"] else F(-1),
                                    F(row["payment"]),
                                ),
                                reverse=True,
                            )[:5],
                        }
                    )
            else:
                counts["rows_without_separator_branch"] += 1
                cycles = directed_cycles(graph)
                if not cycles:
                    raise AssertionError((path.name, trail, "alternative has neither branch"))
                cycle_data = []
                z_tight = full_tight_support(values, z)
                for cycle in cycles:
                    x_levels = {x[i] for i in cycle}
                    z_levels = {z[i] for i in cycle}
                    signs = {"g" if z[i] > x[i] else "n" for i in cycle}
                    if len(x_levels) != 1 or len(z_levels) != 1 or len(signs) != 1:
                        raise AssertionError(("cycle coherence failure", cycle))
                    cycle_mask = sum(1 << i for i in cycle)
                    z_separators = [
                        coalition
                        for coalition in z_tight
                        if (coalition & cycle_mask) not in (0, cycle_mask)
                    ]
                    cycle_data.append(
                        {
                            "cycle": list(cycle),
                            "sign": next(iter(signs)),
                            "lmax_module": not z_separators,
                            "lmax_separator_count": len(z_separators),
                        }
                    )
                    if next(iter(signs)) == "n":
                        loss = x[cycle[0]] - z[cycle[0]]
                        if loss > 0:
                            counts["strict_loss_nongainer_cycles"] += 1
                            for gainer in (
                                i for i in range(6) if z[i] > x[i]
                            ):
                                omitting = [
                                    coalition
                                    for coalition in x_tight
                                    if coalition & cycle_mask == cycle_mask
                                    and not (coalition >> gainer & 1)
                                ]
                                if not omitting:
                                    raise AssertionError(
                                        (
                                            path.name,
                                            trail,
                                            cycle,
                                            gainer,
                                            "strict-loss cycle has no proper gainer omission",
                                        )
                                    )
                                counts[
                                    "strict_loss_gainer_omission_checks"
                                ] += 1
                        else:
                            counts["tied_loss_nongainer_cycles"] += 1
                    counts["cycles_with_zero_coalition_worth"] += (
                        values[cycle_mask] == 0
                    )
                    counts["cycles_with_positive_coalition_worth"] += (
                        values[cycle_mask] > 0
                    )
                    counts["cycles_that_are_common_face_modules"] += not z_separators
                    counts["cycles_separated_by_lmax_face"] += bool(z_separators)
                    if not z_separators and len(block_expansion_controls) < 6:
                        expanded_values = canonical_block_expansion(values, cycle)
                        recomputed_x = tuple(lex_point(6, expanded_values, "min"))
                        recomputed_z = tuple(lex_point(6, expanded_values, "max"))
                        if recomputed_x != tuple(x) or recomputed_z != tuple(z):
                            raise AssertionError(
                                ("canonical block expansion selection failure", trail, cycle)
                            )
                        block_expansion_controls.append(
                            {
                                "source": path.name,
                                "trail": trail,
                                "cycle": list(cycle),
                                "lmin": [str(value) for value in recomputed_x],
                                "lmax": [str(value) for value in recomputed_z],
                            }
                        )
                counts["cycle_rows_with_nongainer_cycle"] += any(
                    row["sign"] == "n" for row in cycle_data
                )
                counts["cycle_rows_with_gainer_cycle"] += any(
                    row["sign"] == "g" for row in cycle_data
                )
                has_common_module = any(row["lmax_module"] for row in cycle_data)
                has_separated_cycle = any(
                    not row["lmax_module"] for row in cycle_data
                )
                counts["cycle_rows_with_common_module"] += has_common_module
                counts["cycle_rows_without_common_module"] += not has_common_module
                counts["cycle_rows_with_separated_cycle"] += has_separated_cycle
                if not has_common_module and not has_separated_cycle:
                    raise AssertionError(
                        (path.name, trail, "irreducible cycle row lacks separator")
                    )
                selected_support = complete_lmin_support(values, x)
                direct = direct_witnesses(x, z, selected_support, target)
                counts["cycle_rows_closed_by_some_direct_packet"] += bool(direct)
                cycle_direct = []
                cycle_tight_direct = []
                containing_cycle_direct = []
                closure_direct = []
                partial_separator_rows = []
                for cycle in cycles:
                    witnesses = direct_witnesses(
                        x, z, selected_support, target, allowed_h=cycle
                    )
                    cycle_direct.extend(witnesses)
                    cycle_tight_direct.extend(
                        row for row in witnesses if row["comparison_is_lmin_tight"]
                    )
                    containing_cycle_direct.extend(
                        row
                        for row in direct
                        if set(cycle) <= set(row["H"])
                        and row["comparison_is_lmin_tight"]
                    )
                    meeting = [
                        coalition
                        for coalition in x_tight
                        if coalition >> cycle[0] & 1
                    ]
                    closure_mask = (1 << 6) - 1
                    for coalition in meeting:
                        closure_mask &= coalition
                    nongainer_closure = tuple(
                        i
                        for i in range(6)
                        if closure_mask >> i & 1 and z[i] <= x[i]
                    )
                    closure_direct.extend(
                        row
                        for row in direct_witnesses(
                            x,
                            z,
                            selected_support,
                            target,
                            allowed_h=nongainer_closure,
                        )
                        if row["comparison_is_lmin_tight"]
                    )
                    partial_separator_rows.extend(
                        partial_cycle_separator_rows(values, x, z, cycle, target)
                    )
                counts["cycle_rows_closed_with_cycle_as_H"] += bool(cycle_direct)
                counts["cycle_rows_closed_tightly_with_cycle_as_H"] += bool(
                    cycle_tight_direct
                )
                counts["cycle_rows_closed_by_tight_nongainer_superset"] += bool(
                    containing_cycle_direct
                )
                counts["cycle_rows_closed_by_full_carrier_closure_as_H"] += bool(
                    closure_direct
                )
                counts["cycle_rows_with_partial_separator"] += bool(
                    partial_separator_rows
                )
                counts["cycle_rows_closed_by_partial_separator_complement"] += any(
                    row["target_reached_by_master"] for row in partial_separator_rows
                )
                if not has_common_module:
                    counts["role_irreducible_rows"] += 1
                    has_tied_cycle = any(
                        row["sign"] == "n"
                        and x[row["cycle"][0]] == z[row["cycle"][0]]
                        for row in cycle_data
                    )
                    counts["role_irreducible_rows_with_tied_cycle"] += (
                        has_tied_cycle
                    )
                    counts["role_irreducible_rows_with_strict_cycle_only"] += (
                        not has_tied_cycle
                    )
                    counts["role_irreducible_rows_closed_with_cycle_as_H"] += bool(
                        cycle_tight_direct
                    )
                    counts[
                        "role_irreducible_rows_closed_by_tight_nongainer_superset"
                    ] += bool(containing_cycle_direct)
                    counts[
                        "role_irreducible_rows_closed_by_one_separator_complement"
                    ] += any(
                        row["target_reached_by_master"]
                        for row in partial_separator_rows
                    )
                if containing_cycle_direct:
                    least_extra = min(
                        len(row["H"]) - len(cycle)
                        for cycle in cycles
                        for row in containing_cycle_direct
                        if set(cycle) <= set(row["H"])
                    )
                    counts[f"cycle_rows_needing_{least_extra}_extra_nongainers"] += 1
                if not direct:
                    exceptional.append(
                        {
                            "source": path.name,
                            "trail": trail,
                            "x": [str(value) for value in x],
                            "z": [str(value) for value in z],
                            "roots": list(roots),
                            "kind": "cycle row has no direct packet",
                            "cycles": cycle_data,
                        }
                    )
                elif not cycle_tight_direct:
                    exceptional.append(
                        {
                            "source": path.name,
                            "trail": trail,
                            "x": [str(value) for value in x],
                            "z": [str(value) for value in z],
                            "roots": list(roots),
                            "kind": "cycle itself has no tight target-reaching direct packet",
                            "cycles": cycle_data,
                            "partial_separator_rows": partial_separator_rows,
                            "some_direct_witness": direct[0],
                        }
                    )

    n7_controls = []
    for case in CASES:
        if len(case["x"]) != 7:
            continue
        n = 7
        x, z = tuple(case["x"]), tuple(case["z"])
        generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
        values = tuple(
            min(coalition_sum(generator, coalition) for generator in generators)
            for coalition in range(1 << n)
        )
        x_tight = full_tight_support(values, x)
        z_tight = full_tight_support(values, z)
        roots = maximum_overlap_roots(x, z)
        audits = tuple(solve_labelled_cover(x_tight, root, n) for root in roots)
        all_unaffordable = not any(audit["affordable"] for audit in audits)
        row = {
            "name": case["name"],
            "maximum_overlap_roots": list(roots),
            "all_full_menu_unaffordable": all_unaffordable,
        }
        if all_unaffordable:
            graph = {
                audit["root"]: tuple(c for c in carriers(audit) if c in roots)
                for audit in audits
            }
            descending = [
                (audit["root"], carrier)
                for audit in audits
                for carrier in carriers(audit)
                if z[carrier] < z[audit["root"]]
            ]
            cycles = directed_cycles(graph)
            cycle_rows = []
            for cycle in cycles:
                cycle_mask = sum(1 << i for i in cycle)
                separators = [
                    coalition
                    for coalition in z_tight
                    if (coalition & cycle_mask) not in (0, cycle_mask)
                ]
                cycle_rows.append(
                    {
                        "cycle": list(cycle),
                        "sign": "g" if z[cycle[0]] > x[cycle[0]] else "n",
                        "lmax_module": not separators,
                        "lmax_separator_count": len(separators),
                    }
                )
            direct = direct_witnesses(x, z, x_tight, F(7, 12))
            row.update(
                {
                    "descending_carrier_arrows": [list(edge) for edge in descending],
                    "cycles": cycle_rows,
                    "target_reaching_direct_packet": bool(direct),
                }
            )
            if not descending and not cycles:
                raise AssertionError((case["name"], "n7 alternative failure"))
        n7_controls.append(row)

    report = {
        "status": "exact-rational discovery/falsification audit",
        **dict(counts),
        "separator_fact": (
            "if r->c is a full Lmin carrier and z_c<z_r, every Lmax-tight "
            "separator D containing r and omitting c has x(D)>z(D), so its "
            "complement has strict positive direct-comparison payment"
        ),
        "role_induction_fact": (
            "for the weighted-role formulation, a cycle that is a tight-face "
            "module at both selectors contracts to fewer roles with the same "
            "atomic weight, total, overlap, and weighted selectors; hence a "
            "role-minimal counterexample has no common module and every one "
            "of its carrier cycles is split by an Lmax-tight separator"
        ),
        "limitations": (
            "archived n=6 pairs only; complement payment need not satisfy the "
            "direct cardinality or order-residual requirements"
        ),
        "exceptional_rows": exceptional,
        "canonical_block_expansion_controls": block_expansion_controls,
        "n7_hostile_and_sharp_controls": n7_controls,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
