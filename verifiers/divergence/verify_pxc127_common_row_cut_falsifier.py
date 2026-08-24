#!/usr/bin/env python3
"""Exact primary audit of the PXC127 square falsifier and row-cut price.

The example is an exact singleton-normalized six-player lower envelope.  It
falsifies only the open PXC126 square-extraction implication.  A single
retained common row nevertheless exposes a two-edge cut matching which pays
the full label currency and the positive post-top demand.
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
sys.path[:0] = [str(ROOT / "src"), str(HERE.parent), str(ARCHIVE)]

from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    coalition_minimum_with_witness,
    csum,
    selector_pair,
    tight_rows,
)
from verify_pxc108_invariant_cover_blocker_circuits import recognize  # noqa: E402
from verify_pxc121_obstruction_spectral_closure import (  # noqa: E402
    actual_top_bound,
    target_coefficient,
)


N = 6
TOTAL = F(25)
DEFINING = {3: F(12), 19: F(69, 5), 39: F(89, 5), 43: F(23), 55: F(99, 5)}
X = (F(32, 5), F(32, 5), F(1), F(51, 10), F(1), F(51, 10))
Z = (F(6), F(6), F(1, 5), F(26, 5), F(9, 5), F(29, 5))
Z_REDUCED = (F(6), F(6), F(1, 5), F(11, 2), F(9, 5), F(11, 2))
CX = (19, 43)
CUT_ROW = 43
BLOCKERS = (35, 55)


def positive(q):
    return max(F(0), q)


def cut_price(x, z, row, top=(0, 1)):
    residual = tuple(i for i in range(len(x)) if i not in top)
    inside = tuple(i for i in residual if row >> i & 1)
    outside = tuple(i for i in residual if not (row >> i & 1))
    a = {i: min(x[i], z[i]) for i in residual}
    b = {i: max(x[i], z[i]) for i in residual}

    def orientation(high, low):
        return sum((
            positive(p - q)
            for p, q in zip(
                sorted((a[i] for i in high), reverse=True),
                sorted(b[i] for i in low),
            )
        ), F(0))

    forward = orientation(inside, outside)
    reverse = orientation(outside, inside)
    return max(forward, reverse), forward, reverse, inside, outside


def mixed_cut_price(x, z, row, top=(0, 1)):
    """Maximum matching price across the cut, orienting every edge freely."""
    residual = tuple(i for i in range(len(x)) if i not in top)
    inside = tuple(i for i in residual if row >> i & 1)
    outside = tuple(i for i in residual if not (row >> i & 1))
    a = {i: min(x[i], z[i]) for i in residual}
    b = {i: max(x[i], z[i]) for i in residual}
    best = F(0)
    best_matching = ()
    for size in range(1, min(len(inside), len(outside)) + 1):
        for left in itertools.combinations(inside, size):
            for right in itertools.permutations(outside, size):
                matching = tuple(zip(left, right))
                price = sum((max(
                    positive(a[i] - b[j]), positive(a[j] - b[i])
                ) for i, j in matching), F(0))
                if price > best:
                    best, best_matching = price, matching
    return best, best_matching


def square_max(x, z, common_rows, blockers, top=(0, 1)):
    residual = tuple(i for i in range(len(x)) if i not in top)
    a = {i: min(x[i], z[i]) for i in residual}
    b = {i: max(x[i], z[i]) for i in residual}
    best = F(0)
    choices = 0
    for C in common_rows:
        for Q in blockers:
            cells = {
                (ec, eq): tuple(i for i in residual if (
                    (C >> i) & 1, (Q >> i) & 1
                ) == (ec, eq))
                for ec in (0, 1) for eq in (0, 1)
            }
            if any(not cell for cell in cells.values()):
                continue
            choices += 1
            value = positive(max(a[i] for i in cells[1, 1]) - min(
                b[i] for i in cells[0, 1]
            )) + positive(max(a[i] for i in cells[1, 0]) - min(
                b[i] for i in cells[0, 0]
            ))
            best = max(best, value)
    return best, choices


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

    values, x, z = selector_pair(DEFINING, N, TOTAL)
    if (x, z) != (X, Z):
        raise AssertionError((x, z))
    audit = audit_game("PXC127", values, x, z, pool_max=20, replay_exact=True)
    if (
        tight_rows(values, x) != CX
        or tight_rows(values, z) != (3, 19, 35, 43, 55)
        or audit["complete_cx_count"] != 1
        or audit["complete_cx_cover_matrix"] != [
            {"cx_rows": [19, 43], "faithful_cover_indices": []}
        ]
        or len(audit["covers"]) != 1
        or audit["covers"][0]["rows"] != [3]
        or tuple(map(F, audit["covers"][0]["fixed_lmax"])) != Z_REDUCED
    ):
        raise AssertionError(("certificate/cover exhaustion changed", audit))

    cover = audit["covers"][0]
    instance = {
        "label": "PXC127",
        "x": x,
        "z": z,
        "top": (0, 1),
        "cx": CX,
        "covers": [{
            "rows": tuple(cover["rows"]),
            "weights": tuple(map(F, cover["weights"])),
            "eta": F(cover["eta"]),
            "alpha": tuple(map(F, cover["alpha"])),
        }],
    }
    verdict = recognize(instance)
    if verdict["classification"] != "common-direction forced-zero":
        raise AssertionError(verdict)
    direction = tuple(map(F, verdict["common_descent_slots"][0]["direction"]))
    negative = tuple(Q for Q in tight_rows(values, z) if csum(direction, Q) < 0)
    if direction != (F(0), F(0), F(0), F(1), F(0), F(-1)) or negative != BLOCKERS:
        raise AssertionError((direction, negative))

    overlap = sum((min(p, q) for p, q in zip(x, z)), F(0))
    BH = actual_top_bound(x, z)
    target = target_coefficient(N) * TOTAL
    demand = target - BH
    label_currency = overlap - BH
    square, square_choices = square_max(x, z, CX, BLOCKERS)
    row_cut, forward, reverse, inside, outside = cut_price(x, z, CUT_ROW)
    mixed_cut, mixed_matching = mixed_cut_price(x, z, CUT_ROW)
    if (
        (overlap, BH, target, demand, label_currency)
        != (F(117, 5), F(16), F(50, 3), F(2, 3), F(37, 5))
        or square != 0
        or square_choices != 0
        or row_cut != forward
        or row_cut != label_currency
        or mixed_cut != row_cut
        or row_cut < demand
        or inside != (3, 5)
        or outside != (2, 4)
    ):
        raise AssertionError((overlap, BH, target, square, row_cut, forward, reverse))

    singleton_witnesses = []
    for player in range(N):
        value, point = coalition_minimum_with_witness(
            DEFINING, N, TOTAL, 1 << player
        )
        if value != 0 or point[player] != 0:
            raise AssertionError((player, value, point))
        singleton_witnesses.append({"player": player, "allocation": point})

    payload = {
        "claim": (
            "exact PXC126 square-only falsifier with a target-reaching "
            "common-row cut price"
        ),
        "game": {
            "total": TOTAL,
            "defining_rows": DEFINING,
            "all_coalition_values": values,
            "singleton_witnesses": singleton_witnesses,
        },
        "selectors": {"Lmin": x, "Lmax": z, "pair_lift_Lmax": Z_REDUCED},
        "tight_rows": {"x": CX, "z": tight_rows(values, z)},
        "complete_cx_count": audit["complete_cx_count"],
        "extreme_top_covers": [{
            "rows": cover["rows"], "weights": cover["weights"],
            "eta": cover["eta"], "alpha": cover["alpha"],
        }],
        "common_direction": direction,
        "outside_union_blockers": BLOCKERS,
        "currencies": {
            "overlap": overlap,
            "B_H": BH,
            "target": target,
            "D_H": demand,
            "label_currency": label_currency,
            "maximum_boolean_square": square,
            "eligible_boolean_squares": square_choices,
            "common_row_cut": CUT_ROW,
            "cut_inside": inside,
            "cut_outside": outside,
            "forward_cut_price": forward,
            "reverse_cut_price": reverse,
            "maximum_cut_price": row_cut,
            "maximum_mixed_cut_price": mixed_cut,
            "maximum_mixed_cut_matching": mixed_matching,
        },
        "conclusion": (
            "PXC126? is false, but the common row rhbK separates the two "
            "high minima b,k from the two low maxima a,j and its cut matching "
            "pays all O-B_H=37/5, far above D_H=2/3"
        ),
        "scope": (
            "one exact six-player counterexample to square extraction and a "
            "positive calibration for common-row cut pricing; not a universal "
            "common-branch theorem and not a counterexample to hybrid overlap"
        ),
    }
    rendered = json.dumps(stringify(payload), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
