#!/usr/bin/env python3
"""Exact n=6 audit of the direct/ceiling/null/common-hinge reduction.

The census tests a proposed *selection architecture*, not an all-n theorem.
It sequentially removes archived pairs closed by the arbitrary-Lmax direct
identity, the ceiling-root interpolation theorem, and null-player descent.
It then checks that every positive-floor residual has a common root coalition
between one complete staged Lmin support and one sparse first-stage Lmax
over-cover, and directly replays the resulting rooted relaxation.
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

from audit_lmax_overcover import records, top_certificate  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
    specialized_root_minimum,
)
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402


def has_direct_packet(x, z, target):
    n = len(x)
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = tuple(i for i in range(n) if z[i] <= x[i])
    for h_size in range(1, len(nongainers)):
        for h_set in itertools.combinations(nongainers, h_size):
            p_set = tuple(i for i in nongainers if i not in h_set)
            for s in range(len(gainers)):
                for j_set in itertools.combinations(gainers, s):
                    row = master_identity(x, z, p_set, gainers, h_set, j_set)
                    if (
                        F(row["base_bound_ratio"]) >= target
                        and row["packet_hits_interval"]
                    ):
                        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    target = F(2, 3)
    counts = Counter()
    residual_common_sizes = Counter()
    positive_residual_common_sizes = Counter()
    first_positive_residual = None
    common_hinge_repair_rows = []
    for path in args.paths:
        data = json.loads(path.read_text())
        for _source, trail, values, x, z in records(data, path):
            if len(x) != 6:
                continue
            counts["records"] += 1
            direct = has_direct_packet(x, z, target)
            if direct:
                counts["direct"] += 1

            total = sum(x, F(0))
            floor = min(x)
            ceiling = max(z)
            interpolation = ceiling - floor + total * floor / ceiling
            ceiling_closes = interpolation >= target * total
            if not direct and ceiling_closes:
                counts["ceiling_after_direct_failure"] += 1

            support_x = complete_lmin_support(values, x)
            support_z = tuple(top_certificate(values, z)["support"])
            common = tuple(sorted(set(support_x).intersection(support_z)))
            if not common:
                counts["empty_common_support"] += 1
                if not (direct or ceiling_closes):
                    raise AssertionError("residual pair has empty common support")

            if direct or ceiling_closes:
                continue
            counts["residual"] += 1
            residual_common_sizes[len(common)] += 1
            ceiling_roots = tuple(
                i for i in range(6)
                if z[i] == ceiling and x[i] >= ceiling
            )
            coordinate_overlap = tuple(min(x[i], z[i]) for i in range(6))
            overlap_roots = tuple(
                i for i, value in enumerate(coordinate_overlap)
                if value == max(coordinate_overlap)
            )
            if len(ceiling_roots) != 1 or ceiling_roots != overlap_roots:
                raise AssertionError("residual ceiling/root alignment changed")
            counts["residual_unique_aligned_root"] += 1

            # A zero Lmin floor invokes the proved null-player descent, so the
            # genuinely live fixed-dimensional region begins only here.
            if floor == 0:
                counts["null_descent_after_direct_ceiling_failure"] += 1
                continue
            counts["positive_floor_residual"] += 1
            if sum((min(a, b) for a, b in zip(x, z)), F(0)) == target * total:
                counts["positive_floor_residual_equality"] += 1
            else:
                counts["positive_floor_residual_strict"] += 1
            positive_residual_common_sizes[len(common)] += 1
            root = ceiling_roots[0]
            root_hinges = tuple(coalition for coalition in common if coalition >> root & 1)
            if not root_hinges:
                raise AssertionError("positive-floor residual has no common root hinge")
            counts["positive_residual_with_common_root_hinge"] += 1
            rooted_bound = specialized_root_minimum(x, z, support_x, common, root)
            if rooted_bound < target:
                raise AssertionError("positive-floor common-hinge root bound failed")
            counts["positive_residual_rooted_bound_closes"] += 1
            lmin_rooted_bound = specialized_root_minimum(x, z, support_x, (), root)
            if lmin_rooted_bound >= target:
                counts["positive_residual_lmin_rooted_closes"] += 1
            else:
                counts["positive_residual_needing_common_hinge_repair"] += 1
                common_hinge_repair_rows.append(f"{path.name} {trail}")
            alpha = tuple(top_certificate(values, z)["alpha"])
            surviving_maximum = max(alpha[i] for i in range(6) if i != root)
            if alpha[root] > surviving_maximum:
                counts["positive_residual_strict_overcover_leader"] += 1
            else:
                if alpha[root] != surviving_maximum:
                    raise AssertionError("selected ceiling root is below another top load")
                counts["positive_residual_tied_overcover_leader"] += 1
                if lmin_rooted_bound < target:
                    counts["common_hinge_repairs_with_tied_root_load"] += 1
            if first_positive_residual is None:
                first_positive_residual = {
                    "source": path.name,
                    "trail": trail,
                    "lmin": [str(q) for q in x],
                    "lmax": [str(q) for q in z],
                    "common_support": list(common),
                    "common_root_hinges": list(root_hinges),
                    "root": root,
                    "common_hinge_root_bound": str(rooted_bound),
                    "lmin_only_root_bound": str(lmin_rooted_bound),
                }

    expected = {
        "records": 374,
        "direct": 296,
        "ceiling_after_direct_failure": 28,
        "residual": 50,
        "empty_common_support": 37,
        "residual_unique_aligned_root": 50,
        "null_descent_after_direct_ceiling_failure": 34,
        "positive_floor_residual": 16,
        "positive_floor_residual_equality": 2,
        "positive_floor_residual_strict": 14,
        "positive_residual_with_common_root_hinge": 16,
        "positive_residual_rooted_bound_closes": 16,
        "positive_residual_lmin_rooted_closes": 13,
        "positive_residual_needing_common_hinge_repair": 3,
        "positive_residual_tied_overcover_leader": 15,
        "positive_residual_strict_overcover_leader": 1,
        "common_hinge_repairs_with_tied_root_load": 3,
    }
    if dict(counts) != expected:
        raise AssertionError({"trichotomy census changed": dict(counts)})
    if dict(residual_common_sizes) != {1: 45, 2: 3, 3: 2}:
        raise AssertionError({"residual common-support sizes changed": residual_common_sizes})
    expected_repairs = [
        "harvest6_601.json $.records[103]",
        "harvest6_602.json $.records[82]",
        "harvest6_602.json $.records[129]",
    ]
    if common_hinge_repair_rows != expected_repairs:
        raise AssertionError({"common-hinge repair rows changed": common_hinge_repair_rows})

    report = {
        "status": "exact finite direct/ceiling/null/common-root-hinge reduction audit",
        **expected,
        "residual_common_support_size_distribution": {
            str(key): value for key, value in sorted(residual_common_sizes.items())
        },
        "positive_residual_common_support_size_distribution": {
            str(key): value
            for key, value in sorted(positive_residual_common_sizes.items())
        },
        "first_positive_residual_control": first_positive_residual,
        "common_hinge_repair_rows": common_hinge_repair_rows,
        "two_spoke_theorem_repairs": [expected_repairs[0], expected_repairs[2]],
        "n6_three_packet_theorem_repair": expected_repairs[1],
        "rooted_cross_check": (
            "n6_sparse_lmax_complete_lmin_roots.json independently records 703 "
            "root LP agreements, zero failures, and minimum common-hinge bound 2/3"
        ),
        "missing_human_lemma": (
            "after null-player descent, failure of direct gluing and ceiling "
            "interpolation forces either a target-priced complete Lmin rooted "
            "packet or a tied-load common-root-hinge repair"
        ),
        "scope": "374 archived n=6 pairs; finite falsification evidence only",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
