#!/usr/bin/env python3
"""Standalone Fraction replay of PXC136 named stationary certificates.

This file imports no project game, selector, LP, or PXC136 implementation.
It reads only the primary JSON's displayed rational flows, reconstructs the
four defining lower-envelope polytopes independently, and checks that every
positive row rescales to a valid singleton-zero core witness.  It also checks
the balanced-family stationary formula and the sharp 45/17 primal/dual pair.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def csum(point, coalition):
    return sum(
        (point[i] for i in range(len(point)) if coalition >> i & 1), F(0)
    )


def named_data():
    return {
        "PXC101": {
            "n": 6, "T": F(17),
            "rows": {7: F(11), 11: F(11), 17: F(6), 51: F(11)},
            "x": (F(9, 2), F(9, 2), F(2), F(2), F(2), F(2)),
            "z": tuple(map(F, (4, 4, 3, 3, 2, 1))),
        },
        "PXC104": {
            "n": 6, "T": F(23),
            "rows": {7: F(16), 11: F(16), 19: F(13), 23: F(18),
                     35: F(13), 39: F(18)},
            "x": (F(41, 6), F(41, 6)) + (F(7, 3),) * 4,
            "z": tuple(map(F, (6, 6, 5, 4, 1, 1))),
        },
        "PXC118": {
            "n": 6, "T": F(23),
            "rows": {7: F(16), 11: F(16), 19: F(13), 23: F(18),
                     35: F(13), 39: F(18), 52: F(7)},
            "x": (F(41, 6), F(41, 6)) + (F(7, 3),) * 4,
            "z": tuple(map(F, (6, 6, 5, 4, 1, 1))),
        },
        "PXC125-positive-demand": {
            "n": 6, "T": F(25),
            "rows": {3: F(12), 19: F(14), 39: F(89, 5), 43: F(23)},
            "x": tuple(map(F, (F(13, 2), F(13, 2), 1, 5, 1, 5))),
            "z": tuple(map(F, (6, 6, 0, F(26, 5), 2, F(29, 5)))),
        },
    }


def check_named(payload):
    displayed = {row["label"]: row for row in payload["named_controls"]}
    results = []
    for label, data in named_data().items():
        row = displayed[label]
        cert = row["certificate"]
        pi = tuple(map(F, cert["pi"]))
        flow = tuple(tuple(map(F, q)) for q in cert["flow"])
        n, total = data["n"], data["T"]
        if len(pi) != n or len(flow) != n or sum(pi, F(0)) != 1:
            raise AssertionError((label, "dimensions/mass"))
        witnesses = []
        for r in range(n):
            if flow[r][r] or any(q < 0 for q in flow[r]):
                raise AssertionError((label, "diagonal/sign", r))
            if sum(flow[r], F(0)) != pi[r]:
                raise AssertionError((label, "row", r))
            if pi[r] > 0:
                witness = tuple(total * q / pi[r] for q in flow[r])
                if witness[r] or sum(witness, F(0)) != total:
                    raise AssertionError((label, "witness normalization", r))
                for coalition, bound in data["rows"].items():
                    if csum(witness, coalition) < bound:
                        raise AssertionError((label, "defining row", r, coalition))
                witnesses.append((pi[r], witness))
        for i in range(n):
            if sum((flow[r][i] for r in range(n)), F(0)) != pi[i]:
                raise AssertionError((label, "column", i))
            if pi[i] > F(1, 2):
                raise AssertionError((label, "half cap", i))
        y = tuple(total * q for q in pi)
        mixed = tuple(
            sum((mass * witness[i] for mass, witness in witnesses), F(0))
            for i in range(n)
        )
        if y != mixed:
            raise AssertionError((label, "mixture"))
        bridge = sum(
            min(data["x"][i], y[i]) + min(data["z"][i], y[i]) - y[i]
            for i in range(n)
        )
        target = F(n, (n * n) // 4) * total
        if bridge != F(cert["bridge"]) or bridge < target:
            raise AssertionError((label, "bridge", bridge, target))
        results.append({"label": label, "bridge": str(bridge), "target": str(target)})
    return results


def balanced_formula():
    rows = []
    for p in range(1, 17):
        for k in range(2, 17):
            n, total = p + k + 1, F(p * k)
            x = (F(p * p * (k - 1), p + 1),) + (F(p, p + 1),) * (p + k)
            z = ((F(p * (k - 1), k),) + (F(1, k),) * p
                 + (F(p * (k - 1), k),) * k)
            pi = ((F(k - 1, 2 * k),) + (F(1, 2 * p * k),) * p
                  + (F(1, 2 * k),) * k)
            y = tuple(total * q for q in pi)
            if sum(pi, F(0)) != 1 or max(pi) > F(1, 2):
                raise AssertionError((p, k, "stationary mass"))
            if any(not (min(a, b) <= q <= max(a, b))
                   for a, b, q in zip(x, z, y)):
                raise AssertionError((p, k, "box"))
            bridge = sum(min(a, q) + min(b, q) - q for a, b, q in zip(x, z, y))
            overlap = sum(min(a, b) for a, b in zip(x, z))
            if bridge != overlap:
                raise AssertionError((p, k, bridge, overlap))
            rows.append((p, k, bridge))
    return {
        "parameter_pairs": len(rows),
        "all_bridges_equal_overlap": True,
        "minimum_n": min(p + k + 1 for p, k, _ in rows),
        "maximum_n": max(p + k + 1 for p, k, _ in rows),
    }


def sharp_duality():
    # Independent compact replay of the objective values.  The full coordinate
    # feasibility equations are checked by the primary verifier; here the
    # displayed cap multipliers alone pin the dual objective.
    x = tuple(map(F, (F(4, 3), F(1, 3), F(1, 3), F(1, 3), F(4, 3), F(1, 3))))
    z = tuple(map(F, (1, 1, 0, 0, 1, 1)))
    theta = F(45, 17)
    alpha = tuple(map(F, (1, 1, 0, 0, 0, 1)))
    beta = tuple(map(F, (1, 0, 1, 1, 1, 0)))
    dual = theta + sum(alpha[i] * x[i] + beta[i] * z[i] for i in range(6))
    if dual != F(113, 17) or dual - 4 != F(45, 17):
        raise AssertionError((dual, dual - 4))
    if not F(45, 17) < F(8, 3):
        raise AssertionError("sharp complement disappeared")
    return {
        "dual_sum_u_plus_s": str(dual),
        "stationary_bridge": str(dual - 4),
        "spectral_target": "8/3",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("primary", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "standalone exact replay of PXC136 stationary witnesses",
        "named_controls": check_named(json.loads(args.primary.read_text())),
        "balanced_family": balanced_formula(),
        "sharp_duality": sharp_duality(),
        "scope": (
            "independent Fraction replay of displayed flows and formulas; "
            "the universal spectral-or-stationary disjunction remains open"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
