#!/usr/bin/env python3
"""Exact audit of the PXC128 fractional common-cut-cover theorem.

The conventional proof is the weighted summation in the paper.  This script
checks the canonical carrier construction, the exact primal/dual LP, and the
PXC122/PXC127 and fractional/infeasible controls.  It is not evidence for the
still-open game-theoretic assertion that the resulting dual carrier measure
always extends to an MCP--MWP packet.
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
sys.path.insert(0, str(ROOT / "src"))

from exactlp import exact_linprog  # noqa: E402


def carriers(x, z, top=()):
    residual = tuple(i for i in range(len(x)) if i not in top)
    a = tuple(min(x[i], z[i]) for i in range(len(x)))
    b = tuple(max(x[i], z[i]) for i in range(len(x)))
    high = sorted(residual, key=lambda i: (-a[i], i))
    low = sorted(residual, key=lambda i: (b[i], i))
    answer = []
    for i, j in zip(high, low):
        if a[i] > b[j]:
            if i == j:
                raise AssertionError("a positive carrier cannot reuse one endpoint")
            answer.append((i, j, a[i] - b[j]))
    if len({i for i, _, _ in answer}) != len(answer):
        raise AssertionError("high endpoints are not distinct")
    if len({j for _, j, _ in answer}) != len(answer):
        raise AssertionError("low endpoints are not distinct")
    return tuple(answer)


def separates(row, edge):
    i, j, _length = edge
    return ((row >> i) & 1) != ((row >> j) & 1)


def fractional_cover(rows, edges):
    if not edges:
        return F(0), tuple(F(0) for _ in rows), F(0), ()
    incidence = tuple(
        tuple(F(int(separates(row, edge))) for row in rows) for edge in edges
    )
    if any(not any(line) for line in incidence):
        return None, None, None, None

    r = len(rows)
    primal_A = [[-incidence[e][c] for c in range(r)] for e in range(len(edges))]
    primal_b = [F(-1)] * len(edges)
    primal_A += [[F(-int(c == d)) for c in range(r)] for d in range(r)]
    primal_b += [F(0)] * r
    status, chi, theta = exact_linprog([F(1)] * r, primal_A, primal_b)
    if status != "optimal":
        raise AssertionError(("primal", status))

    q = len(edges)
    dual_A = [[incidence[e][c] for e in range(q)] for c in range(r)]
    dual_b = [F(1)] * r
    dual_A += [[F(-int(e == f)) for e in range(q)] for f in range(q)]
    dual_b += [F(0)] * q
    status, neg_dual, y = exact_linprog([F(-1)] * q, dual_A, dual_b)
    if status != "optimal" or -neg_dual != chi:
        raise AssertionError(("dual", status, chi, neg_dual))
    return chi, tuple(theta), -neg_dual, tuple(y)


def mixed_cut_price(x, z, top, row):
    residual = tuple(i for i in range(len(x)) if i not in top)
    a = tuple(min(x[i], z[i]) for i in range(len(x)))
    b = tuple(max(x[i], z[i]) for i in range(len(x)))
    left = tuple(i for i in residual if row >> i & 1)
    right = tuple(i for i in residual if not (row >> i & 1))
    best = F(0)
    for size in range(1, min(len(left), len(right)) + 1):
        for chosen in itertools.combinations(left, size):
            for partners in itertools.permutations(right, size):
                price = sum((max(
                    F(0), a[i] - b[j], a[j] - b[i]
                ) for i, j in zip(chosen, partners)), F(0))
                best = max(best, price)
    return best


def audit(name, x, z, top, rows):
    edges = carriers(x, z, top)
    label = sum((length for _, _, length in edges), F(0))
    chi, theta, dual, y = fractional_cover(rows, edges)
    cut_prices = tuple(mixed_cut_price(x, z, top, row) for row in rows)
    canonical_cut_prices = tuple(
        sum((edge[2] for edge in edges if separates(row, edge)), F(0))
        for row in rows
    )
    if any(canonical > mixed for canonical, mixed in zip(
        canonical_cut_prices, cut_prices
    )):
        raise AssertionError("canonical crossing matching exceeds P_cut")
    if chi is not None and max(cut_prices, default=F(0)) * chi < label:
        raise AssertionError("PXC128b failed")
    return {
        "name": name,
        "x": x,
        "z": z,
        "top": top,
        "rows": rows,
        "carriers": edges,
        "label_currency": label,
        "canonical_cut_prices": canonical_cut_prices,
        "mixed_cut_prices": cut_prices,
        "chi": "infinity" if chi is None else chi,
        "primal_theta": theta,
        "dual_value": "infinity" if dual is None else dual,
        "dual_carrier_weights": y,
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

    pxc122 = audit(
        "PXC122_t1",
        (F(13, 2), F(13, 2), F(1), F(5), F(1), F(5)),
        (F(6), F(6), F(0), F(26, 5), F(2), F(29, 5)),
        (0, 1), (19, 43),
    )
    pxc127 = audit(
        "PXC127",
        (F(32, 5), F(32, 5), F(1), F(51, 10), F(1), F(51, 10)),
        (F(6), F(6), F(1, 5), F(26, 5), F(9, 5), F(29, 5)),
        (0, 1), (19, 43),
    )
    triangle = audit(
        "fractional_triangle",
        (F(6), F(0), F(5), F(1), F(4), F(2)),
        (F(6), F(0), F(5), F(1), F(4), F(2)),
        (), ((1 << 0) | (1 << 2), (1 << 0) | (1 << 4),
             (1 << 2) | (1 << 4)),
    )
    uncut = audit(
        "unseparated_carrier",
        (F(4), F(0), F(3), F(1)),
        (F(4), F(0), F(3), F(1)),
        (), ((1 << 0) | (1 << 1),),
    )
    if (
        pxc122["chi"] != 1
        or pxc122["label_currency"] != 7
        or pxc127["chi"] != 1
        or pxc127["label_currency"] != F(37, 5)
        or triangle["chi"] != F(3, 2)
        or triangle["dual_value"] != F(3, 2)
        or uncut["chi"] != "infinity"
    ):
        raise AssertionError("named PXC128 controls changed")

    payload = stringify({
        "claim": "exact primal-dual audit of the PXC128 fractional common-cut-cover theorem",
        "controls": (pxc122, pxc127, triangle, uncut),
        "conclusion": (
            "finite chi gives max_C P_cut(C)>=(O-B_H)/chi; infeasible cover "
            "exposes a positive canonical carrier unseparated by every retained row"
        ),
        "scope": (
            "allocation-level dimension-free cut-cover theorem with exact rational "
            "controls; does not prove that the dual carrier measure extends to a "
            "singleton-attainment MCP--MWP packet"
        ),
    })
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
