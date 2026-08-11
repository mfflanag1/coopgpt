#!/usr/bin/env python3
"""Exact n=7 hostile check of the G(p,k) shared-hinge certificates.

The balanced seven-player master family has two orientations: (p,k)=(2,4)
and (3,3).  For each, this verifier checks the proved closed-form Lmin and
Lmax allocations and three incidence objects supported on the common tight
coalitions C_b={head} union (B minus {b}):

* the sparse first-stage Lmax over-cover;
* the first-stage Lmin under-cover;
* one rooted block-star packet for every omitted b.

The last packet's exact-game slack inequality is saturated.  This identifies
the common hinge used by both lexicographic normal systems in the extremal
family.  It is an example audit, not a general hybrid-overlap proof.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def coalition_sum(point, mask):
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def incidence(mask, player):
    return F(int(bool(mask >> player & 1)))


def audit(p: int, k: int):
    n = p + 1 + k
    head = 0
    ones = tuple(range(1, p + 1))
    block = tuple(range(p + 1, n))
    full = (1 << n) - 1
    g = (F(p * (k - 1)),) + (F(1),) * p + (F(0),) * k
    h = (F(0),) * (p + 1) + (F(p),) * k
    values = [
        min(coalition_sum(g, mask), coalition_sum(h, mask))
        for mask in range(1 << n)
    ]
    q = F(p, p + 1)
    maximum = F(p * (k - 1), k)
    expected_x = (F(p * p * (k - 1), p + 1),) + (q,) * (p + k)
    expected_z = (maximum,) + (F(1, k),) * p + (maximum,) * k
    x = expected_x
    z = expected_z
    assert all(values[1 << i] == 0 for i in range(n))
    assert sum(x, F(0)) == values[full] == sum(z, F(0))
    for mask in range(1, full):
        assert coalition_sum(x, mask) >= values[mask]
        assert coalition_sum(z, mask) >= values[mask]

    coalitions = {}
    for omitted in block:
        mask = 1 << head
        for player in block:
            if player != omitted:
                mask |= 1 << player
        coalitions[omitted] = mask
        assert coalition_sum(x, mask) == values[mask]
        assert coalition_sum(z, mask) == values[mask]

    # Lmax over-cover: equal weight 1/k^2 on the k common hinges.
    oc_weight = F(1, k * k)
    alpha = [F(0)] * n
    alpha[head] = F(1, k)
    for player in block:
        alpha[player] = F(k - 1, k * k)
    assert sum(alpha, F(0)) == 1
    for player in range(n):
        load = sum(
            (oc_weight * incidence(mask, player) for mask in coalitions.values()),
            F(0),
        )
        assert load == alpha[player]
    assert sum((alpha[i] * x[i] for i in range(n)), F(0)) == maximum

    # Lmin under-cover on the same menu.
    uc_weight = F(1, k * (p + 1))
    xi = F(1, p + 1)
    beta = [F(0)] * n
    for player in ones:
        beta[player] = F(1, p + 1)
    for player in block:
        beta[player] = F(1, k * (p + 1))
    assert sum(beta, F(0)) == 1
    for player in range(n):
        load = sum(
            (uc_weight * incidence(mask, player) for mask in coalitions.values()),
            F(0),
        )
        assert load == xi - beta[player]
    assert sum((beta[i] * z[i] for i in range(n)), F(0)) == q
    packing_loads = [
        alpha[i] / F(1, k) + beta[i] / F(1, p + 1) for i in range(n)
    ]
    assert packing_loads == [F(1)] * n

    # Each hinge extends to a rooted block-star circuit.  Its budget is tight.
    rooted = []
    root_mask = 1 << head
    root_slack = coalition_sum(x, root_mask) - values[root_mask]
    for omitted, protector in coalitions.items():
        spokes = tuple(root_mask | (1 << player) for player in ones + (omitted,))
        for player in range(n):
            lhs = incidence(protector, player)
            lhs += sum((incidence(mask, player) for mask in spokes), F(0))
            lhs -= F(p + 1) * incidence(root_mask, player)
            assert lhs == 1
        spoke_slack = sum(
            (coalition_sum(x, mask) - values[mask] for mask in spokes), F(0)
        )
        assert spoke_slack == F(p + 1) * root_slack
        rooted.append(
            {
                "omitted_block_player": omitted,
                "protector_mask": protector,
                "spoke_masks": list(spokes),
                "root_coefficient": p + 1,
                "saturated_slack_budget": str(spoke_slack),
            }
        )

    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    target = F(n, k * (p + 1)) * sum(x, F(0))
    assert overlap == target
    return {
        "p": p,
        "k": k,
        "n": n,
        "total": str(sum(x, F(0))),
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "overlap": str(overlap),
        "overlap_target": str(target),
        "common_hinge_masks": list(coalitions.values()),
        "lmax_overcover": {
            "coalition_weight": str(oc_weight),
            "alpha": [str(value) for value in alpha],
            "eta": "0",
        },
        "lmin_undercover": {
            "coalition_weight": str(uc_weight),
            "xi": str(xi),
            "beta": [str(value) for value in beta],
        },
        "normalized_fractional_packing_loads": [
            str(value) for value in packing_loads
        ],
        "rooted_packets": rooted,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "solver-free exact closed-form and incidence audit",
        "cases": [audit(2, 4), audit(3, 3)],
        "selection_dependency": (
            "uses the proved closed forms for G(p,k); existing generic staged "
            "replays are separate evidence"
        ),
        "scope": "balanced n=7 G(p,k) equality family only; not a general proof",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
