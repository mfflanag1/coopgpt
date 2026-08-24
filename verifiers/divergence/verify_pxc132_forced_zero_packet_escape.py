#!/usr/bin/env python3
"""Exact audit of PXC132 forced-zero active-packet escape.

The theorem is the dimension-free dot-product argument in the manuscript.
This verifier checks its two all-dimensional common-family calibrations and
exhausts all labelled n=6 indecomposable min-semi-balanced catalogue systems
for PXC101, PXC104, and the positive-demand PXC125 control.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
ARCHIVE = HERE.parent / "search_archive"
sys.path[:0] = [str(ROOT / "verifiers" / "lib"), str(ARCHIVE), str(ROOT / "src")]

import catalogue  # noqa: E402
from unrestricted_pxc91c_exact_search import lower_envelope  # noqa: E402


def mask(*players):
    return sum(1 << player for player in players)


def permute_mask(value, permutation):
    return sum(1 << permutation[i] for i in range(len(permutation)) if value >> i & 1)


def csum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def derivative(direction, coalition):
    return csum(direction, coalition)


def labelled_systems(n):
    _, rows = catalogue.load(n)
    seen = set()
    for type_index, row in enumerate(rows, start=1):
        for permutation in itertools.permutations(range(n)):
            lam = tuple(sorted(
                (permute_mask(coalition, permutation), coefficient)
                for coalition, coefficient in row["lam"].items()
            ))
            if lam in seen:
                continue
            seen.add(lam)
            yield type_index, dict(lam), row["r"]


def forced_zero_family_checks():
    pxc101, pxc125 = [], []
    for k in range(2, 65):
        n = k + 4
        outsiders = tuple(range(4, n))
        blocker = mask(0, 4)
        menu = (mask(0, 1), mask(0, 1, 2), mask(0, 1, 3), blocker,
                mask(0, 1, *outsiders))
        direction = [F(0)] * n
        direction[4] = F(-(k - 1))
        for player in range(5, n):
            direction[player] = F(1)
        if sum(direction, F(0)) or derivative(direction, blocker) >= 0:
            raise AssertionError(("PXC101 direction", k))
        if any(derivative(direction, row) for row in menu if row != blocker):
            raise AssertionError(("PXC101 forced-zero menu", k))
        if k in (2, 3, 4, 8, 16, 32, 64):
            pxc101.append({"n": n, "blocker_derivative": derivative(direction, blocker)})

    for t in range(1, 65):
        n = t + 5
        block = tuple(range(5, n))
        blocker = mask(0, 1, 2, *block)
        menu = (
            mask(0, 1), mask(2), mask(0, 1, 2), mask(0, 1, 4),
            mask(0, 1, 2, 4), blocker, mask(0, 1, 3, *block),
            mask(0, 1, 2, 3, *block),
        )
        direction = [F(0)] * n
        direction[3] = F(t)
        for player in block:
            direction[player] = -F(1)
        if sum(direction, F(0)) or derivative(direction, blocker) != -t:
            raise AssertionError(("PXC125 direction", t))
        if any(derivative(direction, row) for row in menu if row != blocker):
            raise AssertionError(("PXC125 forced-zero menu", t))
        if t in (1, 2, 3, 7, 15, 31, 64):
            pxc125.append({"n": n, "blocker_derivative": derivative(direction, blocker)})
    return {"PXC101": pxc101, "PXC125": pxc125}


def catalogue_audit(name, total, constraints, x, z, blockers, systems):
    values = lower_envelope(constraints, 6, total)
    ztight = {row for row in range(1, 63) if csum(z, row) == values[row]}
    records = []
    for blocker in blockers:
        active, all_ztight, root_exception, pair_exception = 0, 0, 0, 0
        prices = set()
        all_ztight_types = set()
        for type_index, lam, ambient in systems:
            exceptional = [row for row, coefficient in lam.items() if coefficient < 0]
            if len(exceptional) != 1 or lam.get(blocker, 0) <= 0:
                continue
            exceptional = exceptional[0]
            gap = F(ambient) * total - sum(
                (F(coefficient) * values[row] for row, coefficient in lam.items()), F(0)
            )
            if gap:
                continue
            active += 1
            beta = F(-lam[exceptional])
            prices.add(beta * (csum(x, exceptional) - values[exceptional]))
            positive = {row for row, coefficient in lam.items() if coefficient > 0}
            if positive <= ztight:
                all_ztight += 1
                all_ztight_types.add(type_index)
            root_exception += exceptional == 1
            pair_exception += exceptional == 3
        records.append({
            "blocker": blocker,
            "active_catalogue_packets": active,
            "active_all_positive_rows_z_tight": all_ztight,
            "all_z_tight_catalogue_types": tuple(sorted(all_ztight_types)),
            "root_exception_packets": root_exception,
            "top_pair_exception_packets": pair_exception,
            "transport_prices_at_x": tuple(sorted(prices)),
        })
    return {"name": name, "z_tight_menu": tuple(sorted(ztight)), "records": records}


def reciprocal_identity():
    rows = (11, 23, 35)
    loads = tuple(sum(1 for row in rows if row >> player & 1) for player in range(6))
    expected = (3, 3, 1, 1, 1, 1)
    if loads != expected:
        raise AssertionError((loads, expected))
    return {"rows": rows, "loads": loads, "identity": "sum rows = 1_N + 2 1_{rh}"}


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
    systems = tuple(labelled_systems(6))
    if len(systems) != 7006:
        raise AssertionError(("labelled catalogue count", len(systems)))
    games = [
        catalogue_audit(
            "PXC101_common", F(17),
            {7: F(11), 11: F(11), 17: F(6), 51: F(11)},
            tuple(F(v) for v in ("9/2", "9/2", 2, 2, 2, 2)),
            tuple(F(v) for v in (4, 4, 3, 3, 2, 1)), (17,), systems,
        ),
        catalogue_audit(
            "PXC104_reciprocal", F(23),
            {7: F(16), 11: F(16), 19: F(13), 23: F(18), 35: F(13), 39: F(18)},
            tuple(F(v) for v in ("41/6", "41/6", "7/3", "7/3", "7/3", "7/3")),
            tuple(F(v) for v in (6, 6, 5, 4, 1, 1)), (23, 39), systems,
        ),
        catalogue_audit(
            "PXC125_positive_demand_common", F(25),
            {3: F(12), 19: F(14), 39: F(89, 5), 43: F(23)},
            tuple(F(v) for v in ("13/2", "13/2", 1, 5, 1, 5)),
            tuple(F(v) for v in (6, 6, 0, "26/5", 2, "29/5")), (39,), systems,
        ),
    ]
    if games[0]["records"][0]["active_all_positive_rows_z_tight"] != 0:
        raise AssertionError("PXC101 unexpectedly acquired an all-z-tight active packet")
    if games[2]["records"][0]["active_all_positive_rows_z_tight"] != 0:
        raise AssertionError("PXC125 unexpectedly acquired an all-z-tight active packet")
    if [item["active_all_positive_rows_z_tight"] for item in games[1]["records"]] != [1, 1]:
        raise AssertionError("PXC104 reciprocal controls changed")
    payload = {
        "claim": "PXC132 forced-zero active-packet escape",
        "symbolic_family_checks": forced_zero_family_checks(),
        "labelled_n6_catalogue_systems": len(systems),
        "catalogue_calibrations": games,
        "reciprocal_fail_open_control": reciprocal_identity(),
        "scope": {
            "proved_conventionally": (
                "a reduced active exceptional packet containing a blocker annihilated only "
                "negatively by a common descent must use at least one positive row not tight at z"
            ),
            "not_proved": "universal selection or sufficient aggregate price of the required non-z-tight rows",
            "finite_role": "the catalogue audit is calibration only and is not used in the dimension-free proof",
        },
    }
    text = json.dumps(encode(payload), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
