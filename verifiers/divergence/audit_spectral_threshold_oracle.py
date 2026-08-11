#!/usr/bin/env python3
"""Exact threshold oracle for the optimized sparse Lmax spectral certificate.

For fixed rational v, Lmin x, Lmax z, and threshold b, a certificate proves
the spectral bound at least b iff every size-|H| subset J with B(J)<b is
excluded by the sharpened anchor.  Once a top player attaining theta=max alpha
is selected, all exclusion constraints are linear.  The oracle maximizes their
common exact margin and returns the best top choice.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402
from audit_lmax_overcover import coalition_sum  # noqa: E402


def subset_bound(x: tuple[F, ...], z: tuple[F, ...], chosen: tuple[int, ...]) -> F:
    maximum = max(z)
    lower_z = sorted((q for q in z if q < maximum), reverse=True)
    remaining_x = sorted(x[i] for i in range(len(x)) if i not in chosen)
    return sum((min(x[i], maximum) for i in chosen), F(0)) + sum(
        (min(a, b) for a, b in zip(remaining_x, lower_z)), F(0)
    )


def threshold_certificate(
    values: tuple[F, ...],
    x: tuple[F, ...],
    z: tuple[F, ...],
    threshold: F,
) -> dict:
    n = len(x)
    full = (1 << n) - 1
    minimum = min(x)
    maximum = max(z)
    top = tuple(i for i, q in enumerate(z) if q == maximum)
    tight = tuple(
        mask
        for mask in range(1, full)
        if coalition_sum(z, mask) == values[mask]
    )
    subsets = tuple(itertools.combinations(range(n), len(top)))
    bad = tuple(chosen for chosen in subsets if subset_bound(x, z, chosen) < threshold)
    excess = {chosen: sum((x[i] - minimum for i in chosen), F(0)) for chosen in bad}

    best = None
    for maximizing_top in top:
        m = len(tight)
        eta_index = m
        alpha_index = {player: m + 1 + pos for pos, player in enumerate(top)}
        theta_index = m + 1 + len(top)
        margin_index = theta_index + 1
        width = margin_index + 1

        equalities: list[list[F]] = []
        rhs: list[F] = []
        for player in range(n):
            row = [F(0)] * width
            for pos, mask in enumerate(tight):
                row[pos] = F(int(bool(mask >> player & 1)))
            row[eta_index] = F(-1)
            if player in alpha_index:
                row[alpha_index[player]] = F(-1)
            equalities.append(row)
            rhs.append(F(0))
        row = [F(0)] * width
        for player in top:
            row[alpha_index[player]] = F(1)
        equalities.append(row)
        rhs.append(F(1))
        row = [F(0)] * width
        row[alpha_index[maximizing_top]] = F(1)
        row[theta_index] = F(-1)
        equalities.append(row)
        rhs.append(F(0))
        if not bad:
            row = [F(0)] * width
            row[margin_index] = F(1)
            equalities.append(row)
            rhs.append(F(0))

        inequalities: list[list[F]] = []
        inequality_rhs: list[F] = []
        # Coalition weights, eta, alpha, and theta are nonnegative.  The
        # common strictness margin is free and maximized.
        for variable in range(theta_index + 1):
            row = [F(0)] * width
            row[variable] = F(-1)
            inequalities.append(row)
            inequality_rhs.append(F(0))
        for player in top:
            row = [F(0)] * width
            row[alpha_index[player]] = F(1)
            row[theta_index] = F(-1)
            inequalities.append(row)
            inequality_rhs.append(F(0))
        for chosen in bad:
            # margin <= alpha.x - mu - theta*E_J
            row = [F(0)] * width
            row[margin_index] = F(1)
            for player in top:
                row[alpha_index[player]] -= x[player]
            row[theta_index] += excess[chosen]
            inequalities.append(row)
            inequality_rhs.append(-minimum)

        objective = [F(0)] * width
        if bad:
            objective[margin_index] = F(-1)
        status, optimum, solution = exact_linprog(
            objective, inequalities, inequality_rhs, equalities, rhs
        )
        if status != "optimal":
            continue
        margin = -optimum
        row = {
            "maximizing_top": maximizing_top,
            "margin": margin,
            "theta": solution[theta_index],
            "eta": solution[eta_index],
            "alpha": tuple(
                solution[alpha_index[i]] if i in alpha_index else F(0)
                for i in range(n)
            ),
            "coalition_weights": tuple(
                (tight[pos], solution[pos])
                for pos in range(m)
                if solution[pos] > 0
            ),
        }
        if best is None or row["margin"] > best["margin"]:
            best = row

    if best is None:
        raise RuntimeError("no normalized Lmax over-cover")
    best["threshold_certified"] = not bad or best["margin"] > 0
    best["bad_subset_count"] = len(bad)
    return best


def controls() -> list[dict]:
    from verify_n7_staged_congestion_obstruction import G as G7, H as H7, X as X7, Z as Z7
    from verify_n8_coefficient_seven_obstruction import G as G8, H as H8, X as X8, Z as Z8

    rows = []
    for name, g, h, x, z in (
        ("n7_coefficient_two", G7, H7, X7, Z7),
        ("n8_coefficient_seven", G8, H8, X8, Z8),
    ):
        n = len(x)
        values = tuple(
            min(coalition_sum(g, mask), coalition_sum(h, mask))
            for mask in range(1 << n)
        )
        threshold = F(4 * n, n * n - (n % 2)) * values[-1]
        result = threshold_certificate(values, x, z, threshold)
        assert result["threshold_certified"]
        rows.append(
            {
                "name": name,
                "n": n,
                "threshold": str(threshold),
                "bad_subset_count": result["bad_subset_count"],
                "best_strict_margin": (
                    str(result["margin"]) if result["bad_subset_count"] else "not needed"
                ),
                "maximizing_top": result["maximizing_top"],
                "theta": str(result["theta"]),
                "eta": str(result["eta"]),
                "alpha": [str(q) for q in result["alpha"]],
                "coalition_weights": [
                    [mask, str(weight)] for mask, weight in result["coalition_weights"]
                ],
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact rational spectral-threshold oracle controls",
        "criterion": (
            "a threshold is certified iff some normalized over-cover excludes "
            "every below-threshold spectral subset with positive common margin"
        ),
        "cases": controls(),
        "scope": "algorithmic oracle and hostile controls; not a proof of SRE for all exact games",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
