#!/usr/bin/env python3
"""Exact audit of the PXC129 carrier-to-cover price dichotomy.

The proof of PXC129 is the tangent/cover-identity argument in the paper.
This audit checks every named calibration with exact rational arithmetic.  It
does not claim that the positive charges aggregate to the spectral deficit;
that is the remaining mechanism-to-price problem.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def q(values):
    return tuple(F(value) for value in values)


def coalition_sum(values, mask):
    return sum((value for i, value in enumerate(values) if mask >> i & 1), F(0))


def carriers(x, z, top):
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


def separates(mask, source, sink):
    return ((mask >> source) & 1) != ((mask >> sink) & 1)


def forward(mask, source, sink):
    return bool(mask >> source & 1) and not bool(mask >> sink & 1)


def audit_cover(x, z, top, edge, rows, weights, eta, alpha):
    source, sink, length = edge
    n = len(x)
    loads = tuple(
        sum((weight for row, weight in zip(rows, weights) if row >> i & 1), F(0))
        for i in range(n)
    )
    expected = tuple(
        eta + (alpha[top.index(i)] if i in top else F(0)) for i in range(n)
    )
    if loads != expected:
        raise AssertionError(("cover loads", rows, loads, expected))
    forward_weight = sum((weight for row, weight in zip(rows, weights)
                          if forward(row, source, sink)), F(0))
    reverse_weight = sum((weight for row, weight in zip(rows, weights)
                          if forward(row, sink, source)), F(0))
    if forward_weight != reverse_weight:
        raise AssertionError(("outsider balance", edge, forward_weight, reverse_weight))
    slacks = tuple(coalition_sum(x, row) - coalition_sum(z, row) for row in rows)
    if any(slack < 0 for slack in slacks):
        raise AssertionError(("z-tight row incompatible with x", rows, slacks))
    top_currency = sum((alpha[q] * (x[i] - z[i]) for q, i in enumerate(top)), F(0))
    cover_currency = sum((weight * slack for weight, slack in zip(weights, slacks)), F(0))
    if cover_currency != top_currency:
        raise AssertionError(("cover comparison identity", cover_currency, top_currency))
    separated_currency = sum((weight * slack for row, weight, slack in zip(rows, weights, slacks)
                              if separates(row, source, sink)), F(0))
    if forward_weight == 0:
        if any(separates(row, source, sink) for row in rows):
            raise AssertionError("zero forward load did not force identical incidence")
        classification = "tangent_forced_outside_blocker"
    else:
        if separated_currency <= 0:
            raise AssertionError(("positive cover cut has no strict selection charge", rows))
        classification = "positive_top_selection_charge"
    return {
        "rows": rows,
        "weights": weights,
        "eta": eta,
        "alpha": alpha,
        "loads": loads,
        "forward_weight": forward_weight,
        "reverse_weight": reverse_weight,
        "row_slacks_at_x": slacks,
        "separated_selection_currency": separated_currency,
        "total_top_selection_currency": top_currency,
        "classification": classification,
        "tangent_direction": tuple(F(int(i == sink) - int(i == source)) for i in range(n)),
        "carrier_length": length,
    }


def audit_game(name, x, z, common_rows, covers, top=(0, 1)):
    edges = carriers(x, z, top)
    records = []
    for edge in edges:
        source, sink, _ = edge
        common_separators = tuple(row for row in common_rows if separates(row, source, sink))
        if common_separators:
            records.append({
                "edge": edge,
                "classification": "common_row_cut",
                "common_separators": common_separators,
                "covers": [],
            })
            continue
        cover_records = [audit_cover(x, z, top, edge, *cover) for cover in covers]
        records.append({
            "edge": edge,
            "classification": "unseparated_carrier_cover_dichotomy",
            "common_separators": (),
            "covers": cover_records,
        })
    return {
        "name": name,
        "x": x,
        "z": z,
        "top": top,
        "common_tight_rows": common_rows,
        "positive_canonical_carriers": edges,
        "carrier_records": records,
    }


def stringify(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [stringify(item) for item in value]
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, dict):
        return {str(key): stringify(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    half = F(1, 2)
    quarter = F(1, 4)
    games = [
        audit_game(
            "PXC101_common_forced_zero",
            q(("9/2", "9/2", 2, 2, 2, 2)), q((4, 4, 3, 3, 2, 1)),
            (7, 11),
            (((3,), (half,), F(0), (half, half)),
             ((7, 11, 51), (quarter,) * 3, quarter, (half, half))),
        ),
        audit_game(
            "PXC116_common_forced_zero",
            q(("25/4", "25/4", "1/2", "9/4", "1/2", "9/4")),
            q((6, 6, 0, 2, 1, 3)), (19, 43),
            (((3,), (half,), F(0), (half, half)),
             ((19, 47), (half, half), half, (half, half)),
             ((23, 43), (half, half), half, (half, half)),
             ((4, 19, 43), (half,) * 3, half, (half, half)),
             ((7, 19, 43), (quarter,) * 3, quarter, (half, half))),
        ),
        audit_game(
            "PXC104_reciprocal",
            q(("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            q((6, 6, 5, 4, 1, 1)), (11,),
            (((3,), (half,), F(0), (half, half)),
             ((11, 19, 39), (quarter,) * 3, quarter, (half, half)),
             ((11, 23, 35), (quarter,) * 3, quarter, (half, half))),
        ),
        audit_game(
            "PXC118_reciprocal",
            q(("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            q((6, 6, 5, 4, 1, 1)), (11, 52),
            (((3,), (half,), F(0), (half, half)),
             ((11, 55), (half, half), half, (half, half)),
             ((11, 19, 39), (quarter,) * 3, quarter, (half, half)),
             ((11, 23, 35), (quarter,) * 3, quarter, (half, half))),
        ),
        audit_game(
            "PXC127_square_falsifier_common_cut",
            q(("32/5", "32/5", 1, "51/10", 1, "51/10")),
            q((6, 6, "1/5", "26/5", "9/5", "29/5")), (19, 43),
            (((3,), (half,), F(0), (half, half)),),
        ),
        audit_game(
            "PXC90_faithful_full_rank",
            q((6, 4, 2, 2, 2, 2, 2)),
            q(("29/7", "29/7", 4, 4, "8/7", "9/7", "9/7")), (),
            (((23, 27, 39, 75, 114),
              (F(1, 7), F(1, 7), F(2, 7), F(2, 7), F(1, 7)),
              F(2, 7), (F(3, 7), F(4, 7))),),
        ),
    ]
    reciprocal = {game["name"]: game for game in games}
    boundary_edge = (2, 4, F(0))
    boundary_controls = {
        "PXC104_reciprocal_boundary": [
            audit_cover(
                reciprocal["PXC104_reciprocal"]["x"],
                reciprocal["PXC104_reciprocal"]["z"], (0, 1), boundary_edge,
                *cover,
            )
            for cover in (
                ((3,), (half,), F(0), (half, half)),
                ((11, 19, 39), (quarter,) * 3, quarter, (half, half)),
                ((11, 23, 35), (quarter,) * 3, quarter, (half, half)),
            )
        ],
        "PXC118_reciprocal_boundary": [
            audit_cover(
                reciprocal["PXC118_reciprocal"]["x"],
                reciprocal["PXC118_reciprocal"]["z"], (0, 1), boundary_edge,
                *cover,
            )
            for cover in (
                ((3,), (half,), F(0), (half, half)),
                ((11, 55), (half, half), half, (half, half)),
                ((11, 19, 39), (quarter,) * 3, quarter, (half, half)),
                ((11, 23, 35), (quarter,) * 3, quarter, (half, half)),
            )
        ],
    }
    for name in ("PXC104_reciprocal", "PXC118_reciprocal"):
        if reciprocal[name]["positive_canonical_carriers"]:
            raise AssertionError((name, "should be a zero-length carrier boundary"))
        classes = {cover["classification"]
                   for cover in boundary_controls[name + "_boundary"]}
        if classes != {"tangent_forced_outside_blocker", "positive_top_selection_charge"}:
            raise AssertionError((name, classes))
    if reciprocal["PXC101_common_forced_zero"]["positive_canonical_carriers"]:
        raise AssertionError("PXC101 should be the zero-carrier common control")
    if any(record["classification"] != "common_row_cut"
           for record in reciprocal["PXC116_common_forced_zero"]["carrier_records"]):
        raise AssertionError("PXC116 carriers should be common-separated")
    if any(record["classification"] != "common_row_cut"
           for record in reciprocal["PXC127_square_falsifier_common_cut"]["carrier_records"]):
        raise AssertionError("PXC127 carriers should be common-separated")
    if reciprocal["PXC90_faithful_full_rank"]["positive_canonical_carriers"]:
        raise AssertionError("PXC90 should be the zero-carrier faithful control")
    payload = stringify({
        "claim": "PXC129 carrier-to-cover top-selection/outside-blocker dichotomy",
        "games": games,
        "zero_length_reciprocal_boundary_controls": boundary_controls,
        "scope": {
            "proved_conventionally": (
                "for every positive concordant carrier: a common tight cut, or for each "
                "normalized z-tight top cover either positive separated-row selection "
                "currency or a tangent Lmax descent forcing an omitted z-tight blocker"
            ),
            "not_proved": (
                "that these local currencies aggregate to the full hybrid-overlap deficit"
            ),
            "calibrations": (
                "PXC101/PXC116 common branch; PXC104/PXC118 zero-length reciprocal boundary; "
                "PXC127 common-cut control; PXC90 faithful full-rank control"
            ),
        },
    })
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
