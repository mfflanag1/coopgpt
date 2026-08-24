#!/usr/bin/env python3
"""Exact audit of PXC133 two-allocation packet conservation.

The theorem is the incidence identity dotted with x-z.  This verifier checks
the PXC101, PXC104, and positive-demand PXC125 packets against their exact
lower-envelope games and separates raw core slack from comparison currency.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
ARCHIVE = HERE.parent / "search_archive"
sys.path[:0] = [str(ARCHIVE), str(ROOT / "src")]

from unrestricted_pxc91c_exact_search import lower_envelope  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402


def csum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def loads(n, rows, weights):
    return tuple(
        sum((weight for row, weight in zip(rows, weights) if row >> i & 1), F(0))
        for i in range(n)
    )


def audit_packet(name, total, constraints, x, z, rows, weights, exceptional, beta, ambient):
    n = len(x)
    values = lower_envelope(constraints, n, total)
    actual_loads = loads(n, rows, weights)
    expected_loads = tuple(ambient + beta * F(bool(exceptional >> i & 1)) for i in range(n))
    if actual_loads != expected_loads:
        raise AssertionError((name, actual_loads, expected_loads))
    slack_x = sum(
        (weight * (csum(x, row) - values[row]) for row, weight in zip(rows, weights)), F(0)
    )
    slack_z = sum(
        (weight * (csum(z, row) - values[row]) for row, weight in zip(rows, weights)), F(0)
    )
    exceptional_shear = beta * (csum(x, exceptional) - csum(z, exceptional))
    comparison_sum = sum(
        (weight * (csum(x, row) - csum(z, row)) for row, weight in zip(rows, weights)), F(0)
    )
    if slack_x - slack_z != exceptional_shear or comparison_sum != exceptional_shear:
        raise AssertionError((name, slack_x, slack_z, comparison_sum, exceptional_shear))
    worth_gap = ambient * total + beta * values[exceptional] - sum(
        (weight * values[row] for row, weight in zip(rows, weights)), F(0)
    )
    if worth_gap < 0:
        raise AssertionError((name, "invalid exactness inequality", worth_gap))
    return {
        "name": name,
        "rows": rows,
        "weights": weights,
        "exceptional": exceptional,
        "exceptional_weight": beta,
        "ambient": ambient,
        "raw_positive_slack_at_x": slack_x,
        "raw_positive_slack_at_z": slack_z,
        "comparison_currency": comparison_sum,
        "exceptional_comparison_shear": exceptional_shear,
        "exactness_worth_gap": worth_gap,
        "active_packet": worth_gap == 0,
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


def spectral_currency_controls():
    games = [
        (
            "PXC101", F(17), {7: F(11), 11: F(11), 17: F(6), 51: F(11)},
            tuple(F(v) for v in ("9/2", "9/2", 2, 2, 2, 2)),
            tuple(F(v) for v in (4, 4, 3, 3, 2, 1)), F(1),
        ),
        (
            "PXC104", F(23),
            {7: F(16), 11: F(16), 19: F(13), 23: F(18), 35: F(13), 39: F(18)},
            tuple(F(v) for v in ("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            tuple(F(v) for v in (6, 6, 5, 4, 1, 1)), F(10, 3),
        ),
        (
            "PXC125", F(25), {3: F(12), 19: F(14), 39: F(89, 5), 43: F(23)},
            tuple(F(v) for v in ("13/2", "13/2", 1, 5, 1, 5)),
            tuple(F(v) for v in (6, 6, 0, "26/5", 2, "29/5")), F(2, 5),
        ),
    ]
    answer = []
    expected = {
        "PXC101": (F(15), F(15), F(15), F(0), F(0)),
        "PXC104": (F(56, 3), F(56, 3), F(56, 3), F(0), F(0)),
        "PXC125": (F(16), F(16), F(23), F(0), F(7)),
    }
    for name, total, constraints, x, z, packet_shear in games:
        values = lower_envelope(constraints, 6, total)
        item = spectral_decomposition(name, values, x, z)
        b_star = F(item["sharpened_spectral_bound_ratio"]) * total
        b_h = F(item["actual_top_bound_ratio"]) * total
        overlap = F(item["overlap_ratio"]) * total
        top_currency = F(item["top_selection_currency_ratio"]) * total
        label_currency = F(item["label_currency_ratio"]) * total
        actual = (b_star, b_h, overlap, top_currency, label_currency)
        if actual != expected[name]:
            raise AssertionError((name, actual, expected[name]))
        answer.append({
            "name": name,
            "B_star": b_star,
            "B_H": b_h,
            "overlap": overlap,
            "spectral_top_selection_currency": top_currency,
            "residual_label_currency": label_currency,
            "packet_net_comparison_shear": packet_shear,
            "packet_shear_not_automatically_a_decomposition_currency": (
                packet_shear > 0 and top_currency == 0 and
                (label_currency == 0 or packet_shear != label_currency)
            ),
        })
    return answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = [
        audit_packet(
            "PXC101_root_mixed_packet", F(17),
            {7: F(11), 11: F(11), 17: F(6), 51: F(11)},
            tuple(F(v) for v in ("9/2", "9/2", 2, 2, 2, 2)),
            tuple(F(v) for v in (4, 4, 3, 3, 2, 1)),
            (7, 17, 41), (F(1),) * 3, 1, F(2), F(1),
        ),
        audit_packet(
            "PXC104_z_tight_cross_packet", F(23),
            {7: F(16), 11: F(16), 19: F(13), 23: F(18), 35: F(13), 39: F(18)},
            tuple(F(v) for v in ("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            tuple(F(v) for v in (6, 6, 5, 4, 1, 1)),
            (11, 23, 35), (F(1),) * 3, 3, F(2), F(1),
        ),
        audit_packet(
            "PXC125_positive_demand_mixed_packet", F(25),
            {3: F(12), 19: F(14), 39: F(89, 5), 43: F(23)},
            tuple(F(v) for v in ("13/2", "13/2", 1, 5, 1, 5)),
            tuple(F(v) for v in (6, 6, 0, "26/5", 2, "29/5")),
            (39, 43, 51), (F(1),) * 3, 35, F(2), F(1),
        ),
    ]
    pxc125 = records[-1]
    demand = F(2, 3)
    if pxc125["raw_positive_slack_at_x"] != F(22, 5):
        raise AssertionError("PXC125 raw packet slack changed")
    if pxc125["comparison_currency"] != F(2, 5) or not pxc125["comparison_currency"] < demand:
        raise AssertionError("PXC125 comparison no-go changed")
    payload = {
        "claim": "PXC133 two-allocation exceptional-packet conservation",
        "symbolic_statement": (
            "every incidence packet has sum lambda_S[x(S)-z(S)] "
            "= beta[x(E)-z(E)]; exactness gaps cancel between the two allocations"
        ),
        "records": records,
        "spectral_currency_controls": spectral_currency_controls(),
        "positive_demand_control": {
            "required_D_H": demand,
            "raw_packet_slack_at_x": pxc125["raw_positive_slack_at_x"],
            "exactness_slack_already_present_at_z": pxc125["raw_positive_slack_at_z"],
            "net_comparison_shear": pxc125["comparison_currency"],
            "raw_slack_would_overstate_comparison_currency": True,
            "comparison_shear_falls_short_of_D_H": True,
        },
        "scope": {
            "proved_conventionally": "dimension-free two-allocation conservation for every incidence packet",
            "not_proved": "that exceptional comparison shears admit a disjoint threshold assignment reaching D_H",
            "route_no_go": "raw core slack at x cannot be counted without subtracting the same exactness slack at z",
        },
    }
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
