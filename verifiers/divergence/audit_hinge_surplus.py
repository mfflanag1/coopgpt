#!/usr/bin/env python3
"""Exact audit of the Lmax common-hinge surplus refinement.

For a dispersion-optimal top over-cover (lambda,alpha,eta),

    epsilon = alpha.Lmin - max(Lmax)
            = sum_A lambda_A [Lmin(A)-v(A)] >= 0.

The second identity shows that epsilon vanishes exactly when every supported
Lmax-tight coalition is also Lmin-tight.  Retaining epsilon sharpens the
spectral anchor's required Lmin excess from (M-mu)/theta to
(M+epsilon-mu)/theta.

This is an archived-game audit, not exhaustive proof evidence.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from audit_lmax_overcover import records, spectral_bound, top_certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])

    rows = []
    zero_surplus = 0
    refined_improvements = 0
    target_failures = []
    equality_rows = []
    improvement_rows = []
    surplus_counts: Counter[str] = Counter()
    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for source, trail, _v, x, z in records(data, source):
            if len(x) != 6 or sum(x, F(0)) != sum(z, F(0)) or sum(x, F(0)) <= 0:
                continue
            certificate = top_certificate(_v, z)
            surplus = sum(
                (certificate["alpha"][i] * x[i] for i in range(len(x))), F(0)
            ) - max(z)
            if surplus < 0:
                raise AssertionError("cross surplus has the wrong sign")
            old_bound = spectral_bound(x, z, certificate["theta"])
            refined_bound = spectral_bound(x, z, certificate["theta"], surplus)
            overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
            if not old_bound <= refined_bound <= overlap:
                raise AssertionError("refined spectral bound is invalid")
            zero_surplus += int(surplus == 0)
            refined_improvements += int(refined_bound > old_bound)
            surplus_counts[str(surplus)] += 1
            total = sum(x, F(0))
            row = {
                "source": str(source),
                "trail": trail,
                "surplus": str(surplus),
                "old_bound_ratio": str(old_bound / total),
                "refined_bound_ratio": str(refined_bound / total),
                "overlap_ratio": str(overlap / total),
            }
            rows.append(row)
            if overlap == F(2, 3) * total:
                equality_rows.append(row)
            if refined_bound > old_bound:
                improvement_rows.append(row)
            if min(x) > 0 and refined_bound < F(2, 3) * total:
                target_failures.append(row)

    report = {
        "status": "exact archived-game audit; not exhaustive proof evidence",
        "records_n6": len(rows),
        "zero_hinge_surplus": zero_surplus,
        "positive_hinge_surplus": len(rows) - zero_surplus,
        "strict_spectral_improvements": refined_improvements,
        "positive_floor_refined_target_failures": target_failures,
        "candidate_equality_rows": equality_rows,
        "strict_improvement_rows": improvement_rows,
        "surplus_counts": dict(sorted(surplus_counts.items())),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
