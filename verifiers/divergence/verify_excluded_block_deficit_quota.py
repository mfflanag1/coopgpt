#!/usr/bin/env python3
"""Exact audit of the excluded-block deficit-quota reduction.

Let ``P/G/H`` be the sign blocks in the direct identity, with ``P`` and
``H`` nongainers, and use the maximal proper gainer packet.  If ``T`` is
the common total and ``D=z(G)-x(G)``, then

    U_(g-1)-L_H
      = [pT-nz(P)]/(n-p) - (p+1)D/g
      = n Q(P)/(n-p) - (p+1)D/g,

where ``Q(P)=sum_{i in P}(T/n-z_i)``.  Thus the direct scalar budget closes
if and only if the excluded nongainer block meets an explicit below-mean
Lmax deficit quota.  This is a dimension-free identity, not a theorem that
the complete staged support always contains a quota-meeting block.

The coefficient calculation is the proof.  The six-player archive and the
seven-player full-root-block counterexample are finite regression controls.
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
from verify_cardinality_ranked_support import source_coefficients  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402


N7_LMIN = (F(3), F(7, 2), F(1), F(3), F(2), F(7, 2), F(1))
N7_LMAX = (F(14, 5), F(16, 5), F(2, 5), F(13, 5), F(16, 5), F(16, 5), F(8, 5))
N7_GENERATORS = (
    (F(6), F(7), F(1), F(0), F(2), F(0), F(1)),
    (F(7), F(0), F(0), F(0), F(0), F(10), F(0)),
    (F(0), F(0), F(0), F(5), F(4), F(6), F(2)),
)


def deficit_coefficients(p: int, g: int, h: int):
    """Coefficients after eliminating z(P) by total balance.

    Coordinate order is X_P, X_H, X_G, Z_H, Z_G.
    """

    n = p + g + h
    return (
        F(-1),
        F(-1),
        F(p - g + 1, g),
        F(n, g + h),
        F(n, g + h) - F(p + 1, g),
    )


def quota_row(x, z, p_set, g_set, h_set):
    n = len(x)
    p = len(p_set)
    g = len(g_set)
    if not (p and g and h_set and p + g + len(h_set) == n):
        raise AssertionError("invalid sign partition")
    total = sum(x, F())
    if total != sum(z, F()):
        raise AssertionError("totals differ")
    gain = sum((z[i] - x[i] for i in g_set), F())
    deficit = sum((F(total, n) - z[i] for i in p_set), F())
    required = F((n - p) * (p + 1), n * g) * gain
    quota_margin = deficit - required
    budget_margin = F(n, n - p) * quota_margin
    direct = master_identity(x, z, p_set, g_set, h_set, g_set[:-1])
    replayed = F(direct["residual_budget"]) - F(direct["h_loss"])
    if replayed != budget_margin:
        raise AssertionError(("deficit-quota replay failed", p_set, replayed, budget_margin))
    return {
        "P": list(p_set),
        "p": p,
        "h": len(h_set),
        "z_P": str(sum((z[i] for i in p_set), F())),
        "below_mean_deficit": str(deficit),
        "required_deficit": str(required),
        "quota_margin": str(quota_margin),
        "budget_margin": str(budget_margin),
        "base_bound_ratio": direct["base_bound_ratio"],
        "closes": budget_margin >= 0,
    }


def n7_control():
    values = tuple(
        min(coalition_sum(row, coalition) for row in N7_GENERATORS)
        for coalition in range(1 << 7)
    )
    support = complete_lmin_support(values, N7_LMIN)
    gainers = (4, 6)
    nongainers = (0, 1, 2, 3, 5)
    cycle = {1, 5}
    rows = []
    seen = set()
    for coalition in support:
        h_set = tuple(i for i in nongainers if coalition >> i & 1)
        if not cycle <= set(h_set) or len(h_set) == len(nongainers):
            continue
        p_set = tuple(i for i in nongainers if i not in h_set)
        key = (p_set, h_set)
        if key in seen:
            continue
        seen.add(key)
        row = quota_row(N7_LMIN, N7_LMAX, p_set, gainers, h_set)
        row["support_coalition"] = coalition
        row["H"] = list(h_set)
        rows.append(row)
    rows.sort(key=lambda row: (row["p"], F(row["z_P"]), row["support_coalition"]))
    closing = [row for row in rows if row["closes"]]
    if len(closing) != 1 or closing[0]["P"] != [2]:
        raise AssertionError(("unexpected n=7 quota repair", closing))
    return rows


def n6_archive(paths):
    counts = Counter()
    best_margins = []
    equality_archive_rows = set()
    for path in paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            n = len(x)
            if n != 6:
                continue
            full_support = full_tight_support(values, x)
            selected_support = complete_lmin_support(values, x)
            roots = maximum_overlap_roots(x, z)
            audits = tuple(solve_labelled_cover(full_support, root, n) for root in roots)
            if any(audit["affordable"] for audit in audits):
                continue
            graph = {
                audit["root"]: tuple(
                    carrier for carrier in carriers(audit) if carrier in roots
                )
                for audit in audits
            }
            gainers = tuple(i for i in range(n) if z[i] > x[i])
            nongainers = tuple(i for i in range(n) if z[i] <= x[i])
            for cycle in directed_cycles(graph):
                if not set(cycle) <= set(nongainers):
                    continue
                counts["nongainer_carrier_cycles"] += 1
                cycle_mask = sum(1 << i for i in cycle)
                candidates = {}
                for coalition in selected_support:
                    if coalition & cycle_mask != cycle_mask:
                        continue
                    h_set = tuple(
                        i for i in nongainers if coalition >> i & 1
                    )
                    p_set = tuple(i for i in nongainers if i not in h_set)
                    if not p_set:
                        continue
                    row = quota_row(x, z, p_set, gainers, h_set)
                    row["support_coalition"] = coalition
                    candidates.setdefault(p_set, row)
                counts["distinct_selected_support_blocks"] += len(candidates)
                closing = [row for row in candidates.values() if row["closes"]]
                counts["quota_meeting_selected_support_blocks"] += len(closing)
                if not closing:
                    raise AssertionError((path.name, trail, cycle, "quota support missing"))
                minimum_p = min(row["p"] for row in closing)
                counts[f"cycles_with_minimum_closing_p_{minimum_p}"] += 1
                equality_blocks = [
                    row
                    for row in closing
                    if row["p"] == 2
                    and row["h"] == 2
                    and len(gainers) == 2
                    and F(row["z_P"]) == 0
                    and sum((z[i] - x[i] for i in gainers), F())
                    == sum(x, F()) / 3
                ]
                if equality_blocks:
                    overlap = sum((min(x[i], z[i]) for i in range(n)), F())
                    if overlap != F(2, 3) * sum(x, F()):
                        raise AssertionError((path.name, trail, "direct equality replay"))
                    counts["carrier_direct_equality_cycles"] += 1
                    counts["carrier_direct_equality_selected_blocks"] += len(
                        equality_blocks
                    )
                    equality_archive_rows.add((path.name, trail))
                best = max(closing, key=lambda row: F(row["budget_margin"]))
                best_margins.append(
                    (
                        F(best["budget_margin"]),
                        path.name,
                        trail,
                        cycle,
                        best,
                        len(gainers),
                        sum((z[i] - x[i] for i in gainers), F()) / sum(x, F()),
                    )
                )
    if counts["nongainer_carrier_cycles"] != 420:
        raise AssertionError(("archive cycle count changed", counts))
    sharp = [row for row in best_margins if row[0] == 0]
    representatives = []
    for requested_p in (1, 2):
        match = next(
            (
                row
                for row in sharp
                if row[4]["p"] == requested_p
            ),
            None,
        )
        if match is not None:
            representatives.append(match)
    return {
        "counts": dict(sorted(counts.items())),
        "minimum_best_budget_margin": str(min(row[0] for row in best_margins)),
        "sharp_best_margin_count": len(sharp),
        "sharp_best_margin_representatives": [
            {
                "source": source,
                "trail": trail,
                "cycle": list(cycle),
                "selected_support": support,
            }
            for _margin, source, trail, cycle, support, _g, _gain_ratio in representatives
        ],
        "sharp_cardinality_counts": {
            f"p={p},g={g},h={6-p-g}": count
            for (p, g), count in sorted(
                Counter((row[4]["p"], row[5]) for row in sharp).items()
            )
        },
        "sharp_distinct_archive_rows": len(
            {(row[1], row[2]) for row in sharp}
        ),
        "carrier_direct_equality_distinct_archive_rows": len(equality_archive_rows),
        "sharp_gain_ratio_counts": {
            str(ratio): count
            for ratio, count in sorted(
                Counter(row[6] for row in sharp).items()
            )
        },
    }


def balanced_equality_controls():
    target = F(7, 12)
    controls = []
    for case in CASES[-2:]:
        x = tuple(case["x"])
        z = tuple(case["z"])
        gainers = tuple(i for i in range(7) if z[i] > x[i])
        nongainers = tuple(i for i in range(7) if z[i] <= x[i])
        rows = []
        for coalition in case["support_x"]:
            h_set = tuple(i for i in nongainers if coalition >> i & 1)
            p_set = tuple(i for i in nongainers if i not in h_set)
            if not p_set or not h_set:
                continue
            row = quota_row(x, z, p_set, gainers, h_set)
            row["support_coalition"] = coalition
            rows.append(row)
        closing = [row for row in rows if row["closes"]]
        if not closing:
            raise AssertionError((case["name"], "expected scalar equality rows"))
        if any(
            row["h"] != 1
            or F(row["budget_margin"]) != 0
            or F(row["base_bound_ratio"]) >= target
            for row in closing
        ):
            raise AssertionError((case["name"], "sharp rooted boundary changed", closing))
        controls.append(
            {
                "name": case["name"],
                "selected_support_rows": len(rows),
                "scalar_closing_rows": len(closing),
                "closing_P": sorted({tuple(row["P"]) for row in closing}),
                "closing_h": 1,
                "quota_margin": "0",
                "direct_bases": sorted(
                    {row["base_bound_ratio"] for row in closing}, key=F
                ),
                "target": str(target),
                "interpretation": (
                    "the scalar quota is sharp, but h=1 lies outside the "
                    "carrier-cycle cardinality lemma and the direct base is "
                    "below target; the rooted equality arm remains necessary"
                ),
            }
        )
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    checked = 0
    increment_checked = 0
    for n in range(3, 101):
        for p in range(1, n - 1):
            for g in range(1, n - p):
                h = n - p - g
                if source_coefficients(p, g, h) != deficit_coefficients(p, g, h):
                    raise AssertionError(("coefficient identity failure", p, g, h))
                checked += 1
                if h >= 2:
                    current = F((n - p) * (p + 1), n * g)
                    following = F((n - p - 1) * (p + 2), n * g)
                    if following - current != F(n - 2 * p - 2, n * g):
                        raise AssertionError(("quota increment failure", p, g, h))
                    increment_checked += 1

    report = {
        "status": "excluded-block deficit-quota identity verified exactly",
        "theorem": (
            "for a sign partition P/G/H and the maximal proper gainer packet, "
            "U_(g-1)-L_H = [pT-nz(P)]/(n-p) - (p+1)D/g = "
            "n Q(P)/(n-p) - (p+1)D/g, where D=z(G)-x(G) and "
            "Q(P)=sum_{i in P}(T/n-z_i)"
        ),
        "criterion": (
            "the direct scalar budget closes if and only if "
            "Q(P)>=[(n-p)(p+1)/(ng)]D"
        ),
        "nested_increment": (
            "if P_(p+1)=P_p union {i}, its quota margin changes by "
            "T/n-z_i-[(n-2p-2)/(ng)]D"
        ),
        "coefficient_rows_checked": checked,
        "nested_increment_rows_checked": increment_checked,
        "parameter_range": "all positive p,g,h with 3<=p+g+h<=100",
        "n7_full_root_block_counterexample": n7_control(),
        "balanced_n7_equality_orientations": balanced_equality_controls(),
        "n6_archive": n6_archive(args.paths) if args.paths else None,
        "algorithmic_boundary": (
            "on a fixed labelled selection cell, scan the complete staged "
            "Lmin support coalitions containing the carrier cycle, form their "
            "excluded nongainer blocks P, and test the exact quota; this decides "
            "the direct carrier arm in time linear in the explicit support menu, "
            "but is not a full exact-game-cone facet enumeration theorem"
        ),
        "scope": (
            "the coefficient identity and iff quota criterion are dimension-free; "
            "the finite parameter grid and n=6/n=7 replays do not prove that a "
            "quota-meeting selected support exists in every hard branch"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
