#!/usr/bin/env python3
"""Exact audit of the sparse Lmax over-cover and spectral overlap bound.

This is a bug audit, not an exhaustive proof of the six-player theorem.  For
each archived exact game it independently reconstructs a first-stage Lmax
dual certificate

    sum_A lambda_A 1_A = eta 1_N + alpha,

where lambda is supported on Lmax-tight proper coalitions, alpha is a
probability vector supported on the Lmax top stratum, and all variables are
nonnegative.  It minimizes theta=max(alpha_i) by exact rational LP.

The certificate implies alpha.Lmin >= M.  Combining this dispersed anchor
with the rearrangement inequality for sum min(x_i,z_i) gives a label-free
spectral lower bound.  The audit checks that bound on the archived n=6 bank.
Zero-floor cases are reported separately because the human null-player
reduction sends them to the proved n<=5 theorem.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402


F = Fraction


def as_fraction(value: Any) -> F:
    if isinstance(value, bool):
        raise ValueError("boolean is not a payoff")
    if isinstance(value, (int, str)):
        return F(value)
    raise ValueError(f"non-exact payoff {value!r}")


def records(node: Any, source: Path, trail: str = "$") -> Iterator[tuple]:
    if isinstance(node, dict):
        lower = {str(key).lower(): key for key in node}
        if {"lmin", "lmax"} <= set(lower):
            raw_x = node[lower["lmin"]]
            raw_z = node[lower["lmax"]]
            raw_v = node[lower["v"]] if "v" in lower else None
            raw_g = node[lower["g"]] if "g" in lower else None
            raw_h = node[lower["h"]] if "h" in lower else None
            if isinstance(raw_x, list) and isinstance(raw_z, list):
                try:
                    x = tuple(as_fraction(q) for q in raw_x)
                    z = tuple(as_fraction(q) for q in raw_z)
                    if isinstance(raw_v, list):
                        v = tuple(as_fraction(q) for q in raw_v)
                    elif isinstance(raw_g, list) and isinstance(raw_h, list):
                        g = tuple(as_fraction(q) for q in raw_g)
                        h = tuple(as_fraction(q) for q in raw_h)
                        if len(g) != len(x) or len(h) != len(x):
                            raise ValueError("generator dimension mismatch")
                        v = tuple(
                            min(
                                sum((g[i] for i in range(len(x)) if mask >> i & 1), F(0)),
                                sum((h[i] for i in range(len(x)) if mask >> i & 1), F(0)),
                            )
                            for mask in range(1 << len(x))
                        )
                    else:
                        raise ValueError("no characteristic function or generator pair")
                except ValueError:
                    pass
                else:
                    if len(x) == len(z) and len(v) == 1 << len(x):
                        yield source, trail, v, x, z
        for key, value in node.items():
            yield from records(value, source, f"{trail}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from records(value, source, f"{trail}[{index}]")


def coalition_sum(point: tuple[F, ...], coalition: int) -> F:
    return sum(
        (point[player] for player in range(len(point)) if coalition >> player & 1),
        F(0),
    )


def top_certificate(v: tuple[F, ...], z: tuple[F, ...]) -> dict:
    """Minimize max alpha_i in the exact first-stage Lmax dual."""
    n = len(z)
    full = (1 << n) - 1
    total = sum(z)
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == v[coalition]
    )

    # Variables: lambda[tight], eta, alpha[top], theta.  exact_linprog treats
    # variables as free, so explicit nonnegativity rows are included.
    m = len(tight)
    eta_index = m
    alpha_index = {player: m + 1 + j for j, player in enumerate(top)}
    theta_index = m + 1 + len(top)
    width = theta_index + 1

    equalities = []
    equality_rhs = []
    for player in range(n):
        row = [F(0)] * width
        for j, coalition in enumerate(tight):
            row[j] = F(int(bool(coalition >> player & 1)))
        row[eta_index] = F(-1)
        if player in alpha_index:
            row[alpha_index[player]] = F(-1)
        equalities.append(row)
        equality_rhs.append(F(0))
    row = [F(0)] * width
    for player in top:
        row[alpha_index[player]] = F(1)
    equalities.append(row)
    equality_rhs.append(F(1))

    inequalities = []
    inequality_rhs = []
    for variable in range(width):
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

    objective = [F(0)] * width
    objective[theta_index] = F(1)
    status, theta, solution = exact_linprog(
        objective,
        inequalities,
        inequality_rhs,
        equalities,
        equality_rhs,
    )
    if status != "optimal":
        raise RuntimeError(f"top certificate LP returned {status}")

    lambdas = tuple(solution[j] for j in range(m))
    eta = solution[eta_index]
    alpha = tuple(
        solution[alpha_index[player]] if player in alpha_index else F(0)
        for player in range(n)
    )
    support = tuple(tight[j] for j, weight in enumerate(lambdas) if weight > 0)

    if theta <= 0 or eta < 0 or any(weight < 0 for weight in lambdas + alpha):
        raise AssertionError("certificate has an invalid sign")
    if theta != max(alpha):
        raise AssertionError("dispersion objective is not max(alpha)")
    if sum(alpha) != 1 or any(alpha[i] != 0 for i in range(n) if i not in top):
        raise AssertionError("alpha is not a probability on the top stratum")
    for player in range(n):
        load = sum(
            (lambdas[j] for j, coalition in enumerate(tight) if coalition >> player & 1),
            F(0),
        )
        if load != eta + alpha[player]:
            raise AssertionError("over-cover incidence identity failed")

    # Complementary slackness/objective identity, reconstructed exactly.
    dual_value = sum(
        (weight * v[coalition] for weight, coalition in zip(lambdas, tight)),
        F(0),
    ) - eta * total
    if dual_value != maximum:
        raise AssertionError("certificate does not attain the Lmax ceiling")

    return {
        "theta": theta,
        "eta": eta,
        "alpha": alpha,
        "support": support,
    }


def spectral_bound(
    x: tuple[F, ...],
    z: tuple[F, ...],
    theta: F,
    cross_surplus: F = F(0),
) -> F:
    """Worst overlap after forgetting labels except the dispersed top anchor."""
    n = len(x)
    minimum = min(x)
    maximum = max(z)
    top_size = sum(value == maximum for value in z)
    lower_z = sorted((value for value in z if value < maximum), reverse=True)
    required_excess = (maximum + cross_surplus - minimum) / theta
    candidates = []
    for chosen in itertools.combinations(range(n), top_size):
        if sum((x[i] - minimum for i in chosen), F(0)) < required_excess:
            continue
        remaining_x = sorted(x[i] for i in range(n) if i not in chosen)
        top_overlap = sum((min(x[i], maximum) for i in chosen), F(0))
        # min(a,b) is a Monge array; opposite sorting minimizes the sum.
        remainder_overlap = sum(
            (min(a, b) for a, b in zip(remaining_x, lower_z)), F(0)
        )
        candidates.append(top_overlap + remainder_overlap)
    if not candidates:
        raise AssertionError("the actual top block should make the anchor feasible")
    return min(candidates)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])

    rows = []
    theta_counts: Counter[str] = Counter()
    eta_zero = 0
    positive_floor = 0
    zero_floor = 0
    positive_spectral_failures = []
    equality_rows = []
    maximum_support = 0

    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for source, trail, v, x, z in records(data, source):
            if len(x) != 6 or sum(x) != sum(z) or sum(x) <= 0:
                continue
            certificate = top_certificate(v, z)
            theta = certificate["theta"]
            bound = spectral_bound(x, z, theta)
            overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
            total = sum(x)
            target = F(2, 3) * total
            if bound > overlap:
                raise AssertionError("spectral lower bound exceeds actual overlap")
            # Directly audit the cross-selection consequence of the certificate.
            if sum((a * b for a, b in zip(certificate["alpha"], x)), F(0)) < max(z):
                raise AssertionError("alpha.Lmin >= M failed")

            row = {
                "source": str(source),
                "trail": trail,
                "theta": str(theta),
                "eta": str(certificate["eta"]),
                "support_size": len(certificate["support"]),
                "overlap_ratio": str(overlap / total),
                "spectral_bound_ratio": str(bound / total),
            }
            rows.append(row)
            theta_counts[str(theta)] += 1
            eta_zero += int(certificate["eta"] == 0)
            maximum_support = max(maximum_support, len(certificate["support"]))
            if min(x) == 0:
                zero_floor += 1
            else:
                positive_floor += 1
                if bound < target:
                    positive_spectral_failures.append(row)
            if overlap == target:
                equality_rows.append(row)

    report = {
        "status": "exact archived-game audit; not exhaustive proof evidence",
        "records_n6": len(rows),
        "positive_floor_records": positive_floor,
        "zero_floor_records_reduced_to_n_le_5": zero_floor,
        "positive_floor_spectral_failures": positive_spectral_failures,
        "candidate_bound_failures_after_null_reduction": len(positive_spectral_failures),
        "theta_counts": dict(sorted(theta_counts.items())),
        "eta_zero_records": eta_zero,
        "maximum_solver_support_size": maximum_support,
        "candidate_equalities": equality_rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
