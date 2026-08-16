#!/usr/bin/env python3
r"""Exact controls for two-stratum spectral closure (PXC75).

At an ordered saturated ceiling root whose Lmax point is two-stratum
(`M` on the root and every gainer, `zeta` on every outsider) and whose
proper Lmax-tight menu is exactly the `gk` decorated co-stars, the
first-stage over-cover linear program depends only on the menu incidence,
so symmetrization pins the canonical dispersion at
`theta=(k-1)/(gk-g-1)`, and the sharpened spectral bound obeys the
dimension-free chain

    B >= (M+s*-f)(gk-g-1)/(k-1) + (g+1)f + k*zeta + M - x_r
      >= (M-zeta)(gk-g-1)/(k-1) + n*zeta + M - x_r,

with `f=min x >= zeta` and over-cover surplus `s*>=0`.  The root closes
the hybrid target whenever the right side dominates it (PXC75b).  This
driver checks the hypotheses instance by instance on a fixed
two-generator family grid, replays the chain exactly, and pins how far
(PXC75b) reaches; the named packet-violation controls must all close.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_lmax_overcover import top_certificate  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_spectral_or_reserve import (  # noqa: E402
    family_instance,
    margins,
    selectors,
)


NAMED_CONTROLS = (
    ((4, 4, 4), 7, (3, 1, 1)),
    ((4, 4, 4), 7, (2, 2, 1)),
    ((5, 5, 5), 8, (4, 2, 1)),
    ((5, 5, 5), 8, (3, 3, 1)),
    ((6, 6, 6), 10, (5, 2, 1)),
    ((6, 6, 6), 10, (4, 2, 2)),
    ((6, 6, 6), 10, (3, 3, 2)),
    ((4, 4, 4, 4), 11, (3, 1, 1)),
    ((4, 4, 4, 4), 11, (2, 2, 1)),
)


def audit_instance(a, H, w):
    """Check the PXC75 hypotheses and replay the chain; None if outside."""
    generators = family_instance(a, H, w)
    n = len(generators[0])
    g = len(a)
    k = len(w)
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    if x == z:
        return None
    M = z[0]
    if not all(z[i] == M for i in range(1, 1 + g)):
        return None
    zetas = tuple(z[j] for j in range(1 + g, n))
    if not all(M > value >= 0 for value in zetas):
        return None
    zeta_min = min(zetas)
    uniform = len(set(zetas)) == 1
    full = (1 << n) - 1
    menu = {
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == values[coalition]
    }
    expected = set()
    for omitted in range(1, 1 + g):
        for outsider in range(1 + g, n):
            coalition = 1 | (1 << outsider)
            for gainer in range(1, 1 + g):
                if gainer != omitted:
                    coalition |= 1 << gainer
            expected.add(coalition)
    if not expected <= menu:
        return None
    rooted_extras = [
        coalition for coalition in menu - expected if coalition & 1
    ]
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1 or roots[0][0] != 0:
        return None
    if any(x[i] > M for i in range(1, n)):
        return None

    delta = g * k - g - 1
    cert = top_certificate(values, z)
    theta = F(cert["theta"])
    if theta > F(k - 1, delta):
        raise AssertionError("symmetric over-cover feasibility failed")
    spec = spectral_decomposition("p", values, x, z)
    surplus = F(spec["hinge_surplus"])
    if surplus < 0:
        raise AssertionError("over-cover surplus lost nonnegativity")
    total = sum(x, F(0))
    f = min(x)
    if f < zeta_min:
        raise AssertionError("Lmin floor fell below the outsider strata")
    required = (M + surplus - f) / theta
    values_nonroot = x[1:]
    best = None
    for subset in combinations(range(len(values_nonroot)), g):
        subset_sum = sum(values_nonroot[i] for i in subset)
        if (x[0] - f) + (subset_sum - g * f) >= required:
            if best is None or subset_sum < best:
                best = subset_sum
    if best is None:
        raise AssertionError("no eligible spectral top block")
    bound = F(spec["sharpened_spectral_bound_ratio"]) * total
    if uniform and bound != M + k * zetas[0] + best:
        raise AssertionError("sharpened bound left the two-stratum form")
    residual_bound = sum(zetas, F(0)) - sum(
        (max(value - f, F(0)) for value in zetas), F(0)
    )
    chain = (
        (M - f) * F(delta, k - 1) + (g + 1) * f + residual_bound + M - x[0]
    )
    weak = (M - zeta_min) * F(delta, k - 1) + n * zeta_min + M - x[0]
    if not bound >= chain >= weak:
        raise AssertionError("stratified spectral chain failed")
    target = F(n, (n * n) // 4) * total
    packet = margins(values, x, z)["packet_margin"]
    return {
        "a": list(a),
        "H": H,
        "w": list(w),
        "n": n,
        "bound": str(bound),
        "chain": str(chain),
        "weak_bound": str(weak),
        "target": str(target),
        "packet_margin": str(packet),
        "uniform_outsiders": uniform,
        "exact_menu": not rooted_extras and menu == expected,
        "theta_equality": theta == F(k - 1, delta),
        "rooted_extras": len(rooted_extras),
        "bound_closes": bound >= target,
        "chain_closes": chain >= target,
        "pxc75b": weak >= target,
    }


def archive_scope(paths):
    """Count how the archived ordered saturated roots meet the hypotheses."""
    counts = {"roots": 0, "qualify": 0, "top_split": 0, "unfed": 0}
    for path in paths:
        payload = json.loads(path.read_text())
        for _source, _trail, values, x, z in records(payload, path):
            for root, gainers, outsiders, _dec in ordered_saturated_roots(
                values, x, z
            ):
                counts["roots"] += 1
                n = len(x)
                ceiling = max(z)
                top_uniform = (
                    z[root] == ceiling
                    and all(z[p] == ceiling for p in gainers)
                    and all(z[j] < ceiling for j in outsiders)
                )
                fed = True
                for a in gainers:
                    for j in outsiders:
                        coalition = (1 << root) | (1 << j)
                        for b in gainers:
                            if b != a:
                                coalition |= 1 << b
                        if coalition_sum(z, coalition) != values[coalition]:
                            fed = False
                            break
                    if not fed:
                        break
                hw = all(
                    x[p] <= ceiling for p in range(n) if p != root
                )
                if not top_uniform:
                    counts["top_split"] += 1
                elif not fed:
                    counts["unfed"] += 1
                elif hw:
                    counts["qualify"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for g, k in ((2, 3), (3, 2), (2, 4), (4, 2), (3, 3), (3, 4), (4, 3)):
        for c in range(2, 6):
            total = g * c
            for H in range(c, total - k + 1):
                rest = total - H
                for w in itertools.combinations_with_replacement(
                    range(1, rest + 1), k
                ):
                    if sum(w) != rest:
                        continue
                    row = audit_instance(
                        (c,) * g, H, tuple(sorted(w, reverse=True))
                    )
                    if row is not None:
                        rows.append(row)

    named = []
    for a, H, w in NAMED_CONTROLS:
        row = audit_instance(a, H, w)
        if row is None:
            raise AssertionError(f"named control {(a, H, w)} left the regime")
        if not (F(row["packet_margin"]) < 0 and row["chain_closes"]):
            raise AssertionError(
                f"named packet violation {(a, H, w)} not chain-closed"
            )
        named.append(row)

    summary = {
        "grid_instances": len(rows),
        "grid_bound_closes": sum(row["bound_closes"] for row in rows),
        "grid_chain_closes": sum(row["chain_closes"] for row in rows),
        "grid_pxc75b": sum(row["pxc75b"] for row in rows),
        "grid_packet_violations": sum(
            F(row["packet_margin"]) < 0 for row in rows
        ),
        "grid_packet_violations_chain_closed": sum(
            F(row["packet_margin"]) < 0 and row["chain_closes"]
            for row in rows
        ),
        "grid_uniform_outsiders": sum(
            row["uniform_outsiders"] for row in rows
        ),
        "grid_exact_menu": sum(row["exact_menu"] for row in rows),
        "grid_theta_equality": sum(row["theta_equality"] for row in rows),
        "grid_rooted_extras": sum(row["rooted_extras"] for row in rows),
        "named_controls": len(named),
        "named_minimum_chain_margin": str(
            min(F(row["chain"]) - F(row["target"]) for row in named)
        ),
    }
    if args.paths:
        scope = archive_scope(args.paths)
        summary["archive_scope"] = scope
        expected_scope = {"roots": 89, "qualify": 0, "top_split": 19,
                          "unfed": 70}
        if scope != expected_scope:
            raise AssertionError(f"archive scope drifted: {scope!r}")
    payload = {
        "claim": (
            "two-stratum decorated-menu roots have dispersion (k-1)/(gk-g-1) "
            "and satisfy the dimension-free spectral chain; the chain closes "
            "every audited packet violation in the regime"
        ),
        "summary": summary,
        "rows": rows,
        "named_rows": named,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
