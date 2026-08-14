#!/usr/bin/env python3
r"""Exact controls for the priced decorated co-star theorem (PXC59).

The theorem is dimension-free human algebra.  This driver scans the n=6
archives and fixed hostile/equality controls for its labelled hypotheses and
checks every displayed rational inequality.  The finite census audits scope;
it is not a proof that the required decorated co-star can always be selected.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_labelled_facet_cover_duality import maximum_overlap_roots  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def overlap(x, z):
    return sum((min(a, b) for a, b in zip(x, z)), F(0))


def certificates(values, x, z):
    n = len(x)
    total = sum(x, F(0))
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    if n < 6 or len(gainers) < 2 or total <= 0 or total != sum(z, F(0)):
        return ()
    g = len(gainers)
    q = n - g
    if q < 2:
        return ()
    gainer_set = set(gainers)
    x_tight = set(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    answer = []
    for root in maximum_overlap_roots(x, z):
        if root in gainer_set:
            continue
        outsiders = tuple(sorted(set(range(n)) - gainer_set - {root}))
        outsider_set = set(outsiders)
        minimum_gainer = min(x[player] for player in gainers)
        if not (
            all(x[root] >= x[player] for player in gainers)
            and all(minimum_gainer >= x[player] for player in outsiders)
        ):
            continue

        rows_by_omitted = {}
        for omitted in gainers:
            required = {root, *(player for player in gainers if player != omitted)}
            rows_by_omitted[omitted] = tuple(
                coalition
                for coalition in sorted(x_tight)
                if coalition >> root & 1
                and not (coalition >> omitted & 1)
                and all(coalition >> player & 1 for player in required)
            )
        if any(not rows for rows in rows_by_omitted.values()):
            continue

        highest_gainer_z = max(z[player] for player in gainers)
        for chosen_rows in itertools.product(
            *(rows_by_omitted[player] for player in gainers)
        ):
            decoration_counts = {
                outsider: sum(
                    bool(coalition >> outsider & 1) for coalition in chosen_rows
                )
                for outsider in outsiders
            }
            if any(count > g - 1 for count in decoration_counts.values()):
                continue
            decorations = tuple(
                tuple(
                    outsider
                    for outsider in outsiders
                    if coalition >> outsider & 1
                )
                for coalition in chosen_rows
            )
            average_decoration = sum(
                (
                    sum((x[player] for player in decoration), F(0))
                    for decoration in decorations
                ),
                F(0),
            ) / (g - 1)
            gainer_x_total = sum((x[player] for player in gainers), F(0))
            packet_left = F(g, g - 1) * x[root] + gainer_x_total + average_decoration
            if packet_left > total:
                raise AssertionError("decorated co-star witness packet failed")

            for index, omitted in enumerate(gainers):
                coalition = chosen_rows[index]
                if (
                    z[omitted] != highest_gainer_z
                    or z[root] < z[omitted]
                    or coalition not in z_tight
                ):
                    continue
                decoration = decorations[index]
                decoration_loss = sum(
                    (x[player] - z[player] for player in decoration), F(0)
                )
                if decoration_loss < 0:
                    raise AssertionError("a decoration contains a gainer")
                total_gain = sum((z[player] - x[player] for player in gainers), F(0))
                transfer_ceiling = x[root] - x[omitted] + decoration_loss
                if total_gain > transfer_ceiling:
                    raise AssertionError("decorated comparison transfer failed")

                mu = F((g - 1) * n, g * q)
                gain_ceiling = (
                    F(g * q - n, g * q) * total
                    + decoration_loss
                    - mu * average_decoration
                )
                if total_gain > gain_ceiling:
                    raise AssertionError("priced decorated gain bound failed")
                proved_floor = (
                    F(n, g * q) * total
                    + mu * average_decoration
                    - decoration_loss
                )
                actual = overlap(x, z)
                if actual < proved_floor:
                    raise AssertionError("priced decorated overlap bound failed")
                target = F(n, (n * n) // 4) * total
                clean = all(not decoration for decoration in decorations)
                answer.append(
                    {
                        "root": root,
                        "gainers": list(gainers),
                        "gainer_count": g,
                        "omitted_highest_gainer": omitted,
                        "lmin_tight_decorated_costars": list(chosen_rows),
                        "decorations": [list(decoration) for decoration in decorations],
                        "decoration_loads": {
                            str(player): count
                            for player, count in decoration_counts.items()
                        },
                        "common_costar": coalition,
                        "average_decoration_mass": str(average_decoration),
                        "aligned_decoration_loss": str(decoration_loss),
                        "decoration_price": str(mu),
                        "packet_left": str(packet_left),
                        "total_gain": str(total_gain),
                        "gain_ceiling": str(gain_ceiling),
                        "proved_floor": str(proved_floor),
                        "hybrid_target": str(target),
                        "actual_overlap": str(actual),
                        "clean_costar_special_case": clean,
                        "priced_bound_closes_target": proved_floor >= target,
                    }
                )
    return tuple(answer)


def lower_envelope_case(case):
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
    return (
        lower_envelope(generators),
        tuple(map(F, case["x"])),
        tuple(map(F, case["z"])),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive_rows = []
    seen_records = 0
    positive_residual_rows = 0
    positive_residual_rows_matching = 0
    positive_residual_rows_closing = 0
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            seen_records += 1
            found = certificates(values, x, z)
            total = sum(x, F(0))
            floor = min(x)
            ceiling = max(z)
            positive_residual = (
                not has_direct_packet(x, z, F(2, 3))
                and ceiling - floor + total * floor / ceiling < F(2, 3) * total
                and floor > 0
            )
            positive_residual_rows += positive_residual
            positive_residual_rows_matching += positive_residual and bool(found)
            positive_residual_rows_closing += positive_residual and any(
                row["priced_bound_closes_target"] for row in found
            )
            if found:
                archive_rows.append(
                    {"source": source.name, "trail": trail, "certificates": found}
                )

    fixed_rows = []
    for case in CASES:
        values, x, z = lower_envelope_case(case)
        fixed_rows.append(
            {"name": case["name"], "certificates": certificates(values, x, z)}
        )

    certificate_count = sum(len(row["certificates"]) for row in archive_rows)
    clean_count = sum(
        certificate["clean_costar_special_case"]
        for row in archive_rows
        for certificate in row["certificates"]
    )
    closing_count = sum(
        certificate["priced_bound_closes_target"]
        for row in archive_rows
        for certificate in row["certificates"]
    )
    actual_counts = (
        seen_records,
        len(archive_rows),
        certificate_count,
        clean_count,
        closing_count,
        positive_residual_rows,
        positive_residual_rows_matching,
        positive_residual_rows_closing,
    )
    expected_counts = (374, 90, 728, 186, 728, 16, 16, 16)
    if actual_counts != expected_counts:
        raise AssertionError(("priced decorated co-star census changed", actual_counts))
    sharp = {
        row["name"]: len(row["certificates"])
        for row in fixed_rows
        if row["name"].startswith("sharp_family")
    }
    if sharp != {"sharp_family_p2_k4": 4, "sharp_family_p3_k3": 3}:
        raise AssertionError(("sharp-family decorated co-star controls changed", sharp))
    hostile = {
        row["name"]: len(row["certificates"])
        for row in fixed_rows
        if not row["name"].startswith("sharp_family")
    }
    if any(hostile.values()):
        raise AssertionError(("a hostile control acquired a certificate", hostile))
    distribution = Counter(
        certificate["gainer_count"]
        for row in archive_rows
        for certificate in row["certificates"]
    )
    report = {
        "status": "exact priced decorated co-star controls verified",
        "human_theorem": (
            "a packing-admissible ordered Lmin decorated co-star and one "
            "aligned common row imply O >= nT/[g(n-g)] + mu*A - L, "
            "where mu=(g-1)n/[g(n-g)]"
        ),
        "archive_records_scanned": seen_records,
        "archive_rows_matching_theorem": len(archive_rows),
        "archive_certificates": certificate_count,
        "archive_clean_certificates": clean_count,
        "archive_certificates_closing_target": closing_count,
        "archive_gainer_count_distribution": {
            str(key): value for key, value in sorted(distribution.items())
        },
        "positive_residual_rows": positive_residual_rows,
        "positive_residual_rows_matching_theorem": positive_residual_rows_matching,
        "positive_residual_rows_closing_target": positive_residual_rows_closing,
        "archive_rows": archive_rows,
        "fixed_hostile_and_equality_controls": fixed_rows,
        "scope": (
            "dimension-free human theorem; finite scans audit exact labelled "
            "hypotheses and arithmetic, not universal decorated-co-star selection"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
