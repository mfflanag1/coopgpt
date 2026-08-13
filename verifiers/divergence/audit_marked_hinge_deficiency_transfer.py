#!/usr/bin/env python3
r"""Exact audit of the marked-hinge/common-support deficiency transfer.

For the dual optimum ``(y, epsilon)`` of (CSD-D), every Lmax-top label has
``y_i >= epsilon``.  If ``A`` is tight at both Lmin and Lmax, its Lmax slack
is zero and dual feasibility gives ``y(A) <= 0``.  Hence

  -y(A \ H) >= |A cap H| epsilon,
   y(H \ A) >= |H \ A| epsilon.

This is dimension-free algebra.  The archive replay checks every common row
and records a positive-deficiency equality control; it is not an all-n
target-pricing theorem or a facet classification.
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

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from audit_surplus_absorption import minimum_surplus_certificate  # noqa: E402


def audit_record(source, trail, values, x, z, counters, controls, aggregate_controls):
    x_tight = set(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    common = tuple(sorted(x_tight & z_tight))
    if not common:
        return
    certificate = minimum_surplus_certificate(values, x, z)
    epsilon = certificate["epsilon_star"]
    y = certificate["dual_y"]
    top = {i for i, value in enumerate(z) if value == max(z)}
    counters["records_with_common_rows"] += 1
    counters["records_with_positive_common_support_deficiency"] += epsilon > 0
    for coalition in common:
        members = {i for i in range(len(x)) if coalition >> i & 1}
        top_in = members & top
        top_out = top - members
        off_in = members - top
        negative_pool = -sum((y[i] for i in off_in), F(0))
        positive_pool = sum((y[i] for i in top_out), F(0))
        if coalition_sum(y, coalition) > 0:
            raise AssertionError("common row violates zero-slack dual constraint")
        if negative_pool < len(top_in) * epsilon:
            raise AssertionError("marked-hinge negative-price transfer failed")
        if positive_pool < len(top_out) * epsilon:
            raise AssertionError("omitted-top positive-price transfer failed")
        counters["common_rows_checked"] += 1
        counters["common_rows_meeting_and_omitting_top"] += bool(top_in and top_out)
        counters["positive_deficiency_transfer_rows"] += bool(
            epsilon > 0 and top_in and top_out
        )
        if epsilon > 0 and top_in and top_out:
            top_trace = members & top
            same_top_trace = tuple(
                support
                for support in certificate["support"]
                if {
                    i for i in range(len(x)) if support >> i & 1
                }
                & top
                == top_trace
            )
            subset_rows = tuple(
                support
                for support in certificate["support"]
                if support & ~coalition == 0
            )
            counters[
                "positive_transfer_rows_with_primal_same_top_trace"
            ] += bool(same_top_trace)
            counters[
                "positive_transfer_rows_with_primal_subset_row"
            ] += bool(subset_rows)
            if (
                not same_top_trace
                and len(certificate["support"]) > 1
                and not aggregate_controls
            ):
                aggregate_controls.append(
                    {
                        "source": source,
                        "trail": trail,
                        "common_hinge": coalition,
                        "top": sorted(top),
                        "hinge_top_trace": sorted(top_trace),
                        "epsilon_star": str(epsilon),
                        "optimal_primal_support": list(certificate["support"]),
                        "optimal_primal_weights": [
                            str(value) for value in certificate["weights"]
                        ],
                        "interpretation": (
                            "no optimal over-cover support row has the hinge's "
                            "top trace; a one-row nested shear is unavailable"
                        ),
                    }
                )
        if (
            epsilon > 0
            and top_in
            and top_out
            and negative_pool == len(top_in) * epsilon
            and positive_pool == len(top_out) * epsilon
            and not controls
        ):
            controls.append(
                {
                    "source": source,
                    "trail": trail,
                    "coalition": coalition,
                    "top": sorted(top),
                    "epsilon_star": str(epsilon),
                    "dual_y": [str(value) for value in y],
                    "top_labels_in_hinge": len(top_in),
                    "top_labels_outside_hinge": len(top_out),
                    "negative_offtop_price_in_hinge": str(negative_pool),
                    "positive_top_price_outside_hinge": str(positive_pool),
                    "hinge_dual_value": str(coalition_sum(y, coalition)),
                }
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    counters = Counter()
    controls = []
    aggregate_controls = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            audit_record(
                path.name,
                trail,
                values,
                x,
                z,
                counters,
                controls,
                aggregate_controls,
            )
    report = {
        "status": "dimension-free dual identity with exact finite replay",
        "statement_checked": (
            "a common hinge containing q Lmax-top labels carries at least "
            "q*epsilon_star of negative dual price on its off-top labels; "
            "every omitted top label separately carries price at least "
            "epsilon_star"
        ),
        "inputs": [path.name for path in args.paths],
        "counts": dict(counters),
        "positive_deficiency_equality_control": controls[0] if controls else None,
        "aggregate_support_necessity_control": (
            aggregate_controls[0] if aggregate_controls else None
        ),
        "limitations": (
            "the identity does not prove that the transferred price reaches "
            "the hybrid-overlap target or that its support is an indecomposable facet"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
