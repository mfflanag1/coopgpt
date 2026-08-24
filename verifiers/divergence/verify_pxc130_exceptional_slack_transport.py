#!/usr/bin/env python3
"""Exact audit of the PXC130 exceptional-set slack-transport lemma.

The conventional proof is the incidence/witness argument in the manuscript.
This verifier checks the coefficient identities, the PXC101/PXC104/PXC118
partition-star calibrations, and a fail-open relaxed selector model which is
excluded by a single singleton-exceptional exact-game inequality.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def coalition_sum(values, mask):
    return sum((value for i, value in enumerate(values) if mask >> i & 1), F(0))


def loads(n, rows, weights):
    return tuple(
        sum((weight for row, weight in zip(rows, weights) if row >> i & 1), F(0))
        for i in range(n)
    )


def check_identity(n, rows, weights, exceptional, beta, ambient):
    actual = loads(n, rows, weights)
    expected = tuple(ambient + beta * F(bool(exceptional >> i & 1)) for i in range(n))
    if actual != expected:
        raise AssertionError((rows, weights, actual, expected))
    return actual


def slack(values, worths, row):
    return coalition_sum(values, row) - worths[row]


def partition_star(name, x, z, pair, blocks):
    n = len(x)
    rows = tuple(pair | block for block in blocks)
    if any(left & right for q, left in enumerate(blocks) for right in blocks[q + 1:]):
        raise AssertionError((name, "blocks overlap"))
    if pair | sum(blocks) != (1 << n) - 1:
        raise AssertionError((name, "blocks do not partition the complement"))
    m = len(blocks)
    worths = {row: coalition_sum(z, row) for row in rows}
    worths[pair] = coalition_sum(z, pair)
    raw_loads = check_identity(n, rows, (F(1),) * m, pair, F(m - 1), F(1))
    raw_slacks = tuple(slack(x, worths, row) for row in rows)
    pair_slack = slack(x, worths, pair)
    if sum(raw_slacks, F(0)) != F(m - 1) * pair_slack:
        raise AssertionError((name, raw_slacks, pair_slack))
    cover_weight = F(1, 2 * (m - 1))
    cover_currency = cover_weight * sum(raw_slacks, F(0))
    if cover_currency != pair_slack / 2:
        raise AssertionError((name, cover_currency, pair_slack / 2))
    return {
        "name": name,
        "rows": rows,
        "blocks": blocks,
        "raw_identity_loads": raw_loads,
        "row_slacks_at_x": raw_slacks,
        "pair_slack_at_x": pair_slack,
        "normalized_cover_weight": cover_weight,
        "normalized_cover_currency": cover_currency,
        "transport_rhs": F(m - 1) * pair_slack,
        "transport_equality": True,
    }


def singleton_exceptional_fail_open():
    # Relabelled catalogue type 41 from an exact n=6 strict-order discovery
    # cell.  The point satisfies the displayed core inequalities but is not an
    # exact game: this one packet has deficit 609/178.
    n = 6
    full = (1 << n) - 1
    exceptional = 1 << 5
    rows = (37, 38, 56, 43, 51)  # 025,125,345,0135,0145
    weights = (F(2), F(2), F(3), F(1), F(1))
    beta, ambient = F(5), F(4)
    identity_loads = check_identity(n, rows, weights, exceptional, beta, ambient)
    z = tuple(F(value) for value in ("1/89", "1/178", "21/178", "16/89", 0, "61/89"))
    worths = {
        37: F(145, 178),
        38: F(72, 89),
        56: F(77, 89),
        43: F(157, 178),
        51: F(62, 89),
        exceptional: F(0),
    }
    row_slacks = tuple(slack(z, worths, row) for row in rows)
    if any(value < 0 for value in row_slacks):
        raise AssertionError(("not core-feasible on packet rows", row_slacks))
    lhs = sum((weight * value for weight, value in zip(weights, row_slacks)), F(0))
    rhs = beta * slack(z, worths, exceptional)
    if lhs >= rhs or rhs - lhs != F(609, 178):
        raise AssertionError((lhs, rhs, rhs - lhs))
    return {
        "catalogue_type": 41,
        "rows": rows,
        "weights": weights,
        "exceptional_singleton": exceptional,
        "exceptional_coefficient": beta,
        "ambient_load": ambient,
        "identity_loads": identity_loads,
        "allocation": z,
        "row_slacks": row_slacks,
        "weighted_positive_slack": lhs,
        "required_singleton_payment": rhs,
        "exactness_packet_deficit": rhs - lhs,
        "classification": "fail-open nonexact core-selector relaxation",
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
    pxc101_x = tuple(F(v) for v in ("9/2", "9/2", 2, 2, 2, 2))
    pxc101_z = tuple(F(v) for v in (4, 4, 3, 3, 2, 1))
    pxc104_x = tuple(F(v) for v in ("41/6", "41/6", "7/3", "7/3", "7/3", "7/3"))
    pxc104_z = tuple(F(v) for v in (6, 6, 5, 4, 1, 1))
    pair = 3
    controls = [
        partition_star("PXC101_PXC102_six_player_anchor", pxc101_x, pxc101_z,
                       pair, (4, 8, 48)),
        partition_star("PXC104_cross_cover_minus", pxc104_x, pxc104_z, pair, (8, 16, 36)),
        partition_star("PXC104_cross_cover_plus", pxc104_x, pxc104_z, pair, (8, 20, 32)),
        partition_star("PXC118_additional_two_block_cover", pxc104_x, pxc104_z,
                       pair, (8, 52)),
    ]
    if {item["normalized_cover_currency"] for item in controls[1:]} != {F(5, 6)}:
        raise AssertionError("reciprocal covers should expose the same pair-shear budget")
    payload = {
        "claim": "PXC130 exceptional-set witness slack transport",
        "symbolic_statement": (
            "if sum lambda_S 1_S = q 1 + beta 1_E and w^E attains v(E), then "
            "sum lambda_S[y(S)-v(S)] >= beta[y(E)-v(E)] for every core y"
        ),
        "partition_star_controls": controls,
        "singleton_exceptional_fail_open_control": singleton_exceptional_fail_open(),
        "scope": {
            "proved_conventionally": (
                "dimension-free witness/slack transport and partition-star comparison-budget "
                "conservation"
            ),
            "not_proved": (
                "universal existence of a demand-paying packet or aggregation to the full "
                "hybrid-overlap deficit"
            ),
            "reciprocal_warning": (
                "alternative cross covers expose the same exceptional-pair budget; their "
                "facet inequalities cannot be added as independent currency without a new "
                "disjoint label/witness argument"
            ),
        },
    }
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
