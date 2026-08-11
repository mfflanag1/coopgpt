#!/usr/bin/env python3
"""Exact checks for the dimension-free tied-ceiling two-spoke repair theorem."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def audit_row(m: int, b: F, c: F, xq: F, A: F) -> None:
    n = m + 3
    total = c + 2 * b + xq
    overlap = total - 2 * A + 2 * b
    ceiling_slack = c + b - 2 * A
    witness_slack = total - 2 * (c + b)
    order_slack = m * b - c
    target = F(n, 2 * (n - 2))
    identity = (
        ceiling_slack
        + F(2, m + 1) * order_slack
        + F(m - 1, 2 * (m + 1)) * witness_slack
    )
    if min(ceiling_slack, witness_slack, order_slack) < 0:
        raise AssertionError("infeasible theorem row")
    if overlap - target * total != identity or identity < 0:
        raise AssertionError("two-spoke master identity failed")
    if F(n, 2 * (n - 2)) < F(n, (n * n) // 4):
        raise AssertionError("two-spoke bound missed the universal target")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = 0
    equality_rows = 0
    for m in range(1, 18):
        for b_int in range(1, 8):
            b = F(b_int)
            for c_num in range(b_int, m * b_int + 1):
                c = F(c_num)
                for xq_num in range(c_num, m * b_int + 1):
                    xq = F(xq_num)
                    # The reverse common-pair comparison only requires
                    # 2A <= c+b; these exact samples include its boundary
                    # and an interior half-step whenever the sign branch
                    # b <= A <= c remains feasible.
                    candidates = {F(c + b, 2), F(c + b, 2) - F(1, 2)}
                    for A in sorted(candidates):
                        if b <= A <= c:
                            audit_row(m, b, c, xq, A)
                            rows += 1
                            total = c + 2 * b + xq
                            overlap = total - 2 * A + 2 * b
                            if overlap == F(m + 3, 2 * (m + 1)) * total:
                                equality_rows += 1

    controls = [
        # harvest6_601.json $.records[103]: r=1, spokes 0 and 3.
        {"n": 6, "b": F(3), "c": F(4), "xq": F(6), "A": F(7, 2)},
        # harvest6_602.json $.records[129]: r=4, spokes 2 and 3.
        {"n": 6, "b": F(2), "c": F(5), "xq": F(5), "A": F(7, 2)},
    ]
    control_bounds = []
    for row in controls:
        m = row["n"] - 3
        audit_row(m, row["b"], row["c"], row["xq"], row["A"])
        total = row["c"] + 2 * row["b"] + row["xq"]
        overlap = total - 2 * row["A"] + 2 * row["b"]
        control_bounds.append(str(overlap / total))

    report = {
        "status": "exact tied-ceiling two-spoke repair identity verified",
        "dimension_range": [4, 20],
        "exact_parameter_rows": rows,
        "identity_equality_rows": equality_rows,
        "theorem_bound": "n/[2(n-2)]",
        "universal_comparison": "n/[2(n-2)] >= n/floor(n^2/4) for n>=4",
        "archived_repair_controls": {
            "harvest6_601.json $.records[103]": control_bounds[0],
            "harvest6_602.json $.records[129]": control_bounds[1],
        },
        "scope": (
            "the displayed rational identity is the proof; the grid and two "
            "archived branch mappings are reproducibility controls"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
