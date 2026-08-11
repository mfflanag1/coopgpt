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
from audit_lmax_overcover import coalition_sum, records  # noqa: E402


def subset_bound(x: tuple[F, ...], z: tuple[F, ...], chosen: tuple[int, ...]) -> F:
    maximum = max(z)
    lower_z = sorted((q for q in z if q < maximum), reverse=True)
    remaining_x = sorted(x[i] for i in range(len(x)) if i not in chosen)
    return sum((min(x[i], maximum) for i in chosen), F(0)) + sum(
        (min(a, b) for a, b in zip(remaining_x, lower_z)), F(0)
    )


def spectral_radius(values: tuple[F, ...], x: tuple[F, ...], z: tuple[F, ...]) -> dict:
    """Maximize (alpha.x-mu)/theta by exact Charnes-Cooper scaling."""
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
    best = None
    for maximizing_top in top:
        m = len(tight)
        eta_index = m
        u_index = {player: m + 1 + pos for pos, player in enumerate(top)}
        scale_index = m + 1 + len(top)
        width = scale_index + 1
        equalities: list[list[F]] = []
        rhs: list[F] = []
        for player in range(n):
            row = [F(0)] * width
            for pos, mask in enumerate(tight):
                row[pos] = F(int(bool(mask >> player & 1)))
            row[eta_index] = F(-1)
            if player in u_index:
                row[u_index[player]] = F(-1)
            equalities.append(row)
            rhs.append(F(0))
        row = [F(0)] * width
        for player in top:
            row[u_index[player]] = F(1)
        row[scale_index] = F(-1)
        equalities.append(row)
        rhs.append(F(0))
        row = [F(0)] * width
        row[u_index[maximizing_top]] = F(1)
        equalities.append(row)
        rhs.append(F(1))

        inequalities: list[list[F]] = []
        inequality_rhs: list[F] = []
        for variable in range(width):
            row = [F(0)] * width
            row[variable] = F(-1)
            inequalities.append(row)
            inequality_rhs.append(F(0))
        for player in top:
            row = [F(0)] * width
            row[u_index[player]] = F(1)
            inequalities.append(row)
            inequality_rhs.append(F(1))

        objective = [F(0)] * width
        for player in top:
            objective[u_index[player]] = -x[player]
        objective[scale_index] = minimum
        status, optimum, solution = exact_linprog(
            objective, inequalities, inequality_rhs, equalities, rhs
        )
        if status != "optimal":
            continue
        radius = -optimum
        scale = solution[scale_index]
        assert scale > 0
        row = {
            "maximizing_top": maximizing_top,
            "radius": radius,
            "scale": scale,
            "theta": F(1, 1) / scale,
            "eta": solution[eta_index] / scale,
            "alpha": tuple(
                solution[u_index[i]] / scale if i in u_index else F(0)
                for i in range(n)
            ),
            "coalition_weights": tuple(
                (tight[pos], solution[pos] / scale)
                for pos in range(m)
                if solution[pos] > 0
            ),
        }
        if best is None or row["radius"] > best["radius"]:
            best = row
    if best is None:
        raise RuntimeError("no normalized scaled Lmax over-cover")
    return best


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
        radius = spectral_radius(values, x, z)
        top_size = sum(q == max(z) for q in z)
        subsets = tuple(itertools.combinations(range(n), top_size))
        bad = tuple(chosen for chosen in subsets if subset_bound(x, z, chosen) < threshold)
        maximum_bad_excess = max(
            (sum((x[i] - min(x) for i in chosen), F(0)) for chosen in bad),
            default=None,
        )
        assert result["threshold_certified"]
        assert maximum_bad_excess is None or radius["radius"] > maximum_bad_excess
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
                "spectral_radius": str(radius["radius"]),
                "maximum_bad_subset_excess": (
                    None if maximum_bad_excess is None else str(maximum_bad_excess)
                ),
                "radius_certificate": {
                    "maximizing_top": radius["maximizing_top"],
                    "theta": str(radius["theta"]),
                    "eta": str(radius["eta"]),
                    "alpha": [str(q) for q in radius["alpha"]],
                    "coalition_weights": [
                        [mask, str(weight)]
                        for mask, weight in radius["coalition_weights"]
                    ],
                },
            }
        )
    return rows


def audit_archive(paths: list[Path], dimension: int) -> dict | None:
    if not paths:
        return None
    pairs = 0
    positive_floor = 0
    empty_bad = 0
    nonempty_bad = 0
    failures = []
    minimum_positive_gap = None
    for source in paths:
        data = json.loads(source.read_text())
        for _source, trail, values, x, z in records(data, source):
            if len(x) != dimension:
                continue
            pairs += 1
            if min(x) == 0:
                continue
            positive_floor += 1
            threshold = F(4 * dimension, dimension * dimension - (dimension % 2)) * values[-1]
            radius = spectral_radius(values, x, z)["radius"]
            top_size = sum(q == max(z) for q in z)
            bad = tuple(
                chosen
                for chosen in itertools.combinations(range(dimension), top_size)
                if subset_bound(x, z, chosen) < threshold
            )
            if not bad:
                empty_bad += 1
                continue
            nonempty_bad += 1
            maximum_bad_excess = max(
                sum((x[i] - min(x) for i in chosen), F(0)) for chosen in bad
            )
            gap = radius - maximum_bad_excess
            if gap <= 0:
                failures.append(
                    {
                        "source": str(source),
                        "trail": trail,
                        "radius": str(radius),
                        "maximum_bad_subset_excess": str(maximum_bad_excess),
                    }
                )
            elif minimum_positive_gap is None or gap < minimum_positive_gap:
                minimum_positive_gap = gap
    return {
        "dimension": dimension,
        "pairs": pairs,
        "positive_floor_pairs": positive_floor,
        "empty_bad_family": empty_bad,
        "nonempty_bad_family": nonempty_bad,
        "spectral_radius_failures": len(failures),
        "first_failure": failures[0] if failures else None,
        "minimum_positive_radius_gap": (
            None if minimum_positive_gap is None else str(minimum_positive_gap)
        ),
        "scope": "finite exact archive regression only",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact rational spectral-threshold oracle controls",
        "criterion": (
            "a threshold is certified iff some normalized over-cover excludes "
            "every below-threshold spectral subset with positive common margin"
        ),
        "cases": controls(),
        "archive": audit_archive(args.paths, args.n),
        "scope": "algorithmic oracle and hostile controls; not a proof of SRE for all exact games",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
