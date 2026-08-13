#!/usr/bin/env python3
"""Exact arithmetic audit of the balanced weighted four-role seesaw theorem.

The human proof gives the two unclipped selector positions and uses the
nonexpansiveness of clipping.  This script exhausts all positive integer
four-role weight vectors through total atomic weight 40, checks the formula
and target inequality exactly, and records the sharp margins by n.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402


def target(n):
    return F(4 * n, n * n - (n % 2))


def row(h):
    rising_large, rising_small = max(h[0], h[2]), min(h[0], h[2])
    falling_large, falling_small = max(h[1], h[3]), min(h[1], h[3])
    t_lmin = F(rising_large, rising_large + falling_large)
    t_lmax = F(rising_small, rising_small + falling_small)
    overlap_ratio = F(1) - abs(t_lmin - t_lmax)
    n = sum(h)
    if overlap_ratio < target(n):
        raise AssertionError((h, overlap_ratio, target(n)))
    # The displayed harmonic lower bound, choosing the orientation of the
    # absolute difference, is checked separately from the target arithmetic.
    if t_lmin >= t_lmax:
        harmonic = F(1, rising_large + falling_large) + F(
            1, rising_small + falling_small
        )
    else:
        harmonic = F(1, rising_large + falling_large) + F(
            1, rising_small + falling_small
        )
    if overlap_ratio < harmonic or harmonic < target(n):
        raise AssertionError((h, overlap_ratio, harmonic, target(n)))
    # Clipping both selector positions to a common rational interval cannot
    # increase their distance.  Audit a fixed exact grid of interval endpoints.
    for left_index in range(9):
        for right_index in range(left_index, 9):
            left, right = F(left_index, 8), F(right_index, 8)
            clipped_lmin = min(max(t_lmin, left), right)
            clipped_lmax = min(max(t_lmax, left), right)
            clipped_overlap = F(1) - abs(clipped_lmin - clipped_lmax)
            if clipped_overlap < overlap_ratio:
                raise AssertionError((h, left, right))
    return overlap_ratio, harmonic


def exact_staged_line(weights, width, left, right, mode):
    """Independently recompute a clipped seesaw selector by staged exact LP."""
    pinned, free, trace = {}, set(range(4)), []
    while free:
        # Variables are t and the free per-capita stage level s.
        aub = [[F(-1), F(0)], [F(1), F(0)]]
        bub = [-left, right]
        aeq, beq = [], []
        for role, payoff in pinned.items():
            slope = F(1 if role in (0, 2) else -1)
            intercept = F(0 if role in (0, 2) else width)
            aeq.append([slope, F(0)])
            beq.append(payoff - intercept)
        for role in free:
            slope = F(1 if role in (0, 2) else -1)
            intercept = F(0 if role in (0, 2) else width)
            if mode == "min":
                aub.append([-slope, F(weights[role])])
                bub.append(intercept)
            else:
                aub.append([slope, F(-weights[role])])
                bub.append(-intercept)
        objective = [F(0), F(-1 if mode == "min" else 1)]
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        if status != "optimal":
            raise AssertionError((weights, width, left, right, mode, status))
        level = -optimum if mode == "min" else optimum
        aeq.append([F(0), F(1)])
        beq.append(level)
        newly = []
        for role in sorted(free):
            slope = F(1 if role in (0, 2) else -1)
            intercept = F(0 if role in (0, 2) else width)
            direction = [F(-slope if mode == "min" else slope), F(0)]
            status, optimum, _ = exact_linprog(direction, aub, bub, aeq, beq)
            if status != "optimal":
                raise AssertionError((mode, role, status))
            extreme = (-optimum if mode == "min" else optimum) + intercept
            if extreme == weights[role] * level:
                newly.append(role)
        if not newly:
            raise AssertionError((mode, "stage pinned nobody", level))
        for role in newly:
            pinned[role] = weights[role] * level
            free.remove(role)
        trace.append({"level": str(level), "newly_pinned_roles": newly})
    return tuple(pinned[i] for i in range(4)), trace


def staged_controls():
    inputs = (
        ((5, 1, 1, 1), F(6), F(0), F(5)),
        ((3, 1, 1, 1), F(7), F(0), F(7)),
        ((4, 2, 1, 1), F(9), F(1), F(8)),
        ((1, 6, 14, 12), F(60), F(9), F(24)),
        ((8, 3, 2, 5), F(11), F(2), F(10)),
        ((2, 7, 9, 4), F(13), F(5), F(9)),
    )
    controls = []
    for weights, width, left, right in inputs:
        rising_large, rising_small = max(weights[0], weights[2]), min(weights[0], weights[2])
        falling_large, falling_small = max(weights[1], weights[3]), min(weights[1], weights[3])
        expected_lmin_t = min(max(width * F(rising_large, rising_large + falling_large), left), right)
        expected_lmax_t = min(max(width * F(rising_small, rising_small + falling_small), left), right)
        lmin, lmin_trace = exact_staged_line(weights, width, left, right, "min")
        lmax, lmax_trace = exact_staged_line(weights, width, left, right, "max")
        if lmin[0] != expected_lmin_t or lmax[0] != expected_lmax_t:
            raise AssertionError((weights, lmin, lmax, expected_lmin_t, expected_lmax_t))
        controls.append(
            {
                "weights": list(weights),
                "width": str(width),
                "interval": [str(left), str(right)],
                "lmin": [str(value) for value in lmin],
                "lmax": [str(value) for value in lmax],
                "lmin_trace": lmin_trace,
                "lmax_trace": lmax_trace,
            }
        )
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    checked = 0
    interval_checks = 0
    by_n = []
    equality_weights = []
    for n in range(4, 41):
        minimum = None
        minimizers = []
        for h0 in range(1, n - 2):
            for h1 in range(1, n - h0 - 1):
                for h2 in range(1, n - h0 - h1):
                    h = (h0, h1, h2, n - h0 - h1 - h2)
                    overlap, harmonic = row(h)
                    checked += 1
                    interval_checks += 45
                    if minimum is None or overlap < minimum:
                        minimum, minimizers = overlap, [h]
                    elif overlap == minimum:
                        minimizers.append(h)
                    if overlap == target(n):
                        equality_weights.append(h)
                    if harmonic < target(n):
                        raise AssertionError(("harmonic target", h))
        by_n.append(
            {
                "n": n,
                "target": str(target(n)),
                "minimum_unclipped_overlap_ratio": str(minimum),
                "margin": str(minimum - target(n)),
                "minimizer_count": len(minimizers),
                "first_minimizer": list(minimizers[0]),
            }
        )

    report = {
        "status": "weighted balanced seesaw audit passed exactly",
        "atomic_weight_range": "4..40",
        "weight_vectors_checked": checked,
        "clipped_interval_checks": interval_checks,
        "independent_exact_staged_lp_controls": staged_controls(),
        "selector_formula": (
            "t_Lmin/W=P/(P+Q), t_Lmax/W=p/(p+q), followed by common-interval clipping"
        ),
        "overlap_formula": "O/T=1-|t_Lmin-t_Lmax|/W",
        "human_bound": (
            "orient the difference; O/T is at least 1/(P+Q)+1/(p+q), "
            "then maximize the integer product of two positive summands with total n"
        ),
        "target": "4n/[n^2-(n mod 2)]",
        "equality_weights_through_40": [list(h) for h in equality_weights],
        "rows": by_n,
        "scope": (
            "the water-filling formula and harmonic/product argument are the proof; "
            "the finite weight/clipping grids and six independently encoded staged LPs "
            "are exact regression checks"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
