#!/usr/bin/env python3
"""Standalone Fraction replay of the PXC137 product-flow identities.

No project game, selector, LP, or PXC136/PXC137 implementation is imported.
The script constructs exact singleton-normalized lower-envelope games from
explicit allocation banks and checks the product occupation measure directly.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(len(point)) if coalition >> i & 1), F(0))


def allocation_bank(n):
    total = n + 5
    rows = []
    for r in range(n):
        point = [0] * n
        for token in range(total):
            choices = [i for i in range(n) if i != r]
            point[choices[(token * (r + 2) + r + token // max(1, n - 2)) % len(choices)]] += 1
        rows.append(tuple(map(F, point)))
        # A second, differently ordered zero-at-r witness avoids accidental
        # two-row symmetry in the lower envelope.
        point = [0] * n
        for token in range(total):
            choices = [i for i in range(n) if i != r]
            point[choices[(token * (r + 3) + 2 * r + 1) % len(choices)]] += 1
        rows.append(tuple(map(F, point)))
    if any(min(row[i] for row in rows) != 0 for i in range(n)):
        raise AssertionError("singleton zero bank")
    return tuple(rows)


def replay(n):
    bank = allocation_bank(n)
    total = sum(bank[0], F(0))
    values = tuple(
        min(coalition_sum(point, coalition) for point in bank)
        for coalition in range(1 << n)
    )
    # Every bank point lies in the lower-envelope core by construction.
    x = bank[0]
    z = bank[3]
    if x == z:
        z = bank[5]
    pi = tuple((x[i] + z[i]) / (2 * total) for i in range(n))
    flow = tuple(
        tuple((x[r] * z[i] + z[r] * x[i]) / (2 * total * total) for i in range(n))
        for r in range(n)
    )
    midpoint = tuple((x[i] + z[i]) / 2 for i in range(n))
    for r in range(n):
        if sum(flow[r], F(0)) != pi[r]:
            raise AssertionError((n, "row", r))
        for coalition in range(1, (1 << n) - 1):
            xs = coalition_sum(x, coalition)
            zs = coalition_sum(z, coalition)
            load = sum((flow[r][i] for i in range(n) if coalition >> i & 1), F(0))
            lhs_slack = total * load - pi[r] * values[coalition]
            rhs_slack = (
                x[r] * (zs - values[coalition])
                + z[r] * (xs - values[coalition])
            ) / (2 * total)
            if lhs_slack != rhs_slack or lhs_slack < 0:
                raise AssertionError((n, "slack", r, coalition, lhs_slack, rhs_slack))
    for i in range(n):
        if sum((flow[r][i] for r in range(n)), F(0)) != pi[i]:
            raise AssertionError((n, "column", i))
        if flow[i][i] != x[i] * z[i] / (total * total):
            raise AssertionError((n, "diagonal", i))
        if not min(x[i], z[i]) <= midpoint[i] <= max(x[i], z[i]):
            raise AssertionError((n, "box", i))
    overlap = sum((min(x[i], z[i]) for i in range(n)), F(0))
    bridge = sum(
        min(x[i], midpoint[i]) + min(z[i], midpoint[i]) - midpoint[i]
        for i in range(n)
    )
    if overlap != bridge:
        raise AssertionError((n, "objective", overlap, bridge))
    return {
        "n": n,
        "total": str(total),
        "bank_size": len(bank),
        "singleton_normalized": all(values[1 << i] == 0 for i in range(n)),
        "overlap": str(overlap),
        "relaxed_bridge": str(bridge),
        "diagonal_mass": str(sum((flow[i][i] for i in range(n)), F(0))),
    }


def sharp_arithmetic():
    total = F(4)
    x = (F(4, 3), F(1, 3), F(1, 3), F(1, 3), F(4, 3), F(1, 3))
    z = (F(1), F(1), F(0), F(0), F(1), F(1))
    diagonal = tuple(x[i] * z[i] / (total * total) for i in range(6))
    if diagonal != (F(1, 12), F(1, 48), F(0), F(0), F(1, 12), F(1, 48)):
        raise AssertionError("sharp product diagonal")
    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    stationary = F(45, 17)
    return {
        "overlap": str(overlap),
        "stationary_optimum_from_independently_pinned_PXC136_certificate": str(stationary),
        "positive_forced_diagonal_loss": str(overlap - stationary),
        "product_diagonal": list(map(str, diagonal)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "standalone PXC137 product-flow identity replay",
        "dimensions": [replay(n) for n in range(3, 11)],
        "sharp_control": sharp_arithmetic(),
        "scope": (
            "independent exact arithmetic for the all-dimensional product/slack identity; "
            "does not independently prove the sharp stationary optimum or the open diagonal-price bound"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
