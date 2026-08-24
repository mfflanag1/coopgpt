#!/usr/bin/env python3
"""Exact named controls for PXC135 mechanism-labelled canonical transport.

The dimension-free proof combines PXC129 with PXC134 and the canonical
opposite-rank construction.  This audit recomputes canonical carriers,
checks their source/sink congestion, and verifies that the positive-demand
named common controls label every carrier by a retained common row.  The
cover-row/outside-blocker alternatives are the already proved PXC129 theorem;
their zero-length boundary controls are retained there.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def q(values):
    return tuple(F(value) for value in values)


def separates(mask, source, sink):
    return bool((mask >> source) & 1) != bool((mask >> sink) & 1)


def canonical_carriers(x, z, top):
    residual = tuple(i for i in range(len(x)) if i not in top)
    low = tuple(min(x[i], z[i]) for i in range(len(x)))
    high = tuple(max(x[i], z[i]) for i in range(len(x)))
    sources = sorted(residual, key=lambda i: (-low[i], i))
    sinks = sorted(residual, key=lambda i: (high[i], i))
    return tuple(
        (source, sink, low[source] - high[sink])
        for source, sink in zip(sources, sinks)
        if low[source] > high[sink]
    )


def threshold_currency(x, z, top):
    residual = tuple(i for i in range(len(x)) if i not in top)
    levels = sorted({F(0)} | {x[i] for i in residual} | {z[i] for i in residual})
    total = F(0)
    for low, high in zip(levels, levels[1:]):
        double_high = {
            i for i in residual if min(x[i], z[i]) >= high
        }
        double_low = {
            i for i in residual if max(x[i], z[i]) <= low
        }
        total += F(min(len(double_high), len(double_low))) * (high - low)
    return total


def audit(name, x, z, common_rows, top=(0, 1)):
    edges = canonical_carriers(x, z, top)
    sources = [edge[0] for edge in edges]
    sinks = [edge[1] for edge in edges]
    if len(sources) != len(set(sources)) or len(sinks) != len(set(sinks)):
        raise AssertionError((name, "canonical orientation congestion"))
    labels = []
    for source, sink, length in edges:
        separators = tuple(
            row for row in common_rows if separates(row, source, sink)
        )
        labels.append(
            {
                "edge": (source, sink),
                "length": length,
                "common_row_labels": separators,
                "classification": (
                    "retained_common_row" if separators
                    else "PXC129_cover_row_or_forced_blocker"
                ),
            }
        )
    value = sum((edge[2] for edge in edges), F(0))
    currency = threshold_currency(x, z, top)
    if value != currency:
        raise AssertionError((name, "canonical value", value, currency))
    return {
        "name": name,
        "canonical_carriers": edges,
        "mechanism_labels": labels,
        "transport_value": value,
        "label_currency": currency,
        "orientation_split_feasible": True,
    }


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records = [
        audit(
            "PXC101_zero_length_common_boundary",
            q(("9/2", "9/2", 2, 2, 2, 2)),
            q((4, 4, 3, 3, 2, 1)),
            (7, 11),
        ),
        audit(
            "PXC104_zero_length_reciprocal_boundary",
            q(("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            q((6, 6, 5, 4, 1, 1)),
            (11,),
        ),
        audit(
            "PXC116_common_control",
            q(("25/4", "25/4", "1/2", "9/4", "1/2", "9/4")),
            q((6, 6, 0, 2, 1, 3)),
            (19, 43),
        ),
        audit(
            "PXC125_positive_demand_common",
            q(("13/2", "13/2", 1, 5, 1, 5)),
            q((6, 6, 0, "26/5", 2, "29/5")),
            (19, 43),
        ),
        audit(
            "PXC127_common_cut_control",
            q(("32/5", "32/5", 1, "51/10", 1, "51/10")),
            q((6, 6, "1/5", "26/5", "9/5", "29/5")),
            (19, 43),
        ),
        audit(
            "PXC90_faithful_full_rank_boundary",
            q((6, 4, 2, 2, 2, 2, 2)),
            q(("29/7", "29/7", 4, 4, "8/7", "9/7", "9/7")),
            (),
        ),
    ]
    by_name = {record["name"]: record for record in records}
    if by_name["PXC125_positive_demand_common"]["transport_value"] != F(7):
        raise AssertionError("PXC125 canonical transport changed")
    if by_name["PXC127_common_cut_control"]["transport_value"] != F(37, 5):
        raise AssertionError("PXC127 canonical transport changed")
    for name in (
        "PXC116_common_control",
        "PXC125_positive_demand_common",
        "PXC127_common_cut_control",
    ):
        if any(
            label["classification"] != "retained_common_row"
            for label in by_name[name]["mechanism_labels"]
        ):
            raise AssertionError((name, "unlabelled named carrier"))

    payload = {
        "claim": "PXC135 mechanism-labelled canonical transport",
        "symbolic_statement": (
            "every positive canonical rank carrier has a common-row, "
            "cover-row, or forced-blocker label by PXC129; the canonical "
            "carriers satisfy split source/sink congestion and total O-B_H"
        ),
        "records": records,
        "scope": {
            "proved_conventionally": (
                "dimension-free qualitative attribution of every label-currency "
                "rectangle to one PXC129 mechanism without orientation congestion"
            ),
            "not_proved": (
                "the quantitative inequality O-B_H >= D_H, or any conversion "
                "of packet comparison shear into spectral currency"
            ),
        },
    }
    rendered = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
